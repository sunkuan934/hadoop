# -*- coding: UTF-8 -*

import base64
import sys
import json
import random

error_code_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                    '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                    '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
                    '30', '31', '32', '1000', '1001', '1002', '1003', '1004',
                    '1005', '1006', '1007', '100001', '10002']


all_error_info = {}
"""all_error_info= {"need_show":show_num, "3D_degrade":{error_code_dict}, "no_show":{error_code_dict}}"""
sub_type_info = {}
need_show_info = {}

def main():
    """解析udw表, 并提取出与矢量图有关的信息"""
    while True:
        try:
            global all_error_info
            global sub_type_info
            global need_show_info
            line_content = sys.stdin.readline()
            if line_content == '' or line_content == '\n':
                break
            if len(line_content) < 27 or 'udwetl_lbs_navi_sensor_data' not in line_content[0:27] or line_content.count("\t") < 4:
                print >> sys.stderr, "line[0:26]:" + line_content[0:26] + '\t' + "len of line:" + str(len(line_content)) \
                    + '\t' + "table count:" + str(line_content.count('\t'))
                print >> sys.stderr, "[read line content is]:" + '\t' + str(line_content)
                continue
        except Exception as e:
            print >> sys.stderr, "[now is stdin.readline()]:" + '\t' + str(e)

        try:
            data_list = line_content.strip().split("\t")
            base64_content = data_list[3]
            json_content = base64.b64decode(base64_content)
            guide_info = json.loads(json_content)[8].strip().split(":")
        except Exception as e:
            print >> sys.stderr, "[now is debase64 and json]:" + '\t' + str(e)

        for elem in guide_info:
            if '0|28' in elem[0:4]:
                try:
                    vector_map_info = elem.strip().split('|')
                    if len(vector_map_info) < 10 or '2' == vector_map_info[5]:
                        continue
                    sub_type_code = ''
                    if '' == vector_map_info[7]:
                        sub_type_code = 'sub_type:0'
                    else:
                        sub_type_code = 'sub_type:' + str(vector_map_info[7]) #0,1,2，3分别对应：不出图，2D, 3D，高精
                    if sub_type_code in sub_type_info.keys():
                        sub_type_info[sub_type_code] += 1
                    else:
                        sub_type_info[sub_type_code] = 1

                    need_show_info_str = ''
                    if vector_map_info[4] == '1':
                        need_show_info_str = 'show_success:'
                    else:
                        need_show_info_str = 'show_fail:'
                    if need_show_info_str in need_show_info:
                        need_show_info[need_show_info_str] += 1
                    else:
                        need_show_info[need_show_info_str] = 1

                    error_code_str = ''
                    if vector_map_info[4] == '1' or vector_map_info[9] == '' or vector_map_info[8] == '':
                        error_code_str = 'need_show:'
                    if vector_map_info[9] != '\n' and vector_map_info[9] != '' \
                        and vector_map_info[9] in error_code_list:
                        error_code_str  = '3D_degrade_error_code:' + str(vector_map_info[9])
                    elif vector_map_info[8] in error_code_list:
                        error_code_str = 'no_show_error_code:' + str(vector_map_info[8])
                    if error_code_str != '':
                        if error_code_str in all_error_info.keys():
                            count = int(all_error_info[error_code_str])
                            all_error_info[error_code_str] = int(count + 1)
                        else:
                            all_error_info[error_code_str] = 1
                except Exception as e:
                    print >> sys.stderr, "[parse vector info error code]:" + '\t' + str(e)

    for each_error_code in all_error_info.keys():
        try:
            print str(each_error_code) + '\t' + str(all_error_info[each_error_code])
        except Exception as e:
            print >> sys.stderr, "[now is print part execption]:" + '\t' + str(e)

    for sub_type_code in sub_type_info.keys():
        try:
            print str(sub_type_code) + '\t' + str(sub_type_info[sub_type_code])
        except Exception as e:
            print >> sys.stderr, "[now is print subtype]:" + '\t' + str(e)

    for need_show_info_str in need_show_info.keys():
        try:
            print str(need_show_info_str) + '\t' + str(need_show_info[need_show_info_str])
        except Exception as e:
            print >> sys.stderr, "[now is print need_show_info]:" + '\t' + str(e)

if __name__ == "__main__":
    main()