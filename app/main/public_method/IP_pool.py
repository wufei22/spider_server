import requests
import time
import re
import json
import os
import random
from bs4 import BeautifulSoup


# 构建IP池
class BuildingIPPool(object):
    def __init__(self):
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        self.local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\.."))



if __name__ == "__main__":
    pass