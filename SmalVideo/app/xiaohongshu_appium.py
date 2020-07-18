import time
import random
from appium import webdriver
from appium.webdriver.webdriver import WebDriver


# appium服务监听地址
server='http://localhost:4723/wd/hub'
# app启动参数
desired_caps = {
  "platformName": "Android",   # 声明是ios还是Android系统
  "platformVersion": "6.0",   # Android内核版本号，可以在夜神模拟器设置中查看
  "deviceName": "Huawei ELE-AL00",  # 这个地方我们可以写 127.0.0.1:62001
  "appPackage": "com.xingin.xhs",  # apk的包名
  "appActivity": "activity.SplashActivity",  # apk的launcherActivity
  "noReset": True,
}


class XiaoHongShu(object):

    def __init__(self):
        self.driver = webdriver.Remote(server, desired_capabilities=desired_caps)

    def get_text(self, key_word):
        time.sleep(3)
        search_box = self.driver.find_element_by_id("com.xingin.xhs:id/bd9")  # 点击搜索框，打开搜索页
        search_box.click()
        time.sleep(3)
        box = self.driver.find_element_by_id('com.xingin.xhs:id/beg')
        time.sleep(3)
        box.send_keys(key_word)
        search_button = self.driver.find_element_by_id("com.xingin.xhs:id/bej")  # 点击搜索
        search_button.click()
        time.sleep(10)
        while True:
            self.swipe_up()
            time.sleep(random.random())

    def get_size(self,):
        """
        获取屏幕大小
        :param driver:
        :return:
        """
        driver = self.driver or self.driver
        if not driver:
            return driver

        x = driver.get_window_size()['width']
        y = driver.get_window_size()['height']
        return [x, y]

    def swipe_up(self, _time: int = 1000):
        """
        向上滑动
        :param driver:
        :param _time:
        :return:
        """
        try:
            size = self.get_size()
            print(size)
            x1 = int(size[0] * 0.5)  # 起始x坐标
            y1 = int(size[1] * 0.80)  # 起始y坐标
            y2 = int(size[1] * 0.30)  # 终点y坐标
            self.driver.swipe(x1, y1, x1, y2, _time)
            return True
        except:
            return False


if __name__ == "__main__":
  a = XiaoHongShu()
  a.get_text("AEMK足膜")
