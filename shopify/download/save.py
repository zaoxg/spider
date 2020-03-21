import os
import requests

"""
保存工具
"""
session = requests.Session()


# 商品属性保存
def save_txt(goodsName, gType, data, siteName):
    # 保存路径
    savePath = './data\\' + siteName + '\\' + goodsName
    if not os.path.exists(savePath):
        os.makedirs(savePath)
        print("{} >> 创建成功".format(savePath))
    with open(savePath + '\\' + gType + '.txt', 'w', encoding='utf-8')as f:
        f.writelines(data)
        f.close()
    print("{0} | {1}>>保存成功".format(goodsName, gType))


# 商品图片保存
def save_file(goodsName, picLink, picName, siteName):
    # 保存路径
    savePath = './data\\' + siteName + '\\' + goodsName + '\\Picture\\'
    if not os.path.exists(savePath):
        os.makedirs(savePath)
        print("{} >> 创建成功".format(savePath))
    with open(savePath + str(picName) + '.jpg', 'wb')as f:
        data = session.get('http:' + picLink)
        f.write(data.content)
        f.close()
    print(f"{goodsName} | {picName} >> {data.status_code}")
