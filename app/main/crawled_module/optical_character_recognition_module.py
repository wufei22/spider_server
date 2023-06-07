import requests
import json
import cv2
import base64
import os
import logging
from app.main.public_method import *


def cv2_to_base64(image, img_type):
    my_type = "." + img_type
    data = cv2.imencode(my_type, image)[1]
    return base64.b64encode(data.tobytes()).decode('utf8')


class OpticalCharacterRecognitionModule(object):
    @staticmethod
    def recognize_character_main(img_path, img_type):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="DEBUG")
        try:
            local_path = os.path.abspath(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
            # print(local_path)
            dic_path = os.path.join(local_path, "config.json")
            # print(dic_path)
            with open(dic_path, "r") as f:
                dic_data = json.load(f)
            url = dic_data["dependencies"]["ocr_config"]["url"]
            img_data = {'images': [cv2_to_base64(cv2.imread(img_path), img_type)]}
            headers = {"Content-type": "application/json"}
            r = requests.post(url=url, headers=headers, data=json.dumps(img_data))
            crawled_logger.debug(msg="识别图片信息")
            logging.shutdown()
            return r.json()["results"]["data"][0]["text"]
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()
