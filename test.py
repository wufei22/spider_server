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


meta_content = "2023-06-02 23∶06"
date_pattern = "^\d{4}-\d{1,2}-\d{1,2}"
print(re.search(pattern=date_pattern, string=meta_content).group())

