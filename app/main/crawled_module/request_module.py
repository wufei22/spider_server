import requests
import re
from app.main.public_method import *
from urllib.robotparser import RobotFileParser


class RequestModule(object):
    def __init__(self):
        # # 1.获取代理ip
        # building_ip_pool = IP_pool.BuildingIPPool()
        # ip_dic = building_ip_pool.main_process()
        # ip = ip_dic["proxy_list"][0]
        # https_ip = "https://" + ip
        # http_ip = "http://" + ip
        # self.proxies = {"https": https_ip, "http": http_ip}
        # 2.获取user-agent
        get_user_agent = random_user_agent.RandomUserAgent()
        self.user_agent = get_user_agent.main_process()
        # 3.定制请求头
        get_header = customize_headers.CustomizeHeaders()
        self.header = get_header.customize_headers(self.user_agent)

    # 1.识别robots.txt协议
    def recognize_robot_agreement(self, robots_url):
        # 1.测试是否有robots.txt地址
        s = requests.session()
        s.keep_alive = False
        response = s.request(method="get",
                                    url=robots_url,
                                    # proxies=self.proxies,
                                    headers=self.header,
                                    verify=False)
        # print(response.status_code, type(response.status_code))
        # 2.若有，则分析该协议，检测其是否可以爬虫
        if response.status_code == 200:
            robots = RobotFileParser()
            robots.set_url(robots_url)
            robots.read()
            # print(robots.can_fetch('', robots_url))
            return robots.can_fetch('', robots_url)
        # 3. 若没有，则直接爬虫
        else:
            return True

    # 2.提取首页网址
    @staticmethod
    def analyze_url(url):
        url_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
        compiled_url = re.match(pattern=url_pattern, string=url).group()
        return compiled_url

    # 3.发送请求
    def send_request(self, robot_agreement, homepage_url):
        if robot_agreement:
            try:
                s = requests.session()
                s.keep_alive = False
                response = s.request(method="get",
                                     url=homepage_url,
                                     # proxies=self.proxies,
                                     headers=self.header,
                                     verify=False)
                if response.status_code == 200:
                    return response
                else:
                    print("请求失败")
                    return None
            except Exception as e:
                # print(e)
                raise e
        else:
            print("基于安全协议，该网站禁止爬虫")
            return None

    # 4.主程序
    def main_process(self, url):
        homepage_url = self.analyze_url(url)
        robots_url = homepage_url + "/robots.txt"
        robots_agreement = self.recognize_robot_agreement(robots_url=robots_url)
        return self.send_request(robot_agreement=robots_agreement, homepage_url=homepage_url)


if __name__ == '__main__':
    request_module = RequestModule()
    # request_module.recognize_robot_agreement(robots_url="https://www.bilibili.com/robots.txt")
    print(request_module.main_process(url="https://www.bilibili.com/").content.decode())
