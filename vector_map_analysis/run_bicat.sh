#!/usr/bin/env bash

JSON_FILE="sugardata.json"
DATE_TODAY=$(date +%Y%m%d)

CURRENTPATH=$(pwd)
if [ -f "$JSON_FILE" ]; then
    rm -rf "$CURRENTPATH/data-date/backup/" && mkdir -p "$CURRENTPATH/data-date/backup/"
    cp "$JSON_FILE" "$CURRENTPATH/data-date/backup/$DATE_TODAY+'sugardata.json'"
fi

DATA=$(date -d "2 days ago" +%Y%m%d)
if [ -n "$1" ]; then
    echo "date input: $1"
    DATA=$1
else
    echo "no date input , date: ${DATA}"
fi
echo "date: + ${DATA}"

HADOOP_DIR=/home/sunkuan/output
HADOOP_CLIENT_DIR=$HADOOP_DIR/hadoop-client
LIB_DIR=/home/sunkuan/upi_mr_demo/lib
HADOOP_BIN_PATH=$HADOOP_CLIENT_DIR/hadoop/bin
export HADOOP_CLASSPATH=$HADOOP_CLASSPATH:${LIB_DIR}/upi-mr.jar
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${LIB_DIR}/native/Linux-amd64-64/
export JAVA_HOME=$HADOOP_CLIENT_DIR/java6
export LANG=en_US

INPUT_TABLE="default.udwetl_lbs_navi_sensor_data"
INPUT_PROJECT="$INPUT_TABLE#filter={event_day='$DATA' AND lbs_navi_sensor_opt2='1' AND lbs_navi_sensor_opt1 <> ''}#inputcols=event_cuid,event_device_not_from_ua,lbs_navi_sensor_opt1,event_day"
OUTPUT_DIR="/user/xingtian-map-navi/sunkuan/vector_map/vmap_err_older/$DATA"

${HADOOP_BIN_PATH}/hadoop fs -test -e "$OUTPUT_DIR"
if [ $? -eq 0 ];then
    ${HADOOP_BIN_PATH}/hadoop fs -rmr "$OUTPUT_DIR"
fi

$HADOOP_BIN_PATH/hadoop streaming -libjars ${LIB_DIR}/upi-mr.jar \
    -D stream.map.input.ignoreKey=true \
    -D mapred.job.priority=VERY_HIGH \
    -jobconf udw.upi.input="${INPUT_PROJECT}" \
    -jobconf udw.mapred.streaming.separator="\t" \
    -jobconf abaci.job.base.environment=centos6u3_hadoop \
	-input "anything" \
	-output "$OUTPUT_DIR" \
	-jobconf mapred.job.name="vector_map_sunkuan" \
    -jobconf mapred.job.queue.name=map-test_normal \
    -inputformat  MultiTableInputFormat \
	-outputformat org.apache.hadoop.mapred.TextOutputFormat \
    -mapper "./mapper.sh" \
    -file ./analysis_script/mapper.py \
    -file ./analysis_script/mapper.sh \
    -reducer "./reducer.sh" \
    -file ./analysis_script/reducer.py \
    -file ./analysis_script/reducer.sh \
    -cacheArchive /user/xingtian-map-navi/sunkuan/pythonEnv/python_env.tar.gz#pythonEnv

LOCALOUTPUT=$CURRENTPATH/data-date/vmap_err_old_version/
BACKUP_DIR=$CURRENTPATH/data-date/daily-date/
if [ -d "${LOCALOUTPUT}" ]; then
    if [ "$(ls -A "$LOCALOUTPUT")" != "" ]; then
        cp "$LOCALOUTPUT"* "$BACKUP_DIR"
        rm "$LOCALOUTPUT" -rf
        mkdir "$LOCALOUTPUT"
        FILE_NUM=$(ls "${BACKUP_DIR}" | wc -l)
        if [ $(("$FILE_NUM")) -ge 30 ]; then
            NEED_DEL_FILE="$(ls "${BACKUP_DIR}" | sort | head -n 1)"
            rm "$BACKUP_DIR$NEED_DEL_FILE"
        fi
    fi
else
    mkdir "$LOCALOUTPUT"
fi
$HADOOP_CLIENT_DIR/hadoop/bin/hadoop dfs -getmerge "$OUTPUT_DIR" "${LOCALOUTPUT}${DATA}"
$HADOOP_CLIENT_DIR/hadoop/bin/hadoop dfs -rmr "$OUTPUT_DIR"
