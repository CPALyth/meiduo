# 美多商城
![](https://img.shields.io/badge/Python-3.6-blue.svg)
![](https://img.shields.io/badge/Django-3.2-blue.svg)
![](https://img.shields.io/badge/ubuntu-20.04-green.svg)
![](https://img.shields.io/badge/mysql-8.0.25-green.svg)
![](https://img.shields.io/badge/redis-4.0.9-green.svg)

基于Django框架的B2C电商项目-美多商城  

## 1 美多商城前台
web应用模式: 前后端不分离
![](https://z3.ax1x.com/2021/05/17/gREWiq.png)
|    模块    |             功能             |
| :--------: | :--------------------------: |
|    用户(users)    |     注册, 登录, 用户中心     |
|    地址(areas)    |   省市区三级联动  |
|    验证(verufications)    |      图形验证, 短信验证      |
| 第三方登录(oauth) |          对接QQ登录          |
|    首页(contents)    |           首页广告           |
|    商品(goods)    | 商品列表, 商品搜索, 商品详情 |
|   购物车(carts)   |    购物车管理, 购物车合并    |
|    订单(orders)    |      确认订单, 提交订单      |
|    支付(payment)    |   对接支付宝, 订单商品评价   |                           |

## 2 美多商城后台
web应用模式: 前后端分离
![](https://z3.ax1x.com/2021/05/24/gjynsI.png)