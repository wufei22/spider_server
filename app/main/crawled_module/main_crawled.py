import random
import re
import time
from app.main.public_method import *
from app.main.crawled_module import database_module, request_module, selenium_module


class MainCrawledProcess(object):
    def __init__(self):
        pass

    # 1.首先连接数据库，获取需要爬取的url
    @staticmethod
    def get_url():
        result = {"search_box_url": None, "no_search_box_url": None}
        database_conn = database.DatabaseConn()
        conn = database_conn.conn_database()
        my_cursor = conn.cursor()
        sql_sentence_having_search_box = "SELECT id, `name`, url, key_words, search_box_path, click_path, area FROM crawler_website_info WHERE search_box = 1 AND is_deleted = 1;"
        my_cursor.execute(sql_sentence_having_search_box)
        result["search_box_url"] = my_cursor.fetchall()
        my_cursor.close()
        my_cursor = conn.cursor()
        sql_sentence_no_search_box = "SELECT id, `name`, url, key_words, search_box_path, click_path, area FROM crawler_website_info WHERE search_box = 0 AND is_deleted = 1;"
        my_cursor.execute(sql_sentence_no_search_box)
        result["no_search_box_url"] = my_cursor.fetchall()
        my_cursor.close()
        conn.close()
        # print(result)
        return result

    # 2.获取网站主页，首先对搜索框的进行爬取，返回结果url
    @staticmethod
    def selenium_crawled(result):
        selenium_crawled_list = []
        selenium_result = result["search_box_url"]
        if selenium_result:
            selenium_module_process = selenium_module.SeleniumModule()
            for i in selenium_result:
                i_dic = {"id": i[0],
                         "name": i[1],
                         "url": i[2],
                         "key_words": i[3],
                         "search_box_path": i[4],
                         "click_path": i[5],
                         "area": i[6]}
                url_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
                compiled_url = re.match(pattern=url_pattern, string=i_dic["url"]).group()
                if "、" in i_dic["key_words"]:
                    search_keyword_list = i_dic["key_words"].split("、")
                else:
                    search_keyword_list = [i_dic["key_words"]]
                searched_url_list = []
                for m in search_keyword_list:
                    searched_url = selenium_module_process.search_data(input_url=compiled_url,
                                                                       search_box_path=i_dic["search_box_path"],
                                                                       click_path=i_dic["click_path"],
                                                                       keywords=m)
                    searched_url_list.append(searched_url)
                    time.sleep(random.randint(5, 10))
                selenium_crawled_list.append({"id": i[0], "searched_url_list": searched_url_list})
            selenium_module_process.quit_browser()
            return selenium_crawled_list

    # 3.爬取用关键字搜索得到的url，再进行分析
    def request_crawled(self, input_list):
        my_request_module = request_module.RequestModule()
        for i in input_list:
            website_id = i["id"]
            website_searched_url_list = i["searched_url_list"]
            for m in website_searched_url_list:
                response_html = my_request_module.main_process(url=m)
                print(response_html.content.decode())
                time.sleep(random.randint(5, 10))
        pass


if __name__ == '__main__':
    main_crawled_process = MainCrawledProcess()
    test_result = main_crawled_process.get_url()
    # test_selenium_crawled_list = main_crawled_process.selenium_crawled(result=test_result)
    # print(test_selenium_crawled_list)
    test_request_crawled_list = [{'id': 1,
          'searched_url_list':
              ['http://search.gd.gov.cn/search/mall/755018?keywords=%E6%A0%B8%E5%AE%9A%E7%94%B3%E8%AF%B7',
               'http://search.gd.gov.cn/search/mall/755018?keywords=%E7%A8%8E%E6%94%B6%E6%94%BF%E7%AD%96',
               'http://search.gd.gov.cn/search/mall/755018?keywords=%E5%88%9B%E6%96%B0']},
         {'id': 2,
          'searched_url_list':
              ['http://search.gd.gov.cn/search/mall/755529?keywords=%E7%94%B3%E6%8A%A5',
               'http://search.gd.gov.cn/search/mall/755529?keywords=%E6%89%B6%E6%8C%81']}]
    test_request_crawled = main_crawled_process.request_crawled(input_list=test_request_crawled_list)



