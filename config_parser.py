'''
读取配置文件 
生成数据库配置和采集模块配置
'''

import configparser

# 读取配置文件
def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    # 读取config['Database']下的所有配置
    db_config = {
        'host': config['Database']['Host'],
        'port': int(config['Database']['Port']),
        'user': config['Database']['User'],
        'password': config['Database']['Password'],
        'database': config['Database']['Database'],
        'charset': config['Database']['Charset'],
        'timeout': int(config['Database']['Timeout']) if config['Database'].get('Timeout') else None,
    }

    # 读取config['Capture']下的配置
    # 如果不存在
    if not config['Capture']['Seconds']:
        capture_config = {'seconds': 2}
    else:
        capture_config = {
            'seconds': int(config['Capture']['Seconds'])
        }

    # 读取config['Modules']下的所有配置 以及 config['ModulesMax']下的所有配置
    # 分别定义模块源路径与单次请求最多请求的数量
    modules = {}
    modules_max = {}
    for key in config['Modules']:
        modules[key] = config['Modules'][key]
    for key in config['ModulesMax']:
        modules_max[key] = int(config['ModulesMax'][key])
    # 对于未指定最大请求数量的模块，默认为1
    for key in modules.keys():
        if not key in modules_max.keys():
            modules_max[key] = 1

    # 如果db或者modules为空 抛出异常
    if not db_config or not modules:
        raise ValueError('Config file is invalid')
    return capture_config, db_config, modules, modules_max

'''
动态模块导入
'''

import importlib
import importlib.util
import sys
import os

# 将模块路径添加到系统搜索路径中
def import_module_path(module_path):
    # 将模块路径添加到系统搜索路径中
    # 不存在则抛出异常
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"module_path: {module_path} not found")
    # 如果module_path是相对目录，将其转换为绝对路径
    module_path = os.path.abspath(module_path)
    if module_path not in sys.path:
        sys.path.insert(0, os.path.dirname(module_path))

# 从包中导入模块
def import_module_from_package(package_name, module_name):
    try:
        module_path = f"{package_name}.{module_name}"
        module = importlib.import_module(module_path)
    except ImportError:
        print(f"import {module_path} failed")
        return None
    return module

# 从模块中导入API
def import_api_from_module(module, api_name):
    try :
        api = getattr(module, api_name)
    except AttributeError:
        print(f"import {api_name} from {module} failed")
        return None
    return api

'''
从数据采集源配置中生成数据源
'''

# 从配置中生成数据源
def gen_datasources_from_config(config):
    datasources = {}
    # 遍历配置中的所有模块
    for key, value in config.items():
        module_path = value
        import_module_path(module_path)
        # 主模块需要以spider命名
        module = import_module_from_package(key, 'spider')
        # 生成数据源实例并保存 需要以DataSource命名
        if module:
            datasources[key] = import_api_from_module(module, 'DataSource')()
    return datasources
