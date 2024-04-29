# 股票标准化
import re

# 格式化港股（可能有误） 1 名称；2 今开；3 昨收；4 最高；5 最低；6 现价；10 成交量；11 成交额；17 日期；18 时刻 
format_hk = lambda data : f"Name = '{data[1]}', OpenPrice = '{data[2]}', YesterdayPrice = '{data[3]}', HighPrice = '{data[4]}', LowPrice = '{data[5]}', Price = '{data[6]}', Volume = '{data[10]}', Amount = '{data[11]}', Date = '{data[17]}', Time = '{data[18]}'"
# 格式化沪深股票 0 名称；1 今开；2 昨收；3 现价；4 最高；5 最低；8 成交量；9 成交额；30 日期；31 时刻
format_shz = lambda data : f"Name = '{data[0]}', OpenPrice = '{data[1]}', YesterdayPrice = '{data[2]}', HighPrice = '{data[4]}', LowPrice = '{data[5]}', Price = '{data[3]}', Volume = '{data[8]}', Amount = '{data[9]}', Date = '{data[30]}', Time = '{data[31]}'"
# 格式化美股 0 名称；1 价格；3 日期 时刻；5 今开；6 最高；7 最低；10 成交量；26 昨收
format_us = lambda data : f"Name = '{data[0]}', OpenPrice = '{data[5]}', YesterdayPrice = '{data[26]}', HighPrice = '{data[6]}', LowPrice = '{data[7]}', Price = '{data[1]}', Volume = '{data[10]}', Date = '{data[3].split(' ')[0]}', Time = '{data[3].split(' ')[1]}'"

# 跳转表
format_methods = {
    'hk': format_hk,
    'sh': format_shz,
    'sz': format_shz,
    'us': format_us
}

# 股票标准化
def format_stock(data, type='sh'):
    # 形如var xxx=a,b,c,d 取出a,b,c,d
    rawdata = re.search('(")(.+)(")', data).group(2)
    stockdata = rawdata.split(',')
    # 返回sql 更新格式
    sql_query = ''
    # 根据股票类型选择格式进行标准化
    if not type in format_methods:
        # 抛出异常
        raise ValueError('Unknown type')
    sql_query = format_methods[type](stockdata)
    return sql_query