import requests
from fake_useragent import UserAgent
import urllib, urllib3
import time
import math, random
import csv
import re
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

kj_1688 = requests.session()
ua = UserAgent()
# api
api = 'https://widget.1688.com/front/getJsonComponent.json?namespace=wdcPcFetchService&widgetId=wdcPcFetchService&methodName=execute&serviceName=wdcKjSecondCateFetchService&param={0}&callback={1}&_={2}'
# 类别列表
resourceList = ["589691", "590366", "590397", "591850", "591862", "591869", "591886", "591895"]
head = {
    "Host": "widget.1688.com",
    "User-Agent": ua.random,
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://kj.1688.com/kitchen_dining.html?spm=a262gg.8864560.jifovpy5.262.164b6510cyeCnv",
    "TE": "Trailers",
}


def get_api():
    # kj = kj_1688.get('kj.1688.com')
    for resource in resourceList:
        # callback参数
        now = int(time.time() * 1000)  # 当前时间戳
        cbk = 'jsonp_' + str(now) + '_' + str(math.ceil(1e5 * random.random()))
        # _参数
        timestamp = str(int(time.time() * 1000 + 1))
        # 确定个数
        param = {
            "source": "1",
            "pageSize": 12,
            "pageNo": 1,
            "resourceId": resource
        }
        # dict转str，data进行encede
        db = json.dumps(param)
        da = urllib.parse.quote(db)
        # 拼接为请求地址
        a_link = api.format(da, cbk, timestamp)
        res = kj_1688.get(a_link, headers=head).text
        # 解析jsonp数据
        data = json.loads(re.findall(r'^\w+\((.*)\)$', res)[0])
        # print(data)
        num = data['content']['result']['data']['pcGetMiaoshaMarketOffer']['page']['totalNum']
        pag = num/12+1
        page = 0
        while p:
            param = {
                "source": "1",
                "pageSize": 12,
                "pageNo": pag,
                "resourceId": resource
            }
            # dict转str，data进行encede
            db = json.dumps(param)
            da = urllib.parse.quote(db)
            # 拼接为请求地址
            a_link = api.format(da, cbk, timestamp)
            res = kj_1688.get(a_link, headers=head).text
            # 解析jsonp数据
            data = json.loads(re.findall(r'^\w+\((.*)\)$', res)[0])
            # print(data)
            for info in data['content']['result']['data']['pcGetMiaoshaMarketOffer']['dataList']:
                print(info)
                offerId = info['offerId']  # 商品id
                subject = info['subject']  # 标题
                price = info['price']  # 价格
                unit = info['unit']  # 计量单位
                sellNum = info['sellNum']  # 销量
                offerPicUrl = info['offerPicUrl']  # 封面图
                companyName = info['companyName']  # 生产商
                url = info['url']  # 商品链接
                companyUrl = info['companyUrl']  # 商家店铺链接
                i = [offerId, subject, price, unit, sellNum, offerPicUrl, companyName, url, companyUrl]
                print(i)

    pass


if __name__ == '__main__':
    get_api()
