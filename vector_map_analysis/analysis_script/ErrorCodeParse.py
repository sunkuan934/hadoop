# -*- coding: utf-8 -*-
from __future__ import division
import os
import sys
import argparse
import logging
import json
import collections

dict_error = {'': '处理成功', '1': '数据非法', '2': '驶入驶出link匹配失败', '3': '第一次匹配失败',
              '4': '第2次匹配失败', '5': '更新行驶路径失败', '6': '实行路径计算失败', '7': '相机参数计算失败',
              '8': '道路太细', '9': 'z值处理失败', '10': '桥区显示失败', '11': '可视化失败', '12': '特殊case过滤',
              '13': '单link需要过滤', '14': '计算请求范围失败', '15': '获取局部路网失败', '16': '自相交',
              '17': '单点下线的问题case', '19': '高精数据错误', '20': '车道关系提取错误',
              '21': '云端生成失败', '22': '边界计算失败', '23': '边界自相交', '24': '箭头计算失败',
              '25': '交叉区域计算失败', '26': '可视化数据校正失败', '27': '渲染数据创建失败', '28': '箭头数据失败',
              '29': '动画失败', '30': '可视化其他错误', '31': '可视化计算超时', '32': '低等级驶入驶出过滤', '1000': '高精数据异常',
              '1001': '高精路线匹配失败', '1002': '高精转换group失败', '1003': '高精转换group路网失败',
              '1004': '高精转换block边界失败', '1005': '高精转换block邻接关系失败', '1006': '高精可视化失败',
              '1007': '不支持高精图', '100001': '下游返回数据异常', '10002': '渲染失败'}


def parse_error_code(src_file_path):
    """将错误信息解析为字典"""

    file_reader = open(src_file_path)
    all_date = 0
    fail_data = 0
    error_info = collections.OrderedDict()
    each_error_code_rate_4_no_show = {}
    sub_type_info = {}
    line = file_reader.readline()
    while line:
        each_error_code_info = line.strip().split('\t')
        if len(each_error_code_info) < 2:
            line = file_reader.readline()
            continue
        if 'show_success:' in each_error_code_info[0] or 'show_fail:' in each_error_code_info[0]:
            all_date += int(each_error_code_info[1])

        if 'sub_type:' in each_error_code_info[0]:
            sub_type_str = each_error_code_info[0]
            if sub_type_str in sub_type_info.keys():
                sub_type_info[sub_type_str] = sub_type_info[sub_type_str] + int(each_error_code_info[1])
            else:
                sub_type_info[sub_type_str] = int(each_error_code_info[1])

        error_code = each_error_code_info[0].strip().split(':')[1]
        if 'no_show_error_code' in each_error_code_info[0]:
            if "not_show" in error_info.keys():
                if error_code in dict_error.keys():
                    error_code_str = dict_error[error_code]
                    if error_code in error_info["not_show"].keys():
                        error_info["not_show"][error_code_str] = error_info["not_show"][error_code_str] \
                                                                 + int(each_error_code_info[1])
                    else:
                        error_info["not_show"][error_code_str] = int(each_error_code_info[1])
            else:
                if error_code in dict_error.keys():
                    error_info.setdefault("not_show", {})
                    error_code_str = dict_error[error_code]
                    error_info["not_show"][error_code_str] = int(each_error_code_info[1])

            if error_code in dict_error.keys() and error_code in each_error_code_rate_4_no_show.keys():
                each_error_code_rate_4_no_show[error_code] = each_error_code_rate_4_no_show[error_code] \
                                                             + int(each_error_code_info[1])
                fail_data = fail_data + int(each_error_code_info[1])
            elif error_code in dict_error.keys() and error_code not in each_error_code_rate_4_no_show.keys():
                each_error_code_rate_4_no_show[error_code] = int(each_error_code_info[1])
                fail_data = fail_data + int(each_error_code_info[1])

        elif '3D_degrade_error_code' in each_error_code_info[0]:
            if "3D_degrade" in error_info.keys():
                if error_code in dict_error.keys():
                    error_code_str = dict_error[error_code]
                    if error_code in error_info["3D_degrade"].keys():
                        error_info["3D_degrade"][error_code_str] = error_info["3D_degrade"][error_code_str] \
                                                                   + int(each_error_code_info[1])
                    else:
                        error_info["3D_degrade"][error_code_str] = int(each_error_code_info[1])
            else:
                if error_code in dict_error.keys():
                    error_code_str = dict_error[error_code]
                    error_info.setdefault("3D_degrade", {})
                    error_info["3D_degrade"][error_code_str] = int(each_error_code_info[1])

        line = file_reader.readline()

    error_info["all_data"] = all_date
    error_info["fail_data"] = fail_data
    return error_info, each_error_code_rate_4_no_show, sub_type_info

class ErrorCodeParse(object):
    """解析从hadoop中拉取下来的每日的矢量图错误码信息"""

    def __init__(self, args):
        """init para"""
        self.parser = args

    def handle_error_code_info(self):
        """根据parser的指定参数, 将错误信息存储到json中"""
        args = self.parser.parse_args()
        src_file_path = args.data_folder + '/' + str(args.date)
        json_content, no_show_content, sub_type_info = parse_error_code(src_file_path)

        dst_file_path = str(args.json_path)
        dst_file_content = open(dst_file_path, 'r')
        orig_json = json.load(dst_file_content)
        dst_file_content.close()
        orig_json[str(args.date)] = json_content

        with open(dst_file_path, 'w') as file_write:
            new_json_content = json.dumps(orig_json, sort_keys=True)
            file_write.write(new_json_content)
            file_write.close()

        type_json_path = './vector_map_type.json'

        try:
            type_json_content = open(type_json_path, 'r')
            type_json_orig_content = json.load(type_json_content)
            type_json_content.close()

            type_json_orig_content[str(args.date)] = sub_type_info
            with open(type_json_path, 'w') as file_write:
                new_json_content = json.dumps(type_json_orig_content, sort_keys=True)
                file_write.write(new_json_content)
                file_write.close()
        except Exception as e:
            print >> sys.stderr, str(e)

        return json_content, no_show_content, sub_type_info
