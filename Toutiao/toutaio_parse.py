import requests
import socket
import time
import datetime
from lxml import etree
import logging
from fake_useragent import UserAgent
ua = UserAgent()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')
path = 'D:/localFile/'
host = '27.43.186.62'
port = '9999'
proxy = {'http': f'https://{host}:{port}'}


def get_host_ip():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_detail(aid):
    head = {
        'User-Agent': ua.random
    }
    response = requests.get(url=f'https://m.toutiao.com/i{aid}/info/v2/', headers=head, proxies=proxy)
    if response.status_code == 200:
        return response.json()


def detail_parse(aid):
    detail = get_detail(str(aid))
    # print(detail)
    try:
        if isinstance(detail['data'], dict):
            title = detail['data']['title']  # 标题
            source = detail['data']['source']  # 作者
            publish = detail['data']['publish_time']  # 发布时间
            pub_time = time.strftime("%Y%m%d%H%M%S", time.localtime(int(publish)))
            pl_num = detail['data']['comment_count']
            zn_num = detail['data']['digg_count']
            zf_num = detail['data']['repost_count']
            content = detail['data']['content']  # 可能为空
            text, img_s = None, None
            if content:
                content_html = etree.HTML(content)
                all_con = content_html.xpath('//text()')
                text = ''.join(all_con)
                img_xp = content_html.xpath('//img/@src')
                img_s = ';'.join(img_xp)
            result = f"<REC>\n<pageType>=新闻\n<title>={title}\n<poster>={source}\n<content>={text}\n<publishTime>={pub_time}\n" \
                     f"<siteName>=今日头条\n<pageUrl>=https://www.toutiao.com/a{aid}\n<dataPusher>=本地\n" \
                     f"<isTopic>=1\n<pls>={pl_num}\n<dzs>={zn_num}\n<zfs>={zf_num}\n<visitNum>=0\n<mainImgUrl>={img_s}\n"
            save(result)
        else:
            logging.warning(detail)
    except TypeError as type_error:
        logging.error(type_error)


def save(result):
    bd_ip = get_host_ip().split('.')
    file_name = f'sjcj_yqz_toutiao_{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}_{bd_ip[2]}_{bd_ip[3]}'
    try:
        with open(f'{path}{file_name}', mode='a', encoding='utf-8') as lf:
            lf.write(result)
            lf.close()
    except Exception as e:
        logging.error(e)
    logging.info(f'{path}{file_name}')
