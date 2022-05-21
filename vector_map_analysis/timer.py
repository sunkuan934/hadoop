#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : sunkuan
# @Mail : sunkuan@baidu.com
# @Project : 定时执行某脚本
# @FileName: timer.py

import os
import datetime
import time
import logging
from testlog import Logger
import shutil


def get_file_lines_num(file_path):
    """获取当前目录下所有文件的总行数"""
    all_lines_num = 0
    del_list = os.listdir(file_path)
    for f in del_list:
        each_file_path = os.path.join(file_path, f)
        if os.path.isfile(each_file_path):
            all_lines_num = all_lines_num + len(open(each_file_path, 'r').readlines())
    return all_lines_num


def delete_file(file_path):
    """若命令执行失败，删除原来目录内的空文件"""
    del_list = os.listdir(file_path)
    for f in del_list:
        each_file_path = os.path.join(file_path, f)
        if os.path.isfile(each_file_path):
            os.remove(each_file_path)
        elif os.path.isdir(each_file_path):
            shutil.rmtree(each_file_path)


count = 0


def re_exe(inc=1000):
    """定时执行脚本"""
    global count
    sended = False
    log_file = './log/vmap_err_older/' + str(datetime.date.today()) + '-timer-log.txt'
    logger = Logger(log_file_name=log_file, log_level=logging.DEBUG, logger_name='timer').get_log()

    while True:
        today = datetime.date.today()
        # 获取2天前的日期
        date_ago = today + datetime.timedelta(days=-2)
        date_ago = date_ago.strftime('%Y%m%d')
        ts_start = datetime.datetime.now()

        if int(ts_start.hour) < 1:
            sended = False
        elif int(ts_start.hour) >= 1 and not sended and count < 5:  # 每天1点定时运行task脚本
            cmd = 'sh run_bicat.sh ' + str(date_ago)
            if os.system(cmd) == 0 and get_file_lines_num("./data-date/vmap_err_old_version/") > 10:
                cmd2 = 'python2 main.py' + ' --date ' + date_ago + \
                       ' --data_folder ./data-date/vmap_err_old_version' + \
                       ' --json_path ./sugardata.json' + \
                       ' --log_folder ./log/vmap_err_older' + \
                       ' --daily_json_path ./daily-json/vmap_err_older'
                if os.system(cmd2) == 0:
                    sended = True
                    count = 0
                    logger.info('Line 43:timer.py success!')
                else:
                    delete_file("./data-date/vmap_err_old_version/")
                    logger.info('Line 69:' + str(count + 1) + 'st try cmd2 failed!' + '\n' + 'try again!')
                    count += 1
            else:
                delete_file("./data-date/vmap_err_old_version/")
                logger.info('Line 72:' + str(count + 1) + 'st try cmd failed!' + '\n' + 'try again!')
                count += 1
        time.sleep(inc)


if __name__ == "__main__":
    re_exe(1800)
