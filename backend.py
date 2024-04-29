'''
后端接口服务
'''

# 连接数据库
from config_parser import read_config
from db_helper import FinanceDB

capture_config, db_config, modules, modules_max = read_config('config.ini')
db = FinanceDB(db_config)

# 服务器

from fastapi import FastAPI, Query, Response, status

app = FastAPI(title='Finance Index', version="0.1.0")

# 数据类型字典
type_dict = {
    'stock': 'Stock',
    'fund': 'Fund',
    'forex': 'Forex',
    'futures': 'Futures',
}

# 获取对应种类的数据页数
@app.get('/pagecount/')
async def get_page_count(response: Response, type: str = Query(None, description='数据类型'), size: int = Query(100, gt=0, description='每页数据量')):
    # 合法性检查
    if type:
        type = type.lower()
        if not type in type_dict:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'error': 'Invalid type'}
    try:
        # 获取页数
        _type = None if not type else type_dict[type]
        res = db.get_indices_pages(_type, size)
        return {'page_count': res}
    except Exception as e:
        # 服务器错误
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'error': str(e)}

# 获取对应种类的数据
@app.get('/data/')
async def get_data(response: Response, type: str = Query(None, description='数据类型'), page: int = Query(1, gt=0, description='页码'), size: int = Query(100, gt=0, description='每页数据量')):
    # 合法性检查
    if type:
        type = type.lower()
        if not type in type_dict:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'error': 'Invalid type'}
    try:
        # 获取数据
        _type = None if not type else type_dict[type]
        res = db.get_typed_page_data(_type, page, size)
        return {'data': res}
    except Exception as e:
        # 服务器错误
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'error': str(e)}

# 启动
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=17987)
    db.close()
    print('Server stopped.')
