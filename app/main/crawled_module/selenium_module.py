import os
import time
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
        # options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        # options.add_argument('--disable-dev-shm-usage')
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
        # self.browser.set_page_load_timeout(20)

    # 关闭浏览器连接
    def quit_browser(self):
        crawled_logging = logging_module.CrawledLogging()
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
                # print(e)
                self.browser.quit()
                crawled_logging.error_log_main(message=e)

    def loading_next_html(self):
        crawled_logging = logging_module.CrawledLogging()
        try:
            current_page_source = self.browser.page_source
            # current_url = self.browser.current_url
            elem = self.query_page_element()
            if elem:
                # realxpath = elem.get_attribute("xpath")
                # print("realXPath" + realxpath)
                self.browser.execute_script("arguments[0].click();", elem)
                time.sleep(5)
                next_page_source = self.browser.page_source
                # charset = self.browser.execute_script("return document.characterSet")
                # print("current" + current_url)
                # print("next" + next_url)
                # print(text_similarity(current_page_source,next_page_source))
                if current_page_source == next_page_source:
                    # print('相同网页')
                    # return (None, False, None, None)
                    crawled_logging.debug_log_main(message="相同网页")
                else:
                    # print('有变化')
                    crawled_logging.debug_log_main(message="网页有变化")
                    # return (charset, True, next_page_source, self.browser.current_url)
                    return next_page_source
            # return (None, False, None, None)
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)

    def query_page_element(self):
        crawled_logging = logging_module.CrawledLogging()
        try:
            text = '下一页'
            xpath = f"//*[text()='{text}']"
            # elem = self.browser.find_element_by_xpath(xpath)
            elem = self.browser.find_element(By.XPATH, xpath)
            if elem:
                return elem
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)
        # 获取下一页失败 再读取一下下页
        try:
            text = '下页'
            xpath = f"//*[text()='{text}']"
            # elem = self.browser.find_element_by_xpath(xpath)
            elem = self.browser.find_element(By.XPATH, xpath)
            return elem
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)

    # 利用selenium加载栏目有分页的页面资源，并返回分页列表
    def loading_column_page_html(self, column_id, column_url):
        # 获取分页的配置
        my_paging_module = paging_module.PagingModule()
        column_page_config = my_paging_module.query_column_page_config(column_id=column_id)
        # print(column_page_config)
        html_src_list = []
        if column_page_config:
            if len(column_page_config) == 1:
                column_page_config_dict = column_page_config[0]
                # 获取需要遍历的页数
                column_page_xpath = column_page_config_dict["column_page_xpath"]
                self.browser.get(url=column_url)
                time.sleep(5)
                # 获取页面资源，并存储进列表中
                html_src_list.append(self.browser.page_source)
                click_element = self.browser.find_element(By.XPATH, column_page_xpath)
                click_element.click()
                time.sleep(5)
                html_src_list.append(self.browser.page_source)
                self.quit_browser()
                return html_src_list
            else:
                column_page_config_dict1 = column_page_config[0]
                column_page_config_dict2 = column_page_config[1]
                # 获取需要遍历的页数
                page_size = column_page_config_dict1["column_default_page"]
                column_page_xpath1 = column_page_config_dict1["column_page_xpath"]
                column_page_xpath2 = column_page_config_dict2["column_page_xpath"]
                html_src_list.append(self.browser.get(url=column_url))
                time.sleep(5)
                click_element = self.browser.find_element(By.XPATH, column_page_xpath1)
                click_element.click()
                time.sleep(5)
                # 获取页面资源，并存储进列表中
                while page_size > 1:
                    current_page_source = self.browser.page_source
                    html_src_list.append(current_page_source)
                    click_element = self.browser.find_element(By.XPATH, column_page_xpath2)
                    click_element.click()
                    time.sleep(5)
                    page_size -= 1
                self.quit_browser()
                return html_src_list
        else:
            self.browser.get(url=column_url)
            time.sleep(5)
            current_page_source = self.browser.page_source
            html_src_list.append(current_page_source)
            count_page = 5
            while count_page > 0:
                next_html = self.loading_next_html()
                if next_html:
                    html_src_list.append(next_html)
                count_page -= 1
                # print(count_page)
            self.quit_browser()
            return html_src_list

    # 利用selenium加载文章有分页的页面资源，并返回分页列表
    def loading_article_page_html(self, article_id, article_url):
        # 获取分页的配置
        my_paging_module = paging_module.PagingModule()
        article_page_config = my_paging_module.query_article_page_config(article_id=article_id)
        html_src_list = []
        if article_page_config:
            if len(article_page_config) == 1:
                article_page_config_dict = article_page_config[0]
                # 获取需要遍历的页数
                article_page_xpath = article_page_config_dict["article_page_xpath"]
                self.browser.get(url=article_url)
                time.sleep(5)
                # 获取页面资源，并存储进列表中
                html_src_list.append(self.browser.page_source)
                click_element = self.browser.find_element(By.XPATH, article_page_xpath)
                click_element.click()
                time.sleep(5)
                html_src_list.append(self.browser.page_source)
                self.quit_browser()
                return html_src_list
            else:
                article_page_config_dict1 = article_page_config[0]
                article_page_config_dict2 = article_page_config[1]
                # 获取需要遍历的页数
                page_size = article_page_config_dict1["article_default_page"]
                article_page_xpath1 = article_page_config_dict1["article_page_xpath"]
                article_page_xpath2 = article_page_config_dict2["article_page_xpath"]
                html_src_list.append(self.browser.get(url=article_url))
                time.sleep(5)
                click_element = self.browser.find_element(By.XPATH, article_page_xpath1)
                click_element.click()
                time.sleep(5)
                # 获取页面资源，并存储进列表中
                while page_size > 1:
                    current_page_source = self.browser.page_source
                    html_src_list.append(current_page_source)
                    click_element = self.browser.find_element(By.XPATH, article_page_xpath2)
                    click_element.click()
                    time.sleep(5)
                    page_size -= 1
                self.quit_browser()
                return html_src_list
        else:
            self.browser.get(url=article_url)
            time.sleep(5)
            current_page_source = self.browser.page_source
            html_src_list.append(current_page_source)
            self.quit_browser()
            return html_src_list

    # 利用selenium加载数据，返回加载的页面数据
    def loading_html(self, input_url):
        crawled_logging = logging_module.CrawledLogging()
        try:
            # 打开网页,返回页面资源数据
            self.browser.get(url=input_url)
            time.sleep(5)
            if "404" not in self.browser.title:
                current_page_source = self.browser.page_source
                self.quit_browser()
                return current_page_source
            else:
                self.quit_browser()
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)
            self.browser.execute_script('window.stop()')
            self.quit_browser()

    # 检测xpath配置是否正确
    def check_xpath(self, input_url, xpath):
        if self.browser.get(url=input_url):
            time.sleep(5)
            current_page = self.browser.page_source
            if self.browser.find_element(By.XPATH, xpath):
                click_element = self.browser.find_element(By.XPATH, xpath)
                click_element.click()
                time.sleep(5)
                next_page = self.browser.page_source
                if next_page != current_page:
                    return True


if __name__ == '__main__':
    test_selenium_module = SeleniumModule()
    # test_html = test_selenium_module.loading_html(input_url="http://stic.sz.gov.cn")
    test_html = test_selenium_module.loading_column_page_html(column_id=5, column_url="http://fgw.sz.gov.cn/gkmlpt/")
