# 外汇标准化
import re

# 外汇标准化
def format_foreign_exchange(data, subtype=''):
    rawdata = re.search('(")(.+)(")', data).group(2)
    stockdata = rawdata.split(',')
    # 对于外汇 9 名称 8 价格 3 昨收 5 今开 6 最高 7 最低 0 时刻 10 17 日期
    date = stockdata[10] if len(stockdata) < 18 else stockdata[17]
    time = stockdata[0]
    price = stockdata[8]
    yesterday = stockdata[3]
    open = stockdata[5]
    high = stockdata[6]
    low = stockdata[7]
    name = stockdata[9]
    # {'Name': name, 'Date': date, 'Time': time, 'Price': price, 'YesterdayPrice': yesterday, 'OpenPrice': open, 'HighPrice': high, 'LowPrice': low}
    # 返回sql 更新格式
    sql_query = f"Name = '{name}', Date = '{date}', Time = '{time}', Price = '{price}', YesterdayPrice = '{yesterday}', OpenPrice = '{open}', HighPrice = '{high}', LowPrice = '{low}'"
    return sql_query