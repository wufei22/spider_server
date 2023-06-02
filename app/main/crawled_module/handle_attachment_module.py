import bs4
import re
import os
import time
import datetime
from app.main.crawled_module import database_module, selenium_module, request_module


class HandleAttachmentModule(object):
    """
    分析处理附件模块
    """

    def __init__(self, article_info):
        """
        初始化方法
        :param article_info: {"website_url": "http://hrss.sz.gov.cn",
                              "website_id": website_id,
                              "column_id": column_id,
                              "article_id": article_id,
                              "article_url": url}
        """
        self.article_info = article_info
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        self.local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\..\.."))

    # 判断页面是否有附件信息
    @staticmethod
    def if_having_attachment(html_src):
        # my_soup = bs4.BeautifulSoup(html_src, "lxml")
        # a_list = my_soup.find_all("a")
        my_pattern = "(\.txt)|(\.doc)|(\.docx)|(\.xls)|(\.xlsx)|(\.pptx)|(\.ppt)|(\.pdf)|(\.zip)|(\.rar)"
        # print(re.search(pattern=my_pattern, string=html_src))
        if re.search(pattern=my_pattern, string=html_src):
            return True

    # 寻找并判断附件信息,进行数据清洗，并返回列表
    def find_attachment_link(self, html_src):
        attachment_list = []
        final_list = []
        my_soup = bs4.BeautifulSoup(html_src, "lxml")
        a_list = my_soup.find_all("a")
        for i in a_list:
            if "href" in i.attrs:
                suffix_pattern = "(txt$)|(doc$)|(docx$)|(xls$)|(xlsx$)|(pptx$)|(ppt$)|(pdf$)|(zip$)|(rar$)"
                compiled_url = re.search(pattern=suffix_pattern, string=i["href"])
                if compiled_url:
                    if i.text:
                        attachment_list.append({"name": i.text,
                                                "href": i["href"],
                                                "attachment_type": compiled_url.group()})
                    else:
                        attachment_list.append({"name": None,
                                                "href": i["href"],
                                                "attachment_type": compiled_url.group()})
        if attachment_list:
            for _ in attachment_list:
                head_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
                compiled_url = re.search(pattern=head_pattern, string=_["href"])
                if not compiled_url:
                    if _["href"][0] == ".":
                        _["href"] = _["href"][1::]
                    _["href"] = self.article_info["website_url"] + _["href"]
                final_list.append(_)
        # print(final_list)
        return final_list

    # 尝试根据href下载链接
    def downloading_attachment(self, attachment_url, attachment_type):
        my_request_module = request_module.RequestModule()
        attachment_data = my_request_module.get_img(current_url=self.article_info["article_url"],
                                                    img_url=attachment_url)
        # 判断是否创建文件夹，若没有，则创建文件夹，文件夹目录为./attachment/主网站id/当前页面id/当前日期
        if attachment_data:
            folder = self.local_path + "/attachment/" + str(self.article_info["website_id"]) + "/" + str(
                self.article_info["column_id"]) + "/" + time.strftime("%Y_%m_%d", time.localtime())
            if not os.path.exists(folder):
                os.makedirs(folder)
            img_path = folder + "/" + str(time.time()).replace(".", "") + "." + attachment_type
            with open(img_path, 'wb') as f:
                f.write(attachment_data)
            return img_path

    # 将下载的附件信息存储进数据库
    @staticmethod
    def save_attachment(attachment_info):
        field_list = []
        my_database_module = database_module.DatabaseModule()
        article_id = attachment_info["article_id"]
        if attachment_info["name"]:
            name = attachment_info["name"]
        else:
            name = None
        if attachment_info["path"]:
            path = attachment_info["path"]
        else:
            path = None
        create_time = attachment_info["create_time"]
        is_deleted = attachment_info["is_deleted"]
        field_list.append(article_id)
        field_list.append(name)
        field_list.append(path)
        field_list.append(create_time)
        field_list.append(is_deleted)
        sql_sentence = "INSERT INTO crawled_attachment_info( article_id, `name`, `path`, create_time, is_deleted) VALUES (%d, %s, %s, %s, %d)"
        # print(sql_sentence)
        return my_database_module.add_data(sql_sentence=sql_sentence, field_list=field_list)

    # 处理附件主程序
    def handle_attachment_main(self, html_src):
        # 1.判断页面是否有附件信息
        if self.if_having_attachment(html_src):
            # 2.寻找并判断附件信息,进行数据清洗，并返回列表
            attachment_info_list = self.find_attachment_link(html_src)
            # print(attachment_info_list)
            if attachment_info_list:
                # 3.根据href下载链接
                for i in attachment_info_list:
                    # print(i)
                    attachment_path = self.downloading_attachment(attachment_url=i["href"],
                                                                  attachment_type=i["attachment_type"])
                    i["attachment_path"] = attachment_path
                    # 4.存储进数据库
                    attachment_info = {"article_id": self.article_info["article_id"],
                                       "name": i["name"],
                                       "path": attachment_path,
                                       "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       "is_deleted": 1}
                    self.save_attachment(attachment_info=attachment_info)
                return attachment_info_list


if __name__ == '__main__':
    url = "http://gjj.beijing.gov.cn/web/zwgk61/xwdt/_300666/10998422/index.html"
    test_selenium_module = selenium_module.SeleniumModule()
    test_html = test_selenium_module.loading_html(input_url=url)
    test_selenium_module.quit_browser()
    test_article_info = {"website_url": "http://gjj.beijing.gov.cn",
                         "website_id": 2,
                         "column_id": 2,
                         "article_id": 2,
                         "article_url": url}
    test_handle_attachment_module = HandleAttachmentModule(article_info=test_article_info)
    test_handle_attachment_module.handle_attachment_main(html_src=test_html)
