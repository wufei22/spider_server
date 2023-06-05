import random
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


def test_task(task_id):
    print("任务：%d 正在执行中\n" % task_id)
    time.sleep(random.randint(5, 8))
    print("任务：%d 执行完毕\n" % task_id)


if __name__ == "__main__":
    test_po = Pool(5)
    test_task_list = [1, 2, 3, 4, 5]
    for i in test_task_list:
        test_po.apply_async(func=test_task, args=(i,))
    test_po.close()
    test_po.join()
    print("这是主进程，测试等待")
