import re
import time
import os
import datetime
from app.main.crawled_module import request_module, database_module


class LoadingImg(object):
    def __init__(self, website, website_id, a_list, current_page=None, current_page_id=None):
        """
        下载图片模块的初始化方法
        :param website: 主网站首页地址，注意结尾是没有/
        :param website_id: 主网站id
        :param a_list: beautiful soup解析的a标签列表
        :param current_page: 当前页面的url地址，默认为none
        :param current_page_id: 当前页面的id
        """
        self.website = website
        self.website_id = str(website_id)
        self.current_page_id = current_page_id
        self.current_page = current_page
        self.a_list = a_list
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        self.local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\..\.."))

    # 筛选a标签列表，如果当前a标签没有栏目文字，只有src，筛选出来添加进新列表
    def filter_tabel(self):
        filter_tabel_list = []
        for i in self.a_list:
            if not i.text:
                # print(i)
                if "title" not in i.attrs:
                    # print(i)
                    if "alt" not in i.attrs:
                        # print(i)
                        if "href" in i.attrs:
                            if i.find("img"):
                                filter_tabel_list.append({"href": i["href"], "src": i.find("img")["src"]})
        return filter_tabel_list

    # 对过滤后的a标签进行数据清洗
    def data_cleaning(self, filter_tabel_list):
        # print(filter_tabel_list)
        cleaning_table_list = []
        filter_tabel_list_new = []
        for i in filter_tabel_list:
            # print(i)
            suffix_pattern = re.compile("(jpg$)|(jpeg$)|(png$)|(gif$)")
            compiled_url = re.search(pattern=suffix_pattern, string=i["src"])
            if compiled_url:
                i["img_type"] = compiled_url.group()
                filter_tabel_list_new.append(i)
        for _ in filter_tabel_list_new:
            head_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
            compiled_url = re.match(pattern=head_pattern, string=_["src"])
            if not compiled_url:
                if _["src"][0] == ".":
                    _["src"] = _["src"][1::]
                _["src"] = self.website + _["src"]
            cleaning_table_list.append(_)
        return cleaning_table_list

    # 尝试根据src下载图片
    def downloading_img(self, img_url, img_type):
        my_request_module = request_module.RequestModule()
        if self.current_page:
            current_url = self.current_page
        else:
            current_url = self.website
        img_data = my_request_module.get_img(current_url=current_url, img_url=img_url)
        # 判断是否创建文件夹，若没有，则创建文件夹，文件夹目录为./column_img/主网站id/当前页面id/当前日期
        if img_data:
            if self.current_page:
                folder = self.local_path + "/column_img/" + str(self.website_id) + "/" + str(self.current_page_id) + "/" + \
                         time.strftime("%Y_%m_%d", time.localtime())
            else:
                folder = self.local_path + "/column_img/" + str(self.website_id) + "/" + \
                         time.strftime("%Y_%m_%d", time.localtime())
            if not os.path.exists(folder):
                os.makedirs(folder)
            img_path = folder + "/" + str(time.time()).replace(".", "") + "." + img_type
            with open(img_path, 'wb') as f:
                f.write(img_data)
            return img_path

    # 将下载的图片信息存储进数据库
    @staticmethod
    def save_img(img_info):
        field_list = []
        website_id = img_info["website_id"]
        if img_info["img_path"]:
            img_path = img_info["img_path"]
        else:
            img_path = 'NULL'
        url = img_info["url"]
        create_time = img_info["create_time"]
        is_deleted = img_info["is_deleted"]
        my_database_module = database_module.DatabaseModule()
        field_list.append(website_id)
        field_list.append(img_path)
        field_list.append(url)
        field_list.append(create_time)
        field_list.append(is_deleted)
        sql_sentence = "INSERT INTO crawled_column_img_info( website_id, img_path, url, create_time, is_deleted) VALUES (%s, %s, %s, %s, %s)"
        # print(sql_sentence)
        return my_database_module.add_data(sql_sentence=sql_sentence, field_list=field_list)

    # 图像资源处理主程序
    def loading_img_main(self):
        # 1.过滤a标签
        filter_tabel_list = self.filter_tabel()
        # print(filter_tabel_list)
        # 2.对过滤后的a标签进行数据清洗
        cleaning_table_list = self.data_cleaning(filter_tabel_list=filter_tabel_list)
        # print(cleaning_table_list)
        # 3.下载图片资源
        for i in cleaning_table_list:
            # print(i)
            img_path = self.downloading_img(img_url=i["src"], img_type=i["img_type"])
            i["img_path"] = img_path
            # 4.存储进数据库
            img_info = {"website_id": self.website_id,
                        "img_path": img_path,
                        "url": i["href"],
                        "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "is_deleted": 1}
            self.save_img(img_info=img_info)
        return cleaning_table_list


if __name__ == '__main__':
    test_website = "http://zwgk.changchun.gov.cn"
    test_website_id = 1
    # test_selenium = selenium_module.SeleniumModule()
    # html_src = test_selenium.loading_html(input_url=test_website)
    # test_soup = bs4.BeautifulSoup(html_src, "lxml")
    # test_a_list = test_soup.find_all("a")
    # test_loading_img = LoadingImg(website=test_website, website_id=test_website_id, a_list=test_a_list)
    # a = test_loading_img.loading_img_main()
    # print(a)
