import re
import bs4
from app.main.crawled_module import selenium_module, database_module, handle_attachment_module


class ArticleAnalyzeModule(object):
    def __init__(self, article_info):
        """
        初始化方法
        :param article_info: {"id": id, "website_id": website_id, "website_url":website_url, "column_id": column_id,
                              "url": url, "having_page": 0/1}
        """
        self.article_info = article_info

    # 获取文章页面资源
    def get_article_html(self):
        if self.article_info["having_page"] == 0:
            my_selenium_module = selenium_module.SeleniumModule()
            html_src = my_selenium_module.loading_html(input_url=self.article_info["url"])
            my_selenium_module.quit_browser()
            html_list = [html_src]
        else:
            my_selenium_module = selenium_module.SeleniumModule()
            html_list = my_selenium_module.loading_article_page_html(article_id=self.article_info["id"],
                                                                     article_url=self.article_info["url"])
        return html_list

    # 获取文章标题
    @staticmethod
    def get_article_title(html_src):
        my_soup = bs4.BeautifulSoup(html_src, "lxml")
        title_list = my_soup.find_all("title")
        # print(title_list)
        if title_list:
            # print(title_list[0].text)
            return title_list[0].text

    # 获取发文单位
    def get_article_unit(self):
        my_database = database_module.DatabaseModule()
        sql_sentence = "SELECT `name` FROM crawled_website_info WHERE id={id}".format(
            id=self.article_info["website_id"])
        my_data = my_database.select_data(sql_sentence=sql_sentence)
        if my_data:
            return my_data[0][0]

    # 获取官方发布日期
    @staticmethod
    def get_article_publish_date(html_src):
        my_soup = bs4.BeautifulSoup(html_src, "lxml")
        meta_list = my_soup.find_all("meta")
        # print(meta_list)
        for i in meta_list:
            if "content" in i.attrs:
                meta_content = i["content"]
                date_pattern = "^\d{4}-\d{1,2}-\d{1,2}"
                if re.match(pattern=date_pattern, string=meta_content):
                    # print(meta_content)
                    return meta_content

    # 获取官方生效日期
    @staticmethod
    def get_article_effective_date():
        return "1999-04-23 15:47:23"

    # 获取文章类别
    @staticmethod
    def get_article_type():
        return 1

    # 判断文章是否为全国性政策的文件
    def get_article_effective_boundary(self):
        my_database = database_module.DatabaseModule()
        sql_sentence = "SELECT region_id FROM crawled_website_info WHERE id={id}".format(
            id=self.article_info["website_id"])
        my_data = my_database.select_data(sql_sentence=sql_sentence)
        if my_data:
            if my_data[0][0] != 0:
                return 2
            else:
                return 1
        else:
            return 2

    # 获取文章内容
    @staticmethod
    def get_article_text(html_list):
        article_text = ""
        for html_src in html_list:
            my_soup = bs4.BeautifulSoup(html_src, "lxml")
            div_list = my_soup.find_all("div")
            text_div = bs4.BeautifulSoup("", "lxml")
            for i in div_list:
                # print(type(i))
                # print(i.find_all("p"))
                if len(i.find_all("p")) > len(text_div.find_all("p")):
                    text_div = i
            # print(text_div)
            p_list = text_div.find_all("p")
            for _ in p_list:
                # print(_)
                # print(_.text)
                article_text += str(_)
                article_text += "\n"
            # print(article_text)
        return article_text

    # 文章解析结果存储进数据库
    @staticmethod
    def save_article_info(article_info):
        field_list = []
        my_id = article_info["id"]
        field_list.append(my_id)
        url = article_info["url"]
        field_list.append(url)
        if article_info["title"]:
            title = article_info["title"]
        else:
            title = None
        field_list.append(title)
        if article_info["article_government_unit"]:
            article_government_unit = article_info["article_government_unit"]
        else:
            article_government_unit = None
        field_list.append(article_government_unit)
        if article_info["article_publish_date"]:
            article_publish_date = article_info["article_publish_date"]
        else:
            article_publish_date = None
        field_list.append(article_publish_date)
        having_attachment = article_info["having_attachment"]
        field_list.append(having_attachment)
        if article_info["effective_date"]:
            effective_date = article_info["effective_date"]
        else:
            effective_date = None
        field_list.append(effective_date)
        if article_info["article_category"]:
            article_category = article_info["article_category"]
        else:
            article_category = 0
        field_list.append(article_category)
        is_national = article_info["is_national"]
        field_list.append(is_national)
        if article_info["article_text"]:
            article_text = article_info["article_text"]
        else:
            article_text = None
        field_list.append(article_text)
        print(field_list)
        my_database = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_analized_article_info( id, url, title, article_government_unit, article_publish_date, having_attachment, effective_date, article_category, is_national, article_text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        print(sql_sentence)
        return my_database.add_data(sql_sentence=sql_sentence, field_list=field_list)

    # 更新文章信息表字段，将已分析的文章分析状态改为已分析
    def update_article_state(self):
        field_list = []
        article_id = self.article_info["id"]
        my_database_module = database_module.DatabaseModule()
        field_list.append(article_id)
        sql_sentence = "UPDATE crawled_article_info SET is_analized=1 WHERE id=%s"
        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)

    # 文章处理主程序
    def article_analyze_main(self):
        # 1.获取页面资源
        html_list = self.get_article_html()
        # 2.获取文章标题
        article_title = self.get_article_title(html_src=html_list[0])
        # 3.获取发文单位
        article_unit = self.get_article_unit()
        # 4.获取官方发布日期
        article_publish_date = self.get_article_publish_date(html_src=html_list[0])
        # 5.获取官方生效日期
        article_effective_date = self.get_article_effective_date()
        # 6.获取文章类别
        article_type = self.get_article_type()
        # 7.判断文章是否为全国性政策的文件
        article_effective_boundary = self.get_article_effective_boundary()
        # 8.获取文章内容
        article_text = self.get_article_text(html_list=html_list)
        # 9.附件处理
        my_handle_attachment_module = handle_attachment_module.HandleAttachmentModule(article_info={
            "website_url": self.article_info["website_url"],
            "website_id": self.article_info["website_id"],
            "column_id": self.article_info["column_id"],
            "article_id": self.article_info["id"],
            "article_url": self.article_info["url"]})
        if my_handle_attachment_module.if_having_attachment(html_list[0]):
            having_attachment = 1
        else:
            having_attachment = 0
        my_handle_attachment_module.handle_attachment_main(html_src=html_list[0])
        # 10.文章解析结果存储进数据库
        article_info = {"id": self.article_info["id"],
                        "url": self.article_info["url"],
                        "title": article_title,
                        "article_government_unit": article_unit,
                        "article_publish_date": article_publish_date,
                        "having_attachment": having_attachment,
                        "effective_date": article_effective_date,
                        "article_category": article_type,
                        "is_national": article_effective_boundary,
                        "article_text": article_text}
        self.save_article_info(article_info=article_info)
        # 11.更新字段
        self.update_article_state()


if __name__ == '__main__':
    test_article_info = {"id": 148,
                         "website_id": 1,
                         "website_url": "http://stic.sz.gov.cn",
                         "column_id": 32,
                         "url": "http://stic.sz.gov.cn/xxgk/zcfg/zcjd/content/post_9891179.html",
                         "having_page": 0,
                         "is_analized": 0}
    test_article_analyze_module = ArticleAnalyzeModule(article_info=test_article_info)
    test_article_analyze_module.article_analyze_main()
