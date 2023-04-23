class CustomizeHeaders(object):

    # 爬虫爬取数据的函数
    @staticmethod
    def customize_headers(user_agent):
        spider_header = {"accept": "application/json, text/javascript, */*; q=0.01",
                         "accept-encoding": "gzip, deflate, br",
                         "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                         "user-agent": user_agent}
        return spider_header


if __name__ == '__main__':
    print(CustomizeHeaders.customize_headers(user_agent=1))
