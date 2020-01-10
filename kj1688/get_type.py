import requests
from fake_useragent import UserAgent
import urllib3
import re
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ua = UserAgent()


head = {
    "Host": "dcms.1688.com",
    "User-Agent": ua.random,
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://kj.1688.com/kitchen_dining.html?spm=a262gg.8864560.jifovpy5.262.164b6510LrcJd5",
    "TE": "Trailers",
}


def type_list(c_api):
    r = requests.get(c_api, headers=head).text
    data = json.loads(re.findall(r'^\w+\((.*)\)$', r)[0])
    # print(data)
    # print(data['content']['data'][0])
    # print(type(data['content']['data'][0]['versionContent']))
    s = json.loads(data['content']['data'][0]['versionContent'])
    # 定义一个品类映射list
    all_list = []
    for i in s['list']:
        big_type = {}
        # 大类
        big_type[i['resourceId']] = i['title']
        small_type = {}
        for s in i['secondList']:
            small_type[s['resourceId']] = s['title']
        big_type['second'] = small_type
        # print(big_cl)
        all_list.append(big_type)
    return all_list


# u = 'https://dcms.1688.com/open/query.json?app=DCMS&dataId=236&to=3000&n=30&fields=versionContent,errorMsgs,crocoServerTime&sk0=89fa29b8baf0fd1056a946fffde4b1c8&resourceId=589695&useCookieMemberId=&rtnMode=1&callback=jsonp_uw8iggjw9ou61si'
# for z in type_list(u):
#     print(z)
