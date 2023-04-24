import bs4
import requests


class AnalyzingModule(object):
    def __init__(self, response):
        self.response = response

    # 1.判断是否有搜索框
    def search_analyze(self):
        try:
            html_data = self.response.content.decode()
        except Exception as e:
            raise e
        soup = bs4.BeautifulSoup(html_data, "lxml")
        # print(soup.body)
        # print(soup.find("form").descendants)
        for child in soup.find("form").descendants:
            # print(child.name)
            if child.name == "input":
                try:
                    input_class = child["class"]
                    print(input_class)
                except Exception as e:
                    # print(e)
                    pass
            elif child.name == "button":
                try:
                    button_class = child["class"]
                    print(button_class)
                except Exception as e:
                    # print(e)
                    pass
        if soup.find("form"):
            return soup.find("form")
        else:
            return None

    # 2.在搜索框中输入内容


if __name__ == '__main__':
    s = requests.session()
    s.keep_alive = False
    my_response = s.get(url="http://hsa.zs.gov.cn/")
    analyzing_module = AnalyzingModule(response=my_response)
    analyzing_module.search_analyze()
