import requests
import json
import cv2
import base64


def cv2_to_base64(image, img_type):
    my_type = "." + img_type
    data = cv2.imencode(my_type, image)[1]
    return base64.b64encode(data.tobytes()).decode('utf8')


class OpticalCharacterRecognitionModule(object):
    @staticmethod
    def recognize_character_main(img_path, img_type):
        try:
            img_data = {'images': [cv2_to_base64(cv2.imread(img_path), img_type)]}
            headers = {"Content-type": "application/json"}
            url = "http://127.0.0.1:9100/predict/chinese_ocr_db_crnn_mobile"
            r = requests.post(url=url, headers=headers, data=json.dumps(img_data))
            return r.json()["results"]["data"][0]["text"]
        except Exception as e:
            print(e)
            return None



