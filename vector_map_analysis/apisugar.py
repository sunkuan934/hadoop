import datetime
import json

from flask import Flask, request

app = Flask(__name__)

error_types = ['数据非法', '驶入驶出link匹配失败', '第一次匹配失败', '第2次匹配失败',
              '更新行驶路径失败', '实行路径计算失败', '相机参数计算失败',
              '道路太细', 'z值处理失败', '桥区显示失败', '可视化失败', 
              '特殊case过滤', '单link需要过滤', '计算请求范围失败', 
              '获取局部路网失败', '自相交', '单点下线的badcase', '诱导数据异常',
              '高精数据错误', '车道关系提取错误', '云端生成失败', '边界计算失败',
              '边界自相交', '箭头计算失败', '交叉区域计算失败', '可视化数据校正失败',
              '渲染数据创建失败', '箭头数据失败', '动画失败', '可视化其他错误', 
              '可视化计算超时', '低等级驶入驶出过滤', '其它']

# '22':'边界计算失败', '23':'边界自相交', '24':'箭头计算失败', 
#               '25':'交叉区域计算失败', '26':'可视化数据校正失败', '27':'渲染数据创建失败', '28':'箭头数据失败', '29':'动画失败', 
#               '30':'可视化其他错误', '31':'可视化计算超时'
visual_err_types = ["可视化失败", "边界计算失败", "边界自相交",
                    "箭头计算失败", "交叉区域计算失败", "可视化数据校正失败", "渲染数据创建失败", 
                    "箭头数据失败", "动画失败", "可视化其他错误", "可视化计算超时"]

sub_type_map = {'sub_type:0':'出图失败', 'sub_type:1':'2D 图', 'sub_type:2':'3D 图', 'sub_type:3':'高精图'}

@app.route("/sugarapi", methods=["POST"])
def check():
    """检查数据"""
    return_dict = {}
    if request.get_data() is None:
        return_dict['return_info'] = 'param error'
        return json.dumps(return_dict, ensure_ascii=False)
    get_data = request.get_data()
    get_data = json.loads(get_data)
    print(get_data)

    type = request.args.get('type')
    date = request.args.get('date')
    time_period = request.args.get('time_period')
    if not type:
        return_dict['return_info'] = 'type param error'
        return json.dumps(return_dict, ensure_ascii=False)
    print("type is " + type)
    if type == "sub_type":
        return_dict = get_sub_type_pie(date)
    elif type == 'data_record1':
        return_dict = get_data_format1()
    elif type == 'data_record2':
        return_dict = get_data_format2()
    elif type == 'data_record3':
        return_dict = get_data_format3()
    elif type == "not_show" and date:
        return_dict = get_not_show_pie(date)
    elif type == "not_show" and time_period:
        if int(time_period) != 7 and int(time_period) != 30:
            return_dict['return_info'] = 'not_show time_period param error'
            return json.dumps(return_dict, ensure_ascii=False)
        return_dict = get_not_show_change(int(time_period))
    elif type == "not_show_visual" and date:
        return_dict = get_not_show_visual_pie(date)
    elif type == "3d_degrade" and date:
        return_dict = get_degrade_pie(date)
    elif type == "3d_degrade" and time_period:
        if int(time_period) != 7 and int(time_period) != 30:
            return_dict['return_info'] = '3d_degrade time_period param error'
            return json.dumps(return_dict, ensure_ascii=False)
    elif type == "3d_degrade" and not time_period and not date:
        print("show latest 3d_degrade data")
        date_ago = datetime.date.today() - datetime.timedelta(days=3)
        return_dict = get_degrade_pie(date_ago)
    elif type == "not_show" and not time_period and not date:
        print("show latest data")
        date_ago = datetime.date.today() - datetime.timedelta(days=3)
        return_dict = get_not_show_pie(date_ago)
    elif type == "not_show_visual" and not date:
        if 'drillDowns' in get_data:
            drillDowns = get_data['drillDowns']
            first_drill = drillDowns[0]
            name = first_drill['item']['name']
            if name == '可视化失败(all)':
                date_ago = datetime.date.today() - datetime.timedelta(days=3)
                return_dict = get_not_show_visual_pie(date_ago)
    elif type == 'all_data':
        return_dict = get_total_number()
    elif type == 'fail_data':
        return_dict = get_fail_number()
    elif type == 'success_percent'and not time_period:
        return_dict = get_success_percent()
    elif type == "success_percent" and time_period:
        if int(time_period) != 7 and int(time_period) != 30:
            return_dict['return_info'] = 'success_percent time_period param error'
            return json.dumps(return_dict, ensure_ascii=False)
        return_dict = get_success_percent_change(int(time_period))
    elif type == "all_data_change" and time_period:
        if int(time_period) != 7 and int(time_period) != 30:
            return_dict['return_info'] = 'all_data change time_period param error'
            return json.dumps(return_dict, ensure_ascii=False)
        return_dict = get_all_data_change(int(time_period))
    else:
        return_dict['return_info'] = 'param error'
        return json.dumps(return_dict, ensure_ascii=False)

    return json.dumps(return_dict, ensure_ascii=False)


def get_total_number():
    """矢量图出图的总数"""
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("get_total_number 加载orig文件完成...")

    return_dict = {"status": 0, "msg": ""}
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    striftdate = date_ago.strftime("%Y%m%d")
    while str(striftdate) not in orig_data:
        date_ago = date_ago - datetime.timedelta(days=1)
        striftdate = date_ago.strftime("%Y%m%d")
    return_dict["data"] = orig_data[str(striftdate)]["all_data"]
    return return_dict


def get_fail_number():
    """矢量图出图失败的总数"""
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    return_dict = {"status": 0, "msg": ""}
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    striftdate = date_ago.strftime("%Y%m%d")
    while str(striftdate) not in orig_data:
        date_ago = date_ago - datetime.timedelta(days=1)
        striftdate = date_ago.strftime("%Y%m%d")
    return_dict["data"] = orig_data[str(striftdate)]["fail_data"]
    return return_dict


def get_success_percent():
    """计算成功的百分比"""
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    return_dict = {"status": 0, "msg": ""}
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    striftdate = date_ago.strftime("%Y%m%d")
    while str(striftdate) not in orig_data:
        date_ago = date_ago - datetime.timedelta(days=1)
        striftdate = date_ago.strftime("%Y%m%d")
    return_dict["data"] = 100 - orig_data[str(striftdate)]["fail_data"] * 100 / orig_data[str(striftdate)]["all_data"]
    return return_dict


def get_not_show_pie(date):
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    return_dict = {"status": 0, "msg": ""}

    # 所有可视化失败的在外面一起汇总，点进去显示小项
    visual_notshow_data = {}
    visual_notshow_data["name"] = "可视化失败(all)"
    visual_notshow_data["value"] = 0
    visual_notshow_data["url"] = "http://www.baidu.com"

    # 比例小于某一部分的要合并
    other_notshow_data = {}
    other_notshow_data["name"] = "其它原因（<1%)"
    other_notshow_data["value"] = 0
    other_notshow_data["url"] = "http://www.baidu.com"

    striftdate = str(date.strftime("%Y%m%d"))
    if striftdate not in orig_data:
        return return_dict
    date_err_data = orig_data[striftdate]
    err_data = []
    all_class = date_err_data["not_show"]

    all_count = 0
    for key, val in all_class.items():
        all_count += val
        if key in visual_err_types: 
            visual_notshow_data["value"] += val

    for key, val in all_class.items():
        single_data = {}
        if key in visual_err_types:
            continue
        elif val / all_count < 0.01:
            other_notshow_data["value"] += val
        else:
            single_data["name"] = key
            single_data["value"] = val
            single_data["url"] = "http://www.baidu.com"
            err_data.append(single_data)
        
    err_data.append(visual_notshow_data)
    err_data.append(other_notshow_data)
    return_dict["data"] = err_data
    return  return_dict

# 可视化下钻饼图
def get_not_show_visual_pie(date):
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    return_dict = {"status": 0, "msg": ""}
    return_dict["data"] = ''
    striftdate = str(date.strftime("%Y%m%d"))
    if striftdate not in orig_data:
        return return_dict
    date_err_data = orig_data[striftdate]
    visual_err_data = []
    all_class = date_err_data["not_show"]

    for key, val in all_class.items():
        single_data = {}
        if key not in visual_err_types:
            continue
        else:
            single_data["name"] = key
            single_data["value"] = val
            single_data["url"] = "http://www.baidu.com"
            visual_err_data.append(single_data)
            # print(single_data)
    return_dict["data"] = visual_err_data
    return  return_dict


def get_degrade_pie(date):
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    return_dict = {"status": 0, "msg": ""}
    striftdate = str(date.strftime("%Y%m%d"))
    date_err_data = orig_data[striftdate]
    err_data = []
    all_class = date_err_data["3D_degrade"]
    for key, val in all_class.items():
        single_data = {}
        single_data["name"] = key
        single_data["value"] = val
        single_data["url"] = "http://www.baidu.com"
        err_data.append(single_data)
    return_dict["data"] = err_data
    return return_dict

def get_sub_type_pie(date):
    orig_data = {}
    with open("vector_map_type.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    return_dict = {"status": 0, "msg": ""}
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    striftdate = str(date_ago.strftime("%Y%m%d"))
    
    all_class = orig_data[striftdate]
    sub_type = []
    all_num = 0
    for key, val in all_class.items():
        all_num = int(all_num) + int(val)
    for key, val in all_class.items():
        if key not in sub_type_map:
            continue
        single_data = {}
        each_type_name = sub_type_map[key]
        single_data["name"] = each_type_name
        single_data["value"] = val
        single_data["url"] = "http://www.baidu.com"
        sub_type.append(single_data)
    return_dict["data"] = sub_type
    return return_dict

def get_data_format1():
    return_dict = {"status": 0, "msg": ""}
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    striftdate = str(date_ago.strftime("%Y%m%d"))
    return_dict["data"] = striftdate[0:4]
    return return_dict

def get_data_format2():
    return_dict = {"status": 0, "msg": ""}
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    striftdate = str(date_ago.strftime("%Y%m%d"))
    return_dict["data"] = striftdate[4:6]
    return return_dict

def get_data_format3():
    return_dict = {"status": 0, "msg": ""}
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    striftdate = str(date_ago.strftime("%Y%m%d"))
    return_dict["data"] = striftdate[6:8]
    return return_dict

def get_not_show_change(time_period):
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    return_dict = {"status": 0, "msg": "", "data":{}}
    date_end = date_ago
    date_start = date_ago - datetime.timedelta(days=time_period)

    if str(date_end.strftime("%Y%m%d")) not in orig_data:
        date_end -= datetime.timedelta(days=1)
        date_start -= datetime.timedelta(days=1)

    categories = []
    series = [] # 大小是errcode的类别数目
    # errcode 类别, 每个errcode有一个dict
    errcodes_dict = {}
    for errcode in error_types:
        errcodes_dict[errcode] = {}
        errcodes_dict[errcode]["name"] = errcode
        errcodes_dict[errcode]["data"] = []
    for i in range(0, time_period):
        date_cur = date_end - datetime.timedelta(days=time_period - i - 1)
        if str(date_cur.strftime("%Y%m%d")) in orig_data:
            total_fail = orig_data[date_cur.strftime("%Y%m%d")]["fail_data"]
            errcode_data_date = orig_data[date_cur.strftime("%Y%m%d")]
            categories.append(str(date_cur))

            for err_key in errcodes_dict:
                if err_key in errcode_data_date["not_show"]:
                    err_num = errcode_data_date["not_show"][err_key]
                    if total_fail:
                        if err_num / total_fail > 0.01:
                            errcodes_dict[err_key]["data"].append('%.4f' % (err_num / total_fail))     
                else:
                    errcodes_dict[err_key]["data"].append(0.0)
    for (key, val) in errcodes_dict.items():
        series.append(val)

    return_dict["data"]["categories"] = []
    return_dict["data"]["categories"] = categories
    return_dict["data"]["series"] = series
    return return_dict


def get_all_data_change(time_period):
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    return_dict = {"status": 0, "msg": "", "data":{}}
    date_end = date_ago
    date_start = date_ago - datetime.timedelta(days=time_period)

    if str(date_end.strftime("%Y%m%d")) not in orig_data:
        date_end -= datetime.timedelta(days=1)
        date_start -= datetime.timedelta(days=1)

    categories = []
    series = [] # 大小是errcode的类别数目
    # errcode 类别, 每个errcode有一个dict
    errcodes_dict = {}
    # for errcode in error_types:
    errcodes_dict['出图总次数'] = {}
    errcodes_dict['出图总次数']["name"] = '出图总次数'
    errcodes_dict['出图总次数']["data"] = []
    for i in range(0, time_period):
        date_cur = date_end - datetime.timedelta(days=time_period - i - 1)
        if str(date_cur.strftime("%Y%m%d")) in orig_data:
            all_data = orig_data[date_cur.strftime("%Y%m%d")]["all_data"]
            categories.append(str(date_cur))
            errcodes_dict["出图总次数"]["data"].append(orig_data[date_cur.strftime("%Y%m%d")]["all_data"])
    
    for key, val in errcodes_dict.items():
        series.append(val)

    return_dict["data"]["categories"] = []
    return_dict["data"]["categories"] = categories
    return_dict["data"]["series"] = series
    # print(return_dict)
    return return_dict


def get_success_percent_change(time_period):
    orig_data = {}
    with open("sugardata.json", "r") as f:
        orig_data = json.load(f)
        print("加载orig文件完成...")
    date_ago = datetime.date.today() - datetime.timedelta(days=3)
    return_dict = {"status": 0, "msg": "", "data":{}}
    date_end = date_ago
    date_start = date_ago - datetime.timedelta(days=time_period)

    if str(date_end.strftime("%Y%m%d")) not in orig_data:
        date_end -= datetime.timedelta(days=1)
        date_start -= datetime.timedelta(days=1)

    categories = []
    series = [] # 大小是errcode的类别数目
    # errcode 类别, 每个errcode有一个dict
    errcodes_dict = {}
    errcodes_dict['出图成功率'] = {}
    errcodes_dict['出图成功率']["name"] = '出图成功率'
    errcodes_dict['出图成功率']["data"] = []

    errcodes_dict['出图总次数'] = {}
    errcodes_dict['出图总次数']["name"] = '出图总次数'
    errcodes_dict['出图总次数']["data"] = []

    for i in range(0, time_period):
        date_cur = date_end - datetime.timedelta(days=time_period - i - 1)
        if str(date_cur.strftime("%Y%m%d")) in orig_data:
            categories.append(str(date_cur))
            success_rate = '%.4f' % (1 - orig_data[date_cur.strftime("%Y%m%d")]["fail_data"] \
                / orig_data[date_cur.strftime("%Y%m%d")]["all_data"])
            errcodes_dict["出图成功率"]["data"].append(success_rate)
            errcodes_dict["出图总次数"]["data"].append(orig_data[date_cur.strftime("%Y%m%d")]["all_data"])
    
    for key, val in errcodes_dict.items():
        series.append(val)

    return_dict["data"]["categories"] = []
    return_dict["data"]["categories"] = categories
    return_dict["data"]["series"] = series
    return return_dict


if __name__ == '__main__':
    app.run(host='**.**.**.**', port=8888, debug=True)

