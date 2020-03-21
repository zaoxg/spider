import os
import requests


class SaveFile(object):
    def __init__(self, path):
        self.path = r'./data/{}/'.format(path)

    def save_txt(self, folder, file, data):
        # 保存路径
        path = self.path + folder + '/'
        if not os.path.exists(path):
            os.makedirs(path)
            print("{} >> 创建成功".format(path))
        with open(path + f'{file}.txt', 'w', encoding='utf-8') as txt:
            txt.writelines(data)
            txt.close()
        print(f"{path} | {file}.txt >> 保存成功")

    def save_picture(self, folder, file, source):
        path = self.path + folder + '/'
        if not os.path.exists(path):
            os.makedirs(path)
            print("{} >> 创建成功".format(path))
        with open(path + f'{file}.jpg', 'wb') as picture:
            data = requests.get(source)
            picture.write(data.content)
            picture.close()
        print(f"{path} | {file}.jpg >> {data.status_code}")

    def save_video(self, folder, file, source):
        path = self.path + folder + '/'
        if not os.path.exists(path):
            os.makedirs(path)
            print("{} >> 创建成功".format(path))
        with open(path + f'{file}.mp4', 'wb') as video:
            data = requests.get(source)
            video.write(data.content)
            video.flush()
        print(f"{path} | {file}.mp4 >> {data.status_code}")
