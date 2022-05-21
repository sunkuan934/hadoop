# -*- coding: UTF-8 -*
import sys

error_code_count = {}
sub_type_info = {}
need_show_info = {}

def main():
    while True:
        try:
            try:
                global error_code_count
                global sub_type_info
                global need_show_info
                line_content = sys.stdin.readline()
                if line_content == '' or line_content == '\n':
                    break
            except Exception as e:
                print >> sys.stderr, "[Line " + sys._getframe().f_lineno + "]: " + str(e) + "readline failed"

            if '\t' not in line_content:
                continue
            pre_type_str = line_content.strip().split('\t')[0]
            if pre_type_str[-1].islower():
                pre_type_str = pre_type_str[:-1]

            if 'sub_type:' in line_content:
                sub_type_str = pre_type_str
                count = int(line_content.strip().split('\t')[1])
    
                if sub_type_str in sub_type_info.keys():
                    sub_type_info[sub_type_str] = sub_type_info[sub_type_str] + count
                else:
                    sub_type_info[sub_type_str] = count
            elif 'show_success:' in line_content or 'show_fail:' in line_content:
                need_show_info_str = pre_type_str
                count = int(line_content.strip().split('\t')[1])
                if need_show_info_str in need_show_info.keys():
                    need_show_info[need_show_info_str] = need_show_info[need_show_info_str] + count
                else:
                    need_show_info[need_show_info_str] = count
            else:
                try:
                    error_code = pre_type_str
                    count = int(line_content.strip().split('\t')[1])
                except Exception as e:
                    print >> sys.stderr, "[Line " + sys._getframe().f_lineno + "]: " + str(e) + ":count to int failed"
                if error_code in error_code_count.keys():
                    try:
                        original_count = int(error_code_count[error_code])
                        error_code_count[error_code] = count + original_count
                    except Exception as e:
                        print >> sys.stderr, "[Line " + sys._getframe().f_lineno + "]: "+ str(e) + ":acclumate count failed"
                else:
                    error_code_count[error_code] = count
    
        except Exception as e:
            print >> sys.stderr, "[Line " + sys._getframe().f_lineno + "]: " + str(e) + ":process data error!"

    for error_code in error_code_count.keys():
        print str(error_code) + '\t' + str(error_code_count[error_code])
    
    for sub_type_code in sub_type_info.keys():
        print str(sub_type_code) + '\t' + str(sub_type_info[sub_type_code])
    
    for need_show_info_str in need_show_info.keys():
        print str(need_show_info_str) + '\t' + str(need_show_info[need_show_info_str])

if __name__ == '__main__':
    main()