import requests
import time
import pandas as pd
import requests

url = "https://youjia.baidu.com/view/carDatabase"

h = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Dest': 'document',
  'Accept-Language': 'zh-CN,zh;q=0.9',
}


session = requests.session()
session.get(url, headers=h)

all_item = []


class YouJia(object):
    def __init__(self):
        self.session = requests.session()
        self.all_cx = []
        self.all_brand = []
        self.fold = None
        self.pn = []

    def get_type(self):
        """
        获取所有的品牌名及编码
        :return: {'cd': 品牌id, 'nm': 平排名}
        """
        # resp = session.get(url=u, headers=h)
        # print(resp.request.headers)
        resp = session.get(url='https://youjia.baidu.com/gethomeinfo', params={'token': '1_526c1239fc0b0512a2bd13ac6b962f5f'}, headers=h)
        # print(resp.json())
        brand_list = resp.json()['Result']

        for brand in brand_list['brand_list']:
            # print(brand)
            self.all_brand += [{'cd': br['code'], 'nm': br['name']} for br in brand['brandList']]

    def get_brand(self, bd: int):
        """

        :param bd: 品牌id
        :return:
        """
        resp = session.get(url='https://youjia.baidu.com/conditionsearch',
                           params={
                                'token': '1_526c1239fc0b0512a2bd13ac6b962f5f',
                                'sort': 4,
                                'brand': bd,
                                'rn': 25,
                                'pn': 1
                            }).json()
        print(resp['Result']['series'])
        self.all_cx += [s['seriesId'] for s in resp['Result']['series']]
        # print(resp['Result']['total'])
        fp = int(resp['Result']['total']/25) if resp['Result']['total']%25 == 0 else int(resp['Result']['total']/25+1)
        print(fp)
        for pp in range(2, fp+1):
            self.get_next(bd=bd, p=pp)

    def get_next(self, bd: int, p: int):
        resp = session.get(url='https://youjia.baidu.com/conditionsearch',
                           params={
                                'token': '1_526c1239fc0b0512a2bd13ac6b962f5f',
                                'sort': 4,
                                'brand': bd,
                                'rn': 25,
                                'pn': p
                            }).json()
        self.all_cx += [s['seriesId'] for s in resp['Result']['series']]

    def get_detail(self, sid):
        resp = session.get(url='https://youjia.baidu.com/getcarpiclist',
                    params={
                        'token': '1_526c1239fc0b0512a2bd13ac6b962f5f',
                        'city': '',
                        'is_bd_app': 1,
                        'pn': 1,
                        'rn': 30,
                        'series_id': sid,
                        'series_name': '',
                        'tag_name': '外观',
                        'own_total': 130
                    }).json()
        self.fold = resp['Result']['lists']['seriesName']
        self.pn += [pl['ObjURL'] for pl in resp['Result']['lists']['list']]
        fp = int(resp['Result']['total'] / 30) if resp['Result']['total'] % 30 == 0 else int(
            resp['Result']['total'] / 30 + 1)
        for pp in range(2, fp+1):
            self.detail_next(sid, pp)

    def detail_next(self, sid, p: int):
        resp = session.get(url='https://youjia.baidu.com/getcarpiclist',
                           params={
                               'token': '1_526c1239fc0b0512a2bd13ac6b962f5f',
                               'city': '',
                               'is_bd_app': 1,
                               'pn': p,
                               'rn': 30,
                               'series_id': sid,
                               'series_name': '',
                               'tag_name': '外观',
                               'own_total': 130
                           }).json()
        self.pn += [pl['ObjURL'] for pl in resp['Result']['lists']['list']]

    def save(self):
        df = pd.DataFrame()
        df['link'] = self.pn
        df.to_csv(f'./img/{self.fold}.csv')


yj = YouJia()
yj.get_type()
print(yj.all_brand)
for b in yj.all_brand:
    print(b)
    yj.get_brand(bd=int(b['cd']))
print(yj.all_cx)
for s in yj.all_cx:
    yj.get_detail(sid=int(s))
    yj.save()


