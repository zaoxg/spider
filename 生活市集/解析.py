import json


def read_city():
    # 读取外部城市及商圈文件
    load = './小类.json'
    small_class = {}
    with open(load, 'r', encoding='utf8')as f:
        file = json.load(f)
        # print(file)
        for data in file['entities']['category']:
            # print(data)
            for small in data['category']:
                small_class[small['id']] = small['name']
    print(small_class)


def read():
    # 读取外部城市及商圈文件
    load = './小类.json'
    small_class = {}
    small_list = {}
    with open(load, 'r', encoding='utf8')as f:
        file = json.load(f)
        # print(file)
        for data in file['entities']['category']:
            print(data)
            # for small in data['category']:
            #     small_class[small['id']] = small['name']
            small_class[[data['id']]] = data['name']
            for small in data['category']:
                small_list[small['id']] = small['name']
            print(small_list)
            small_class['small'] = small_list
    print(small_class)


def r():
    load = './small.json'
    small_class = {}
    with open(load, 'r', encoding='utf8')as f:
        file = json.load(f)
        # file = f.read()
        # fs = file.replace("'", "\"")
        # print(fs)
        f.close()
        print(file['740'])


r()
