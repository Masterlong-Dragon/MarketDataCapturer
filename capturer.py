'''
数据采集服务
'''

from config_parser import gen_datasources_from_config
from db_helper import FinanceDB

class Capturer:
    def __init__(self, db_config, modules, modules_max):
        # 读取配置
        self.db_config, self.modules, self.modules_max = db_config, modules, modules_max
        # 获取数据采集源
        self.sources = gen_datasources_from_config(self.modules)
        # 数据库连接
        self.db = FinanceDB(self.db_config)

    def run_once(self):
        # 获取采集对象总页数
        total_page = self.db.get_indices_pages()
        # 分页逐步采集
        for page in range(1, total_page + 1):
            # 当前页所有数据
            indices = self.db.query_all_indices(page)
            # 以数据源为单位分组
            group = {}
            # index[4]即source字段
            for index in indices:
                if index[4] not in group:
                    group[index[4]] = []
                # 缓存必要信息 index_id ticker type subtype
                group[index[4]].append((index[0], index[1], index[2], index[5]))
            # 逐个数据源采集
            for source, codes in group.items():
                print('Current data source', source, 'Max requests at a time', self.modules_max[source])
                print('Current requests at total of', len(codes))
                for i in range(0, len(codes), self.modules_max[source]):
                    # 合并需要采集的code
                    code_arr = [code[1] for code in codes[i : i + self.modules_max[source]]]
                    # print('当前请求', code_arr)
                    # 获取api原始响应
                    raw = self.sources[source].raw(code_arr)
                    # 如果获取失败则跳过
                    if not raw:
                        continue
                    # 逐条解析
                    for j, code in enumerate(codes[i : i + self.modules_max[source]]):
                        index_id, ticker, type, subtype = code
                        # print('当前解析', ticker)
                        # 进行解析并更新数据库
                        data = self.sources[source].parse(raw[j], type, subtype)
                        # print(data)
                        self.db.update_data_info(type, index_id, data)
    
    def close(self):
        self.db.close()