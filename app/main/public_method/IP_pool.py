import requests
import json
import os
import warnings
from urllib import parse

# 忽略告警
warnings.filterwarnings("ignore")


# 构建IP池
class BuildingIPPool(object):
    def __init__(self):
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        self.local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\..\.."))

    # 获取token
    def get_token(self):
        s = requests.session()
        s.keep_alive = False
        dic_path = os.path.join(self.local_path, "config.json")
        # print(dic_path)
        with open(dic_path, "r") as f:
            dic_data = json.load(f)
        # print(dic_data)
        get_token_url = dic_data["dependencies"]["ip_pool_web"] + dic_data["dependencies"]["get_token"]["url"]
        # print(get_token_url)
        get_token_method = dic_data["dependencies"]["get_token"]["method"]
        # print(get_token_method)
        get_token_content_type = dic_data["dependencies"]["get_token"]["content_type"]
        # print(get_token_content_type)
        get_token_payload = dic_data["dependencies"]["get_token"]["payload"]
        # print(get_token_payload)
        get_token_header = {"Content-Type": get_token_content_type}
        if get_token_method == "POST":
            if get_token_content_type == "application/x-www-form-urlencoded":
                get_token_payload = parse.urlencode(get_token_payload)
            else:
                get_token_payload = json.loads(get_token_payload)
        # print(get_token_payload)
        get_token_response = requests.request(method=get_token_method,
                                              url=get_token_url,
                                              headers=get_token_header,
                                              data=get_token_payload,
                                              verify=False)
        try:
            get_token_response = json.loads(get_token_response.content.decode())
            response_code = get_token_response["code"]
            # print(response_code, type(response_code))
            # print(get_token_response)
            if response_code == -1:
                print("获取token失败，缺少参数")
            elif response_code == -2:
                print("secret_id/secret_key参数错误")
            else:
                return get_token_response
        except Exception as e:
            print("获取token失败,接口未连通")
            raise e

    # 获取代理IP
    def get_ip(self, token_dic):
        s = requests.session()
        s.keep_alive = False
        dic_path = os.path.join(self.local_path, "config.json")
        # print(dic_path)
        with open(dic_path, "r") as f:
            dic_data = json.load(f)
        # print(dic_data)
        get_ip_url = dic_data["dependencies"]["ip_pool_web"] + dic_data["dependencies"]["get_ip"]["url"]
        # print(get_ip_url)
        get_ip_method = dic_data["dependencies"]["get_ip"]["method"]
        # print(get_ip_method)
        get_ip_content_type = dic_data["dependencies"]["get_ip"]["content_type"]
        # print(get_ip_content_type)
        get_ip_payload = dic_data["dependencies"]["get_ip"]["payload"]
        # print(get_ip_payload)
        get_ip_header = {"Content-Type": get_ip_content_type}
        if get_ip_method == "POST":
            if get_ip_content_type == "application/x-www-form-urlencoded":
                get_ip_payload = parse.urlencode(get_ip_payload)
            else:
                get_ip_payload = json.loads(get_ip_payload)
        get_ip_payload["signature"] = token_dic["data"]["secret_token"]
        # print(get_ip_payload)
        get_ip_response = requests.request(method=get_ip_method,
                                           url=get_ip_url,
                                           headers=get_ip_header,
                                           params=get_ip_payload,
                                           verify=False)
        try:
            get_ip_response = json.loads(get_ip_response.content.decode())
            response_code = get_ip_response["code"]
            # print(response_code, type(response_code))
            # print(get_ip_response)
            if response_code == -1:
                print("参数错误，请求无效")
            elif response_code == 1:
                print("今日提取余额已用尽")
            elif response_code == 2:
                print("订单已过期")
            elif response_code == 3:
                print("没有找到符合条件的代理")
            elif response_code == 4:
                print("账号尚未通过实名认证")
            elif response_code == -2:
                print("订单无效。如果刚下单，请耐心等待一会儿，1分钟内订单会自动生效。")
            elif response_code == -3:
                print("参数错误")
            elif response_code == -4:
                print("提取失败")
            elif response_code == -5:
                print("此订单不能提取私密代理")
            elif response_code == -6:
                print("调用此接口的IP不在您设置的IP白名单内")
            elif response_code == -51:
                print("超过最大IP调用")
            elif response_code == -16:
                print("订单已退款")
            elif response_code == -15:
                print("订单已过期")
            elif response_code == -14:
                print("订单被封禁，请联系客服处理")
            elif response_code == -13:
                print("订单已过期")
            elif response_code == -12:
                print("订单无效")
            elif response_code == -11:
                print("订单尚未支付")
            else:
                print(get_ip_response["data"])
                return get_ip_response["data"]
        except Exception as e:
            print("获取token失败,接口未连通")
            raise e

    # 获取IP主程序
    def main_process(self):
        token_dic = self.get_token()
        ip_dic = self.get_ip(token_dic=token_dic)
        return ip_dic


if __name__ == "__main__":
    building_ip_pool = BuildingIPPool()
    # print(building_ip_pool.local_path)
    # building_ip_pool.get_token()
    building_ip_pool.main_process()
