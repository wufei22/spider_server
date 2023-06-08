import requests
import json
import cv2
import base64
import os
from app.main.public_method import *


def cv2_to_base64(image, img_type):
    my_type = "." + img_type
    data = cv2.imencode(my_type, image)[1]
    return base64.b64encode(data.tobytes()).decode('utf8')


class OpticalCharacterRecognitionModule(object):
    @staticmethod
    def recognize_character_main(img_path, img_type):
        crawled_logging = logging_module.CrawledLogging()
        try:
            local_path = os.path.abspath(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
            print(local_path)
            dic_path = os.path.join(local_path, "config.json")
            print(dic_path)
            with open(dic_path, "r") as f:
                dic_data = json.load(f)
            url = dic_data["dependencies"]["ocr_config"]["url"]
            img_data = {'images': [cv2_to_base64(cv2.imread(img_path), img_type)]}
            headers = {"Content-type": "application/json"}
            r = requests.post(url=url, headers=headers, data=json.dumps(img_data))
            crawled_logging.debug_log_main(message="识别图片信息")
            return r.json()["results"]["data"][0]["text"]
            # return "测试"
        except Exception as e:
            print(e)
            crawled_logging.error_log_main(message=e)
