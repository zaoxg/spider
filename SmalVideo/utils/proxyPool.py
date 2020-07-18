"""
    获取代理

"""
import requests
import json
import time


def get_ip():
    url = "http://d.jghttp.golangapi.com/getip?num=1&type=2&pro=0&city=0&yys=0&port=1&pack=25961&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions="
    url = "http://http.9vps.com/getip.asp?username=13939105640&pwd=430d2b9187a3f971f4b2dca0196276c5&geshi=1&fenge=5&fengefu=&getnum=1"
    res = requests.get(url)

    proxies = {
        "http": "http://%s" % res.text,
        "https": "https://%s" % res.text,
    }
    return proxies