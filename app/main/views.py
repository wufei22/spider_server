import json
import flask
from flask import request, Blueprint
from multiprocessing import process
from app.main.crawled_module import *
from concurrent.futures import ThreadPoolExecutor

crawled = Blueprint('crawled', __name__)


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
    if request.method == "POST":
        param_dic = flask.request.get_json()
        if "website_id" in param_dic:
            website_id = param_dic["website_id"]
            my_main_crawled_process = main_crawled.MainCrawledProcess()
            my_main_crawled_process.grading_column(website_id=website_id)
        else:
            return json.dumps({"code": "401", "message": "缺少参数"}, ensure_ascii=False)
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
        my_main_crawled_process.multiprocessing_task()
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
