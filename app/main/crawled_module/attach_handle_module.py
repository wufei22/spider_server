import re
import logging
import datetime
import os
import time
import bs4
from app.main.crawled_module import database_module, selenium_module, paging_module
from app.main.public_method import *


class AttachHandle(object):
    """
    a标签处理成栏目
    """

    def __init__(self, website, website_id):
        self.website = website
        self.website_id = website_id

    # 从数据库中获取判定重复的url列表和column列表
    def get_column(self):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT `column_name`, " \
                           "column_url " \
                           "FROM crawled_column_info " \
                           "WHERE website_id={website_id} AND is_deleted=1".format(website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            # print(my_data)
            column_list = []
            column_name_list = []
            if my_data:
                for i in my_data:
                    column_name_list.append(i[0])
                    column_list.append(i[1])
                column_dict = {"column_list": column_list, "column_name_list": column_name_list}
                crawled_logger.debug(msg="成功获取栏目列表")
                logging.shutdown()
                return column_dict
            else:
                crawled_logger.debug(msg="获取栏目列表失败")
                logging.shutdown()
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()

    # 从数据库中获取判断重复的文章列表
    def get_article(self):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT url FROM crawled_article_info WHERE website_id={website_id} AND is_deleted=1".format(
                website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            article_list = []
            if my_data:
                for i in my_data:
                    article_list.append(i[0])
                crawled_logger.debug(msg="获取文章列表成功")
            else:
                crawled_logger.debug(msg="获取文章列表失败")
            logging.shutdown()
            return article_list
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()

    # 提取首页网址
    @staticmethod
    def analyze_url(url):
        url_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
        compiled_url = re.match(pattern=url_pattern, string=url)
        if compiled_url:
            return compiled_url.group()

    # 尝试根据src下载html资源
    @staticmethod
    def downloading_html(html_src, url, website_id):
        # 判断是否创建文件夹，若没有，则创建文件夹，文件夹目录为./column_img/主网站id/当前页面id/当前日期
        if html_src:
            local_path = os.path.abspath(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
            folder = local_path + "/html_src/" + "/" + str(website_id) + time.strftime("%Y_%m_%d", time.localtime())
            if not os.path.exists(folder):
                os.makedirs(folder)
            html_path = folder + "/" + str(time.time()).replace(".", "") + ".txt"
            with open(html_path, 'wb') as f:
                f.write(html_src.encode())
                f.write(url.encode())

    # 获取网页后缀名
    @staticmethod
    def get_suffix(url):
        url_pattern = re.compile("[^.]*$")
        url_suffix = re.search(pattern=url_pattern, string=url)
        if url_suffix:
            return url_suffix.group()

    # 根据标签是否有href以及href是否为空来进行过滤
    @staticmethod
    def filter_with_href(a_info):
        if "href" in a_info.attrs:
            if a_info["href"]:
                if a_info["href"] != "/" and a_info["href"] != "./":
                    return True

    # 根据是否在同一域名下来进行过滤
    def filter_with_domain(self, a_info):
        if self.analyze_url(url=a_info["href"]) == self.analyze_url(url=self.website) or a_info["href"][0] == "/" or a_info["href"][0] == ".":
            return True

    # 根据链接后缀不为文件名来后缀
    def filter_with_suffix(self, a_info):
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT `value` FROM crawled_config_dict WHERE `name`='file_suffix'"
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        if my_data:
            keywords_list = []
            for i in my_data:
                keywords_list.append(i[0])
            if self.get_suffix(url=a_info["href"]) not in keywords_list:
                return True

    # 判断是否为索引index结尾，以index为结尾的默认去除/index再来判断是否重复
    def filter_with_index(self, a_info):
        my_url = a_info["href"]
        url_pattern = re.compile("/index.[^.]*$")
        compiled_url = re.findall(pattern=url_pattern, string=my_url)
        if compiled_url:
            my_url = my_url.replace("/index", "")
        if my_url != self.analyze_url(url=self.website):
            if my_url != self.website:
                return True

    # 排除所有name为全英文或全数字的a标签
    @staticmethod
    def filter_name_with_all_str(column_name):
        name_pattern = re.compile("(^\d*$)|(^[A-Za-z]+$)")
        if not re.search(pattern=name_pattern, string=column_name):
            return True

    # 排除所有name为分页关键字的a标签
    @staticmethod
    def filter_name_with_paging_keywords(column_name):
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT `value` FROM crawled_config_dict WHERE `name`='page_keyword'"
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        if my_data:
            keywords_list = []
            for i in my_data:
                keywords_list.append(i[0])
            if column_name not in keywords_list:
                return True

    # 排除所有name为地区名称的a标签
    @staticmethod
    def filter_name_with_area_keywords(column_name):
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT `value` FROM crawled_config_dict WHERE `name`='area_keyword'"
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        if my_data:
            keywords_list = []
            for i in my_data:
                keywords_list.append(i[0])
            if column_name not in keywords_list:
                return True

    # 排除所有name长度大于10的标签
    @staticmethod
    def filter_name_with_length(column_name):
        if len(column_name) <= 10:
            return True

    # 排除所有name出现在链接里的标签
    @staticmethod
    def filter_name_with_href(column_name, url):
        if column_name not in url:
            return True

    # 和数据库进行查重校验
    def filter_with_duplicates(self, column_name, url):
        column_dict = self.get_column()
        if column_dict:
            if column_name not in column_dict["column_name_list"]:
                if url not in column_dict["column_list"]:
                    return True
        else:
            return True

    # 文章的查重校验
    def filter_article_with_duplicates(self, url):
        article_list = self.get_article()
        if url not in article_list:
            return True

    # 根据算法来匹配栏目关键词
    @staticmethod
    def filter_with_nlp():
        return True

    # 获取a标签的名称
    @staticmethod
    def get_attach_name(a_info):
        """
        获取a标签的名称
        :param a_info: a标签信息
        :return: column_name
        """
        if a_info.text:
            return a_info.text
        elif "title" in a_info.attrs:
            return a_info["title"]
        elif "alt" in a_info.attrs:
            return a_info["alt"]

    # 判断是否为文章页
    @staticmethod
    def html_is_article(html_src):
        """
        判断是否为文章页
        :param html_src: html页面
        :return:
        """
        if html_src:
            if ("article" in html_src) or ("Article" in html_src):
                return False
            else:
                return True
        else:
            return True

    # a标签栏目过滤
    def attach_filter(self, a_info):
        """
        根据规则过滤a标签
        :param a_info: beautiful soup获取的所有a标签的单个信息
        :return:
        """
        # 标签链接不为空
        if self.filter_with_href(a_info=a_info):
            # 同一域名下
            if self.filter_with_domain(a_info=a_info):
                # 链接后缀不为文件名
                if self.filter_with_suffix(a_info=a_info):
                    # 去除/index来判断重复
                    if self.filter_with_index(a_info=a_info):
                        # 获取column_name
                        column_name = self.get_attach_name(a_info=a_info)
                        if column_name:
                            # 排除所有name为全英文或全数字的a标签
                            if self.filter_name_with_all_str(column_name=column_name):
                                # 排除所有name为分页关键字的a标签
                                if self.filter_name_with_paging_keywords(column_name=column_name):
                                    # 排除所有name为地区名称的a标签
                                    if self.filter_name_with_area_keywords(column_name=column_name):
                                        # 排除所有name长度大于10的标签
                                        if self.filter_name_with_length(column_name=column_name):
                                            # 排除所有name出现在链接里的标签
                                            if self.filter_name_with_href(column_name=column_name,
                                                                          url=a_info["href"]):
                                                # 和数据库进行查重校验
                                                if self.filter_with_duplicates(column_name=column_name,
                                                                               url=a_info["href"]):
                                                    # 根据算法来匹配栏目关键词
                                                    if self.filter_with_nlp():
                                                        return True

    # a标签文章过滤
    def attach_article_filter(self, a_info):
        """
        根据规则过滤a标签,筛选出文章a标签
        :param a_info: beautiful soup获取的所有a标签的单个信息
        :return: True/False
        """
        # 标签链接不为空
        if self.filter_with_href(a_info=a_info):
            # 同一域名下
            if self.filter_with_domain(a_info=a_info):
                # 链接后缀不为文件名
                if self.filter_with_suffix(a_info=a_info):
                    # 去除/index来判断是否与主网站重复
                    if self.filter_with_index(a_info=a_info):
                        # 和数据库进行查重校验
                        if self.filter_article_with_duplicates(url=a_info["href"]):
                            # 判断是否为文章
                            my_selenium_module = selenium_module.SeleniumModule()
                            if a_info["href"][0] == "/":
                                input_url = self.website + a_info["href"]
                            else:
                                input_url = a_info["href"]
                            response_html = my_selenium_module.loading_html(input_url=input_url)
                            my_selenium_module.quit_browser()
                            if not self.html_is_article(html_src=response_html):
                                return True

    # img过滤
    def attach_img_filter(self, img_info):
        """
        图像的过滤规则
        :param img_info:{"column_name": img_name, "href": img_url}
        :return:
        """
        column_name = img_info["column_name"]
        url = img_info["href"]
        # 标签链接不为空
        if url:
            # 同一域名下
            if self.filter_with_domain(a_info=img_info):
                # 链接后缀不为文件名
                if self.filter_with_suffix(a_info=img_info):
                    # 去除/index来判断重复
                    if self.filter_with_index(a_info=img_info):
                        if column_name:
                            # 排除所有name为全英文或全数字的a标签
                            if self.filter_name_with_all_str(column_name=column_name):
                                # 排除所有name为分页关键字的a标签
                                if self.filter_name_with_paging_keywords(column_name=column_name):
                                    # 排除所有name为地区名称的a标签
                                    if self.filter_name_with_area_keywords(column_name=column_name):
                                        # 排除所有name长度大于10的标签
                                        if self.filter_name_with_length(column_name=column_name):
                                            # 排除所有name出现在链接里的标签
                                            if self.filter_name_with_href(column_name=column_name, url=url):
                                                # 和数据库进行查重校验
                                                if self.filter_with_duplicates(column_name=column_name, url=url):
                                                    # 根据算法来匹配栏目关键词
                                                    if self.filter_with_nlp():
                                                        return True

    # 栏目存储进库
    @staticmethod
    def save_column(column_info):
        field_list = []
        my_database_module = database_module.DatabaseModule()
        website_id = column_info["website_id"]
        field_list.append(website_id)
        parent_id = column_info["parent_id"]
        field_list.append(parent_id)
        column_name = column_info["column_name"]
        field_list.append(column_name)
        column_url = column_info["column_url"]
        field_list.append(column_url)
        create_time = column_info["create_time"]
        field_list.append(create_time)
        having_page = column_info["having_page"]
        field_list.append(having_page)
        in_use = column_info["in_use"]
        field_list.append(in_use)
        is_deleted = column_info["is_deleted"]
        field_list.append(is_deleted)
        remark = column_info["remark"]
        field_list.append(remark)
        sql_sentence = "INSERT INTO crawled_column_info" \
                       "( website_id, parent_id, `column_name`, column_url, create_time, having_page, in_use, " \
                       "is_deleted, remark) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # print(sql_sentence)
        return my_database_module.add_data(sql_sentence=sql_sentence, field_list=field_list)

    # 文章存储进数据库
    @staticmethod
    def save_article(article_info):
        field_list = []
        website_id = article_info["website_id"]
        field_list.append(website_id)
        column_id = article_info["column_id"]
        field_list.append(column_id)
        url = article_info["url"]
        field_list.append(url)
        create_time = article_info["create_time"]
        field_list.append(create_time)
        having_page = article_info["having_page"]
        field_list.append(having_page)
        is_analized = article_info["is_analized"]
        field_list.append(is_analized)
        is_deleted = article_info["is_deleted"]
        field_list.append(is_deleted)
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_article_info" \
                       "( website_id, column_id, url, create_time, having_page, is_analized, in_use, is_deleted) " \
                       "VALUES (%s, %s, %s, %s, %s, %s, 1, %s)"
        # print(sql_sentence)
        return my_database_module.add_data(sql_sentence=sql_sentence, field_list=field_list)

    # 获取所有一级栏目列表
    def get_all_first_column(self):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT id, parent_id, `column_name`, column_url, having_page " \
                           "FROM crawled_column_info WHERE website_id={website_id} AND is_deleted=1 " \
                           "AND in_use=1 AND parent_id IS NULL;".format(website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            column_list = []
            if my_data:
                for i in my_data:
                    column_list.append({"column_id": i[0],
                                        "parent_id": i[1],
                                        "column_name": i[2],
                                        "column_url": i[3],
                                        "having_page": i[4]})
                crawled_logger.info(msg="获取所有栏目列表成功")
            else:
                crawled_logger.info(msg="获取所有栏目列表失败")
            logging.shutdown()
            return column_list
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()

    # 获取所有二级栏目列表
    def get_all_second_column(self):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT id, parent_id, `column_name`, column_url, having_page " \
                           "FROM crawled_column_info WHERE website_id={website_id} AND is_deleted=1 " \
                           "AND in_use=1 AND parent_id IS NOT NULL;".format(website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            column_list = []
            if my_data:
                for i in my_data:
                    column_list.append({"column_id": i[0],
                                        "parent_id": i[1],
                                        "column_name": i[2],
                                        "column_url": i[3],
                                        "having_page": i[4]})
                crawled_logger.info(msg="获取所有栏目列表成功")
            else:
                crawled_logger.info(msg="获取所有栏目列表失败")
            logging.shutdown()
            return column_list
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()

    # 获取所有栏目列表
    def get_all_column(self):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT id, parent_id, `column_name`, column_url, having_page " \
                           "FROM crawled_column_info WHERE website_id={website_id} AND is_deleted=1 " \
                           "AND in_use=1;".format(website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            column_list = []
            if my_data:
                for i in my_data:
                    column_list.append({"column_id": i[0],
                                        "parent_id": i[1],
                                        "column_name": i[2],
                                        "column_url": i[3],
                                        "having_page": i[4]})
                crawled_logger.info(msg="获取所有栏目列表成功")
            else:
                crawled_logger.info(msg="获取所有栏目列表失败")
            logging.shutdown()
            return column_list
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()

    # a标签过滤主程序
    def column_filter_main(self, a_list, img_info_list, parent_id):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            filtered_a_list = []
            final_list = []
            if a_list:
                # print(a_list)
                crawled_logger.debug(msg="开始过滤标签信息")
                for i in a_list:
                    crawled_logger.debug(msg="开始过滤标签{i}".format(i=i))
                    if self.attach_filter(a_info=i):
                        if i["href"][0] == "/":
                            input_url = self.website + i["href"]
                        elif i["href"][0] == ".":
                            input_url = self.website + i["href"][1::]
                        else:
                            input_url = i["href"]
                        filtered_a_list.append({"website_id": self.website_id,
                                                "parent_id": parent_id,
                                                "column_name": self.get_attach_name(i),
                                                "column_url": input_url,
                                                "create_time": datetime.datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"),
                                                "in_use": 1,
                                                "is_deleted": 1,
                                                "remark": None})
                if filtered_a_list:
                    crawled_logger.debug(msg="过滤后的a标签列表为{filtered_a_list}".format(filtered_a_list=filtered_a_list))
                else:
                    crawled_logger.debug(msg="未获取到过滤后的a标签列表信息")
            else:
                crawled_logger.debug(msg="没有采集到标签信息")
            if img_info_list:
                crawled_logger.debug(msg="开始过滤图像信息")
                for _ in img_info_list:
                    crawled_logger.debug(msg="正在过滤图像标签{_}".format(_=_))
                    if self.attach_img_filter(img_info=_):
                        if _["href"][0] == "/":
                            input_url = self.website + _["href"]
                        elif _["href"][0] == ".":
                            input_url = self.website + _["href"][1::]
                        else:
                            input_url = _["href"]
                        filtered_a_list.append({"website_id": self.website_id,
                                                "parent_id": parent_id,
                                                "column_name": _["column_name"],
                                                "column_url": input_url,
                                                "create_time": datetime.datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"),
                                                "in_use": 1,
                                                "is_deleted": 1,
                                                "remark": None})
            else:
                crawled_logger.debug(msg="没有采集到图像信息")
            # 排除文章的url,并判断是否有分页标识
            crawled_logger.debug(msg="开始通过article标识鉴别列表页")
            if filtered_a_list:
                # 测试阶段只取一条
                # filtered_a_list = filtered_a_list[0:1:]
                for m in filtered_a_list:
                    crawled_logger.debug(msg="开始通过article标识鉴别列表页{m}".format(m=m))
                    my_selenium_module = selenium_module.SeleniumModule()
                    n_html = my_selenium_module.loading_html(input_url=m["column_url"])
                    my_selenium_module.quit_browser()
                    if n_html:
                        self.downloading_html(n_html, url=m["column_url"], website_id=m["website_id"])
                        if self.html_is_article(html_src=n_html):
                            my_paging_module = paging_module.PagingModule()
                            if my_paging_module.recognize_page(html_src=n_html):
                                m["having_page"] = 1
                            else:
                                m["having_page"] = 0
                            final_list.append(m)
            else:
                crawled_logger.debug(msg="没有过滤后的数据")
            # 7. 将过滤后的栏目存储进数据库
            crawled_logger.debug(msg="存储进入数据库")
            if final_list:
                for n in final_list:
                    crawled_logger.debug(msg="将栏目信息存储进数据库{n}".format(n=n))
                    self.save_column(column_info=n)
            else:
                crawled_logger.debug(msg="最终没有栏目存储进数据库")
            logging.shutdown()
        except Exception as e:
            crawled_logger.error(msg=e)
            logging.shutdown()

    # 根据栏目遍历文章,并将文章存储入库
    def crawled_article_main(self):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            # {"column_id": i[0], "parent_id": i[1], "column_name": i[2], "column_url": i[3], "having_page": i[4]}
            column_list = self.get_all_column()
            if column_list:
                for i in column_list:
                    # 没有分页配置的情况
                    crawled_logger.debug(msg="根据栏目获取文章列表{i}".format(i=i))
                    if i["having_page"] == 0:
                        my_selenium_module = selenium_module.SeleniumModule()
                        column_html = my_selenium_module.loading_html(input_url=i["column_url"])
                        my_selenium_module.quit_browser()
                        if column_html:
                            column_soup = bs4.BeautifulSoup(column_html, "lxml")
                            a_list = column_soup.find_all("a")
                            # 文章过滤
                            article_list = []
                            if a_list:
                                for a_info in a_list:
                                    crawled_logger.debug(msg="文章过滤{a_info}".format(a_info=a_info))
                                    if self.attach_article_filter(a_info=a_info):
                                        # 判断是否有分页标识
                                        my_paging_module = paging_module.PagingModule()
                                        if a_info["href"][0] == "/":
                                            input_url = self.website + a_info["href"]
                                        elif a_info["href"][0] == ".":
                                            input_url = self.website + a_info["href"][1::]
                                        else:
                                            input_url = a_info["href"]
                                        my_selenium_module = selenium_module.SeleniumModule()
                                        html_article_src = my_selenium_module.loading_html(input_url=input_url)
                                        my_selenium_module.quit_browser()
                                        if my_paging_module.recognize_page(html_src=html_article_src):
                                            article_list.append({"website_id": self.website_id,
                                                                 "column_id": i["column_id"],
                                                                 "url": input_url,
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 1,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                                        else:
                                            article_list.append({"website_id": self.website_id,
                                                                 "column_id": i["column_id"],
                                                                 "url": input_url,
                                                                 "create_time": datetime.datetime.now().strftime(
                                                                     "%Y-%m-%d %H:%M:%S"),
                                                                 "having_page": 0,
                                                                 "is_analized": 0,
                                                                 "is_deleted": 1})
                            # 将文章存储进数据库
                            for article_info in article_list:
                                crawled_logger.debug(msg="将文章存储进数据库{article_info}".format(article_info=article_info))
                                self.save_article(article_info=article_info)
                    # 有分页配置的情况
                    else:
                        my_selenium_module = selenium_module.SeleniumModule()
                        column_html_list = my_selenium_module.loading_column_page_html(column_id=i["column_id"],
                                                                                       column_url=i["column_url"])
                        my_selenium_module.quit_browser()
                        for column_html in column_html_list:
                            column_soup = bs4.BeautifulSoup(column_html, "lxml")
                            a_list = column_soup.find_all("a")
                            # 文章过滤
                            article_list = []
                            if a_list:
                                for a_info in a_list:
                                    crawled_logger.debug(msg="文章过滤{a_info}".format(a_info=a_info))
                                    if self.attach_article_filter(a_info=a_info):
                                        # 判断是否有分页标识
                                        my_paging_module = paging_module.PagingModule()
                                        my_selenium_module = selenium_module.SeleniumModule()
                                        html_third_article_src = my_selenium_module.loading_html(
                                            input_url=a_info["href"])
                                        my_selenium_module.quit_browser()
                                        if html_third_article_src:
                                            if my_paging_module.recognize_page(html_src=html_third_article_src):
                                                article_list.append({"website_id": self.website_id,
                                                                     "column_id": i["column_id"],
                                                                     "url": a_info["href"],
                                                                     "create_time": datetime.datetime.now().strftime(
                                                                         "%Y-%m-%d %H:%M:%S"),
                                                                     "having_page": 1,
                                                                     "is_analized": 0,
                                                                     "is_deleted": 1})
                                            else:
                                                article_list.append({"website_id": self.website_id,
                                                                     "column_id": i["column_id"],
                                                                     "url": a_info["href"],
                                                                     "create_time": datetime.datetime.now().strftime(
                                                                         "%Y-%m-%d %H:%M:%S"),
                                                                     "having_page": 0,
                                                                     "is_analized": 0,
                                                                     "is_deleted": 1})
                            # 将文章存储进数据库
                            for article_info in article_list:
                                crawled_logger.debug(msg="文章存储进数据库库{article_info}".format(article_info=article_info))
                                self.save_article(article_info=article_info)
                crawled_logger.debug(msg="获取文章成功{website_id}".format(website_id=self.website_id))
                logging.shutdown()
                return True
            else:
                crawled_logger.debug(msg="未获取到栏目信息{website_id}".format(website_id=self.website_id))
                logging.shutdown()
        except Exception as e:
            crawled_logger.error(msg=e)
            logging.shutdown()


if __name__ == '__main__':
    test_attach_handle = AttachHandle(website=None, website_id=1)
    test_data = test_attach_handle.get_all_column()
    print(test_data)

