import requests
from fake_useragent import UserAgent
import urllib3
import datetime
import re
import csv
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

s = requests.session()
ua = UserAgent()

api = 'https://sosu.buy123.com.tw/api/item_api/get_items_by_category/{0}/{1}/0/3000'
ref = 'https://www.buy123.com.tw/site/category/12/%E5%B1%85%E5%AE%B6%E7%94%9F%E6%B4%BB%E9%9B%9C%E8%B2%A8'
c = 'cfduid=dd2e94b17ba1df6735d3ca4d678592fde1576819538; cf_clearance=81a8beae23aeff281795633e513465c768fcd36e-1576825460-0-250; __auc=70280b8916f21c286c326abec19; _gcl_au=1.1.2051219186.1576819394; _ga=GA1.3.1934821855.1576819400; _gid=GA1.3.1162146887.1576819400; cto_lwid=16639413-ee6a-477c-b73a-4d66d16e6633; device_hash=5dfc5b59ae97af3cec39f4df; cto_bundle=2Z7Wyl8wV0pDY0IlMkJMWUpVMyUyQjNuREdaWWJHWlUxSTB0RHUxNVVHblMzVjZVUVJ6YVpVdU9PUElHMEo1OURuRnVwU2RXQ09WWWR0NWpuNVZsbWxzYTZqRFh1STdRNTRacEhPJTJGVHNzb2RiJTJGTWFJWE0wSXphRnRjd3hJd2JvRTNHczVGRVZGN3NNRnlSZ1AyU1p6N0cxNHFoTjZmQSUzRCUzRA; _fbp=fb.2.1576824248744.1286443359; mp_0b491a9aa9ed2234245a1e42339f66e5_mixpanel=%7B%22distinct_id%22%3A%20%2216f21c2edb22fb-0f6f752aaeda7c-4c302a7b-1fa400-16f21c2edb3452%22%2C%22%24device_id%22%3A%20%2216f21c2edb22fb-0f6f752aaeda7c-4c302a7b-1fa400-16f21c2edb3452%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.buy123.com.tw%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.buy123.com.tw%22%7D'

head = {
    'Host': 'sosu.buy123.com.tw',
    'User-Agent': ua.random,
    'Origin': 'https://www.buy123.com.tw',
    'Connection': 'keep-alive',
    'Referer': ref,
    # 'Cookie': c,
    'TE': 'Trailers'
}
p = {'https': '114.33.189.29:34275'}

home = 'https://www.buy123.com.tw/'

big_class = {
    '12': '居家生活雜貨',
    '25': '收納用品',
    '5': '家事清潔',
    '66': '餐廚用品',
    '485': '日用/護理/彩妝',
    '74': '雨具',
    '87': '寢具',
    '51': '傢俱',
    '1': '3C/車用周邊',
    '19': '家電/影音設備',
    '103': '食品',
    '120': '服飾配件',
    '76': '婦幼/親子',
    '39': '運動紓壓/旅遊'
}


# 返回一个小类别的映射
def small_class():
    load = './small.json'
    with open(load, 'r', encoding='utf8')as f:
        small_cl = json.load(f)
        f.close()
        return small_cl


# 构造请求api的日期时间
def d_ti():
    now = datetime.datetime.now()
    d = re.findall(r'\d+', str(now))
    ti = d[0] + d[1] + d[2] + d[3]
    return ti


# 获取大类别的映射
def get_big():
    # 大类映射
    big_class = {}
    # 获取类别
    link_all = s.get(home).text
    cl_li = re.findall(r'<li id="\d+" class="">(.*?)</li>', link_all)
    # print(cl_li)
    for x in cl_li:
        # print(x)
        y = re.findall(r'<a href="/site/category/(\d+)/(.*?)">(.*?)<span class="text">(.*?)</span>(.*?)</a>', x)
        # print(y[0][0], y[0][3])
        big_class[y[0][0]] = y[0][3]
    print(big_class)


# 获取小类别的映射
def get_small():
    eji = 'https://www.buy123.com.tw/site/category/12/%E5%B1%85%E5%AE%B6%E7%94%9F%E6%B4%BB%E9%9B%9C%E8%B2%A8#?ref=d_category_maincategory_12'
    # 获取类别
    eji_all = s.get(eji).text
    ejs = re.findall(r'<script>window.__PRELOADED_STATE__ = (.*?)</script>', eji_all)
    print(ejs)


def get():
    small = small_class()
    # 拼接大类别
    for k in big_class.keys():
        response = s.get(api.format(k, d_ti()), headers=head, verify=False).json()
        # print(response)
        for item in response['items']:
            id = item['id']  # *
            name = item['name']  # 名称/标题 *
            full_name = item['full_name']  # 全名
            dealid = item['dealid']
            desc_short = item['desc_short']  # 描述 *
            original_price = item['original_price']  # 原价
            contractid = item['contractid']  # 拼接cid
            square_img = 'https://images.buy123.com.tw/thumb/{0}'.format(item['square_img'])  # 封面图，https://images.buy123.com.tw/thumb/{}
            price = item['price']  # 特价
            new_display_user_rating = item['new_display_user_rating']  # 评分
            display_rate_count = item['display_rate_count']  # 评分数
            grade = item['grade']  # 品级
            categoryid = item['categoryid']  # 类别id
            skuid = item['skuid']  # 商品id，https://www.buy123.com.tw/site/sku/{skuid}/{name}?cid={contractid}#?ref=d_category_product_0
            google_category_id = item['google_category_id']  # google的类别id？
            isstar = item['is_star']  # 是否为明星商品
            count = item['count']  # 已抢购件数
            display_price = item['coupon']['click_discount']['display_price']  # 当前价格
            category_frontend_root = big_class[item['category_frontend_root']]  # 商品大类
            category_frontend_id = small[item['category_frontend_id']]  # 商品小类
            spt = 'https://images.buy123.com.tw/thumb/{0}'.format(item['square_img'])  # 商品图
            spl = 'https://www.buy123.com.tw/site/sku/{0}/{1}?cid={2}#?ref=d_category_product_0'.format(skuid, name, contractid)  # 商品链接
            # id， skuid(拼接用)，商品名称，描述，品级，是否明星商品，评分，评分数，已抢购件数，当前价格，大类，小类，封面图， 商品链接
            info_l = [id, skuid, name, desc_short, grade, isstar, new_display_user_rating, display_rate_count, count, display_price, category_frontend_root, category_frontend_id, spt, spl]
            write_csv(info_l)
            print(info_l)


def write_csv(info_l):
    # newline的作用是防止每次插入都有空行
    with open('data/' + '生活市集' + '.csv', 'a+', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 以读的方式打开csv 用csv.reader方式判断是否存在标题
        with open('data/' + '生活市集' + '.csv', 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            if not [row for row in reader]:
                writer.writerow(['id', 'skuid(拼接用)', '商品名称', '描述', '品级', '是否明星商品', '评分', '评分数', '已抢购件数', '当前价格', '大类', '小类', '封面图', '商品链接'])
                writer.writerow(info_l)
            else:
                writer.writerow(info_l)


if __name__ == '__main__':
    get()
    pass
