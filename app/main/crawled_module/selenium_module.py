import os
import random
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from app.main.public_method import *
from app.main.crawled_module import paging_module


class SeleniumModule(object):

    # 初始化设置代理ip,伪装请求头，隐藏浏览器指纹特征
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
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(chrome_options=options)
        # 4.隐藏浏览器的指纹特征
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        local_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
        javascript_path = os.path.join(local_path, "stealth.min.js")
        with open(javascript_path, "r") as f:
            js = f.read()
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

    # 利用selenium加载栏目有分页的页面资源，并返回分页列表
    def loading_column_page_html(self, column_id, column_url):
        # 获取分页的配置
        my_paging_module = paging_module.PagingModule()
        column_page_config_dict = my_paging_module.query_column_page_config(column_id=column_id)
        html_src_list = []
        if column_page_config_dict:
            # 获取需要遍历的页数
            page_size = column_page_config_dict["column_default_page"]
            column_page_xpath = column_page_config_dict["column_page_xpath"]
            self.browser.get(url=column_url)
            time.sleep(5)
            # 获取页面资源，并存储进列表中
            while page_size > 0:
                current_page_source = self.browser.page_source
                html_src_list.append(current_page_source)
                click_element = self.browser.find_element(By.XPATH, column_page_xpath)
                click_element.click()
                time.sleep(5)
                page_size -= 1
            return html_src_list
        else:
            self.browser.get(url=column_url)
            time.sleep(5)
            current_page_source = self.browser.page_source
            html_src_list.append(current_page_source)
            return html_src_list

    # 利用selenium加载文章有分页的页面资源，并返回分页列表
    def loading_article_page_html(self, article_id, article_url):
        # 获取分页的配置
        my_paging_module = paging_module.PagingModule()
        article_page_config_dict = my_paging_module.query_article_page_config(article_id=article_id)
        html_src_list = []
        if article_page_config_dict:
            # 获取需要遍历的页数
            page_size = article_page_config_dict["article_max_page"]
            article_page_xpath = article_page_config_dict["article_page_xpath"]
            self.browser.get(url=article_url)
            time.sleep(5)
            # 获取页面资源，并存储进列表中
            while page_size > 0:
                current_page_source = self.browser.page_source
                html_src_list.append(current_page_source)
                click_element = self.browser.find_element(By.XPATH, article_page_xpath)
                click_element.click()
                time.sleep(5)
                page_size -= 1
            return html_src_list
        else:
            self.browser.get(url=article_url)
            time.sleep(5)
            current_page_source = self.browser.page_source
            html_src_list.append(current_page_source)
            return html_src_list

    # 利用selenium加载数据，返回加载的页面数据
    def loading_html(self, input_url):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            # 打开网页,返回页面资源数据
            self.browser.get(url=input_url)
            time.sleep(5)
            current_page_source = self.browser.page_source
            return current_page_source
        except Exception as e:
            crawled_logger.error(msg=e)
            logging.shutdown()

    # 检测xpath配置是否正确
    def check_xpath(self, input_url, xpath):
        if self.browser.get(url=input_url):
            time.sleep(random.randint(15, 20))
            current_page = self.browser.page_source
            if self.browser.find_element(By.XPATH, xpath):
                click_element = self.browser.find_element(By.XPATH, xpath)
                click_element.click()
                time.sleep(random.randint(15, 20))
                next_page = self.browser.page_source
                if next_page != current_page:
                    return True

    # 关闭浏览器连接
    def quit_browser(self):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        if self.browser:
            try:
                # 获取所有handles
                my_handles = self.browser.window_handles
                if my_handles:
                    for i in reversed(range(len(my_handles))):
                        self.browser.switch_to.window(my_handles[i])
                        self.browser.close()
                        time.sleep(1)
                    self.browser.quit()
                else:
                    self.browser.close()
                    self.browser.quit()
            except Exception as e:
                self.browser.quit()
                crawled_logger.error(msg=e)
        logging.shutdown()


if __name__ == '__main__':
    selenium_module = SeleniumModule()
    # test_url = selenium_module.search_data(input_url="http://stic.sz.gov.cn/",
    #                                        search_box_path='//*[@id="keywords"]',
    #                                        click_path='//*[@id="searchForm"]/div/a',
    #                                        keywords='补贴',
    #                                        sort_by_time=1,
    #                                        sort_by_time_path='//*[@id="sort-way"]/a[2]')
    test_html = selenium_module.loading_html(input_url="http://cdhrss.chengdu.gov.cn")
    print(test_html)
    # if "article" in test_html or "Article" in test_html:
    #     print(123456451)
    selenium_module.quit_browser()
