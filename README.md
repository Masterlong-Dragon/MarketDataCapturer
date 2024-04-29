# MarketDataCapturer
本项目是2023-2024学年下《软件工程经济学》的行情显示后端。前端详见[MarketDataView](https://github.com/LZY2275/MarketDataView)

实时市场行情获取存储，以及http查询接口提供。

## 安装配置

### 基础配置

- 数据库配置

  - 在旧版MySQL5上测试通过。[详细请见数据库建立指示](database.md)

  - 在financialindices须根据采集模块要求填入正确待收集资产信息。

    > 必须字段包括：
    >
    > \-    Ticker：在采集模块中使用的最终代码
    >
    > \-    Type：种类，包括Forex（外汇）、Fund（基金）、Futures（期货）、Stock（股票）
    >
    > \-    Source：数据采集模块名称 设置实际使用的采集模块
    >
    > \-    SubType：补充信息，用于采集模块具体运行时可能的补充参数。 
    >
    > 对于sina采集模块，特定指标/产品需要下列补充参数：
    >
    > - 期货：需要提供指标/产品代码类型前缀（直接复制Ticker项即可）
    >
    > - 股票：需要提供指标/产品代码类型，目前支持的有：沪深（sh，sz），美股（us），港股（hk，采集结果可能有误）

  - 可动态更改其内容以改变实时抓取配置。

- 采集程序环境要求 python>=3.8.0 （未在更低版本上测试）

  - 需要补充的依赖包
    - fastapi
    - uvicorn
    - apscheduler
    - mysql-connector

- 数据采集服务为service.py

- http服务器为backend.py

  完成config.ini填写配置后，且确认数据库建立正确，通过python环境运行上述两个脚本即可。

配置文档需要完成数据库配置（已建立对应表项，在financialindices中填入了正确的待收集资产信息）、采集配置、数据源模块配置。

注意数据源模块配置，Modules与ModulesMax中的项应当一一对应（或缺省ModulesMax默认为），名称与financialindices中的相对应。Modules为数据源提供的参数是该数据源模块的路径（相对路径、绝对路径均可）

Capture部分以秒为单位描述采集间隔。不支持小数。

config.ini

> **[Database]**
> Host = 请填写
> Port = 请填写
> User = 请填写
> Password = 请填写
> Database = 请填写
> Charset = 请填写
> Timeout = 请填写
>
> **[Capture]**
> Seconds = 2
>
> **[Modules]**
> Sina = ./sina
>
> **[ModulesMax]**
> Sina = 50

### 拓展内容

本系统支持自定义拓展数据源。默认数据源为sina（新浪财经）。

拓展数据源需要以python包的形式组织，形式上与sina相同，必须包括：

- source（包名）
  - spider.py
    - 须包含DataSource类
      - 须包含方法raw(self, code)
        - 其中code是一个数组，包含了单次请求包含的一系列资产代码号
        - 返回的结果是未经过格式化符合数据库格式的基础信息（数组 ）
      - 须包含方法parse(self, raw_info, type, subtype='')
        - raw_info是raw返回结果中某单个元素的值
        - type，subtype是该元素对应配置信息中的值
        - 返回结果是格式化后的该资产信息
  - ...自定义处理的其它模块以辅助上述两个方法的实现

## 后端api说明

> 默认后端地址127.0.0.1:17987
>

### pagecount

get请求

指定查询的种类，单次查询下一页内容的最多数量

#### Prameters

| Name                 | Description                     |
| :------------------- | :------------------------------ |
| type: string(query)  | 数据类型                        |
| size: integer(query) | 每页数据量*Default value* : 100 |

- type可缺省 默认返回所有类型计数
  - type可为
    - stock 股票
    - fund 基金
    - futures 期货
    - forex 外汇
- size可缺省 默认为100/页

#### Responses

| Code | Description |
| ---- | ----------- |
| 200  | 正确返回    |
| 422  | 非法输入    |
| 500  | 内部错误    |

> 正确返回：
>
> {
>
> "page_count": 1
>
> }

### data

get请求

指定查询的类型，当前查询页，每页最多数量

> 请在使用data api前通过pagecount确认当前获取目标的可能总页数

#### Parameters

| Name                 | Description                      |
| :------------------- | :------------------------------- |
| type: string(query)  | 行情类型                         |
| page: integer(query) | 页码 *Default value* : 1         |
| size: integer(query) | 每页数据量 *Default value* : 100 |

- type可缺省 默认返回所有类型计数
  - type可为
    - stock 股票
    - fund 基金
    - futures 期货
    - forex 外汇
- page可缺省 默认为1
- size可缺省 默认为100/页

#### Responses

| Code | Description |
| ---- | ----------- |
| 200  | 正确返回    |
| 422  | 非法输入    |
| 500  | 内部错误    |

标准返回格式（可以忽略其中暂时用不上的部分，只取关键字段）：

*time部分是秒数 可转换为时刻*

- 缺省type时 返回四个类型的数据

  > {
  >
  > "data": {
  >
  > ​    "Forex": [...],
  >
  > ​    "Fund": [
  >
  > ​      {
  >
  > ​        "FundDataID": 4,
  >
  > ​        "IndexID": 26,
  >
  > ​        "Name": "华夏成长混合",
  >
  > ​        "Date": "2024-04-25",
  >
  > ​        "Time": 54240.0,
  >
  > ​        "Price": 0.7341,
  >
  > ​        "YesterdayPrice": 0.734,
  >
  > ​        "Changed": 0.0136
  >
  > ​      },
  >
  > ​      {
  >
  > ​        "FundDataID": 5,
  >
  > ​        "IndexID": 27,
  >
  > ​        "Name": "嘉实新能源新材料股票A",
  >
  > ​        "Date": "2024-04-25",
  >
  > ​        "Time": 54240.0,
  >
  > ​        "Price": 1.4493,
  >
  > ​        "YesterdayPrice": 1.43,
  >
  > ​        "Changed": 1.3497
  >
  > ​      }
  >
  > ​    ],
  >
  > ​    "Futures": [...],
  >
  > ​    "Stock": [...]
  >
  > }
  >
  > }

- stock 股票

  示例中美股的数据缺失了amount部分

  > {
  >  "data": [
  >      {
  >          "StockDataID": 12,
  >          "IndexID": 36,
  >          "Name": "道琼斯",
  >          "Date": "2024-04-25",
  >          "Time": 85209.0,
  >          "OpenPrice": 38052.09,
  >          "YesterdayPrice": 38460.922,
  >          "HighPrice": 38052.09,
  >          "LowPrice": 37754.379,
  >          "Price": 37869.488,
  >          "Volume": 159151362,
  >          "Amount": null
  >      },
  >      {
  >          "StockDataID": 13,
  >          "IndexID": 37,
  >          "Name": "标普500指数",
  >          "Date": "2024-04-25",
  >          "Time": 85209.0,
  >          "OpenPrice": 5019.88,
  >          "YesterdayPrice": 5071.63,
  >          "HighPrice": 5019.88,
  >          "LowPrice": 4990.58,
  >          "Price": 5010.87,
  >          "Volume": 963562583,
  >          "Amount": null
  >      }
  >  ]
  > }

- fund 基金

  > {
  >
  > "data": [
  >
  > ​    {
  >
  > ​      "FundDataID": 4,
  >
  > ​      "IndexID": 26,
  >
  > ​      "Name": "华夏成长混合",
  >
  > ​      "Date": "2024-04-25",
  >
  > ​      "Time": 54240.0,
  >
  > ​      "Price": 0.7341,
  >
  > ​      "YesterdayPrice": 0.734,
  >
  > ​      "Changed": 0.0136
  >
  > ​    },
  >
  > ​    {
  >
  > ​      "FundDataID": 5,
  >
  > ​      "IndexID": 27,
  >
  > ​      "Name": "嘉实新能源新材料股票A",
  >
  > ​      "Date": "2024-04-25",
  >
  > ​      "Time": 54240.0,
  >
  > ​      "Price": 1.4493,
  >
  > ​      "YesterdayPrice": 1.43,
  >
  > ​      "Changed": 1.3497
  >
  > ​    }
  >
  > ]
  >
  > }

- futures 期货

  （部分值为null）

  > {
  >  "data": [
  >      {
  >          "FuturesDataID": 5,
  >          "IndexID": 39,
  >          "Name": "WTI纽约原油",
  >          "Price": 82.38,
  >          "Date": "2024-04-25",
  >          "Time": 85211.0,
  >          "OpenPrice": 82.83,
  >          "MaxPrice": 83.33,
  >          "MinPrice": 81.99,
  >          "ClosePrice": null,
  >          "YesterdayPrice": 82.81,
  >          "Volume": null,
  >          "Amount": 394758.0
  >      },
  >      {
  >          "FuturesDataID": 6,
  >          "IndexID": 40,
  >          "Name": "布伦特原油",
  >          "Price": 86.55,
  >          "Date": "2024-04-25",
  >          "Time": 85204.0,
  >          "OpenPrice": 86.88,
  >          "MaxPrice": 87.47,
  >          "MinPrice": 86.23,
  >          "ClosePrice": null,
  >          "YesterdayPrice": 87.04,
  >          "Volume": null,
  >          "Amount": 0.0
  >      }
  >  ]
  > }

- forex 外汇

  > {
  >  "data": [
  >      {
  >          "FXDataID": 8,
  >          "IndexID": 29,
  >          "Name": "美元指数",
  >          "Date": "2024-04-25",
  >          "Time": 85205.0,
  >          "Price": 105.6758,
  >          "YesterdayPrice": 105.816,
  >          "OpenPrice": 105.8005,
  >          "HighPrice": 106.0017,
  >          "LowPrice": 105.4693
  >      },
  >      {
  >          "FXDataID": 9,
  >          "IndexID": 30,
  >          "Name": "欧元兑人民币即期汇率",
  >          "Date": "2024-04-25",
  >          "Time": 84977.0,
  >          "Price": 7.763,
  >          "YesterdayPrice": 7.7458,
  >          "OpenPrice": 7.757,
  >          "HighPrice": 7.7741,
  >          "LowPrice": 7.7391
  >      }
  >  ]
  > }
