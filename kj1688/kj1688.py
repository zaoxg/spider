import requests
from fake_useragent import UserAgent
import urllib, urllib3
import time
import math, random
import csv
import re
import json
from kj1688.GetType import type_list
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

kj_1688 = requests.session()
ua = UserAgent()

api = 'https://widget.1688.com/front/getJsonComponent.json?namespace=wdcPcFetchService&widgetId=wdcPcFetchService&methodName=execute&serviceName=wdcKjSecondCateFetchService&param={0}&callback={1}&_={2}'
u = 'https://dcms.1688.com/open/query.json?app=DCMS&dataId=236&to=3000&n=30&fields=versionContent,errorMsgs,crocoServerTime&sk0=89fa29b8baf0fd1056a946fffde4b1c8&resourceId=589695&useCookieMemberId=&rtnMode=1&callback=jsonp_uw8iggjw9ou61si'
tp_l = type_list(u)

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


def s_type():
    for d in tp_l:
        # print(d)
        # print(list(d.keys()))
        # 大类
        b_tp = d[list(d.keys())[0]]
        for l in d[list(d.keys())[1]]:
            # print('小类id{0},名称是{1}'.format(l, d['second'][l]))
            s_tp = d['second'][l]
            get_api(b_tp, l, s_tp)


def get_api(b_tp, l, s_tp):
    # kj = kj_1688.get('kj.1688.com')
    # for resource in resourceList:
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
        "resourceId": l
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
    pag = int(num / 12 + 1)
    page = 0
    # 翻页参数pageNo
    while pag:
        page = page + 1
        param = {
            "source": "1",
            "pageSize": 12,
            "pageNo": page,
            "resourceId": l
        }
        # dict转str，data进行encede
        db = json.dumps(param)
        da = urllib.parse.quote(db)
        pag = pag - 1
        # 拼接为请求地址
        a_link = api.format(da, cbk, timestamp)
        try:
            res = kj_1688.get(a_link, headers=head, timeout=1).text
            # 解析jsonp数据
            data = json.loads(re.findall(r'^\w+\((.*)\)$', res)[0])
            # print(data)
            for info in data['content']['result']['data']['pcGetMiaoshaMarketOffer']['dataList']:
                # print(info)
                offerId = info['offerId']  # 商品id
                subject = info['subject']  # 标题
                price = info['price']  # 价格
                unit = info['unit']  # 计量单位
                sellNum = info['sellNum']  # 销量
                offerPicUrl = info['offerPicUrl']  # 封面图
                companyName = info['companyName']  # 生产商
                url = info['url']  # 商品链接
                companyUrl = info['companyUrl']  # 商家店铺链接
                i = [offerId, subject, price, unit, sellNum, b_tp, s_tp, offerPicUrl, companyName, url, companyUrl]
                print(i)
                write_csv(i)
        except Exception as w:
            print(w)
        time.sleep(0.3)


def write_csv(i):
    # newline的作用是防止每次插入都有空行
    with open('data/' + 'kj1688' + '.csv', 'a+', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 以读的方式打开csv 用csv.reader方式判断是否存在标题
        with open('data/' + 'kj1688' + '.csv', 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            if not [row for row in reader]:
                writer.writerow(['商品id', '标题', '价格', '计量单位', '销量', '大类', '小类', '封面图', '生产商', '商品链接', '商家店铺链接'])
                writer.writerow(i)
            else:
                writer.writerow(i)


if __name__ == '__main__':
    s_type()
