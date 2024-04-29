import urllib.request

# 导入各个数据源的解析方法
from .stock import format_stock
from .futures import format_futures
from .fund import format_fund
from .foreign_exchange import format_foreign_exchange

# 测试导入
def import_test():
    print('import success')

# 数据解析跳转表
parse_methods = {
            'Stock': format_stock,
            'Futures': format_futures,
            'Fund': format_fund,
            'Forex': format_foreign_exchange
}

# 基于新浪财经的数据源
class DataSource():
    _prefix_url = "https://hq.sinajs.cn/list="

    # 原始数据获取
    def raw(self, code):
        # 将数组形式的code转换为字符串
        if isinstance(code, list):
            code = ','.join(code)
        else:
            code = str(code)
        url = self._prefix_url + code       #http://hq.sinajs.cn/list=s_sh000001
        info = self.http_request(url)
        # 换行分割 \n
        return info.split('\n')
    
    # 数据解析
    def parse(self, raw_info, type, subtype=''):
        # 根据type选择解析方法
        if not type in parse_methods:
            raise ValueError('Unknown type')
        return parse_methods[type](raw_info, subtype)
    
    # http请求
    def http_request(self, url):
        try:
            req = urllib.request.Request(url)
            # 需要添加Referer和User-Agent，否则新浪会拒绝请求
            req.add_header('Referer', 'https://finance.sina.com.cn')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36')
            r = urllib.request.urlopen(req)
            # 捕获原始信息
            result = r.read().decode('gb2312')
            return result
        except Exception as e:
            print([url, repr(e)])