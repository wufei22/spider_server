# coding=utf-8
import bs4
from app.main.crawled_module import database_module, request_module, selenium_module, attach_handle_module, \
    loading_img_module, article_analyze_module, crawled_logging_module
from app.main.redis_module import *
from app.main.public_method import *


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
        crawled_logging = logging_module.CrawledLogging()
        try:
            # 1. 识别当前网站的反爬虫协议
            my_request_module = request_module.RequestModule()
            if my_request_module.main_process(url=input_info["url"]):
                # 2. 获取所有a标签列表
                my_selenium_module = selenium_module.SeleniumModule()
                response_html = my_selenium_module.loading_html(input_url=input_info["url"])
                my_selenium_module.quit_browser()
                if response_html:
                    crawled_logging.debug_log_main(message="渲染网站首页成功{input_info}".format(input_info=input_info))
                    my_soup = bs4.BeautifulSoup(response_html, features="lxml")
                    a_list = my_soup.find_all("a")
                    # 3. 加载图片信息
                    crawled_logging.debug_log_main(message="开始处理图像栏目{input_info}".format(input_info=input_info))
                    my_loading_img_module = loading_img_module.LoadingImg(website=input_info["url"],
                                                                          website_id=input_info["id"],
                                                                          a_list=a_list)
                    img_info_list = my_loading_img_module.loading_img_main()
                    # 4. 过滤a标签
                    crawled_logging.debug_log_main(message="开始处理a标签{input_info}".format(input_info=input_info))
                    my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                                website_id=input_info["id"])
                    my_attach_handle_module.column_filter_main(a_list=a_list,
                                                               img_info_list=img_info_list,
                                                               parent_id=None)
                    crawled_logging.debug_log_main(message="成功采集一级栏目信息")
                    return True
                else:
                    crawled_logging.debug_log_main(message="渲染网站首页失败{input_info}".format(input_info=input_info))
            else:
                crawled_logging.debug_log_main(message="网络有爬虫协议或网络未连通{input_info}".format(input_info=input_info))
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)

    # 主网站采集二级栏目的方法
    @staticmethod
    def grading_second_column(input_info):
        """
        采集主网站的二级栏目，并将采集结果存入数据库
        :param input_info:一级栏目的信息，结构类似{"id": web_id, "name": web_name, "url": web_url}
        :return: True/False
        """
        crawled_logging = logging_module.CrawledLogging()
        crawled_logging.debug_log_main(message="开始采集二级栏目{input_info}".format(input_info=input_info))
        try:
            # 1. 获取所有待采集的一级栏目列表
            my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                        website_id=input_info["id"])
            first_column_list = my_attach_handle_module.get_all_first_column()
            # i的数据格式类似{"column_id": i[0], "parent_id": i[1], "column_name": i[2], "column_url": i[3], "having_page": i[4]}
            if first_column_list:
                for i in first_column_list:
                    crawled_logging.debug_log_main(message="一级栏目信息{i}".format(i=i))
                    # 2. 获取所有a标签列表
                    my_selenium_module = selenium_module.SeleniumModule()
                    response_html = my_selenium_module.loading_html(input_url=i["column_url"])
                    my_selenium_module.quit_browser()
                    if response_html:
                        crawled_logging.debug_log_main(message="加载一级栏目页面成功{input_info}".format(input_info=input_info))
                        my_soup = bs4.BeautifulSoup(response_html, features="lxml")
                        a_list = my_soup.find_all("a")
                        # 3. 加载图片信息
                        crawled_logging.debug_log_main(message="开始处理图片{input_info}".format(input_info=input_info))
                        my_loading_img_module = loading_img_module.LoadingImg(website=input_info["url"],
                                                                              website_id=input_info["id"],
                                                                              a_list=a_list,
                                                                              current_page=i["column_url"],
                                                                              current_page_id=i["column_id"])
                        img_info_list = my_loading_img_module.loading_img_main()
                        # 4. 过滤a标签
                        crawled_logging.debug_log_main(message="开始处理a标签{input_info}".format(input_info=input_info))
                        my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                                    website_id=input_info["id"])
                        my_attach_handle_module.column_filter_main(a_list=a_list, img_info_list=img_info_list,
                                                                   parent_id=i["column_id"])
                        crawled_logging.debug_log_main(message="成功采集二级栏目信息{i}".format(i=i))
                    else:
                        crawled_logging.debug_log_main(message="加载一级栏目页面失败{i}".format(i=i))
                return True
            else:
                crawled_logging.debug_log_main(message="获取一级栏目列表失败{input_info}".format(input_info=input_info))
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)

    # 主网站采集三级栏目的方法
    @staticmethod
    def grading_third_column(input_info):
        """
        采集主网站的三级栏目，并将采集结果存入数据库
        :param input_info:一级栏目的信息，结构类似{"id": web_id, "name": web_name, "url": web_url}
        :return: True/False
        """
        crawled_logging = logging_module.CrawledLogging()
        crawled_logging.debug_log_main(message="开始采集三级栏目{input_info}".format(input_info=input_info))
        try:
            # 1. 获取所有待采集的二级栏目列表
            my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                        website_id=input_info["id"])
            second_column_list = my_attach_handle_module.get_all_second_column()
            # i的数据格式类似{"column_id": i[0], "parent_id": i[1], "column_name": i[2], "column_url": i[3], "having_page": i[4]}
            if second_column_list:
                for i in second_column_list:
                    crawled_logging.debug_log_main(message="待分析的二级栏目信息{i}".format(i=i))
                    # 2. 获取所有a标签列表
                    my_selenium_module = selenium_module.SeleniumModule()
                    response_html = my_selenium_module.loading_html(input_url=i["column_url"])
                    my_selenium_module.quit_browser()
                    if response_html:
                        crawled_logging.debug_log_main(message="加载二级栏目页面{input_info}".format(input_info=input_info))
                        my_soup = bs4.BeautifulSoup(response_html, features="lxml")
                        a_list = my_soup.find_all("a")
                        # 3. 加载图片信息
                        crawled_logging.debug_log_main(message="开始处理图片{input_info}".format(input_info=input_info))
                        my_loading_img_module = loading_img_module.LoadingImg(website=input_info["url"],
                                                                              website_id=input_info["id"],
                                                                              a_list=a_list,
                                                                              current_page=i["column_url"],
                                                                              current_page_id=i["column_id"])
                        img_info_list = my_loading_img_module.loading_img_main()
                        # 5. 过滤a标签
                        crawled_logging.debug_log_main(message="开始过滤a标签{input_info}".format(input_info=input_info))
                        my_attach_handle_module = attach_handle_module.AttachHandle(website=input_info["url"],
                                                                                    website_id=input_info["id"])
                        my_attach_handle_module.column_filter_main(a_list=a_list,
                                                                   img_info_list=img_info_list,
                                                                   parent_id=i["column_id"])
                        crawled_logging.debug_log_main(message="成功采集三级栏目信息{i}".format(i=i))

                    else:
                        crawled_logging.debug_log_main(message="加载二级栏目页面失败{input_info}".format(input_info=input_info))
                return True
            else:
                crawled_logging.debug_log_main(message="获取二级栏目列表失败{input_info}".format(input_info=input_info))
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)

    # 采集栏目主方法
    def grading_column(self, website_id):
        crawled_logging = logging_module.CrawledLogging()
        field_list = [website_id]
        try:
            website_info = self.get_url(input_id=website_id)
            if website_info:
                crawled_logging.debug_log_main(message="开始采集栏目{website_id}".format(website_id=website_id))
                my_database_module = database_module.DatabaseModule()
                sql_sentence = "UPDATE crawled_website_info SET execution_status=0 WHERE id=%s"
                my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
                if self.grading_first_column(input_info=website_info):
                    if self.grading_second_column(input_info=website_info):
                        if self.grading_third_column(input_info=website_info):
                            my_database_module = database_module.DatabaseModule()
                            sql_sentence = "UPDATE crawled_website_info SET execution_status=1 WHERE id=%s"
                            my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
                        else:
                            my_database_module = database_module.DatabaseModule()
                            sql_sentence = "UPDATE crawled_website_info SET execution_status=4 WHERE id=%s"
                            my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
                            crawled_logging.debug_log_main(message="采集三级栏目失败{website_id}".format(website_id=website_id))
                    else:
                        my_database_module = database_module.DatabaseModule()
                        sql_sentence = "UPDATE crawled_website_info SET execution_status=4 WHERE id=%s"
                        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
                        crawled_logging.debug_log_main(message="采集二级栏目失败{website_id}".format(website_id=website_id))
                else:
                    my_database_module = database_module.DatabaseModule()
                    sql_sentence = "UPDATE crawled_website_info SET execution_status=4 WHERE id=%s"
                    my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
                    crawled_logging.debug_log_main(message="采集一级栏目失败{website_id}".format(website_id=website_id))
            else:
                crawled_logging.debug_log_main(message="获取网站信息失败{website_id}".format(website_id=website_id))
                my_database_module = database_module.DatabaseModule()
                sql_sentence = "UPDATE crawled_website_info SET execution_status=4 WHERE id=%s"
                my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "UPDATE crawled_website_info SET execution_status=4 WHERE id=%s"
            my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)

    # 根据栏目列表爬取文章，并把文章存储进库
    def crawled_article(self, website_id):
        """
        根据栏目列表爬取文章，并把文章存储进库
        :param website_id: 网站id
        :return:
        """
        crawled_logging = logging_module.CrawledLogging()
        try:
            website_info = self.get_url(input_id=website_id)
            # 1. 从数据库中获取栏目列表
            my_attach_handle_module = attach_handle_module.AttachHandle(website=website_info["url"],
                                                                        website_id=website_info["id"])
            if my_attach_handle_module.crawled_article_main():
                print(1111)
                crawled_logging.debug_log_main(message="根据栏目爬取文章成功{website_info}".format(website_info=website_info))
            else:
                crawled_logging.debug_log_main(message="根据栏目爬取文章失败{website_info}".format(website_info=website_info))
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)

    # 分析文章
    def analyze_article(self, website_id, task_id):
        crawled_logging = logging_module.CrawledLogging()
        try:
            crawled_logging.debug_log_main(message="开始分析文章{website_id}".format(website_id=website_id))
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
                    crawled_logging.debug_log_main(message="分析文章，文章id为{article_id}".format(article_id=article_info["id"]))
                    my_crawled_logging_module = crawled_logging_module.CrawledLoggingModule()
                    my_crawled_logging_module.start_article_log(website_id=website_id, article_id=i[0], task_id=task_id)
                    my_article_analyze_module = article_analyze_module.ArticleAnalyzeModule(article_info=article_info)
                    try:
                        my_article_analyze_module.article_analyze_main()
                        my_crawled_logging_module.end_article_log(website_id=website_id, article_id=i[0], task_status=2, task_id=task_id)
                    except Exception as e:
                        # print(e)
                        crawled_logging.error_log_main(message=e)
                        my_crawled_logging_module.end_article_log(website_id=website_id, article_id=i[0], task_status=1, task_id=task_id)
            else:
                crawled_logging.debug_log_main(message="未获取到文章列表{website_id}".format(website_id=website_id))
        except Exception as e:
            # print(e)
            crawled_logging.error_log_main(message=e)

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
    def one_crawled_task(self, website_id, task_id):
        crawled_logging = logging_module.CrawledLogging()
        crawled_logging.debug_log_main(message="开始爬虫任务{website_id}".format(website_id=website_id))
        field_list = []
        my_crawled_logging_module = crawled_logging_module.CrawledLoggingModule()
        my_crawled_logging_module.start_website_log(website_id=website_id, task_id=task_id)
        my_database_module = database_module.DatabaseModule()
        field_list.append(website_id)
        sql_sentence = "UPDATE crawled_website_info SET execution_status=2 WHERE id=%s"
        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
        try:
            self.crawled_article(website_id=website_id)
            self.analyze_article(website_id=website_id, task_id=task_id)
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "UPDATE crawled_website_info SET execution_status=3 WHERE id=%s"
            my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
            my_crawled_logging_module.end_website_log(website_id=website_id, task_status=2, task_id=task_id)
        except Exception as e:
            # print(e)
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "UPDATE crawled_website_info SET execution_status=4 WHERE id=%s"
            my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)
            crawled_logging.error_log_main(message=e)
            my_crawled_logging_module.end_website_log(website_id=website_id, task_status=1, task_id=task_id)

    # 多进程执行爬虫任务
    def multiprocessing_task(self):
        # # 1.redis发布消息，任务开始
        # my_redis_module = redis_main.RedisModule()
        # my_redis_module.publish_theme(channel_name="crawled_task", send_message=json.dumps({"crawled_task": 1}))
        # 2.添加任务日志
        my_crawled_logging_module = crawled_logging_module.CrawledLoggingModule()
        task_id = my_crawled_logging_module.start_task_log()
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
            self.one_crawled_task(website_id=website_id, task_id=task_id)
        # 5.添加任务成功日志
        my_crawled_logging_module.end_task_log(task_status=2, task_id=task_id)

    # 中止爬虫任务
    @staticmethod
    def terminate_the_task():
        my_redis_module = redis_main.RedisModule()
        my_redis_module.publish_theme(channel_name="crawled_task", send_message=0)

    # 多进程采集栏目
    def multiprocessing_grading(self, website_id):
        my_crawled_logging_module = crawled_logging_module.CrawledLoggingModule()
        task_id = my_crawled_logging_module.start_task_log()
        # 获取需要执行爬虫任务的网站id列表
        self.grading_column(website_id=website_id)
        self.one_crawled_task(website_id=website_id, task_id=task_id)
        my_crawled_logging_module.end_task_log(task_status=2, task_id=task_id)
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
    main_crawled_process.multiprocessing_grading(website_id=28)
