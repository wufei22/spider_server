# coding=utf-8
import time

import bs4
import datetime
from multiprocessing import Pool
from app.main.crawled_module import database_module, request_module, selenium_module, attach_handle_module, \
    loading_img_module, paging_module, article_analyze_module, optical_character_recognition_module, \
    crawled_logging_module
from app.main.redis_module import *


class MainCrawledProcess(object):

    # 连接数据库，获取需要爬取的url
    @staticmethod
    def get_url(input_id):
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT id, `name`, url FROM crawled_website_info WHERE id = {id};".format(id=input_id)
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        if my_data:
            website_info = {"id": my_data[0][0],
                            "name": my_data[0][1],
                            "url": my_data[0][2]}
            return website_info

    # 主网站采集一级栏目的方法
    @staticmethod
    def grading_first_column(input_info):
        """
        采集主网站的一级栏目，并将采集结果存入数据库
        :param input_info:主网站的信息，结构类似{"id": web_id, "name": web_name, "url": web_url}
        :return: True/False
        """
        # 1. 识别当前网站的反爬虫协议
        print(input_info)
        my_request_module = request_module.RequestModule()
        if my_request_module.main_process(url=input_info["url"]):
            # 2. 获取所有a标签列表
            my_selenium_module = selenium_module.SeleniumModule()
            response_html = my_selenium_module.loading_html(input_url=input_info["url"])
            time.sleep(10)
            my_selenium_module.quit_browser()
            if response_html:
                my_soup = bs4.BeautifulSoup(response_html, features="lxml")
                a_list = my_soup.find_all("a")
                # 3. 加载图片信息
                my_loading_img_module = loading_img_module.LoadingImg(website=input_info["url"],
                                                                      website_id=input_info["id"],
                                                                      a_list=a_list)
                img_info_list = my_loading_img_module.loading_img_main()
                # 4. 通过OCR识别图片的信息
                for i in img_info_list:
                    my_optical_character_recognition_module = optical_character_recognition_module.OpticalCharacterRecognitionModule()
                    i["column_name"] = my_optical_character_recognition_module.recognize_character_main(
                        img_path=i["img_path"], img_type=i["img_type"])
                # 5. 过滤a标签
                my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                            website_id=input_info["id"])
                filtered_a_list = []
                if a_list:
                    for _ in a_list:
                        if my_attach_handle_module.attach_filter(a_info=_):
                            if _["href"][0] == "/":
                                input_url = input_info["url"] + _["href"]
                            else:
                                input_url = _["href"]
                            filtered_a_list.append({"website_id": input_info["id"],
                                                    "first_level_column": input_url,
                                                    "first_level_column_name": my_attach_handle_module.get_attach_name(
                                                        _),
                                                    "create_time": datetime.datetime.now().strftime(
                                                        "%Y-%m-%d %H:%M:%S"),
                                                    "in_use": 1,
                                                    "is_deleted": 1,
                                                    "remark": "null"})
                if img_info_list:
                    for m in img_info_list:
                        if my_attach_handle_module.attach_img_filter(img_info=m):
                            if m["href"][0] == "/":
                                input_url = input_info["url"] + m["href"]
                            else:
                                input_url = m["href"]
                            filtered_a_list.append({"website_id": input_info["id"],
                                                    "first_level_column": input_url,
                                                    "first_level_column_name": m["column_name"],
                                                    "create_time": datetime.datetime.now().strftime(
                                                        "%Y-%m-%d %H:%M:%S"),
                                                    "in_use": 1,
                                                    "is_deleted": 1,
                                                    "remark": "null"})
                # print(filtered_a_list)
                # 6. 排除文章的url,并判断是否有分页标识
                final_list = []
                if filtered_a_list:
                    for n in filtered_a_list:
                        # print(n["first_level_column"])
                        my_selenium_module1 = selenium_module.SeleniumModule()
                        n_html = my_selenium_module1.loading_html(input_url=n["first_level_column"])
                        if n_html:
                            if my_attach_handle_module.html_is_article(html_src=n_html):
                                my_paging_module = paging_module.PagingModule()
                                if my_paging_module.recognize_page(html_src=n_html):
                                    n["having_page"] = 1
                                else:
                                    n["having_page"] = 0
                                final_list.append(n)
                # 7. 将过滤后的栏目存储进数据库
                if final_list:
                    for j in final_list:
                        my_attach_handle_module.save_first_column(first_column_info=j)
                my_selenium_module.quit_browser()
                # print(img_info_list)
                return True

    # 主网站采集二级栏目的方法
    @staticmethod
    def grading_second_column(input_info):
        """
        采集主网站的二级栏目，并将采集结果存入数据库
        :param input_info:一级栏目的信息，结构类似{"id": web_id, "name": web_name, "url": web_url}
        :return: True/False
        """
        # 1. 获取所有待采集的一级栏目列表
        my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                    website_id=input_info["id"])
        first_column_list = my_attach_handle_module.get_all_first_column()
        # i的数据格式类似{"first_column_id": 1, 'first_column_url': 'http://stic.sz.gov.cn/znjqr/', 'first_column_name': '智能问答'}
        for i in first_column_list:
            # 2. 获取所有a标签列表
            my_selenium_module = selenium_module.SeleniumModule()
            response_html = my_selenium_module.loading_html(input_url=i["first_column_url"])
            if response_html:
                my_soup = bs4.BeautifulSoup(response_html, features="lxml")
                a_list = my_soup.find_all("a")
                # 3. 加载图片信息
                my_loading_img_module = loading_img_module.LoadingImg(website=input_info["url"],
                                                                      website_id=input_info["id"],
                                                                      a_list=a_list,
                                                                      current_page=i["first_column_url"],
                                                                      current_page_id=i["first_column_id"])
                img_info_list = my_loading_img_module.loading_img_main()
                # 4. 通过OCR识别图片的信息
                for _ in img_info_list:
                    my_optical_character_recognition_module = optical_character_recognition_module.OpticalCharacterRecognitionModule()
                    _["column_name"] = my_optical_character_recognition_module.recognize_character_main(
                        img_path=i["img_path"], img_type=i["img_type"])
                # 5. 过滤a标签
                filtered_a_list = []
                if a_list:
                    for m in a_list:
                        if my_attach_handle_module.attach_filter(a_info=m):
                            if m["href"][0] == "/":
                                input_url = input_info["url"] + m["href"]
                            else:
                                input_url = m["href"]
                            filtered_a_list.append({"website_id": input_info["id"],
                                                    "first_level_column": i["first_column_url"],
                                                    "first_level_column_name": i["first_column_name"],
                                                    "second_level_column": input_url,
                                                    "second_level_column_name": my_attach_handle_module.get_attach_name(
                                                        m),
                                                    "create_time": datetime.datetime.now().strftime(
                                                        "%Y-%m-%d %H:%M:%S"),
                                                    "in_use": 1,
                                                    "is_deleted": 1,
                                                    "remark": "null"})
                if img_info_list:
                    for n in img_info_list:
                        if my_attach_handle_module.attach_img_filter(img_info=n):
                            if n["href"][0] == "/":
                                input_url = input_info["url"] + n["href"]
                            else:
                                input_url = n["href"]
                            filtered_a_list.append({"website_id": input_info["id"],
                                                    "first_level_column": i["first_column_url"],
                                                    "first_level_column_name": i["first_column_name"],
                                                    "second_level_column": input_url,
                                                    "second_level_column_name": n["column_name"],
                                                    "create_time": datetime.datetime.now().strftime(
                                                        "%Y-%m-%d %H:%M:%S"),
                                                    "in_use": 1,
                                                    "is_deleted": 1,
                                                    "remark": "null"})
                # print(filtered_a_list)
                # 6. 排除文章的url
                final_list = []
                if filtered_a_list:
                    for j in filtered_a_list:
                        # print(n["first_level_column"])
                        j_html = my_selenium_module.loading_html(input_url=j["second_level_column"])
                        if j_html:
                            if my_attach_handle_module.html_is_article(html_src=j_html):
                                my_paging_module = paging_module.PagingModule()
                                if my_paging_module.recognize_page(html_src=j_html):
                                    j["having_page"] = 1
                                else:
                                    j["having_page"] = 0
                                final_list.append(j)
                # 7. 将过滤后的栏目存储进数据库
                if final_list:
                    for k in final_list:
                        my_attach_handle_module.save_second_column(second_column_info=k)
            my_selenium_module.quit_browser()
            return True

    # 主网站采集三级栏目的方法
    @staticmethod
    def grading_third_column(input_info):
        """
        采集主网站的三级栏目，并将采集结果存入数据库
        :param input_info:一级栏目的信息，结构类似{"id": web_id, "name": web_name, "url": web_url}
        :return: True/False
        """
        # 1. 获取所有待采集的二级栏目列表
        my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                    website_id=input_info["id"])
        second_column_list = my_attach_handle_module.get_all_second_column()
        # print(second_column_list)
        # i的数据格式类似{"first_column_id": 1, 'first_column_url': 'http://stic.sz.gov.cn/znjqr/', 'first_column_name': '智能问答'}
        for i in second_column_list:
            # 2. 获取所有a标签列表
            my_selenium_module = selenium_module.SeleniumModule()
            response_html = my_selenium_module.loading_html(input_url=i["second_level_column"])
            if response_html:
                my_soup = bs4.BeautifulSoup(response_html, features="lxml")
                a_list = my_soup.find_all("a")
                # 3. 加载图片信息
                my_loading_img_module = loading_img_module.LoadingImg(website=input_info["url"],
                                                                      website_id=input_info["id"],
                                                                      a_list=a_list,
                                                                      current_page=i["second_level_column"],
                                                                      current_page_id=i["column_id"])
                img_info_list = my_loading_img_module.loading_img_main()
                # 4. 通过OCR识别图片的信息
                for _ in img_info_list:
                    my_optical_character_recognition_module = optical_character_recognition_module.OpticalCharacterRecognitionModule()
                    _["column_name"] = my_optical_character_recognition_module.recognize_character_main(
                        img_path=i["img_path"], img_type=i["img_type"])
                # 5. 过滤a标签
                filtered_a_list = []
                if a_list:
                    for m in a_list:
                        if my_attach_handle_module.attach_filter(a_info=m):
                            if m["href"][0] == "/":
                                input_url = input_info["url"] + m["href"]
                            else:
                                input_url = m["href"]
                            filtered_a_list.append({"website_id": input_info["id"],
                                                    "first_level_column": i["first_column_url"],
                                                    "first_level_column_name": i["first_column_name"],
                                                    "second_level_column": i["second_level_column"],
                                                    "second_level_column_name": i["second_level_column_name"],
                                                    "third_level_column": input_url,
                                                    "third_level_column_name": my_attach_handle_module.get_attach_name(
                                                        m),
                                                    "create_time": datetime.datetime.now().strftime(
                                                        "%Y-%m-%d %H:%M:%S"),
                                                    "in_use": 1,
                                                    "is_deleted": 1,
                                                    "remark": "null"})
                if img_info_list:
                    for n in img_info_list:
                        if my_attach_handle_module.attach_img_filter(img_info=n):
                            if n["href"][0] == "/":
                                input_url = input_info["url"] + n["href"]
                            else:
                                input_url = n["href"]
                            filtered_a_list.append({"website_id": input_info["id"],
                                                    "first_level_column": i["first_column_url"],
                                                    "first_level_column_name": i["first_column_name"],
                                                    "second_level_column": i["second_level_column"],
                                                    "second_level_column_name": i["second_level_column_name"],
                                                    "third_level_column": input_url,
                                                    "third_level_column_name": n["column_name"],
                                                    "create_time": datetime.datetime.now().strftime(
                                                        "%Y-%m-%d %H:%M:%S"),
                                                    "in_use": 1,
                                                    "is_deleted": 1,
                                                    "remark": "null"})
                # print(filtered_a_list)
                # 6. 排除文章的url
                final_list = []
                if filtered_a_list:
                    for j in filtered_a_list:
                        # print(n["first_level_column"])
                        j_html = my_selenium_module.loading_html(input_url=j["third_level_column"])
                        if j_html:
                            if my_attach_handle_module.html_is_article(html_src=j_html):
                                my_paging_module = paging_module.PagingModule()
                                if my_paging_module.recognize_page(html_src=j_html):
                                    j["having_page"] = 1
                                else:
                                    j["having_page"] = 0
                                final_list.append(j)
                # 7. 将过滤后的栏目存储进数据库
                if final_list:
                    for k in final_list:
                        my_attach_handle_module.save_third_column(third_column_info=k)
                my_selenium_module.quit_browser()
        return True

    # 采集栏目主方法
    def grading_column(self, website_id):
        field_list = [website_id]
        print(field_list)
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "UPDATE crawled_website_info SET execution_status=0 WHERE id=%s"
        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
        website_info = self.get_url(input_id=website_id)
        if self.grading_first_column(input_info=website_info):
            if self.grading_second_column(input_info=website_info):
                if self.grading_third_column(input_info=website_info):
                    my_database_module = database_module.DatabaseModule()
                    sql_sentence = "UPDATE crawled_website_info SET execution_status=1 WHERE id=%s"
                    my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)

    # 根据栏目列表爬取文章，并把文章存储进库
    def crawled_article(self, website_id):
        """
        根据栏目列表爬取文章，并把文章存储进库
        :param website_id: 网站id
        :return:
        """
        website_info = self.get_url(input_id=website_id)
        # 1. 从数据库中获取栏目列表
        my_attach_handle_module = attach_handle_module.AttachHandle(website=website_info["url"],
                                                                    website_id=website_info["id"])
        column_list = my_attach_handle_module.get_all_column()
        # print(column_list)
        my_selenium_module = selenium_module.SeleniumModule()
        # 2. 遍历栏目列表，加载栏目页面并判断是否有翻页标签
        for i in column_list:
            # 三级栏目爬虫
            if i["third_level_column"] is not None:
                # 没有分页配置的情况
                if i["having_page"] == 0:
                    third_level_column_html = my_selenium_module.loading_html(input_url=i["third_level_column"])
                    if third_level_column_html:
                        third_level_column_soup = bs4.BeautifulSoup(third_level_column_html, "lxml")
                        a_list = third_level_column_soup.find_all("a")
                        # 文章过滤
                        article_list = []
                        if a_list:
                            for a_info in a_list:
                                if my_attach_handle_module.attach_article_filter(a_info=a_info):
                                    # 判断是否有分页标识
                                    my_paging_module = paging_module.PagingModule()
                                    if a_info["href"][0] == "/":
                                        input_url = website_info["url"] + a_info["href"]
                                    else:
                                        input_url = a_info["href"]
                                    html_third_article_src = my_selenium_module.loading_html(input_url=input_url)
                                    if my_paging_module.recognize_page(html_src=html_third_article_src):
                                        article_list.append({"website_id": website_info["id"],
                                                             "column_id": i["column_id"],
                                                             "url": input_url,
                                                             "create_time": datetime.datetime.now().strftime(
                                                                 "%Y-%m-%d %H:%M:%S"),
                                                             "having_page": 1,
                                                             "is_analized": 0,
                                                             "is_deleted": 1})
                                    else:
                                        article_list.append({"website_id": website_info["id"],
                                                             "column_id": i["column_id"],
                                                             "url": input_url,
                                                             "create_time": datetime.datetime.now().strftime(
                                                                 "%Y-%m-%d %H:%M:%S"),
                                                             "having_page": 0,
                                                             "is_analized": 0,
                                                             "is_deleted": 1})
                        # 将文章存储进数据库
                        for article_info in article_list:
                            my_attach_handle_module.save_article(article_info=article_info)
                # 有分页配置的情况
                else:
                    third_level_column_html_list = my_selenium_module.loading_column_page_html(column_id=i["column_id"],
                                                                                               column_url=i[
                                                                                                   "third_level_column"])
                    for third_level_column_html in third_level_column_html_list:
                        third_level_column_soup = bs4.BeautifulSoup(third_level_column_html, "lxml")
                        a_list = third_level_column_soup.find_all("a")
                        # 文章过滤
                        article_list = []
                        if a_list:
                            for a_info in a_list:
                                if my_attach_handle_module.attach_article_filter(a_info=a_info):
                                    # 判断是否有分页标识
                                    my_paging_module = paging_module.PagingModule()
                                    html_third_article_src = my_selenium_module.loading_html(input_url=a_info["href"])
                                    if html_third_article_src:
                                        if my_paging_module.recognize_page(html_src=html_third_article_src):
                                            article_list.append({"website_id": website_info["id"],
                                                                 "column_id": i["column_id"],
                                                                 "url": a_info["href"],
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 1,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                                        else:
                                            article_list.append({"website_id": website_info["id"],
                                                                 "column_id": i["column_id"],
                                                                 "url": a_info["href"],
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 0,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                        # 将文章存储进数据库
                        for article_info in article_list:
                            my_attach_handle_module.save_article(article_info=article_info)
            # 二级栏目爬虫
            elif i["third_level_column"] is None and i["second_level_column"] is not None:
                # 没有分页配置的情况
                if i["having_page"] == 0:
                    third_level_column_html = my_selenium_module.loading_html(input_url=i["second_level_column"])
                    if third_level_column_html:
                        third_level_column_soup = bs4.BeautifulSoup(third_level_column_html, "lxml")
                        a_list = third_level_column_soup.find_all("a")
                        # 文章过滤
                        article_list = []
                        if a_list:
                            for a_info in a_list:
                                if my_attach_handle_module.attach_article_filter(a_info=a_info):
                                    # 判断是否有分页标识
                                    my_paging_module = paging_module.PagingModule()
                                    if a_info["href"][0] == "/":
                                        input_url = website_info["url"] + a_info["href"]
                                    else:
                                        input_url = a_info["href"]
                                    html_third_article_src = my_selenium_module.loading_html(input_url=input_url)
                                    if my_paging_module.recognize_page(html_src=html_third_article_src):
                                        article_list.append({"website_id": website_info["id"],
                                                             "column_id": i["column_id"],
                                                             "url": input_url,
                                                             "create_time": datetime.datetime.now().strftime(
                                                                 "%Y-%m-%d %H:%M:%S"),
                                                             "having_page": 1,
                                                             "is_analized": 0,
                                                             "is_deleted": 1})
                                    else:
                                        article_list.append({"website_id": website_info["id"],
                                                             "column_id": i["column_id"],
                                                             "url": input_url,
                                                             "create_time": datetime.datetime.now().strftime(
                                                                 "%Y-%m-%d %H:%M:%S"),
                                                             "having_page": 0,
                                                             "is_analized": 0,
                                                             "is_deleted": 1})
                        # 将文章存储进数据库
                        for article_info in article_list:
                            my_attach_handle_module.save_article(article_info=article_info)
                # 有分页配置的情况
                else:
                    third_level_column_html_list = my_selenium_module.loading_column_page_html(column_id=i["column_id"],
                                                                                               column_url=i[
                                                                                                   "second_level_column"])
                    for third_level_column_html in third_level_column_html_list:
                        third_level_column_soup = bs4.BeautifulSoup(third_level_column_html, "lxml")
                        a_list = third_level_column_soup.find_all("a")
                        # 文章过滤
                        article_list = []
                        if a_list:
                            for a_info in a_list:
                                if my_attach_handle_module.attach_article_filter(a_info=a_info):
                                    # 判断是否有分页标识
                                    my_paging_module = paging_module.PagingModule()
                                    if a_info["href"][0] == "/":
                                        input_url = website_info["url"] + a_info["href"]
                                    else:
                                        input_url = a_info["href"]
                                    html_third_article_src = my_selenium_module.loading_html(input_url=input_url)
                                    if html_third_article_src:
                                        if my_paging_module.recognize_page(html_src=html_third_article_src):
                                            article_list.append({"website_id": website_info["id"],
                                                                 "column_id": i["column_id"],
                                                                 "url": input_url,
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 1,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                                        else:
                                            article_list.append({"website_id": website_info["id"],
                                                                 "column_id": i["column_id"],
                                                                 "url": input_url,
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 0,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                        # 将文章存储进数据库
                        for article_info in article_list:
                            my_attach_handle_module.save_article(article_info=article_info)
            # 一级栏目爬虫
            elif i["third_level_column"] is None and i["second_level_column"] is None and i["first_column_url"] is not None:
                # 没有分页配置的情况
                if i["having_page"] == 0:
                    third_level_column_html = my_selenium_module.loading_html(input_url=i["first_column_url"])
                    if third_level_column_html:
                        third_level_column_soup = bs4.BeautifulSoup(third_level_column_html, "lxml")
                        a_list = third_level_column_soup.find_all("a")
                        # 文章过滤
                        article_list = []
                        if a_list:
                            for a_info in a_list:
                                if my_attach_handle_module.attach_article_filter(a_info=a_info):
                                    # 判断是否有分页标识
                                    my_paging_module = paging_module.PagingModule()
                                    if a_info["href"][0] == "/":
                                        input_url = website_info["url"] + a_info["href"]
                                    else:
                                        input_url = a_info["href"]
                                    html_third_article_src = my_selenium_module.loading_html(input_url=input_url)
                                    if my_paging_module.recognize_page(html_src=html_third_article_src):
                                        article_list.append({"website_id": website_info["id"],
                                                             "column_id": i["column_id"],
                                                             "url": input_url,
                                                             "create_time": datetime.datetime.now().strftime(
                                                                 "%Y-%m-%d %H:%M:%S"),
                                                             "having_page": 1,
                                                             "is_analized": 0,
                                                             "is_deleted": 1})
                                    else:
                                        article_list.append({"website_id": website_info["id"],
                                                             "column_id": i["column_id"],
                                                             "url": input_url,
                                                             "create_time": datetime.datetime.now().strftime(
                                                                 "%Y-%m-%d %H:%M:%S"),
                                                             "having_page": 0,
                                                             "is_analized": 0,
                                                             "is_deleted": 1})
                        # 将文章存储进数据库
                        for article_info in article_list:
                            my_attach_handle_module.save_article(article_info=article_info)
                # 有分页配置的情况
                else:
                    first_level_column_html_list = my_selenium_module.loading_column_page_html(column_id=i["column_id"],
                                                                                               column_url=i[
                                                                                                   "first_column_url"])
                    # print(first_level_column_html_list)
                    for first_level_column_html in first_level_column_html_list:
                        first_level_column_soup = bs4.BeautifulSoup(first_level_column_html, "lxml")
                        a_list = first_level_column_soup.find_all("a")
                        # 文章过滤
                        article_list = []
                        if a_list:
                            for a_info in a_list:
                                # print(a_info)
                                if my_attach_handle_module.attach_article_filter(a_info=a_info):
                                    # 判断是否有分页标识
                                    my_paging_module = paging_module.PagingModule()
                                    if a_info["href"][0] == "/":
                                        input_url = website_info["url"] + a_info["href"]
                                    else:
                                        input_url = a_info["href"]
                                    html_third_article_src = my_selenium_module.loading_html(input_url=input_url)
                                    if html_third_article_src:
                                        if my_paging_module.recognize_page(html_src=html_third_article_src):
                                            article_list.append({"website_id": website_info["id"],
                                                                 "column_id": i["column_id"],
                                                                 "url": input_url,
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 1,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                                        else:
                                            article_list.append({"website_id": website_info["id"],
                                                                 "column_id": i["column_id"],
                                                                 "url": input_url,
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 0,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                        # print(article_list)
                        # 将文章存储进数据库
                        for article_info in article_list:
                            my_attach_handle_module.save_article(article_info=article_info)

    # 分析文章
    def analyze_article(self, website_id):
        website_info = self.get_url(input_id=website_id)
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT id, website_id, column_id, url, having_page FROM crawled_article_info WHERE website_id={website_id} AND is_analized=0 AND is_deleted=1;".format(
            website_id=website_id)
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        if my_data:
            for i in my_data:
                article_info = {"id": i[0], "website_id": website_id, "website_url": website_info["url"],
                                "column_id": i[2],
                                "url": i[3], "having_page": i[4]}
                my_crawled_logging_module = crawled_logging_module.CrawledLoggingModule()
                my_crawled_logging_module.start_article_log(website_id=website_id, article_id=i[0])
                my_article_analyze_module = article_analyze_module.ArticleAnalyzeModule(article_info=article_info)
                try:
                    my_article_analyze_module.article_analyze_main()
                    my_crawled_logging_module.end_article_log(website_id=website_id, article_id=i[0], task_status=2)
                except Exception as e:
                    print(e)
                    my_crawled_logging_module.end_article_log(website_id=website_id, article_id=i[0], task_status=1)

    # 检测配置的xpath是否正确的方法
    @staticmethod
    def check_xpath_config(input_url, xpath):
        my_selenium_module = selenium_module.SeleniumModule()
        if my_selenium_module.check_xpath(input_url=input_url, xpath=xpath):
            return True

    # 检测给定的url是否为网站首页
    @staticmethod
    def check_is_homepage(input_url):
        homepage = attach_handle_module.AttachHandle.analyze_url(url=input_url)
        if homepage == input_url:
            return True

    # 单个爬虫任务
    def one_crawled_task(self, website_id):
        field_list = []
        my_crawled_logging_module = crawled_logging_module.CrawledLoggingModule()
        my_crawled_logging_module.start_website_log(website_id=website_id)
        my_database_module = database_module.DatabaseModule()
        field_list.append(website_id)
        sql_sentence = "UPDATE crawled_website_info SET execution_status=2 WHERE id=%s"
        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
        try:
            self.crawled_article(website_id=website_id)
            self.analyze_article(website_id=website_id)
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "UPDATE crawled_website_info SET execution_status=3 WHERE id=%s"
            my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
            my_crawled_logging_module.end_website_log(website_id=website_id, task_status=2)
        except Exception as e:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "UPDATE crawled_website_info SET execution_status=4 WHERE id=%s"
            my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
            print(e)
            my_crawled_logging_module.end_website_log(website_id=website_id, task_status=1)

    # 多进程执行爬虫任务
    def multiprocessing_task(self):
        # # 1.redis发布消息，任务开始
        # my_redis_module = redis_main.RedisModule()
        # my_redis_module.publish_theme(channel_name="crawled_task", send_message=json.dumps({"crawled_task": 1}))
        # 2.添加任务日志
        my_crawled_logging_module = crawled_logging_module.CrawledLoggingModule()
        my_crawled_logging_module.start_task_log()
        # 3.获取需要执行爬虫任务的网站id列表
        website_id_list = []
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT id FROM crawled_website_info WHERE execution_status IN (1, 2, 3, 4) AND in_use=1 AND is_deleted=1;"
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        # print(my_data)
        if my_data:
            for i in my_data:
                website_id_list.append(i[0])
        # print(website_id_list)
        for website_id in website_id_list:
            self.one_crawled_task(website_id=website_id)
        # 5.添加任务成功日志
        my_crawled_logging_module.end_task_log(task_status=2)

    # 中止爬虫任务
    @staticmethod
    def terminate_the_task():
        my_redis_module = redis_main.RedisModule()
        my_redis_module.publish_theme(channel_name="crawled_task", send_message=0)

    # 多进程采集栏目
    def multiprocessing_grading(self):
        # 获取需要执行爬虫任务的网站id列表
        website_id_list = []
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT id FROM crawled_website_info WHERE execution_status IN (1, 2, 3, 4) AND in_use=1 AND is_deleted=1;"
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        if my_data:
            for i in my_data:
                website_id_list.append(i[0])
        # my_po = Pool(1)
        for website_id in website_id_list:
            self.grading_column(website_id=website_id)
            # 异步开启进程, 非阻塞型, 能够向池中添加进程而不等待其执行完毕就能再次执行循环
        #     my_po.apply_async(func=self.grading_column, args=(website_id,))
        # my_po.close()  # 关闭pool, 则不会有新的进程添加进去
        # my_po.join()  # 必须在join之前close, 然后join等待pool中所有的进程执行完毕


if __name__ == '__main__':
    main_crawled_process = MainCrawledProcess()
    # main_crawled_process.grading_column(website_id=1)
    # main_crawled_process.crawled_article(website_id=1)
    # main_crawled_process.analyze_article(website_id=1)
    # main_crawled_process.multiprocessing_task()
    # main_crawled_process.crawled_article(website_id=16)
    # main_crawled_process.analyze_article(website_id=16)
    main_crawled_process.multiprocessing_grading()
