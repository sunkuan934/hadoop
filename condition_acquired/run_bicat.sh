#!/bin/sh

CURRENTPATH=$(pwd)
DATA=$(date +%Y%m%d)
CONDITION=""
PROPORTION="True"
FIRST_CONDITION="true"
FIRST_HOUR="true"
FIRST_ERR_CODE="true"
FIRST_DEGRADE_CODE="true"
FIRST_SUB_TYPE="true"
FIRST_NEED_SHOW_IMAGE="true"
FIRST_ADMIN="true"
FIRST_CUID="true"

modify_condition () {
    # $1:i, $2:FIRST_ADMIN, $3:"FIRST_ADMIN"
    if [ ${FIRST_CONDITION} = "true" ] && [ $1 -eq 0 ]; then
        CONDITION="(${CONDITION_ELEM}"
        FIRST_CONDITION="false"
    elif [ $2 = "true" ] && [ $1 -eq 0 ]; then
        CONDITION="${CONDITION} and (${CONDITION_ELEM}"
        case $3 in
        "hour")
            FIRST_HOUR="false";;
        "err_code")
            FIRST_ERR_CODE="false";;
        "degrade_code")
            FIRST_DEGRADE_CODE="false";;
        "sub_type")
            FIRST_SUB_TYPE="false";;
        "need_show_image")
            FIRST_NEED_SHOW_IMAGE="false";;
        "admin")
            FIRST_ADMIN="false";;
        "cuid")
            FIRST_CUID="false";;
        esac
    else
        CONDITION="${CONDITION} or ${CONDITION_ELEM}"
    fi
}

for arg in $*; do
    INPUT_PARA=($(echo $arg | tr ':' ' '))
    PRE_CONDITION=${INPUT_PARA[0]}
    EACH_CONDITION=${INPUT_PARA[1]}
    OLD_IFS="$IFS" && IFS="|" && filter=(${EACH_CONDITION}) && IFS="$OLD_IFS"
    case $PRE_CONDITION in
    "-t"|"-TIME"|"-Time"|"-time")
        DATA=${EACH_CONDITION}
        if [ "$(echo ${DATA} | grep -E '20[0-9]{2}((0[1-9])|(1[012]))((0[1-9])|([12][0-9])|(3[01]))')" != ${DATA} ]; then
            echo -e "ERROR:\033[37;31m<${DATA}> is the wrong time format!\033[0m"
            echo -e "RIGHT TIME FORMAT IS:\033[37;32mYYYYMMDD, eg:20220507\033[0m"
            exit 1
        fi ;;
    "-h"|"-hour")
        PRE_CONDITION="hour"
        for i in ${!filter[*]}; do
            if (( ${filter[i]} > 23 )) || (( ${filter[i]} < 0 )); then
                echo "THE HOUR $(expr $i + 1)ST INPUT PARAMETER ERROR! CORRECT HOUR : 0, 1, 2, 3 ... and 23!"
                exit 1
            fi
            CONDITION_ELEM="${PRE_CONDITION} == ${filter[i]}"
            modify_condition ${i} ${FIRST_HOUR} ${PRE_CONDITION}
            TASK_NAME="${TASK_NAME}_${PRE_CONDITION}_${filter[i]}"
        done 
        CONDITION="${CONDITION})" ;;
    "-e"|"-err_code")
        PRE_CONDITION="err_code"
        for i in ${!filter[*]}; do
            CONDITION_ELEM="${PRE_CONDITION} == ${filter[i]}"
            modify_condition ${i} ${FIRST_ERR_CODE} ${PRE_CONDITION}
            TASK_NAME="${TASK_NAME}_${PRE_CONDITION}_${filter[i]}"
        done 
        CONDITION="${CONDITION})" ;;
    "-d"|"-degrade_code")
        PRE_CONDITION="degrade_code"
        for i in ${!filter[*]}; do
            CONDITION_ELEM="${PRE_CONDITION} == ${filter[i]}"
            modify_condition ${i} ${FIRST_DEGRADE_CODE} ${PRE_CONDITION}
            TASK_NAME="${TASK_NAME}_${PRE_CONDITION}_${filter[i]}"
        done 
        CONDITION="${CONDITION})" ;;
    "-s"|"-sub_type")
        PRE_CONDITION="sub_type"
        for i in ${!filter[*]}; do
            if (( ${filter[i]} > 4 )) || (( ${filter[i]} < 0 )); then
                echo "THE sub_type $(expr $i + 1)ST INPUT PARAMETER ERROR! CORRECT sub_type : 0, 1, 2, 3 and 4!"
                exit 1
            fi
            CONDITION_ELEM="${PRE_CONDITION} == ${filter[i]}"
            modify_condition ${i} ${FIRST_SUB_TYPE} ${PRE_CONDITION}
            TASK_NAME="${TASK_NAME}_${PRE_CONDITION}_${filter[i]}"
        done 
        CONDITION="${CONDITION})" ;;
    "-n"|"-need_show_image")
        PRE_CONDITION="need_show_image"
        for i in ${!filter[*]}; do
            if (( ${filter[i]} != 0 )) && (( ${filter[i]} != 1 )); then
                echo "THE need_show_image $(expr $i + 1)ST INPUT PARAMETER ERROR! CORRECT need_show_image：0 and 1!"
                exit 1
            fi
            CONDITION_ELEM="${PRE_CONDITION} == ${filter[i]}"
            modify_condition ${i} ${FIRST_NEED_SHOW_IMAGE} ${PRE_CONDITION}
            TASK_NAME="${TASK_NAME}_${PRE_CONDITION}_${filter[i]}"
        done
        CONDITION="${CONDITION})" ;;
    "-a"|"-admin")
        PRE_CONDITION="admin"
        for i in ${!filter[*]}; do
            if [ "$(echo ${filter[i]} | grep -E '[1-8][1-7][0-9]{4}')" != "${filter[i]}" ]; then
                echo "THE admin $(expr $i + 1)ST INPUT PARAMETER ERROR! CHECK AGAIN PLEASE!"
                exit 1
            fi
            CONDITION_ELEM="${PRE_CONDITION} == ${filter[i]}"
            modify_condition ${i} ${FIRST_ADMIN} ${PRE_CONDITION}
            TASK_NAME="${TASK_NAME}_${PRE_CONDITION}_${filter[i]}"
        done 
        CONDITION="${CONDITION})" ;;
    "-c"|"-cuid")
        PRE_CONDITION="cuid"
        for i in ${!filter[*]}; do
            CONDITION_ELEM="\"${filter[i]}\" in cuid"
            modify_condition ${i} ${FIRST_CUID} ${PRE_CONDITION}
            TASK_NAME="${TASK_NAME}_${PRE_CONDITION}_${filter[i]}"
        done
        CONDITION="${CONDITION})" ;;
    "-p")
        PROPORTION="(count % ${filter[0]} == 0)" ;;
    "-H"|"--help")
        echo '|------------------------------------------------------------------------------------------------------------------------|'
        echo '| Usage: sh run_bicat.sh "OPTION:para1|para2|para3"..."OPTION:para1|para2"                                               |'
        echo '|------------------------------------------------------------------------------------------------------------------------|'
        echo '| OPTION                | FILTER EACH_CONDITION  | PARAS EXAMPLE              | MEAN                                          |'
        echo '| -t,-TIME,-Time,-time  | data              | "-t:20220503"              | data=2022/5/3                                 |'
        echo '| -h,-hour              | hour              | "-h:12|17"                 | clock 12 or clock 17                          |'
        echo '| -e,-err_code          | err_code          | "-e:23|25"                 | err_code=23 or err_code=25                    |'
        echo '| -s,-sub_type          | sub_type          | "-s:2|3"                   | sub_type=2 or sub_type=3                      |'
        echo '| -n,-need_show_image   | need_show_image   | "-n:0"                     | need_show_image=0                             |'
        echo '| -a,-admin             | admin             | "-a:440300|440301"         | admin=440300 or admin=440301                  |'
        echo '| -c,-cuid              | cuid              | "-c:d20741b99e|4f56614d8"  | cuid string contain "d20741b99e" or 4f56614d8 |'
        echo '| -p                    | PROPORTION        | "-p:20"                    | choose one out of every 20                    |'
        echo '|------------------------------------------------------------------------------------------------------------------------|'
        exit 0;;
    esac
done

echo "${CONDITION}"
echo "task name is:vector_map_sunkuan${TASK_NAME}"

if [ -e ./bak/mapper.py ]; then
    rm ./bak/mapper.py
fi
cp ./script/mapper.py ./bak/
sed "s/condition_str/${CONDITION}/" ./script/mapper.py > mapper2.py && mv ./mapper2.py ./script/mapper.py
sed "s/proportion_str/${PROPORTION}/" ./script/mapper.py > mapper2.py && mv ./mapper2.py ./script/mapper.py

HADOOP_CLIENT_DIR=/home/zym/output/hadoop-client
LIB_DIR=/home/zym/upi_mr_demo/lib
HADOOP_BIN_PATH=$HADOOP_CLIENT_DIR/hadoop/bin
export HADOOP_CLASSPATH="$HADOOP_CLASSPATH":${LIB_DIR}/upi-mr.jar
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH":${LIB_DIR}/native/Linux-amd64-64/
export JAVA_HOME=$HADOOP_CLIENT_DIR/java6
export LANG=en_US

INPUT_PROJECT="table_name#filter={event_day='${DATA}'}#inputcols=log_id,req_basic,req_body,response,cuid,maneuver_types,event_day,event_hour"
OUTPUT_DIR="/user/xingtian-map-navi/sunkuan/vector_map/filter_data/$DATA/$TASK_NAME"

${HADOOP_BIN_PATH}/hadoop fs -test -e "${OUTPUT_DIR}"
if [ $? -eq 0 ];then
    ${HADOOP_BIN_PATH}/hadoop fs -rmr "/user/xingtian-map-navi/sunkuan/vector_map/filter_data"
    ${HADOOP_BIN_PATH}/hadoop fs -mkdir "/user/xingtian-map-navi/sunkuan/vector_map/filter_data"
fi

$HADOOP_BIN_PATH/hadoop streaming -libjars ${LIB_DIR}/upi-mr.jar \
    -D stream.map.input.ignoreKey=true \
    -D stream.tmpdir=../hadoop_tmp \
    -D mapred.job.priority=VERY_HIGH \
    -D mapred.reduce.tasks=10 \
    -jobconf udw.upi.input="${INPUT_PROJECT}" \
    -jobconf udw.mapred.streaming.separator="\t" \
    -jobconf abaci.job.base.environment=centos6u3_hadoop \
	-input "anything" \
	-output "${OUTPUT_DIR}" \
	-jobconf mapred.job.name="vector_map_sunkuan_${TASK_NAME}" \
    -jobconf mapred.job.queue.name=map-test_normal \
    -inputformat  MultiTableInputFormat \
	-outputformat org.apache.hadoop.mapred.TextOutputFormat \
    -mapper "./mapper.sh" \
    -file ./script/mapper.py \
    -file ./script/mapper.sh \
    -reducer "NONE" \
    -file ./script/reducer.py \
    -file ./script/reducer.sh \
    -cacheArchive /user/xingtian-map-navi/sunkuan/pythonEnv/python_env.tar.gz#pythonEnv

rm ./script/mapper.py && cp ./bak/mapper.py ./script/mapper.py

LOCALOUTPUT=$CURRENTPATH/result/${DATA}/${TASK_NAME}/
BACKUP_DIR=$CURRENTPATH/bak/${DATA}/${TASK_NAME}/
if [ $? -eq 0 ] && [ -d "${LOCALOUTPUT}" ]; then
    if [ "$(ls -A "${LOCALOUTPUT}")" != "" ]; then
        if [ -d "${LOCALOUTPUT}" ]; then
            rm -rf "${BACKUP_DIR}"
        else
            mkdir -p "$BACKUP_DIR"
        fi
        cp "${LOCALOUTPUT}"* "${BACKUP_DIR}"
        rm "${LOCALOUTPUT}" -rf
        mkdir "${LOCALOUTPUT}"
        FILE_NUM=$(ls "${BACKUP_DIR}" | wc -l)
        if [ $(("${FILE_NUM}")) -ge 30 ]; then
            NEED_DEL_FILE="$(ls "${BACKUP_DIR}" | sort | head -n 1)"
            rm "${BACKUP_DIR}${NEED_DEL_FILE}"
        fi
    fi
else
    mkdir -p "${LOCALOUTPUT}"
fi
$HADOOP_CLIENT_DIR/hadoop/bin/hadoop dfs -getmerge "${OUTPUT_DIR}" "${LOCALOUTPUT}${DATA}"
$HADOOP_CLIENT_DIR/hadoop/bin/hadoop dfs -rmr "${OUTPUT_DIR}"