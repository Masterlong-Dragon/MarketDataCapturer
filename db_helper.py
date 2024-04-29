'''
用于连接数据库，执行查询和更新操作
包含基础的数据库操作函数
包含特化的行情数据操作函数
'''

import mysql.connector

# 获取数据库连接
def get_connection(config):
    # 由于教学使用mysql数据库版本较旧 需要使用use_pure=True 以及注意字符集
    return mysql.connector.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        port=config['port'],
        connection_timeout=config['timeout'],
        charset=config['charset'],
        use_pure=True
    )

'''
查询更新封装
'''

# 获取游标
def get_cursor(connection, dictionary=False):
    return connection.cursor(dictionary=dictionary)

# 执行查询操作
def execute_query(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()

# 执行更新操作
def execute_update(cursor, query):
    cursor.execute(query)
    return cursor.rowcount

# 关闭游标
def close_cursor(cursor):
    cursor.close()

# 关闭连接
def close_connection(connection):
    connection.close()

'''
行情数据操作类
'''

class FinanceDB:
    # 初始化数据库连接
    def __init__(self, db_config):
        self.connection = get_connection(db_config)
        self.cursor = get_cursor(self.connection)
        self.dict_cursor = get_cursor(self.connection, dictionary=True)

        # 表名映射
        self.table_name = {
            'Forex' : 'foreignexchangedata',
            'Fund': 'funddata',
            'Futures': 'futuresdata',
            'Stock': 'stockdata'
        }
    # 执行查询操作
    def query(self, query):
        return execute_query(self.cursor, query)

    # 执行更新操作
    def update(self, query):
        return execute_update(self.cursor, query)

    # 关闭连接
    def close(self):
        close_cursor(self.cursor)
        close_connection(self.connection)
    
    # 获取表的页数 用于分页查询 处理可能的大量数据
    def get_indices_pages(self, type=None, page_size=100):
        if not type or not type in self.table_name:
            table_name = 'financialindices'
        else:
            table_name = self.table_name[type]
        # 查询总数
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.query(query)
        # 计算页数
        return result[0][0] // page_size + (1 if result[0][0] % page_size != 0 else 0)

    # 分页查询financialindices表中的所有内容 处理可能的大量数据
    def query_all_indices(self, page, type=None, page_size=100):
        # 分页查询
        if not type or not type in self.table_name:
            table_name = 'financialindices'
            query = f"SELECT * FROM {table_name} LIMIT {page_size} OFFSET {page_size * (page - 1)}"
            cursor = self.cursor
        else:
            table_name = self.table_name[type]
            # 对于具体数据表项需要整理为字典类型
            # 确保在配置表项中存在
            cursor = self.dict_cursor
            query = f"""
                    SELECT {table_name}.*
                    FROM {table_name}
                    JOIN financialindices ON {table_name}.IndexID = financialindices.IndexID
                    LIMIT {page_size}
                    OFFSET {page_size * (page - 1)}
                    """
        return execute_query(cursor, query)
    
    # 插入数据到financialindices表
    '''
    INSERT INTO financialindices
    (IndexID, Ticker, `Type`, Description, Source, SubType)
    VALUES(0, '', '', '', '', '');
    '''
    def insert_indices(self, ticker, type, source='sina', subtype='', description=''):
        # 插入数据
        query = f"INSERT INTO financialindices (IndexID, Ticker, `Type`, Description, Source, SubType) VALUES({0}, '{ticker}', '{type}', '{description}', '{source}', '{subtype}')"
        res = self.update(query)
        self.connection.commit()
        return res
    
    # 更新financialindices表中的数据
    '''
    UPDATE financialindices
    SET ...
    WHERE Ticker='ticker';
    '''
    def update_indices(self, ticker, source, query):
        # 更新数据 增加source考虑了多数据源处理同一ticker的情况（其实感觉不太可能
        query = f"UPDATE financialindices SET {query} WHERE Ticker='{ticker} AND Source='{source}';"
        res = self.update(query)
        self.connection.commit()
        return res
    
    # 更新具体表项的数据 
    def update_data_info(self, type, index_id, query):
        # 获取表名
        # 错误校验
        if not type in self.table_name:
            raise ValueError('Invalid type')
        table = self.table_name[type]
        # 更新数据
        query = f"UPDATE {table} SET {query} WHERE IndexID={index_id}"
        res = self.update(query)
        self.connection.commit()
        return res
    
    # 查询当前页内容的具体数据 对四个类别的表分别做自然连接查询
    def get_page_data_all(self, page, page_size=100):
        # 执行一次
        page_info = self.query_all_indices(page, None, page_size)
        # 查询数据
        data = {}
        for type in self.table_name:
            data[type] = []
        for index in page_info:
            # 获取属性
            index_id = index[0]
            type = index[2]
            # 查询对应数据
            table = self.table_name[type]
            # 查询数据
            query = f"SELECT * FROM {table} WHERE IndexID={index_id}"
            # 转换为字典类型
            res = execute_query(self.dict_cursor, query)
            data[type].append(res[0])
        return data
    
    # 查询具体表项的数据
    def get_typed_page_data(self, type, page, page_size=100):
        if not type:
            return self.get_page_data_all(page, page_size)
        # 错误校验
        if not type in self.table_name:
            raise ValueError('Invalid type')
        # 查询数据
        return self.query_all_indices(page, type, page_size)