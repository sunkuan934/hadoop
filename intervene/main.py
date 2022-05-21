import os
import sys
import json
import pymysql

connector=pymysql.connect(host = '***.**.**.**', user = '****', passwd = '*******'
                            ,port = 3306, db = 'db_name', charset = 'gbk')

cur = connector.cursor()

sql_strategy_str = 'select id from  strategy'
cur.execute(sql_strategy_str)
strategy_data = cur.fetchall()

sql_control_version_str = 'select id from strategy_control_version'
cur.execute(sql_control_version_str)
control_version_data = cur.fetchall()

control_version = int(control_version_data[-1][1]) + 1


need_intervened_case_num = 0

pre_word_str = 'INSERT INTO strategy (id, situation, data)' + '\n' + 'VALUES' + '\n'
dst_word_str = ''
id = int(strategy_data[-1][0]) + 1
dst_file_path = "./intervene_info"
fd = open(dst_file_path)

new_case = True
line = fd.readline().strip().split('\n')[0]
while line:
    try:
        if '#' in line:
            line = fd.readline().strip().split('\n')[0]
            continue
        dict_info = json.loads(line)
        temp_dst_word_str = ''
        if 'showHDExpandMap' in dict_info.keys() and dict_info['showHDExpandMap'] != '':
            temp_dst_word_str = temp_dst_word_str + '"showHDExpandMap":' + str(dict_info['showHDExpandMap'])

        need_show = 1 if 'show' not in dict_info.keys() or dict_info['show'] == '1' or dict_info['show'] == '' else 0
        if temp_dst_word_str == '':
            temp_dst_word_str = temp_dst_word_str + '"show":' + str(need_show)
        else:
            temp_dst_word_str = temp_dst_word_str + ',"show":' + str(need_show)

        if need_show:
            if 'filter' in dict_info.keys() and dict_info['filter'] != '':
                temp_dst_word_str = temp_dst_word_str + ',"filter":' + str(dict_info['filter'])
            if 'merge' in dict_info.keys() and dict_info['merge'] != '':
                temp_dst_word_str = temp_dst_word_str + ',"merge":' + str(dict_info['merge'])
            if 'camera' in dict_info.keys() and dict_info['camera'] != '':
                camera_info_str = str(dict_info['camera'])[2:-2].replace('{', '')
                camera_info_str = camera_info_str.replace('}', '')
                camera_info_str = camera_info_str.replace(' ', '')
                camera_infos = camera_info_str.split(',')
                if camera_infos[0].split(':')[1] != '0' and camera_infos[1].split(':')[1] != '0':
                    temp_dst_word_str = temp_dst_word_str + ',"camera":[{"angle":' + camera_infos[0].split(':')[1] + '}'
                    temp_dst_word_str = temp_dst_word_str + ',{"angle":' + str(camera_infos[1].split(':')[1]) + '}]'
                elif camera_infos[0].split(':')[1] != '0' or camera_infos[1].split(':')[1] != '0':
                    angle_value = camera_infos[0].split(':')[1] if camera_infos[0].split(':')[1] != '0' \
                    else camera_infos[1].split(':')[1]
                    temp_dst_word_str = temp_dst_word_str + ',"camera":[{"angle":' + str(angle_value) + '}]'
            if 'visualize' in dict_info.keys() and dict_info['visualize'] != '':
                temp = list(dict_info['visualize'])
                if dict_info['visualize'][str(temp[0])] != 0 and dict_info['visualize'][str(temp[1])] != 0:
                    temp_dst_word_str = temp_dst_word_str + ',"visualize":'
                    temp_dst_word_str = temp_dst_word_str + '{"' + str(temp[0]) + '":' \
                        + str(dict_info['visualize'][temp[0]])
                    temp_dst_word_str = temp_dst_word_str + ',"' + str(temp[1]) + '":' \
                        + str(dict_info['visualize'][temp[1]]) + '}'
                elif dict_info['visualize'][str(temp[0])] != 0 or dict_info['visualize'][str(temp[1])] != 0:
                    temp_dst_word_str = temp_dst_word_str + ',"visualize":'
                    visualize_elem = str(temp[0]) if dict_info['visualize'][str(temp[0])] != 0 else str(temp[1])
                    visualize_elem_value = dict_info['visualize'][visualize_elem]
                    temp_dst_word_str = temp_dst_word_str + '{"' + str(visualize_elem) + '":' \
                        + str(visualize_elem_value) + '}'
            if 'admin' in dict_info.keys() and dict_info['in_out_link'] != '':
                temp_dst_word_str = temp_dst_word_str + ',"admin":' + '"' + str(dict_info['admin']) + '"'
        else:
            if 'admin' in dict_info.keys() and dict_info['in_out_link'] != '':
                temp_dst_word_str = temp_dst_word_str + ',"admin":' + '"' + str(dict_info['admin']) + '"'
        if 'in_out_link' in dict_info.keys() and dict_info['in_out_link'] != '':
            situlation = str(dict_info['in_out_link'])
            search_sql = 'select * from strategy where situation = \'' + situlation + '\';'
            cur.execute(search_sql)
            results = cur.fetchall()
            new_case = (len(results) == 0)
            if not new_case:
                update_sql_pre_word_str = 'UPDATE strategy' + '\n' + 'SET data = '
                updata_sql_dst_word_str = '\'{' + temp_dst_word_str + '}\'' + '\n' + 'WHERE situation = '\
                     + '\'' + situlation + '\''
                update_strategy_data_sql = (update_sql_pre_word_str + updata_sql_dst_word_str)
                updata_sql_dst_sql_len = len(update_strategy_data_sql)
                update_strategy_data_sql = update_strategy_data_sql[:updata_sql_dst_sql_len - 2] + ';'
                print (update_strategy_data_sql + '\n')
                # cur.execute(insert_strategy_data_sql)
                # connector.commit()  #确认并执行上边的sql语句
            else:
                dst_word_str = dst_word_str + '(' + str(id) + ',\'' + dict_info['in_out_link'] \
                    + '\'' + ',\'{' + temp_dst_word_str + '}\'),' + '\n'
                need_intervened_case_num += 1
                id += 1
        # print (dst_word_str)
    except Exception as e:
        print (str(e))
        line = fd.readline().strip().split('\n')[0]
        continue

    line = fd.readline().strip().split('\n')[0]
    

insert_strategy_data_sql = (pre_word_str + dst_word_str)
dst_sql_len = len(insert_strategy_data_sql)
insert_strategy_data_sql = insert_strategy_data_sql[:dst_sql_len - 2] + ';'
print (insert_strategy_data_sql + '\n')
 
update_control_version_sql = 'UPDATE strategy_control_version SET control_version = '\
        + str(control_version) + ' WHERE id = 1;'
print (update_control_version_sql + '\n')
# cur.execute(insert_strategy_data_sql)
# connector.commit()  #确认并执行上边的sql语句

# cur.execute(update_control_version_sql)
# connector.commit()  #确认并执行上边的sql语句

cur.close()
connector.close()