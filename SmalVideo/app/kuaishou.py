"""
    1.提取数据库中状态值为0的用户页面URl
    2.通过PC端用户Url获取某用户下的第一页（24条）数据
    3.提取数据插入数据库，并修改爬取成功的用户url状态值为1

"""
import requests
import re
import json
import time
import traceback
import random
import functools
from utils.db import MysqlUtil
from utils.logUtil import logDebug
# from utils.proxies import Proxy_start
# from utils.proxies import get_proxy2
from utils.proxyPool import get_ip
from requests.exceptions import ConnectionError
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.packages.urllib3.exceptions import ProxyError as urllib3_ProxyError
from threading import Thread


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
                except ConnectionError as ce:
                    if (isinstance(ce.args[0], MaxRetryError) and isinstance(ce.args[0].reason, urllib3_ProxyError)):
                        # proxies = Proxy_start().get_proxy2()
                        print("IP失效了")
                        change_ip()
                    print("TryTime_except==%s"%traceback.format_exc())
                    # logDebug("tryTime","TryTime_except==%s"%traceback.format_exc())
                except Exception:
                    print("TryTime_except==%s" % traceback.format_exc())
                time.sleep(timeout)

        return __decorator
    return wrap1


def change_ip():
    proxies = get_ip()
    time.sleep(5)
    return proxies


class Kuaishou(object):

    def __init__(self):
        self.database = MysqlUtil()
        self.platform = "kuaishou"


    def get_url(self):
        sql = "select url from kuaishou_user where status=0"
        url_list = self.database.query(sql)
        # th_list = []
        proxies = get_ip()
        for url in url_list:
            self.http_parse(url=url[0], proxies=proxies)
        #     th = Thread(target=self.http_parse, args=(url[0],))
            # th.start()
            # th_list.append(th)
            # if len(th_list) > 10:
            #     for th_one in th_list:
            #         th_one.join()
            #     th_list = []


    @tryTime(3)
    def http_parse(self, url, proxies=None):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0  ; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", }
        cookie = {
            "did": "web_037faf96b0356b0aad5a7046f107df30",
            "didv": "1592206611759",
            "kuaishou.live.bfb1s": "9b8f70844293bed778aade6e0a8f9942",
            "clientid": "3",
            "client_key": "65890b29",
            "userId": "1617317305",
            "userId": "1617317305",
            "kuaishou.live.web_st": "ChRrdWFpc2hvdS5saXZlLndlYi5zdBKgAeB3htSCr-_avKu7i3kUblJE5YuBYkvTBRijpUBxc9d2ZsLMukuMZJmR_w0DomvvRxJHotBY09ohDtKNqs11CpiOu4jEWMQgjX49jhXvFlC44ievb382cnpHEvO50J0gOZzfEQJrVdPt164l-3UaeEbeGoxAhMt6BeiCOzekTgKq55goSYiOPXeKF5mP5Hu4qvyqe28vy-iLRcM6hohDMTgaEsvpGUru20c-iIt7T0W8MQrXwiIgeRy5aOLf1fYBBqOhIw0qCBM7wZcf1MZJJckpoSThnw0oBTAB",
            "kuaishou.live.web_ph": "65b6fd2ff66d8079064b42f5c586e6f57598"
        }
        if "profile" in url:
            try:
                res = requests.get(url=url, headers=headers, cookies=cookie, verify=False, proxies=proxies, timeout=10)
                time.sleep(0.5)
                error_list = ["【快手短视频App】快手，记录世界记录你", "没有作品"]
                for error in error_list:
                     if error not in res.text:
                        user_id = url.split("?")[0].split("/")[-1]
                        self.get_content(res.text, user_id)
                     else:
                        print("失败")
                        proxies = change_ip()
                        print("更换IP")
                        self.http_parse(url=url, proxies=proxies)
            except:
                logDebug(self.platform, "url:{},错误原因:{}".format(url, traceback.format_exc()))
    # def http_judge(self, result):
    #     error_list = ["【快手短视频App】快手，记录世界记录你", "没有作品"]
    #     for error in error_list:
    #         if error in result:
    #             print("失败")
    #             global proxies
    #             proxies = Proxy_start().get_proxy2()
    #             print(proxies)
    #             return True                                                                                                                                                                                                                                                  
    #     return False

    def get_content(self, content, user_id):
        try:
            res = re.findall(r"__APOLLO_STATE__=(.*?);", content)
            if res:
                res_josn = json.loads(res[0])
                # 结构最外层
                content = res_josn["clients"]["graphqlServerClient"]
                # 所有视频的ID
                video_list = content['$ROOT_QUERY.publicFeeds({"count":24,"pcursor":"","principalId":"%s"})'% user_id]["list"]
                item = {}
                for video in video_list:
                    video_id = video["id"]
                    # 视频发布时间
                    timeStamp = content[video_id]["timestamp"]
                    timeArray = time.localtime(timeStamp / 1000)
                    now_time = int(time.time())
                    if now_time - int(timeStamp / 1000) < 259200:
                        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                        item["publishTime"] = otherStyleTime
                        # 视频ID
                        item["videoId"] = content[video_id]["id"]
                        # 视频标题
                        item["title"] = content[video_id]["caption"]
                        # 用户ID
                        item["userId"] = content[video_id]["user"]["id"].split(":")[-1]
                        # 用户名
                        item["userName"] = content["User:{}".format(item["userId"])]["name"]
                        # 视频播放量
                        displayView = content["${}.counts".format(video_id)]["displayView"]
                        if "w" in displayView:
                            displayView = float(displayView.split("w")[0]) * 10000
                            item["displayView"] = int(displayView)
                        else:
                            item["displayView"] = displayView
                        # 视频点赞量
                        displayLike = content["${}.counts".format(video_id)]["displayLike"]
                        if "w" in displayLike:
                            displayLike = float(displayLike.split("w")[0]) * 10000
                            item["displayLike"] = int(displayLike)
                        else:
                            item["displayLike"] = displayLike
                        # 视频评论量
                        item["displayComment"] = content["${}.counts".format(video_id)]["displayComment"]
                        # 视频url
                        item["url"] = "https://live.kuaishou.com/u/{}/{}".format(item["userId"], item["videoId"])
                        sql = "insert into video.kuaishou(videoId, userName,userId, title,publishTime, displayView, displayLike, displayComment, url) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (item["videoId"], item["userName"], item["userId"], item["title"], item["publishTime"], item["displayView"], item["displayLike"], item["displayComment"], item["url"], )
                        update_sql = "UPDATE video.kuaishou_user SET status=1 WHERE userId='%s'" % item["userId"]
                        self.database.save_data(sql)
                        self.database.update_data(update_sql)
                        print(item)
                    else:
                        update_sql = "UPDATE video.kuaishou_user SET status=1 WHERE userId='%s'" % item["userId"]
                        self.database.update_data(update_sql)
                        print("3天以外")
            else:
                # logDebug(self.platform, "用户ID:{},内容{}".format(user_id, content))
                print(content, user_id,)
        except:
            logDebug(self.platform, "用户ID:{},错误原因:{}".format(user_id, traceback.format_exc()))


if __name__ == "__main__":
    a = Kuaishou()
    a.get_url()
