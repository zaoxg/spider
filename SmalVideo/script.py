import json
import sys
from utils.db import MysqlUtil
from urllib import parse
sys.path.append(r'D:\venv\pc2\Lib\site-packages')


def response(flow):
    # 提取请求的 url 地址
    url = "xiaohongshu.com/api/sns/v10/search/notes"
    if url in flow.request.url:
        url = flow.request.url
        keyword = url.split("?")[-1].split("keyword=")[-1].split("&")[0]
        keyword = parse.unquote(keyword)
        response_body = flow.response.text
        data = json.loads(response_body)
        content_list = data.get("data").get("items")
        if content_list is not None:
            for content in content_list:
                if content:
                    article_id = content.get("note").get("id")
                    sql = "insert into video.xhs_list(article_id, keyword) values ('%s','%s')" % (article_id, keyword)
                    MysqlUtil().save_data(sql)
                    print(article_id)




