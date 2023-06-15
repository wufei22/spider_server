import json
import flask
import os
from flask import request, Blueprint
from app.main.crawled_module import *
from concurrent.futures import ThreadPoolExecutor
from flask_kafka.consumer import KafkaConsumer

crawled = Blueprint('crawled', __name__)
# realpath方法即使是在其他地方调用也可以获取真实的绝对路径
local_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
dic_path = os.path.join(local_path, "config.json")
with open(dic_path, "r") as f:
    dic_data = json.load(f)
config_dic = dic_data["dependencies"]["kafka_config"]
bootstrap_servers = config_dic["ip"] + ":" + config_dic["port"]


# 判断url是否为首页的接口
@crawled.route('/isHomepage', methods=["GET", "POST"])
def is_homepage():
    if request.method == "POST":
        param_dic = flask.request.get_json()
        # print(param_dic)
        if "website_url" in param_dic:
            website_url = param_dic["website_url"]
            my_main_crawled_process = main_crawled.MainCrawledProcess()
            if my_main_crawled_process.check_is_homepage(website_url):
                return json.dumps({"code": '200', "message": "ok", "data": {"is_homepage": True}}, ensure_ascii=False)
            else:
                return json.dumps({"code": '200', "message": "ok", "data": {"is_homepage": False}}, ensure_ascii=False)
        else:
            return json.dumps({"code": "401", "message": "缺少参数"}, ensure_ascii=False)
    else:
        return json.dumps({"code": "403", "message": "仅支持post方法"}, ensure_ascii=False)


# 分析栏目的接口
@crawled.route('/getColumn', methods=["GET", "POST"])
def get_column():
    if request.method == "GET":
        with KafkaConsumer(config_dic["topic"], bootstrap_servers=bootstrap_servers) as consumer:
            for message in consumer:
                key = message.key.decode('utf-8')
                # print(key)
                value = message.value.decode('utf-8')
                # print(value)
                if value:
                    # 执行异步任务的逻辑
                    # 在这里添加你的异步任务处理代码，根据需要进行相应的操作
                    # 例如，可以使用Celery或类似的异步任务队列来处理任务
                    executor = ThreadPoolExecutor(1)
                    my_main_crawled_process = main_crawled.MainCrawledProcess()
                    executor.submit(my_main_crawled_process.grading_column, int(value))
                    consumer.close()
                    return json.dumps({"code": "200", "message": "ok"}, ensure_ascii=False)
            consumer.close()
            return json.dumps({"code": "400", "message": "未消费kafka消息"}, ensure_ascii=False)
    else:
        return json.dumps({"code": "403", "message": "仅支持post方法"}, ensure_ascii=False)


# 检测xpath添加是否正确的接口
@crawled.route('/checkXpath', methods=["GET", "POST"])
def check_xpath():
    if request.method == "POST":
        param_dic = flask.request.get_json()
        if "input_url" in param_dic and "xpath" in param_dic:
            input_url = param_dic["input_url"]
            xpath = param_dic["xpath"]
            my_main_crawled_process = main_crawled.MainCrawledProcess()
            if my_main_crawled_process.check_xpath_config(input_url=input_url, xpath=xpath):
                return json.dumps({"code": '200', "message": "ok", "data": {"xpath_config": True}}, ensure_ascii=False)
            else:
                return json.dumps({"code": '200', "message": "ok", "data": {"xpath_config": False}}, ensure_ascii=False)
        else:
            return json.dumps({"code": "401", "message": "缺少参数"}, ensure_ascii=False)
    else:
        return json.dumps({"code": "403", "message": "仅支持post方法"}, ensure_ascii=False)


# 手动执行爬虫任务的接口
@crawled.route('/startTask', methods=["GET", "POST"])
def start_task():
    if request.method == "GET":
        my_main_crawled_process = main_crawled.MainCrawledProcess()
        if my_main_crawled_process.is_crawled():
            executor = ThreadPoolExecutor(1)
            executor.submit(my_main_crawled_process.multiprocessing_task)
            return json.dumps({"code": "200", "message": "ok"}, ensure_ascii=False)
        else:
            return json.dumps({"code": "400", "message": "已有爬虫任务在执行"}, ensure_ascii=False)
    else:
        return json.dumps({"code": "403", "message": "仅支持get方法"}, ensure_ascii=False)


# 中止爬虫任务的接口
@crawled.route('/endTask', methods=['GET', "POST"])
def end_task():
    if request.method == "GET":
        my_main_crawled_process = main_crawled.MainCrawledProcess()
        my_main_crawled_process.terminate_the_task()
        return json.dumps({"code": '200', "message": "ok", "data": {"end_task": True}}, ensure_ascii=False)
    else:
        return json.dumps({"code": "403", "message": "仅支持get方法"}, ensure_ascii=False)


# 手动执行爬虫任务的接口
@crawled.route('/startGrading', methods=["GET", "POST"])
def start_grading():
    if request.method == "POST":
        param_dic = flask.request.get_json()
        executor = ThreadPoolExecutor(1)
        # print(param_dic)
        if "website_id" in param_dic:
            website_id = param_dic["website_id"]
            my_main_crawled_process = main_crawled.MainCrawledProcess()
            executor.submit(my_main_crawled_process.multiprocessing_grading, website_id)
            return json.dumps({"code": "200", "message": "ok"}, ensure_ascii=False)
        else:
            return json.dumps({"code": "401", "message": "缺少参数"}, ensure_ascii=False)
    else:
        return json.dumps({"code": "403", "message": "仅支持post方法"}, ensure_ascii=False)


if __name__ == '__main__':
    print(local_path)
    print(config_dic)
