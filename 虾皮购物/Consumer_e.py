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
    'DNT': '1',
    'TE': 'Trailers'
}
api = 'https://xiapi.xiapibuy.com/api/v2/item/get?itemid={}&shopid={}'

exitFlag = 0


class Consumer(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.queue_name = 'Xiapinfo'

    def run(self):
        print("开始线程：" + self.name)
        recv_task(self.queue_name, callback)
        print("退出线程：" + self.name)


def callback(ch, method, properties, body):
    try:
        # 将消息转换为utf8编码，然后解析
        inf = body.decode('utf-8')
        # print(type(s), s)
        i = json.loads(inf)
        print(i['itemid'], i['shopid'], i['title'], i['b_type'], i['s_type'], i['url'])
        # 调用爬取函数
        get_info(i['itemid'], i['shopid'], i['b_type'], i['s_type'], i['url'])
        # 通知队列消息完成
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # time.sleep(1.5)
    except Exception as get_error:
        # 出现异常把消息重新放入队列
        send_task('Xiapinfo', body)
        print('Error  >>>>>>  ', get_error)
        time.sleep(2)


def get_info(itemid, shopid, b_type, s_type, url):
    # print(big, small, api)
    res = xp_session.get(api.format(itemid, shopid), headers=head).json()
    itemid = res['item']['itemid']  # 商品id
    name = res['item']['name']  # 名称
    sold = res['item']['sold']  # 月销量
    price = res['item']['price'] / 100000  # 价格
    star = res['item']['item_rating']['rating_star']  # 评分
    cmt_count = res['item']['cmt_count']  # 评论数
    liked_count = res['item']['liked_count']  # 喜欢人数
    brand = res['item']['brand']  # 品牌
    shopid = res['item']['shopid']  # 商家id
    location = res['item']['shop_location']  # 商家地址
    hisold = res['item']['historical_sold']  # 历史销量
    write_db(itemid, name, sold, hisold, price, star, b_type, s_type, cmt_count, liked_count, brand, shopid, location, url)


def write_db(itemid, name, sold, hisold, price, star, b_type, s_type, cmt_count, liked_count, brand, shopid, location, url):
    # print(itemid, name, sold, hisold, price, star, b_type, s_type, cmt_count, liked_count, brand, shopid, location)
    sql = """
        INSERT IGNORE INTO Xiapi(商品id,名称,销量,历史销量,价格,评分,大类别,小类别,评论数,喜欢人数,品牌,商家id,商家地址,link
        ) VALUES("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}","{11}","{12}","{13}")
    """
    # 从数据库连接池中取出一条连接
    conn = db_pool.connection()
    cursor = conn.cursor()
    # 随便查一下吧
    insert_sql = sql.format(itemid, name, sold, hisold, price, star, b_type, s_type, cmt_count, liked_count, brand, shopid, location, url)
    # print(insert_sql)
    cursor.execute(insert_sql)
    conn.commit()
    # 把连接返还给连接池
    conn.close()
    print(insert_sql)


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
