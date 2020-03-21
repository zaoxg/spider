import requests
import json
import time
from lxml import etree
from LINE.Save import SaveFile

# 首页，有数据，也可以获取一下session
home = 'https://timeline.line.me/user/'
keep = SaveFile(path='gkinmall')


class LineSpider(object):
    def __init__(self, mid, cookie):
        self.id = mid
        self.cookie = cookie
        self.scroll = None
        self.session = requests.Session()

    # 首页数据以及下次请求需要的scroll
    def home(self):
        with self.session.get(
            url=home+self.id,
            headers={
                'Host': 'timeline.line.me',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                'Referer': 'https://access.line.me/',
                'Cookie': self.cookie
            }
        ) as response:
            print(response.status_code)
            # print(response.headers)
            html = etree.HTML(response.text)
            script = html.xpath('//script[@id="init_data"]/text()')[0]
            home_data = json.loads(script)
            scroll = home_data['userHome']['nextScrollId']  # 请求接口需要用到
            # print(scroll)
            self.scroll = scroll

            # 用户信息
            homeId = home_data['userHome']['homeId']  # 主页id
            postCount = home_data['userHome']['homeInfo']['postCount']  # 帖子数
            nickname = home_data['userHome']['homeInfo']['userInfo']['nickname']  # 用户名
            # 或许可以建一个以nickname为名的文件夹


            # 帖子相关
            print(len(home_data['userHome']['feeds']))  # 条数
            for data in home_data['userHome']['feeds']:
                # print(data)
                cid = data['feedInfo']['id']
                writing = data['post']['contents']['text']  # 这个就是tmd文案，2020年3月21日11:28:18
                keep.save_txt(folder=cid, file=cid, data=[writing, ])
                # 资源列表，目前看有两种：图片(PHOTO)，视频(VIDEO)
                for source in data['post']['contents']['media']:
                    if source['type'] == 'VIDEO':
                        uri = source["resourceId"]
                        sourceURI = f'https://obs.line-scdn.net/{uri}/mp4'
                        keep.save_video(folder=cid, file=uri, source=sourceURI)
                    if source['type'] == 'PHOTO':
                        sourceURI = f'https://obs.line-scdn.net/{uri}'
                        keep.save_picture(folder=cid, file=uri, source=sourceURI)
        print('home() ---> ', self.scroll)

    def info(self):
        scroll = self.scroll
        print('info() --- >', scroll)
        api = 'https://timeline.line.me/api/post/list.json'
        while body['nextScrollId']:
            parms = {
                'homeId': self.id,
                'scrollId': scroll,
                'postLimit': 10,
                'commentLimit': 2,
                'likeLimit': 20,
                'requestTime': str(time.time() * 1000).split('.')[0],
            }
            hrad = {
                'Host': 'timeline.line.me',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
                'X-Line-AcceptLanguage': 'zh_CN',
                'X-Timeline-WebVersion': '1.13.9',
                'Referer': f'https://timeline.line.me/user/{self.id}',
                'Cookie': self.cookie
            }
            with self.session.get(
                url=api,
                params=parms,
                headers=hrad
            ) as response:
                body = response.json()
                scroll = body['result']['nextScrollId']  # 把下一页的这个玩意重新赋值给self.scroll
                for one in body['result']['feeds']:
                    cid = one['feedInfo']['id']  # 或许有用？？2020年3月21日14:44:15
                    nickname = one['post']['userInfo']['nickname']
                    writing = one['post']['contents']['text']  # 文案
                    keep.save_txt(folder=cid, file=cid, data=[writing, ])

                    # 资源列表，目前看有两种：图片(PHOTO)，视频(VIDEO)
                    for source in one['post']['contents']['media']:
                        if source['type'] == 'VIDEO':
                            uri = source["resourceId"]
                            sourceURI = f'https://obs.line-scdn.net/{source["resourceId"]}/mp4'
                            keep.save_video(folder=cid, file=uri, source=sourceURI)
                        if source['type'] == 'PHOTO':
                            uri = source["resourceId"]
                            sourceURI = f'https://obs.line-scdn.net/{source["resourceId"]}'
                            keep.save_picture(folder=cid, file=uri, source=sourceURI)
            print('info()end ---> ', scroll)

    def run(self):
        start = time.time()
        self.home()
        self.info()
        end = time.time()
        download = end - start
        print(f'下载耗时: {download}s')
        pass
