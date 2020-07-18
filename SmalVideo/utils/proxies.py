#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 轮询代理池

import sys
sys.path.append("./")
import urllib
import urllib.request
import time
import re
import requests
import random

def get_proxy_status(proxies):
    try:
        url_list = [
            "https://www.baidu.com/",
            "https://www.360.cn/",
            # "http://ip.3322.org/"
        ]
        url = random.choice(url_list)
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"
        }
        response = requests.get(url, headers=headers, proxies=proxies, timeout=3, verify=False)
        # print(response.text)
        if response.status_code == 200:
            return True
    except Exception as e:
        return False


class Proxy_start(object):
    def __init__(self):
        try:
            self.proxy_url='http://118.31.104.230:19876/proxy/queryProxyInfo.json?username=buyer&password=YUANshi123'
            # self.proxy_url='http://118.31.104.230:19876/proxy/queryProxyInfo.json?username=credit&password=YUANshi123'
            # self.proxy_url='http://118.31.104.230:19876/proxy/queryProxyInfo.json?username=shoppingCart&password=YUANshi123'
            # self.proxy_url = 'http://118.31.104.230:19876/proxy/queryProxyInfo.json?username=check&password=YUANshi123'
            # self.proxy_url = 'http://10.31.54.65:19876/proxy/queryProxyInfo.json?username=buyer&password=YUANshi123'
            self.proxy_list = [proxy for proxy in urllib.request.urlopen(self.proxy_url, timeout=10).read().decode("utf-8").split("\r\n")]
            self.proxy_list.pop()
            # print(len(self.proxy_list))
        except Exception as e:
            time.sleep(10)
            self.__init__()

    # 获取代理
    def get_proxy_list(self):
        try:
            pro_list = [proxy for proxy in urllib.request.urlopen(self.proxy_url, timeout=10).read().decode("utf-8").split("\r\n")]
            pro_list.pop()
            return pro_list
        except Exception as e:
            self.get_proxy_list()

    # 添加代理
    def add_proxy(self):
        try:
            if len(self.proxy_list) < 10:
                result_get_proxy = self.get_proxy_list()
                print(result_get_proxy)
                for pro in result_get_proxy:
                    if len(pro) == 0:
                        continue
                    if pro in self.proxy_list:
                        continue
                    self.proxy_list.insert(0, pro)
                for pro_s in self.proxy_list:
                    if pro_s not in result_get_proxy:
                        self.proxy_list.remove(pro_s)
            return self.proxy_list
        except Exception as e:
            return self.proxy_list

    # 轮询代理
    def get_proxy(self):
        try:
            self.proxy_list = self.add_proxy()
            proxy = self.proxy_list[-1]
            self.proxy_list.remove(proxy)
            self.proxy_list.insert(0, proxy)
            return proxy
        except Exception as e:
            self.get_proxy()

    # 删除代理
    def delete_proxy(self, proxy):
        try:
            for proxies in self.proxy_list:
                try:
                    result = re.search('(' + proxy + ')', proxies).group(1)
                    if result:
                        self.proxy_list.remove(proxies)
                        print("删除")
                        return "delete_proxy 成功!"
                except:
                    pass

            return "delete_proxy 失败!"
        except Exception as e:
            return "delete_proxy 失败!"


    # 获取代理
    def get_check_proxy(self):
        complete_proxy = self.proxy_time()
        ip_port = complete_proxy.split(",")[0]
        # print(ip_port)
        # ip = ip_port[0]
        # port = ip_port[1]
        # print(ip,port)
        # proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        #     "host": ip,
        #     "port": port,
        #     "user": "yuanshi1",
        #     "pass": "yuanshi1",
        # }
        # proxyMetas = "https://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        #     "host": ip,
        #     "port": port,
        #     "user": "yuanshi1",
        #     "pass": "yuanshi1",
        # }
        proxies = {
            "http": "http://%s" % ip_port,
            "https": "https://%s" % ip_port,
        }
        # print(proxies)
        # proxies = {
        #     "http": proxyMeta,
        #     "https": proxyMetas,
        # }
        result = get_proxy_status(proxies)
        # print(result)
        if result:
            return proxies
        else:
            self.delete_proxy(ip_port)
            self.get_check_proxy()
        # return proxies


    # 检测代理有效时间
    def proxy_time(self):
        while True:
            complete_proxy = self.get_proxy()
            proxy_end_time = int(complete_proxy.split(",")[-1])
            if proxy_end_time - time.time() >= 120:
                break
            error_ip = complete_proxy.split(",")[0]
            self.delete_proxy(error_ip)

        return complete_proxy

    # 获取所有的代理IP
    def get_all_proxy(self):
        return self.proxy_list

proxy_start = Proxy_start()


def get_proxy2():
    proxies = proxy_start.get_check_proxy()
    if proxies != None:
        return proxies
    else:
        return get_proxy2()

def delete_proxy(proxy):

    return proxy_start.delete_proxy(proxy)

if __name__ == '__main__':
    print(get_proxy2())

