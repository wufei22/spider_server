import os
import random
import time

from selenium import webdriver
from app.main.public_method import *
from selenium.webdriver.common.by import By


class SeleniumModule(object):

    # 1.初始化设置代理ip,伪装请求头，隐藏浏览器指纹特征
    def __init__(self):
        options = webdriver.ChromeOptions()
        # 1.获取代理ip
        # building_ip_pool = IP_pool.BuildingIPPool()
        # ip_dic = building_ip_pool.main_process()
        # ip = ip_dic["proxy_list"][0]
        # https_ip = "https://" + ip
        # # 2.添加代理ip
        # options.add_argument('--proxy-server=%s' % https_ip)
        # 3.伪装请求头user-agent
        get_user_agent = random_user_agent.RandomUserAgent()
        user_agent = get_user_agent.main_process()
        options.add_argument('--user-agent=' + user_agent)
        self.browser = webdriver.Chrome(chrome_options=options)
        # 4.隐藏浏览器的指纹特征
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\..\.."))
        javascript_path = os.path.join(local_path, "stealth.min.js")
        with open(javascript_path, "r") as f:
            js = f.read()
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

    # 2.获取网页，并搜索相关的内容,返回搜索结果的页面
    def search_data(self, input_url, search_box_path, click_path, keywords):
        # 1.打开网页
        self.browser.get(url=input_url)
        self.browser.implicitly_wait(random.randint(5, 10))
        # 2.输入搜索关键词并搜索
        try:
            search_box = self.browser.find_element(by=By.XPATH, value=search_box_path)
            # if not search_box:
            #     raise ValueError("页面根据给定的路径找不到搜索框")
            search_box.send_keys(keywords)
            click_button = self.browser.find_element(by=By.XPATH, value=click_path)
            # if not click_button:
            #     raise ValueError("页面根据给定的路径找不到搜索点击按钮")
            click_button.click()
            # 3.等待搜索结果加载完成
            time.sleep(random.randint(5, 10))
            self.browser.implicitly_wait(random.randint(5, 10))
            self.browser.switch_to.window(self.browser.window_handles[-1])
            # print(self.browser.current_url)
            current_url = self.browser.current_url
            # self.browser.quit()
            return current_url
        except Exception as e:
            print(e)
            raise ValueError("页面根据给定的路径找不到搜索框或者是点击按钮，请确认路径是否正确")

    # 3.关闭浏览器连接
    def quit_browser(self):
        self.browser.quit()


if __name__ == '__main__':
    selenium_module = SeleniumModule()
    selenium_module.search_data(input_url="http://fgw.sz.gov.cn/",
                                search_box_path="//form/input[@id='textfield_pc']",
                                click_path="//form/div[@id='submitbuttom_pc']",
                                keywords="补贴")
