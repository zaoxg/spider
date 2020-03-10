import re
import json
import requests
import demjson
import csv
from fake_useragent import UserAgent


ET_session = requests.Session()
ua = UserAgent()

head = {
    "Host": "www.etmall.com.tw",
    "User-Agent": ua.random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def get_type_list():
    with ET_session.get(
        url="https://www.etmall.com.tw/",
        headers=head
    ) as response:
        # recatDOM渲染，使用正则匹配
        type_data = re.findall(r'Components.DropMenu([\s\S]*?)document.getElementById\("dropMenu"\)\)', response.text)
        if not type_data:
            raise Exception("extract json error")
        t_data = type_data[0].strip().strip(',').strip(')')
        type_json_data = demjson.decode(t_data)
        # print(json_data)
        # 第一条是品牌
        for cate_data in type_json_data['CategoriesTree'][10:]:
            for s in cate_data['SubCategories']:
                # 大类别
                b_cate = s['Category']['CateName']
                for ss in s['SubCategories']:
                    s_cid = ss['Category']['CateID']
                    s_cate = ss['Category']['CateName']
                    s_url = 'https://www.etmall.com.tw' + ss['Category']['DefaultUrl']
                    # print(b_cate, s_cid, s_cate, s_url)
                    msg_data = json.dumps({"bCate": b_cate, "sCid": s_cid, "sCate": s_cate, "sUrl": s_url})
                    # print(msg_data)
                    get_goods(msg_data)


def get_goods(msg):
    json_msg = json.loads(msg)
    print(json_msg)
    head['Referer'] = 'https://www.etmall.com.tw/'
    with ET_session.get(
        url=json_msg['sUrl'],
        headers=head
    ) as response:
        try:
            goods_data = re.findall(r'Components.MList([\s\S]*?)document.getElementById\("MListContainer"\)\)', response.text)
            if not goods_data:
                raise Exception("goods json error")
        except:
            goods_data = re.findall(r'Components.SList([\s\S]*?)document.getElementById\("SLiatContainer"\)\)', response.text)
        # 删除掉空格，符号以及)
        g_data = goods_data[0].strip().strip(',').strip(')')
        goods_json_data = demjson.decode(g_data)
        num = goods_json_data['model']['ProductList']['totalProducts']  # 商品数量，后面会用到
        for goods in goods_json_data['model']['ProductList']['products']:
            pid = goods['id']  # 商品id
            title = goods['title']  # 商品名称
            price = goods['finalPrice']  # 折后价格
            link = 'https://www.etmall.com.tw' + goods['pageLink']
            goods_info = [pid, title, price, json_msg['bCate'], json_msg['sCate'], link, json_msg['sCid'], json_msg['sUrl']]
            strong(goods_info)
        # 从这里开始进行2+页的请求
        for p in range(1, num//40+1):
            with ET_session.get(
                url=json_msg['sUrl'],
                headers=head,
                    params={
                        "page": num
                    }
            ) as response:
                try:
                    goods_data = re.findall(r'Components.MList([\s\S]*?)document.getElementById\("MListContainer"\)\)',
                                            response.text)
                    if not goods_data:
                        raise Exception("goods json error")
                except:
                    goods_data = re.findall(r'Components.SList([\s\S]*?)document.getElementById\("SLiatContainer"\)\)',
                                            response.text)
                g_data = goods_data[0].strip().strip(',').strip(')')
                goods_json_data = demjson.decode(g_data)
                num = goods_json_data['model']['ProductList']['totalProducts']  # 商品数量
                for goods in goods_json_data['model']['ProductList']['products']:
                    pid = goods['id']  # 商品id
                    title = goods['title']  # 商品名称
                    price = goods['finalPrice']  # 折后价格
                    link = 'https://www.etmall.com.tw' + goods['pageLink']
                    goods_info = [pid, title, price, json_msg['bCate'], json_msg['sCate'], link, json_msg['sCid'], json_msg['sUrl']]
                    strong(goods_info)


# 商品id，标题，价格，大类别，小类别，链接，小类id，小类url
def strong(g_info):
    print(g_info)
    # newline的作用是防止每次插入都有空行
    with open('ETMall_2.csv', 'a+', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # 以读的方式打开csv 用csv.reader方式判断是否存在标题
        with open('ETMall_2.csv', 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            if not [row for row in reader]:
                writer.writerow(
                    ['商品id', '商品名称', '价格', '商品大类', '商品小类', '链接', '小类id', '小类url'])
                writer.writerow(g_info)
            else:
                writer.writerow(g_info)


if __name__ == '__main__':
    get_type_list()
