# 获取系统分类成份股get_stock_list

### 根据入参返回指定证券代码列表

```
    def get_stock_list(market = None,
                       list_type: int = 0) -> List:
```

### 输入参数

| 参数        | 是否必选 | 参数类型 | 参数说明   |
| --------- | ---- | ---- | ------ |
| market    | Y    | str  | 指定代码   |
| list_type | Y    | int  | 返回数据类型 |

- list_type = 0 只返回代码，list_type = 1 返回代码和名称

```
默认为全部A股
    0:自选股 1:持仓股
    5:所有A股 6:上证指数成份股 7:上证主板 8:深证主板 9:重点指数 
    10:所有板块指数 11:缺省行业板块 12:概念板块 13:风格板块 14:地区板块 15:缺省行业分类+概念板块 16:研究行业一级 17:研究行业二级 18:研究行业三级
    21:含H股 22:含可转债 23:沪深300 24:中证500 25:中证1000 26:国证2000 27:中证2000 28:中证A500
    30:REITs 31:ETF基金 32:可转债 33:LOF基金 34:所有可交易基金 35:所有沪深基金 36:T+0基金
    49:金融类企业 50:沪深A股 51:创业板 52:科创板 53:北交所
    101:国内期货 102:港股 103:美股
    91:ETF追踪的指数
    92:国内期货主力合约
```

### 接口使用(获取A股和港股列表)

A股可以获得代码和名称，但港股只能获取代码列表。

```
from tqcenter import tq
tq.initialize(__file__)


# 所有A股可以获得代码和名称
a_stock_list = tq.get_stock_list(market = "5", list_type=1)
print(a_stock_list)
print(len(a_stock_list))

[{'Code': '000001.SZ', 'Name': '平安银行'}, {'Code': '000002.SZ', 'Name': '万 科Ａ'}, {'Code': '000004.SZ', 'Name': '*ST国华'}, ...]
5515

# 102:港股 - 只能获得代码，不能获得名称。
h_stock_list = tq.get_stock_list(market = "102", list_type=0)
print(h_stock_list)
print(len(h_stock_list))

['00001.HK', '00002.HK', '00003.HK', '00004.HK', ...]
3345
```

### 数据样本

```
[{'Code': '000001.SZ', 'Name': '平安银行'}, {'Code': '000002.SZ', 'Name': '万 科Ａ'}, {'Code': '000004.SZ', 'Name': '*ST国华'}, ...]
5515
```
