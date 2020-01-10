import requests
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
from DBUtils.PersistentDB import PersistentDB, PersistentDBError, NotSupportedError


b_api = 'https://xiapi.xiapibuy.com/api/v2/fe_category/get_list'
s_api = 'https://xiapi.xiapibuy.com/api/v0/search/api/facet/?fe_categoryids={}&page_type=search'


config = {
    'host': '47.97.166.98',
    'port': 3306,
    'database': 'Shop',
    'user': 'root',
    'password': '100798',
    'charset': 'utf8mb4'
}


def get_db_pool(is_mult_thread):
    if is_mult_thread:
        poolDB = PooledDB(
            # 指定数据库连接驱动
            creator=pymysql,
            # 连接池允许的最大连接数,0和None表示没有限制
            maxconnections=0,
            # 初始化时,连接池至少创建的空闲连接,0表示不创建
            mincached=2,
            # 连接池中空闲的最多连接数,0和None表示没有限制
            maxcached=5,
            # 连接池中最多共享的连接数量,0和None表示全部共享(其实没什么卵用)
            maxshared=3,
            # 连接池中如果没有可用共享连接后,是否阻塞等待,True表示等等,
            # False表示不等待然后报错
            blocking=True,
            # 开始会话前执行的命令列表
            setsession=[],
            # ping Mysql服务器检查服务是否可用
            ping=0,
            **config
        )
    else:
        poolDB = PersistentDB(
            # 指定数据库连接驱动
            creator=pymysql,
            # 一个连接最大复用次数,0或者None表示没有限制,默认为0
            maxusage=1000,
            **config
        )
    return poolDB


# 获取大类id及名称
def b_type():
    # 请求大类的api获得大类别的id和name
    print('开始获取类别...')
    res = requests.get(b_api).json()
    # print(res)
    tp_list = []
    for tp in res['data']['category_list']:
        b_tp = {}
        # 大类
        b_tp[str(tp['catid'])] = tp['display_name']
        s_tp = {}
        # 通过大类别的id获取小类别的api
        s = requests.get(s_api.format(tp['catid'])).json()
        # print(s)
        for i in s['facets']:
            # print(i['category']['display_name'], i['category']['catid'])
            s_tp[str(i['category']['catid'])] = i['category']['display_name']
        b_tp['cate'] = s_tp
        tp_list.append(b_tp)
    print('类别映射为:', tp_list)
    return tp_list


def e_tag():
    # 请求大类的api获得大类别的id和name
    print('开始获取类别...')
    res = requests.get(b_api).json()
    # print(res)
    tp_list = []
    for tp in res['data']['category_list']:
        b_tp = {}
        # 大类
        b_tp[str(tp['catid'])] = tp['display_name']
        b_tp['eTag'] = 'None'
        tp_list.append(b_tp)
    print('类别映射为:', tp_list)
    return tp_list


e_tag()
