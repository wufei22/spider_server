import time
import datetime
import bs4
import re
import requests
import urllib3
import base64
import json
import os
from multiprocessing import Pool
from selenium import webdriver
from app.main.crawled_module import selenium_module, database_module
#
# urls = [
#     "http://www.python.org",
#     "http://www.python.org/about/",
#     "http://www.onlamp.com/pub/a/python/2003/04/17/metaclasses.html",
#     "http://www.python.org/doc/",
#     "http://www.python.org/download/",
#     "http://www.python.org/getit/",
#     "http://www.python.org/community/",
#     "https://wiki.python.org/moin/",
# ]


# def get_status_code(url):
#     resp = requests.get(url)
#     print("url:{}\ncode:{}\n{}".format(url, resp.status_code, "-" * 100))


if __name__ == "__main__":
    # 维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
    # p = Pool(10)
    # for url in urls:
    #     # 异步开启进程, 非阻塞型, 能够向池中添加进程而不等待其执行完毕就能再次执行循环
    #     p.apply_async(func=get_status_code, args=(url,))
    # print("Waiting for all subprocesses done...")
    # p.close()  # 关闭pool, 则不会有新的进程添加进去
    # p.join()  # 必须在join之前close, 然后join等待pool中所有的进程执行完毕
    # print('All subprocesses done.')
    a = None
    b = None
    test_database_module = database_module.DatabaseModule()
    sql_sentence = "INSERT INTO crawled_website_info (`name`, url, create_time, update_time, region_id, execution_status, in_use, is_deleted, remark) VALUES('测试', 'www.baidu.com', '2023-05-22 22:19:05', %s, 0, 0, 0, 0, %s)"
    test_database_module.add_data(sql_sentence=sql_sentence, field_list=[a, b])
