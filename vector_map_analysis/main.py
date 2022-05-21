# -*- coding: utf-8 -*-
from __future__ import division
import os
import sys
import smtplib
import csv
from testlog import Logger
import argparse
import logging
import json
import datetime

sys.path.append('./analysis_script')
from ErrorCodeParse import ErrorCodeParse

import email.mime.text
import email.mime.multipart

dict_error = {'': '处理成功', '1': '数据非法', '2': '驶入驶出link匹配失败', '3': '第一次匹配失败', 
            '4': '第2次匹配失败', '5': '更新行驶路径失败', '6': '实行路径计算失败', '7': '相机参数计算失败',
            '8': '道路太细', '9': 'z值处理失败', '10': '桥区显示失败', '11': '可视化失败', '12': '特殊case过滤',
            '13': '单link需要过滤', '14': '计算请求范围失败', '15': '获取局部路网失败', '16': '自相交',
            '17': '单点下线的badcase', '19':'高精数据错误', '20': '车道关系提取错误',
            '21':'云端生成失败', '22':'边界计算失败', '23':'边界自相交', '24':'箭头计算失败',
            '25':'交叉区域计算失败', '26':'可视化数据校正失败', '27':'渲染数据创建失败', '28':'箭头数据失败',
            '29':'动画失败', '30':'可视化其他错误', '31':'可视化计算超时', '32':'低等级驶入驶出过滤', '1000':'高精数据异常',
            '1001':'高精路线匹配失败', '1002':'高精转换group失败', '1003':'高精转换group路网失败',
            '1004':'高精转换block边界失败', '1005':'高精转换block邻接关系失败', '1006':'高精可视化失败',
            '1007':'不支持高精图', '100001':'下游返回数据异常', '10002':'渲染失败'}

def send_mail(mail_from, mail_to, msg):
    """发送邮件通知"""
    try:
        mail_host = "mail2-in.baidu.com"  # 设置服务器
        s = smtplib.SMTP()
        logger.info("connecting to mail_host")
        s.connect(mail_host)
        logger.info("sending mail success!")
        s.sendmail(mail_from, mail_to, msg.as_string())
        s.close()
        return True
    except Exception as e:
        print(str(e))
        return False


def generate_tr_from_list(list_input, dict_chaxun) :
    """根据字典内容生成Html的表格样式"""
    rst = ''
    for i in list_input:
        if i[0] in dict_chaxun:
            pass
        else:
            print(i[0] + 'not exist')
            continue
        row = dict_chaxun[i[0]]
        value = 100 * float(i[1])
        rst += '\n' + ('<tr><td>%s</td><td style="color:blue">%.2f%%</td></tr>' % (row, value))
    return rst


def generate_html_msg_from_error_code_info(json_content, no_show_content, sub_type_info):
    """根据每日的错误码信息,生成Html格式的字符串"""
    all_count = json_content["all_data"]
    fail_count = json_content["fail_data"]
    no_show_content = {k: '%.4f' % (v / fail_count) for k, v in no_show_content.items()}
    list_error_code = sorted(no_show_content.items(), key=lambda x: x[1], reverse=True)

    table_error_code = '<p>共统计%s条数据, 其中出图成功%s, 失败%s, 出图成功率%.2f%%。在失败的数据中：</p>' % \
                       (all_count, all_count - fail_count, fail_count, 100 * (1.0 - fail_count / all_count))
    table_error_code += '<table border="1", cellspacing="0", cellpadding=“0”>'
    table_error_code += '\n' + '<tr><th>出图失败原因</th><th>比例</th><tr>'
    table_error_code += generate_tr_from_list(list_error_code, dict_error)
    table_error_code += '\n' + '</table>'

    success_show = 0
    for sub_type_str in sub_type_info.keys():
        if sub_type_str == 'sub_type:0':
            continue
        success_show = success_show + int(sub_type_info[sub_type_str])
    table_sub_type = '<table border="1", cellspacing="0">'
    table_sub_type += '\n' + '<tr><th>二维/三维/高精</th><th>比例</th><tr>'
    table_sub_type += '\n' + ('<tr><td>%s</td><td style="color:blue">%.4f%%</td></tr>' % \
        ('2D', 100 * (sub_type_info['sub_type:1'] / success_show)))
    table_sub_type += '\n' + ('<tr><td>%s</td><td style="color:blue">%.4f%%</td></tr>' % \
        ('3D', 100 * (sub_type_info['sub_type:2'] / success_show)))
    if 'sub_type:3' in sub_type_info.keys():
        table_sub_type += '\n' + ('<tr><td>%s</td><td style="color:blue">%.4f%%</td></tr>' % \
            ('高精', 100 * (sub_type_info['sub_type:3'] / success_show)))
    table_sub_type += '\n' + '</table>'

    table_if_show = '<table border="1", cellspacing="0">' + '\n'
    table_if_show += '<tr><th>if show</th><th>统计</th><tr>' + '\n'
    table_if_show += ('<tr><td>%s</td><td style="color:blue">%.4f%%</td></tr>' % ('不出图', fail_count / all_count)) + '\n'
    table_if_show += ('<tr><td>%s</td><td style="color:blue">%.4f%%</td></tr>' % \
        ('出图', (all_count - fail_count) / all_count)) + '\n'
    table_if_show += '</table>'
    
    html_msg = str(parser.parse_args().date) + '回传数据分析,' + '<p>矢量图未出图error_code统计如下:</p>' + table_error_code + \
               '<p>出图类型比例分布：</p>' + table_sub_type + '<p>show统计情况为:</p>' + table_if_show
    return html_msg

if __name__ == "__main__":
    def createParser():
        """解析输入的参数"""
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('--data_folder', type=str, default='../data-date/vmap_err_latest', help='data folder')
        parser.add_argument('--log_folder', type=str, default='./log/vmap_err_latest', help='log folder')
        parser.add_argument('--json_path', type=str, default='sugardata_latest.json', help='saved json path')
        parser.add_argument('--daily_json_path', type=str, default='./daily-json/vmap_err_latest',\
         help='daily-json saved path')
        parser.add_argument('--date', type=str, help='date for analysis')
        return parser

    parser = createParser()
    args = parser.parse_args()
    logger = Logger(log_file_name= args.log_folder + "/" + str(datetime.date.today()) \
        + '-main-log.txt', log_level=logging.DEBUG, logger_name='test').get_log()
    logger.info(datetime.date.today())
    error_code_parse = ErrorCodeParse(parser)
    json_content, no_show_content, sub_type_info = error_code_parse.handle_error_code_info()

    html_msg = generate_html_msg_from_error_code_info(json_content, no_show_content, sub_type_info)
    
    from_mail = "sunkuan@baidu.com"
    to_mail = "sunkuan@baidu.com,bairui03@baidu.com,hongqize@baidu.com"
    msg = email.mime.multipart.MIMEMultipart()
    msg.attach(email.mime.text.MIMEText(html_msg, _subtype='html', _charset='utf-8'))

    msg['Subject'] = "【" + str(parser.parse_args().date) + '放大图回传数据分析】'
    msg['From'] = from_mail
    msg['To'] = to_mail
    send_mail(from_mail, to_mail.split(','), msg)
    logger.info("Send success")
    sys.exit(0)