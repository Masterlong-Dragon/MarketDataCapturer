# 期货标准化
import re

# 对于type 0 7 价格 1 8 日期 13 时间 7 开盘价 9 最高价 5 最低价 6 昨收 8 成交量 10
format_0_7 = lambda data : f"Price = '{data[1 if data[1] != '' else 8]}', Date = '{data[13]}', Time = '{data[7]}', OpenPrice = '{data[9]}', MaxPrice = '{data[5]}', MinPrice = '{data[6]}', YesterdayPrice = '{data[8]}', Amount = '{data[10]}'"
# 对于type 2 价格 4 15 日期 37 时间 38 开盘价 1 最高价 2 最低价 3 收盘价 9 昨收 14 成交量 7 成交额 5
format_2 = lambda data : f"Price = '{data[4 if data[4] != '' else 15]}', Date = '{data[37]}', Time = '{data[38]}', OpenPrice = '{data[1]}', MaxPrice = '{data[2]}', MinPrice = '{data[3]}', ClosePrice = '{data[9]}', YesterdayPrice = '{data[14]}', Amount = '{data[7]}', Volume = '{data[5]}'"
# 默认格式 价格 9 11 日期 18 时间 见代码 开盘价 3 最高价 4 最低价 5 收盘价 10 昨收 11 成交量 14 成交额 15
format_default = lambda data : f"Price = '{data[9 if data[9] != '' else 11]}', Date = '{data[18]}', Time = '{data[2][0:2] + ':' + data[2][2:4] + ':' + data[2][4:]}', OpenPrice = '{data[3]}', MaxPrice = '{data[4]}', MinPrice = '{data[5]}', ClosePrice = '{data[10]}', YesterdayPrice = '{data[11]}', Amount = '{data[14]}', Volume = '{data[15]}'"

# 跳转表for基础数据
format_methods = {
    0: format_0_7,
    7: format_0_7,
    2: format_2
}

# 跳转表for名称
format_name_index = {
    0: 14,
    3: 10,
    2: 0
}

# 期货标准化
def lqf_format(data, type):

    sql_query = ''

    # 根据期货类型选择格式进行标准化
    if not type in format_methods:
        sql_query = format_default(data)
    else:
        sql_query = format_methods[type](data)
    # 名称标准化
    name = 'unknown'
    if not type in format_name_index:
        name = data[1]
    else:
        name = data[format_name_index[type]]
        # 特殊处理 需要从ticker中提取名称
        if type == 2:
            name = name.replace('CFF_RE_TF', "5国债").replace('CFF_RE_IF', "IF").replace('CFF_RE_T', "10国债").replace('CFF_RE_IH', "IH").replace('CFF_RE_IC', "IC")
    # 返回sql 更新格式
    sql_query = f"Name = '{name}', " + sql_query
    return sql_query

# 期货标准化
def format_futures(data, type=''):
    # 形如var xxx=a,b,c,d 取出a,b,c,d
    rawdata = re.search('(")(.+)(")', data).group(2)
    stockdata = rawdata.split(',')
    # 补充一个元素
    stockdata.insert(0, type)
    # 新浪财经api内部逻辑 这里直接转写过来
    '''
    "0": ["hf_", code, "_0"],
            "1": ['nf_', code, "_1"],
            "2": ["CFF_RE_", code, "_2"],
            "3": [code, "_3"],
            "7": ["gds_", code, "_7"]
    '''
    # 生成type
    if type.startswith('hf'):
        type = 0
    elif type.startswith('nf'):
        type = 1
    elif type.startswith('CFF_RE'):
        type = 2
    elif type.startswith('ds'):
        type = 7
    else:
        type = 3
    # 返回sql 更新格式
    return lqf_format(stockdata, type)
