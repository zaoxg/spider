import requests
import json
import re
from threading import Thread
from utils.db import MysqlUtil


class XiaoHongShu(object):

    def __init__(self):
        self.database = MysqlUtil()

    def get_url(self):
        sql = "select article_id from xhs_list where status=0 and keyword='AEMK足膜'"
        article_list = self.database.query(sql)
        print(article_list)
        th_list = []
        for article in article_list:
            th = Thread(target=self.get_detail, args=(article[0],))
            th.start()
            th_list.append(th)
            if len(th_list) > 5:
                for th_one in th_list:
                    th_one.join()
                th_list = []

    def get_detail(self, article_id):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "www.xiaohongshu.com",
            "Pragma": "no-cache",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "cookie": "rookie=yes;",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        }
        detail_url = "https://www.xiaohongshu.com/discovery/item/" + article_id
        res = requests.get(url=detail_url, timeout=10, headers=headers)

        result = re.search(r'SSR_STATE__=(.*?)</script>', res.text, flags=re.S).group(1)
        result = result.replace("undefined", "1")
        if result:
            data = json.loads(result, strict=False)
            notedata = data["NoteView"].get("content", data["NoteView"].get("noteInfo"))
            item = {}
            # 文章标题
            item["title"] = notedata.get("generatedTitle")
            # 文章发布时间
            item["publishTime"] = notedata.get("time")
            # 文章id
            item["articleId"] = notedata.get("id")
            # 文章收藏数
            item["collects"] = notedata.get("collects")
            # 文章喜欢数
            item["likes"] = notedata.get("likes")
            # 文章评论数
            item["comments"] = notedata.get("comments")
            # 文章分享数
            item["shareCount"] = notedata.get("shareCount")
            # 关键词
            keywords = notedata.get("keywords")
            item["keywords"] = ",".join(keywords)
            # 文章url
            item["url"] = detail_url
            sql = "insert into video.xiaohongshu(articleId, title,publishTime, collects,likes, comments, shareCount,keywords,url) values ( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (item["articleId"], item["title"], item["publishTime"], item["collects"], item["likes"], item["comments"], item["shareCount"], item["keywords"], item["url"])
            self.database.save_data(sql)
            print(item)


if __name__ == "__main__":
    a = XiaoHongShu()
    a.get_url()
