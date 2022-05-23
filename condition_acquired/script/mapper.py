# -*- coding: UTF-8 -*
"""using UTF-8 code style"""

import os
import base64
import csv
import sys
import json 

count = int(0)
def main():
    """解析udw表,并提取出与矢量图有关的信息"""
    while True:
        global count
        try:
            line = sys.stdin.readline()
            if line == '' or line == '\n':
                break
            if len(line) < 40 or 'table_name' not in line[0:40] or line.count("\t") < 7:
                print >> sys.stderr, "line[0:36]:" + line[0:36] + '\t' + "len of line:" + str(len(line)) \
                    + '\t' + "table count:" + str(line.count('\t'))
                print >> sys.stderr, "[read line content is]:" + '\t' + str(line)
                continue
        except Exception as e:
            print >> sys.stderr, "[now is stdin.readline()]:" + '\t' + str(e)
        try:
            data_list = line.strip().split("\t")
            log_id = data_list[1]
            req_base = data_list[2]
            req_body_base64 = data_list[3]
            response = data_list[4]
            cuid = data_list[5]
            time = data_list[7]
            hour = int(data_list[8])
            response_dict = json.loads(response)
            try:
                err_code = -1
                degrade_code = -1
                sub_type = -1
                need_show_image = -1
                admin = 0
                for key, value in response_dict.iteritems():
                    if "err_code" == key:
                        err_code = int(value)
                    if "degrade_code" == key:
                        degrade_code = int(value)
                    if "need_show_image" == key:
                        need_show_image = int(value)
                    if "sub_type" == key:
                        sub_type = int(value)
                    if "admin" == key:
                        admin = int(value)
            except Exception as e:
                print >> sys.stderr, "[parse error_code error]:" + '\t' + str(e)
                continue
        except Exception as e:
            print >> sys.stderr, "[now is debase64 and json]:" + '\t' + str(e)
        
        if condition_str:
            count = count + 1
            if proportion_str:
                print req_body_base64
if __name__ == "__main__":
    main()