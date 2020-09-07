import requests
import time
import datetime
import random
import pymongo
from pymongo.errors import DuplicateKeyError
from fake_useragent import UserAgent
import logging
import hashlib
from threading import Thread
from queue import Queue
from Toutiao.toutaio_parse import detail_parse
from Toutiao.fenci import _word_split

# logger = logging.getLogger()
# fh = logging.FileHandler("tt.log", encoding="utf-8", mode="a")
# formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
# fh.setFormatter(formatter)
# logger.addHandler(fh)
# logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                    datefmt='%a %d %b %Y-%m-%d %H:%M:%S',
                    filemode='a')
ua = UserAgent()
clint = pymongo.MongoClient(host='127.0.0.1', port=27017)
db = clint.Spider


def try_again():
    pass


def encrypt_md5(arg):
    # 创建md5对象
    md5 = hashlib.md5()
    # 这里必须用encode()函数对字符串进行编码，不然会报 TypeError: Unicode-objects must be encoded before hashing
    md5.update(arg.encode(encoding='utf-8'))
    # 加密
    return md5.hexdigest()


def kk():
    all_keyword = []
    # ks = requests.get(url='').json()
    # for k in ks:
    #     all_keyword += _word_split(k['keyword'])
    str_a = '(中国电科|中国电子科技集团|中国电子科技集团公司|这个电子科技集团有限公司|中电集团|中电科|电科集团|((中国电科|中电科)&(研究所|公司|集团)))&!中国电科院'
    all_keyword += _word_split(str_a)
    return all_keyword


class Toutiao(object):
    def __init__(self, kwd: str):
        self._domain = 'https://www.toutiao.com'
        self._search_api = 'https://www.toutiao.com/api/search/content'
        self._head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        self._session = requests.session()
        self._keyword = kwd
        self._session.get(url=self._domain, headers=self._head)

    def get_list(self, o):
        p = {
            'aid': 24,
            'app_name': 'web_search',
            'offset': o,
            'format': 'json',
            'keyword': self._keyword
        }
        resp = self._session.get(url=self._search_api, params=p)
        # logging.info(f'请求头 - {resp.request.headers}')
        # logging.info(f'响应头 - {resp.headers}')
        return resp

    def checking(self, resp):
        """
        验证response响应数据是否为空
        :param resp: 响应数据
        :return: 是否返回数据, 正常是list
        """
        json_data = resp.json()
        if isinstance(json_data['data'], list):
            return True
        elif isinstance(json_data['data'], dict):
            return False
        else:
            logging.warning('没有返回数据')
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
                except DuplicateKeyError as has:
                    logging.info(f'{aid}已存在')
                logging.info(aid)


def in_queue():
    """
    查询所有未完成的任务并放入队列
    :return:
    """
    find_results = db.toutiao.find({'status': 0})
    for find_result in find_results:
        q.put(find_result)


class Work(Thread):
    def run(self):
        while True:
            # 判断queue是否为空，为空则从数据库中去未完成的任务
            if not q.empty():
                t = q.get()['article_id']
                detail_parse(t)
                db.toutiao.update_one({'_id': encrypt_md5(t)}, {'$set': {'status': 1}})
                logging.info(f'任务{t}完成')
                time.sleep(random.randint(0, 3))
            else:
                in_queue()
                time.sleep(5)


if __name__ == '__main__':
    q = Queue(200)
    head = {
        'User-Agent': ua.random
    }
    for _ in range(1):  # 控制线程数量
        Work().start()
    # 关键词生产任务
    for k in kk():
        logging.info(k)
        toutiao = Toutiao(kwd=k)
        offset = 0
        while True:
            res = toutiao.get_list(o=offset)
            if toutiao.checking(res):
                toutiao.parse_list(res)
                time.sleep(random.randint(3, 7))
                offset += 20
                continue
            else:
                for _ in range(3):
                    res = toutiao.get_list(o=offset)
                    if toutiao.checking(res):
                        toutiao.parse_list(res)
                        time.sleep(random.randint(2, 5))
                        continue
                    else:
                        logging.warning('仍然没有数据')
                break
