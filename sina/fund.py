 # 基金标准化
import re

# 基金标准化
def format_fund(data, subtype=''):
    # 形如var xxx=a,b,c,d 取出a,b,c,d
    rawdata = re.search('(")(.+)(")', data).group(2)
    stockdata = rawdata.split(',')
    # 对于基金 关注0 名称；1 时刻；2 实时净值；6 涨跌额； 7 日期
    date = stockdata[7]
    time = stockdata[1]
    price = stockdata[2]
    yesterday = stockdata[3]
    changed = stockdata[6]
    name = stockdata[0]
    # {'Name': name, 'Date': date, 'Time': time, 'Price': price, 'YesterdayPrice': yesterday, 'Changed': changed}
    # 返回sql 更新格式
    sql_query = f"Name = '{name}', Date = '{date}', Time = '{time}', Price = '{price}', YesterdayPrice = '{yesterday}', Changed = '{changed}'"
    return sql_query