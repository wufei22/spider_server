import re
from app.main.crawled_module import database_module, selenium_module


class AttachHandle(object):
    """
    a标签处理成栏目
    """

    def __init__(self, website, website_id):
        self.website = website
        self.website_id = website_id

    # 从数据库中获取判定重复的url列表和column列表
    def get_column(self):
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT first_level_column, first_level_column_name, second_level_column, second_level_column_name, third_level_column, third_level_column_name FROM crawled_column_info WHERE website_id={website_id} AND is_deleted=1".format(
                website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            # print(my_data)
            column_list = []
            column_name_list = []
            if my_data:
                for i in my_data:
                    if i[0]:
                        column_list.append(i[0])
                    if i[1]:
                        column_name_list.append(i[1])
                    if i[2]:
                        column_list.append(i[2])
                    if i[3]:
                        column_name_list.append(i[3])
                    if i[4]:
                        column_list.append(i[4])
                    if i[5]:
                        column_name_list.append(i[5])
                column_dict = {"column_list": column_list, "column_name_list": column_name_list}
                return column_dict
        except Exception as e:
            print(e)
            return None

    # 从数据库中获取判断重复的文章列表
    def get_article(self):
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT url FROM crawled_article_info WHERE website_id={website_id} AND is_deleted=1".format(
                website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            article_list = []
            if my_data:
                for i in my_data:
                    article_list.append(i[0])
            return article_list
        except Exception as e:
            print(e)
            return None

    # 提取首页网址
    @staticmethod
    def analyze_url(url):
        url_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
        compiled_url = re.match(pattern=url_pattern, string=url)
        if compiled_url:
            return compiled_url.group()

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
            return True

    # 根据是否在同一域名下来进行过滤
    def filter_with_domain(self, a_info):
        if self.analyze_url(url=a_info["href"]) == self.analyze_url(url=self.website) or a_info["href"][0] == "/":
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
        if len(column_name) <= 6:
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

    # 一级栏目存储进库
    @staticmethod
    def save_first_column(first_column_info):
        my_database_module = database_module.DatabaseModule()
        website_id = first_column_info["website_id"]
        first_level_column = first_column_info["first_level_column"]
        first_level_column_name = first_column_info["first_level_column_name"]
        create_time = first_column_info["create_time"]
        having_page = first_column_info["having_page"]
        in_use = first_column_info["in_use"]
        is_deleted = first_column_info["is_deleted"]
        if first_column_info["remark"]:
            remark = first_column_info["remark"]
        else:
            remark = 'NULL'
        sql_sentence = "INSERT INTO crawled_column_info( website_id, first_level_column, first_level_column_name, create_time, having_page, in_use, is_deleted, remark) VALUES (%d, '%s', '%s', '%s', %d, %d, %d, '%s')" % (website_id, first_level_column, first_level_column_name, create_time, having_page, in_use, is_deleted, remark)
        # print(sql_sentence)
        return my_database_module.add_data(sql_sentence=sql_sentence)

    # 二级栏目存储进库
    @staticmethod
    def save_second_column(second_column_info):
        website_id = second_column_info["website_id"]
        first_level_column = second_column_info["first_level_column"]
        first_level_column_name = second_column_info["first_level_column_name"]
        second_level_column = second_column_info["second_level_column"]
        second_level_column_name = second_column_info["second_level_column_name"]
        create_time = second_column_info["create_time"]
        having_page = second_column_info["having_page"]
        in_use = second_column_info["in_use"]
        is_deleted = second_column_info["is_deleted"]
        if second_column_info["remark"]:
            remark = second_column_info["remark"]
        else:
            remark = 'NULL'
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_column_info( website_id, first_level_column, first_level_column_name, second_level_column, second_level_column_name, create_time, having_page, in_use, is_deleted, remark) VALUES (%d, '%s', '%s', '%s', '%s', '%s', %d, %d, %d, '%s')" % (website_id, first_level_column, first_level_column_name, second_level_column, second_level_column_name, create_time, having_page, in_use, is_deleted, remark)
        return my_database_module.add_data(sql_sentence=sql_sentence)

    # 三级栏目存储进库
    @staticmethod
    def save_third_column(third_column_info):
        website_id = third_column_info["website_id"]
        first_level_column = third_column_info["first_level_column"]
        first_level_column_name = third_column_info["first_level_column_name"]
        second_level_column = third_column_info["second_level_column"]
        second_level_column_name = third_column_info["second_level_column_name"]
        third_level_column = third_column_info["third_level_column"]
        third_level_column_name = third_column_info["third_level_column_name"]
        create_time = third_column_info["create_time"]
        having_page = third_column_info["having_page"]
        in_use = third_column_info["in_use"]
        is_deleted = third_column_info["is_deleted"]
        if third_column_info["remark"]:
            remark = third_column_info["remark"]
        else:
            remark = 'NULL'
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_column_info( website_id, first_level_column, first_level_column_name, second_level_column, second_level_column_name, third_level_column, third_level_column_name, create_time, having_page, in_use, is_deleted, remark) VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, %d, %d, '%s')" % (website_id, first_level_column, first_level_column_name, second_level_column, second_level_column_name, third_level_column, third_level_column_name, create_time, having_page, in_use, is_deleted, remark)
        return my_database_module.add_data(sql_sentence=sql_sentence)

    # 文章存储进数据库
    @staticmethod
    def save_article(article_info):
        website_id = article_info["website_id"]
        column_id = article_info["column_id"]
        url = article_info["url"]
        create_time = article_info["create_time"]
        having_page = article_info["having_page"]
        is_analized = article_info["is_analized"]
        is_deleted = article_info["is_deleted"]
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_article_info( website_id, column_id, url, create_time, having_page, is_analized, in_use, is_deleted) VALUES (%d, %d, '%s', '%s', %d, %d, 1, %d)" % (website_id, column_id, url, create_time, having_page, is_analized, is_deleted)
        print(sql_sentence)
        return my_database_module.add_data(sql_sentence=sql_sentence)

    # 获取所有一级栏目列表
    def get_all_first_column(self):
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT id, first_level_column,first_level_column_name FROM crawled_column_info WHERE website_id={website_id} AND is_deleted=1 AND second_level_column IS NULL AND third_level_column IS NULL AND first_level_column IS NOT NULL;".format(
                website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            first_column_list = []
            if my_data:
                for i in my_data:
                    first_column_list.append(
                        {"first_column_id": i[0], "first_column_url": i[1], "first_column_name": i[2]})
            return first_column_list
        except Exception as e:
            print(e)
            return None

    # 获取所有二级栏目列表
    def get_all_second_column(self):
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT id, first_level_column,first_level_column_name, second_level_column, second_level_column_name FROM crawled_column_info WHERE website_id={website_id} AND is_deleted=1 AND third_level_column IS NULL AND first_level_column IS NOT NULL AND second_level_column IS NOT NULL;".format(
                website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            second_column_list = []
            if my_data:
                for i in my_data:
                    second_column_list.append({"column_id": i[0],
                                               "first_column_url": i[1],
                                               "first_column_name": i[2],
                                               "second_level_column": i[3],
                                               "second_level_column_name": i[4]})
            return second_column_list
        except Exception as e:
            print(e)
            return None

    # 获取所有栏目列表
    def get_all_column(self):
        try:
            my_database_module = database_module.DatabaseModule()
            sql_sentence = "SELECT id, first_level_column,first_level_column_name, second_level_column, second_level_column_name, third_level_column, third_level_column_name, having_page FROM crawled_column_info WHERE website_id={website_id} AND is_deleted=1 AND in_use=1;".format(
                website_id=self.website_id)
            my_data = my_database_module.select_data(sql_sentence=sql_sentence)
            column_list = []
            if my_data:
                for i in my_data:
                    column_list.append({"column_id": i[0],
                                        "first_column_url": i[1],
                                        "first_column_name": i[2],
                                        "second_level_column": i[3],
                                        "second_level_column_name": i[4],
                                        "third_level_column": i[5],
                                        "third_level_column_name": i[6],
                                        "having_page": i[7]})
            return column_list
        except Exception as e:
            print(e)
            return None


if __name__ == '__main__':
    test_attach_handle = AttachHandle(website=None, website_id=1)
    test_data = test_attach_handle.get_all_first_column()
    print(test_data)
    a = [{'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/static/zzzb/zl-zzzb.html', 'create_time': '2023-06-01 16:04:29', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/zyxw/85597.html', 'create_time': '2023-06-01 16:05:52', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/shgfwxzj/queryyezhu/67617.html', 'create_time': '2023-06-01 16:09:15', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/index.html', 'create_time': '2023-06-01 16:10:42', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/ghjh/205310.html', 'create_time': '2023-06-01 16:12:08', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/jgld/208058.html', 'create_time': '2023-06-01 16:13:31', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/ywtb/208990.html', 'create_time': '2023-06-01 16:15:26', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/zyxw/85597.html', 'create_time': '2023-06-01 16:21:44', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/index.html', 'create_time': '2023-06-01 16:23:14', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/ghjh/index.html', 'create_time': '2023-06-01 16:25:39', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/jgld/index.html', 'create_time': '2023-06-01 16:27:06', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/ywtb/index.html', 'create_time': '2023-06-01 16:30:12', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/213879.html', 'create_time': '2023-06-01 16:32:20', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/213470.html', 'create_time': '2023-06-01 16:32:56', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/213468.html', 'create_time': '2023-06-01 16:33:34', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/213873.html', 'create_time': '2023-06-01 16:34:13', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/213875.html', 'create_time': '2023-06-01 16:34:54', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/213869.html', 'create_time': '2023-06-01 16:35:29', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/213871.html', 'create_time': '2023-06-01 16:36:09', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/212744.html', 'create_time': '2023-06-01 16:36:53', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/212742.html', 'create_time': '2023-06-01 16:37:36', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/211453.html', 'create_time': '2023-06-01 16:38:19', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209764.html', 'create_time': '2023-06-01 16:38:58', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209542.html', 'create_time': '2023-06-01 16:39:40', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209532.html', 'create_time': '2023-06-01 16:40:21', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209534.html', 'create_time': '2023-06-01 16:40:58', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209535.html', 'create_time': '2023-06-01 16:41:39', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209543.html', 'create_time': '2023-06-01 16:42:20', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209524.html', 'create_time': '2023-06-01 16:43:01', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209536.html', 'create_time': '2023-06-01 16:43:46', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209544.html', 'create_time': '2023-06-01 16:44:28', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/newxxgk/zcwj/gfxwj/209525.html', 'create_time': '2023-06-01 16:45:04', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/index/5319.html', 'create_time': '2023-06-01 16:45:40', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/index/558.html', 'create_time': '2023-06-01 16:46:24', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/index/64329.html', 'create_time': '2023-06-01 16:47:02', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}, {'website_id': 16, 'column_id': 196, 'url': 'https://www.shgjj.com/html/index/45263.html', 'create_time': '2023-06-01 16:47:41', 'having_page': 0, 'is_analized': 0, 'is_deleted': 1}]
    for i in a:
        test_attach_handle.save_article(article_info=i)
