import requests
import urllib3
import time
import datetime
import random
import pymongo
from pymongo.errors import DuplicateKeyError
from fake_useragent import UserAgent
import logging
from threading import Thread, Timer
from queue import Queue
from Toutiao.toutaio_parse import detail_parse
from Toutiao.util import encrypt_md5


logger = logging.getLogger()
fh = logging.FileHandler("toutiao.log", encoding="utf-8", mode="a")
formatter = logging.Formatter("%(asctime)s %(threadName)s %(name)s %(levelname)s %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(threadName)s %(filename)s %(levelname)s %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     filemode='a')
ua = UserAgent()
clint = pymongo.MongoClient(host='127.0.0.1', port=27017)
db = clint.Spider
host = '27.43.186.62'
port = '9999'
proxy = {'http': f'https://{host}:{port}'}
resp_t = requests.get('https://www.baidu.com', timeout=5, headers={'User-Agent': ua.random}, proxies=proxy)
if resp_t.status_code == 200:
    print('ok')


class Toutiao(object):
    def __init__(self, kwd: str):
        self._domain = 'https://www.toutiao.com'
        self._search_api = 'https://www.toutiao.com/api/search/content'
        self._head = {
            'Host': 'www.toutiao.com',
            'User-Agent': ua.random,
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        self._session = requests.session()
        self._keyword = kwd
        # self._session.get(url=self._domain, headers=self._head, proxies=proxy)

    def get_list(self, o):
        p = {
            'aid': 24,
            'app_name': 'web_search',
            'offset': o,
            'format': 'json',
            'keyword': self._keyword
        }
        resp = self._session.get(url=self._search_api, headers=self._head, params=p, proxies=proxy)
        logger.info(resp.request.url)
        # logging.info(f'请求头 - {resp.request.headers}')
        # logging.info(f'响应头 - {resp.headers}')
        return resp

    def checking(self, resp):
        """
        验证response响应数据是否为空
        :param resp: 响应数据
        :return: 是否返回数据, 正常是list
        """
        # print(resp.text)
        json_data = resp.json()
        if isinstance(json_data['data'], list):
            return True
        elif isinstance(json_data['data'], dict):
            return False
        else:
            logger.warning('没有返回数据')
            return False

    def parse_list(self, resp):
        """
        解析返回响应把文章id放入mongodb
        :param resp: 响应
        :return:
        """
        json_data = resp.json()
        for data in json_data['data']:
            if 'article_url' in data.keys():
                aid = data['id']
                task = {'_id': encrypt_md5(aid), 'article_id': aid, 'status': 0, 'create_time': datetime.datetime.now()}
                try:
                    db.toutiao.insert_one(task)
                    logger.info(aid)
                except DuplicateKeyError:
                    logger.info(f'{aid}已存在')


def in_queue():
    """
    查询所有未完成的任务并放入队列
    :return:
    """
    find_results = db.toutiao.find({'status': 0})
    for find_result in find_results:
        q.put(find_result)
        db.toutiao.update_one({'_id': find_result['_id']}, {'$set': {'status': 2}})


class Work(Thread):
    def run(self):
        while True:
            # 判断queue是否为空，为空则从数据库中去未完成的任务
            if not q.empty():
                t = q.get()['article_id']
                try:
                    detail_parse(t)
                    db.toutiao.update_one({'_id': encrypt_md5(t)}, {'$set': {'status': 1}})
                    logger.info(f'任务 - {t} -> 完成')
                except requests.exceptions.ProxyError:
                    logger.warning(f'{t} -- requests.exceptions.ProxyError -> Cannot connect to proxy')
                except urllib3.exceptions.MaxRetryError:
                    logger.warning(f'{t} -- urllib3.exceptions.MaxRetryError -> Cannot connect to proxy')
                # time.sleep(random.randint(0, 1))
            elif not db.toutiao.find({'status': 0}).count():
                time.sleep(10)
                continue
            else:
                in_queue()


if __name__ == '__main__':
    q = Queue(200)
    for _ in range(1):  # 控制线程数量
        Work().start()
        print('启动子线程')
    # 关键词生产任务
    def producer():
        # print('这里执行了哦')
        while True:
            keywords = db.toutiao_keyword.find({'status': 0}, {'create_time': 0})
            if keywords.count():
                for keyword in keywords:
                    logger.info(keyword)
                    toutiao = Toutiao(kwd=keyword['keyword'])
                    offset = 0
                    while True:
                        res = toutiao.get_list(o=offset)
                        if toutiao.checking(res):
                            toutiao.parse_list(res)
                            offset += 20
                            # time.sleep(random.randint(3, 7))
                            continue
                        else:
                            for _ in range(2):
                                res = toutiao.get_list(o=offset)
                                if toutiao.checking(res):
                                    toutiao.parse_list(res)
                                    # time.sleep(random.randint(2, 5))
                                    continue
                                else:
                                    logger.warning(f'{keyword["keyword"]}-{offset}仍然没有数据')
                            # 将关键词任务标记为完成
                            db.toutiao_keyword.update_one({'_id': keyword['_id']}, {'$set': {'status': 1}})
                            logger.info(f'{keyword["keyword"]} -> 采集完成')
                            break
            else:
                logger.info('所有任务采集完成 -> 退出')
                break
        global main_thread
        main_thread = Timer(30, producer)
        main_thread.start()
    # main_thread = Timer(30, producer)
    # main_thread.start()
    producer()
