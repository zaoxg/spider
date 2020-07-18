"""
通过读取excel的链接，将重定向之后的userID，url保存到数据库

"""
import requests
import pandas as pd
import time
import random
import functools
import traceback
from utils.proxyPool import get_ip
from utils.db import MysqlUtil
from requests.exceptions import ConnectionError
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.packages.urllib3.exceptions import ProxyError as urllib3_ProxyError
from threading import Thread

# 获取ip
proxies = get_ip()


def change_ip():
    global proxies
    proxies = get_ip()


def tryTime(maxTry, timeout=random.random()):
    """
    重试
    :param maxTry:重试次数
    :param timeout:睡眠时间
    :return:
    """

    def wrap1(func):
        # functools.wraps 可以将原函数对象的指定属性复制给包装函数对象,
        @functools.wraps(func)
        def __decorator(*args, **kwargs):
            tryTime = 0
            while tryTime <= maxTry:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    print("TryTime_except==%s"%traceback.format_exc())
                    # logDebug("tryTime","TryTime_except==%s"%traceback.format_exc())
                time.sleep(timeout)

        return __decorator

    return wrap1


class Get_user(object):

    def __init__(self):
        self.database = MysqlUtil()

    def get_id(self, file_name):
        data = pd.read_excel(file_name, usecols=[0])
        result_list = data.values.tolist()
        id_list = []
        for user_id in result_list:
            id_list.append(user_id[0])
        return id_list

    @tryTime(3)
    def get_url(self, file_name):
        url_list = self.get_id(file_name)
        for url in url_list:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
            # 请求网页
            try:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
                time.sleep(0.3)
                url = response.url
                short_url = url.split("?")[0]
                user_id = short_url.split("?")[0].split("/")[-1]
                if "profile" in short_url:
                    sql = "insert into video.kuaishou_user(userID, url) values ('%s', '%s')" % (user_id, short_url)
                    self.database.save_data(sql)
                    print(short_url)
            except ConnectionError as ce:
                if (isinstance(ce.args[0], MaxRetryError) and isinstance(ce.args[0].reason, urllib3_ProxyError)):
                    # proxies = Proxy_start().get_proxy2()
                    print("IP失效了")
                    change_ip()


if __name__ == "__main__":
    a = Get_user()
    th_list = []
    th = Thread(target=a.get_url, args=("快手账号统计.xlsx",))
    th.start()
    th_list.append(th)
    if len(th_list) > 20:
        for th_one in th_list:
            th_one.join()
        th_list = []

