import bs4
from app.main.crawled_module import database_module


class PagingModule(object):

    # 判断是否有分页标识
    @staticmethod
    def recognize_page(html_src):
        """
        判断是否有分页标识
        :param html_src: 加载的页面资源
        :return: True/False
        """
        my_soup = bs4.BeautifulSoup(html_src, "lxml")
        if my_soup.find_all(name="div", attrs={"class": "page"}) or my_soup.find_all(name="div",
                                                                                     attrs={"class": "pagination"}):
            # print(my_soup.find_all(name="div", attrs={"class": "page"}))
            # print(my_soup.find_all(name="div", attrs={"class": "pagination"}))
            return True

    # 将栏目的分页配置存储进数据库
    @staticmethod
    def save_column_page_config(page_config_info):
        """
        将栏目页面的分页配置存储进数据库
        :param page_config_info:文章配置字典，格式类似{}
        :return:
        """
        field_list = []
        my_database_module = database_module.DatabaseModule()
        column_id = page_config_info["column_id"]
        column_page_type = page_config_info["column_page_type"]
        column_page_xpath = page_config_info["column_page_xpath"]
        if page_config_info["column_default_page"]:
            column_default_page = page_config_info["column_default_page"]
        else:
            column_default_page = 1
        column_max_page = page_config_info["column_max_page"]
        can_use = page_config_info["can_use"]
        is_deleted = page_config_info["is_deleted"]
        if page_config_info["create_user"]:
            create_user = page_config_info["create_user"]
        else:
            create_user = 0
        if page_config_info["update_user"]:
            update_user = page_config_info["update_user"]
        else:
            update_user = 0
        if page_config_info["create_time"]:
            create_time = page_config_info["create_time"]
        else:
            create_time = None
        if page_config_info["update_time"]:
            update_time = page_config_info["update_time"]
        else:
            update_time = None
        field_list.append(column_id)
        field_list.append(column_page_type)
        field_list.append(column_page_xpath)
        field_list.append(column_default_page)
        field_list.append(column_max_page)
        field_list.append(can_use)
        field_list.append(is_deleted)
        field_list.append(create_user)
        field_list.append(update_user)
        field_list.append(create_time)
        field_list.append(update_time)
        sql_sentence = "INSERT INTO crawled_column_page_config_info( column_id, column_page_type, column_page_xpath, column_default_page, column_max_page, can_use, is_deleted, create_user, update_user, create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        return my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)

    # 根据id查询栏目的分页配置
    @staticmethod
    def query_column_page_config(column_id):
        """
        根据栏目的id查询栏目的分页配置
        :param column_id: 栏目id
        :return:
        """
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT id, column_id, column_page_type, column_page_xpath, column_default_page, column_max_page, xpath_index FROM crawled_column_page_config_info WHERE is_deleted=1 AND column_id={column_id} AND can_use=1 ORDER BY xpath_index;".format(
            column_id=column_id)
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        # print(my_data)
        if my_data:
            if len(my_data) == 1:
                column_page_config = [{"column_config_id": my_data[0][0],
                                       "column_id": my_data[0][1],
                                       "column_page_type": my_data[0][2],
                                       "column_page_xpath": my_data[0][3],
                                       "column_default_page": my_data[0][4],
                                       "column_max_page": my_data[0][5],
                                       "xpath_index": my_data[0][6]}]
                return column_page_config
            else:
                column_page_config = [{"column_config_id": my_data[0][0],
                                       "column_id": my_data[0][1],
                                       "column_page_type": my_data[0][2],
                                       "column_page_xpath": my_data[0][3],
                                       "column_default_page": my_data[0][4],
                                       "column_max_page": my_data[0][5],
                                       "xpath_index": my_data[0][6]},
                                      {"column_config_id": my_data[1][0],
                                       "column_id": my_data[1][1],
                                       "column_page_type": my_data[1][2],
                                       "column_page_xpath": my_data[1][3],
                                       "column_default_page": my_data[1][4],
                                       "column_max_page": my_data[1][5],
                                       "xpath_index": my_data[1][6]}]
                return column_page_config

    # 将文章页面的分页配置存储进数据库
    @staticmethod
    def save_article_page_config(page_config_info):
        """
        将文章页面的分页配置存储进数据库
        :param page_config_info:文章配置字典，格式类似{}
        :return:
        """
        field_list = []
        article_id = page_config_info["article_id"]
        article_page_type = page_config_info["article_page_type"]
        article_page_xpath = page_config_info["article_page_xpath"]
        article_max_page = page_config_info["article_max_page"]
        can_use = page_config_info["can_use"]
        is_deleted = page_config_info["is_deleted"]
        if page_config_info["create_user"]:
            create_user = page_config_info["create_user"]
        else:
            create_user = 0
        if page_config_info["create_user"]:
            update_user = page_config_info["update_user"]
        else:
            update_user = 0
        if page_config_info["create_time"]:
            create_time = page_config_info["create_time"]
        else:
            create_time = None
        if page_config_info["create_user"]:
            update_time = page_config_info["update_time"]
        else:
            update_time = None
        my_database_module = database_module.DatabaseModule()
        field_list.append(article_id)
        field_list.append(article_page_type)
        field_list.append(article_page_xpath)
        field_list.append(article_max_page)
        field_list.append(can_use)
        field_list.append(is_deleted)
        field_list.append(create_user)
        field_list.append(update_user)
        field_list.append(create_time)
        field_list.append(update_time)
        sql_sentence = "INSERT INTO crawled_article_page_config_info( article_id, article_page_type, article_page_xpath, article_max_page, can_use, is_deleted, create_user, update_user, create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        return my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)

    # 根据id查询文章的分页配置
    @staticmethod
    def query_article_page_config(article_id):
        """
        根据栏目的id查询栏目的分页配置
        :param article_id: 文章id
        :return:
        """
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "SELECT id, article_id, article_page_type, article_page_xpath, article_max_page, xpath_index FROM crawled_article_page_config_info WHERE is_deleted=1 AND article_id={article_id} AND can_use=1;".format(
            article_id=article_id)
        my_data = my_database_module.select_data(sql_sentence=sql_sentence)
        # print(my_data)
        if my_data:
            if len(my_data) == 1:
                article_page_config = [{"article_config_id": my_data[0][0],
                                       "article_id": my_data[0][1],
                                       "article_page_type": my_data[0][2],
                                       "article_page_xpath": my_data[0][3],
                                       "article_default_page": my_data[0][4],
                                       "article_max_page": my_data[0][5],
                                       "xpath_index": my_data[0][6]}]
                return article_page_config
            else:
                article_page_config = [{"article_config_id": my_data[0][0],
                                       "article_id": my_data[0][1],
                                       "article_page_type": my_data[0][2],
                                       "article_page_xpath": my_data[0][3],
                                       "article_default_page": my_data[0][4],
                                       "article_max_page": my_data[0][5],
                                       "xpath_index": my_data[0][6]},
                                      {"article_config_id": my_data[1][0],
                                       "article_id": my_data[1][1],
                                       "article_page_type": my_data[1][2],
                                       "article_page_xpath": my_data[1][3],
                                       "article_default_page": my_data[1][4],
                                       "article_max_page": my_data[1][5],
                                       "xpath_index": my_data[1][6]}]
                return article_page_config


if __name__ == '__main__':
    # my_selenium_module = selenium_module.SeleniumModule()
    # response_html = my_selenium_module.loading_html(input_url="http://sdc.chinasoftinc.com:9400/#/todos/list")
    # my_selenium_module.quit_browser()
    my_paging_module = PagingModule()
    # my_paging_module.recognize_page(html_src=response_html)
    my_paging_module.query_column_page_config(column_id=31)
