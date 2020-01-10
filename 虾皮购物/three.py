#!/usr/bin/python3

import threading
import time
import json
import requests
from fake_useragent import UserAgent
from rq import recv_task, send_task
from DBPool import get_db_pool

xp_session = requests.session()
ua = UserAgent()
db_pool = get_db_pool(False)
head = {
    'Host': 'xiapi.xiapibuy.com',
    'User-Agent': ua.random,
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    # 'Referer': 'https://xiapi.xiapibuy.com/%E5%B0%8F%E5%8F%AF%E6%84%9B-%E8%83%8C%E5%BF%83-cat.62.2165',
    'X-Requested-With': 'XMLHttpRequest',
    'X-API-SOURCE': 'pc',
    'If-None-Match-': '55b03-d89805e42f3c40319a1bb0402535e226',
    'DNT': '1',
    'Connection': 'keep-alive',
    # 'Cookie': '_gcl_au=1.1.432545707.1577329245; SPC_IA=-1; SPC_EC=-; SPC_F=fa6Tt3DeFaR8tjgTmSwTrdZInnM8jYaa; REC_T_ID=e9bcd9ea-278b-11ea-b67d-9c741a644d45; SPC_T_ID="Orxm3siHYzIiOa2ZQvyqRTkWXsNumArS/7eIXJgd6cZoBtsh7sgGwybyCz86DVh6SN+WnsGce4JdcfCaSqRoM1DWQ1fbjq0HAhv/kTOnftk="; SPC_U=-; SPC_T_IV="JKgl7YCaLsARIQgm/sheIg=="; __BWfp=c1577329249525x816a2f680; cto_bundle=qEyMzl9XSkRyZld0d1lCelNBMnM2TWxvJTJCQ2JqaUh3UXh4cjVRVmI5YTd3T2lNUXVzUDFSWWJXM3JyWU50bklqek1LdXElMkIlMkZYJTJCRXBMeTQ2SXpSWW9ZMk1hbE10dzRWcGt5MkhnVDNRejhzclU5M3dra3k3OCUyQlZJMUk1b1R1UVVpajRkN3JvNGcxZ1lDJTJCNVZvMkJzR0dzclclMkZWc3hoNldHWUY5MHBlMnIxMmpwMVNFWSUzRA; _ga=GA1.2.582021135.1577329325; _med=refer; SPC_SI=ak2ho3wwm1ebkdgmteromq50qqkg9s2g; csrftoken=mUYYXxQU1ZbcM6ii26DwoUVnk60t7SQe; welcomePkgShown=true',
    'TE': 'Trailers'
}


exitFlag = 0


class Consumer(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.queue_name = 'Xiapi'

    def run(self):
        print("开始线程：" + self.name)
        recv_task(self.queue_name, callback)
        print("退出线程：" + self.name)


def callback(ch, method, properties, body):
    # 调用爬取函数
    par(body)
    # 通知队列消息完成
    ch.basic_ack(delivery_tag=method.delivery_tag)
    # time.sleep(1.5)


def par(body):
    # 将消息转换为utf8编码，然后解析
    s = body.decode('utf-8')
    # print(type(s), s)
    i_json = json.loads(s)
    b_tp = i_json['big']
    s_tp = i_json['small']
    api = i_json['link']
    # print(i['big'], i['small'], i['link'])
    try:
        # print(big, small, api)
        r = xp_session.get(api, headers=head).json()
        # print(r)
    except Exception as get_error:
        # 出现异常把消息重新放入队列
        send_task('Xiapi', body)
        print('Error  >>>>>>  ', get_error)
        time.sleep(2)
    for i in r['items']:
        # print(i)
        itemid = i['itemid']  # 商品id
        mingcheng = i['name']  # 标题
        xiaoliang = i['historical_sold']  # 销量
        # price = i['price'] / 100000  # 价格
        # print(price)
        star = i['item_rating']['rating_star']  # 评分
        b_type = b_tp
        s_type = s_tp
        weizhi = i['shop_location']  # 商家位置
        shopid = i['shopid']  # 商家id
        brand = i['brand']  # 自有品牌
        # price_min = i['price_min'] / 100000  # 最低价格
        # price_max = i['price_min'] / 100000  # 最高价格
        link = 'https://xiapi.xiapibuy.com/' + mingcheng.replace(' ', '-') + '-i.' + str(shopid) + '.' + str(itemid)
        # print(link)
        # in_list = [itemid, mingcheng, xiaoliang, price, star, b_type, s_type, weizhi, shopid, brand, price_min, price_max, link]
        in_list = [itemid, mingcheng, xiaoliang, star, b_type, s_type, weizhi, shopid, brand, link]
        # print(in_list)
        write_db(itemid, mingcheng, xiaoliang, star, b_type, s_type, weizhi, shopid, brand, link)


def write_db(itemid, mingcheng, xiaoliang, star, b_type, s_type, weizhi, shopid, brand, link):
    # print(itemid, mingcheng, xiaoliang, star, b_type, s_type, weizhi, shopid, brand, link)
    sql = """
        INSERT IGNORE INTO XiapiShop(商品id,名称,销量,评分,大类别,小类别,商家地址,商家id,品牌,link
        ) VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')
    """
    try:
        # 从数据库连接池中取出一条连接
        conn = db_pool.connection()
        cursor = conn.cursor()
        # 随便查一下吧
        insert_sql = sql.format(itemid, mingcheng, xiaoliang, star, b_type, s_type, weizhi, shopid, brand, link)
        # print(insert_sql)
        cursor.execute(insert_sql)
        conn.commit()
        # 把连接返还给连接池
        conn.close()
    except Exception as db_error:
        print('数据库异常 >>>>>> ', db_error)


if __name__ == '__main__':
    # 记录开始时间
    start_time = time.time()
    ConsumerList = ["Consumer-1", "Consumer-2", "Consumer-3", "Consumer-4", "Consumer-5", "Consumer-6",
                    "Consumer-7", "Consumer-8", "Consumer-9", "Consumer-10", "Consumer-11", "Consumer-12",
                    "Consumer-13", "Consumer-14", "Consumer-15", "Consumer-16", "Consumer-17", "Consumer-18",
                    "Consumer-19", "Consumer-20", "Consumer-21", "Consumer-22", "Consumer-23", "Consumer-24"]
    threads = []
    threadID = 1

    for name in ConsumerList:
        thread = Consumer(threadID, name)
        thread.start()
        threads.append(thread)
        threadID += 1
    for t in threads:
        t.join()
    print("退出主线程")
    end_time = time.time()
    run_time = (end_time - start_time)
    print(run_time)
