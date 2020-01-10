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
    'DNT': '1',
    'Connection': 'keep-alive',
    # 'Cookie': '_gcl_au=1.1.432545707.1577329245; SPC_IA=-1; SPC_EC=-; SPC_F=fa6Tt3DeFaR8tjgTmSwTrdZInnM8jYaa; REC_T_ID=e9bcd9ea-278b-11ea-b67d-9c741a644d45; SPC_T_ID="Orxm3siHYzIiOa2ZQvyqRTkWXsNumArS/7eIXJgd6cZoBtsh7sgGwybyCz86DVh6SN+WnsGce4JdcfCaSqRoM1DWQ1fbjq0HAhv/kTOnftk="; SPC_U=-; SPC_T_IV="JKgl7YCaLsARIQgm/sheIg=="; __BWfp=c1577329249525x816a2f680; cto_bundle=qEyMzl9XSkRyZld0d1lCelNBMnM2TWxvJTJCQ2JqaUh3UXh4cjVRVmI5YTd3T2lNUXVzUDFSWWJXM3JyWU50bklqek1LdXElMkIlMkZYJTJCRXBMeTQ2SXpSWW9ZMk1hbE10dzRWcGt5MkhnVDNRejhzclU5M3dra3k3OCUyQlZJMUk1b1R1UVVpajRkN3JvNGcxZ1lDJTJCNVZvMkJzR0dzclclMkZWc3hoNldHWUY5MHBlMnIxMmpwMVNFWSUzRA; _ga=GA1.2.582021135.1577329325; _med=refer; SPC_SI=ak2ho3wwm1ebkdgmteromq50qqkg9s2g; csrftoken=mUYYXxQU1ZbcM6ii26DwoUVnk60t7SQe; welcomePkgShown=true',
    'TE': 'Trailers'
}


exitFlag = 0


class ConPro(threading.Thread):
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
    try:
        # 将消息转换为utf8编码，然后解析
        s = body.decode('utf-8')
        # print(type(s), s)
        i = json.loads(s)
        print(i['big'], i['small'], i['link'])
        # 调用解析函数
        par(i['big'], i['small'], i['link'])
        # 通知队列消息完成
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # time.sleep(1.5)
    except Exception as e:
        # 出现异常把消息重新放入队列
        send_task('Xiapi', body)
        print('Error  >>>>>>  ', e)
        time.sleep(2)


def par(big, small, api):
    # print(big, small, api)
    r = xp_session.get(api, headers=head).json()
    # print(r)
    in_fo = {}
    for i in r['items']:
        itemid = i['itemid']  # 商品id
        shopid = i['shopid']  # 商家id
        title = i['name']  # 标题
        b_type = big
        s_type = small
        link = 'https://xiapi.xiapibuy.com/' + title.replace(' ', '-') + '-i.' + str(shopid) + '.' + str(itemid)
        # print(in_list)
        in_fo['itemid'] = itemid
        in_fo['shopid'] = shopid
        in_fo['title'] = title
        in_fo['b_type'] = b_type
        in_fo['s_type'] = s_type
        in_fo['url'] = link
        # print(json.dumps(in_fo))
        send_task('Xiapinfo', json.dumps(in_fo))


if __name__ == '__main__':
    # 记录开始时间
    start_time = time.time()
    ConsumerList = ["Con&Pro-1", "Con&Pro-2", "Con&Pro-3", "Con&Pro-4", "Con&Pro-5", "Con&Pro-6",
                    "Con&Pro-7", "Con&Pro-8", "Con&Pro-9", "Con&Pro-10", "Con&Pro-11", "Con&Pro-12"]
    threads = []
    threadID = 1

    for name in ConsumerList:
        thread = ConPro(threadID, name)
        thread.start()
        threads.append(thread)
        threadID += 1
    for t in threads:
        t.join()
    print("退出主线程")
    end_time = time.time()
    run_time = (end_time - start_time)
    print(run_time)
