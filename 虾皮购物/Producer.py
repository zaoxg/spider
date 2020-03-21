import requests
import json
import queue
import threading
import urllib3
import time
from rq import send_task
from 虾皮购物.GetType import b_type
from fake_useragent import UserAgent
urllib3.disable_warnings()

ua = UserAgent()
sessions = requests.session()
exitFlag = 0


class MyThread(threading.Thread):
    def __init__(self, threadID, name, que):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.que = que

    def run(self):
        print("开启线程：" + self.name)
        send(self.name, self.que)
        print("Exiting ", self.name)
        pass


def send(name, data_queue):
    # 商品列表的api
    # api = 'https://xiapi.xiapibuy.com/api/v2/search_items/?by=sales&fe_categoryids={}&limit=50&newest={}&order=desc&page_type=search&version=2'  # 台湾商品列表api
    # api = 'https://shopee.co.th/api/v2/search_items/?by=relevancy&limit=50&match_id={}&newest={}&order=desc&page_type=search&version=2'  # 泰国商品列表api
    api = 'https://th.xiapibuy.com/api/v2/search_items/?by=relevancy&limit=50&match_id={}&newest={}&order=desc&page_type=search&version=2'
    # 第3个字段是店铺id, 拼接url和id得出url
    while not exitFlag:
        queueLock.acquire()
        # 好像是不为空? 2020年3月14日17:12:02
        if not data_queue.empty():
            data = data_queue.get()
            queueLock.release()
            try:
                # print(name + '>>>>>>' + data)
                # print(data[0], data[1], data[2])
                # 爬虫爬取的页数 2020年3月14日17:13:03
                page = 20
                j_s = {}
                for p in range(1, page):
                    of = (p - 1) * 20
                    link = api.format(data[2], of)
                    j_s['big'] = data[0]
                    j_s['small'] = data[1]
                    j_s['link'] = link
                    # 构造商品类别页码放入mq 2020.03.14 15:10:00
                    send_task('Xiapi', json.dumps(j_s))
                time.sleep(0.1)
            except Exception as e:
                print('出事了 ---- E --- R --- R --- O --- R ----> ', e)
                # 不知道会出啥问题，就又放到queue了 2020.03.14 15:10:00
                data_queue.put(data)
                # print(response)
        else:
            queueLock.release()


def get_d():
    for d in b_type:
        # print(d)
        # print(list(d.keys()))
        # 大类
        # print(d.keys())
        b_tp = d[list(d.keys())[0]]
        # print(b_tp)  # 大类的名称
        for l in d[list(d.keys())[1]]:
            # print('小类id{0},名称是{1}'.format(l, d['second'][l]))
            s_tp = d['cate'][l]
            i_tuple = (b_tp, s_tp, l)
            # 加到队列里
            data_queue.put(i_tuple)


if __name__ == '__main__':
    # 记录开始时间
    start_time = time.time()
    crawlList = ["Producer-1", "Producer-2", "Producer-3", "Producer-4"]
    queueLock = threading.Lock()
    data_queue = queue.Queue()
    threads = []
    threadID = 1

    for name in crawlList:
        thread = MyThread(threadID, name, data_queue)
        thread.start()
        threads.append(thread)
        threadID += 1

    queueLock.acquire()
    # 从数据库获取待爬取的数据
    b_type = b_type()
    get_d()
    queueLock.release()

    while not data_queue.empty():
        pass
    exitFlag = 1

    for t in threads:
        t.join()
    print("退出主线程")
    end_time = time.time()
    run_time = (end_time - start_time)
    print(run_time)
