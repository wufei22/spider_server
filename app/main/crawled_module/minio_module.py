import os
import json
from minio import Minio


class MinioModule(object):
    def __init__(self):
        local_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
        dic_path = os.path.join(local_path, "config.json")
        with open(dic_path, "r") as f:
            dic_data = json.load(f)
        config_dic = dic_data["dependencies"]["minio_config"]
        end_point = str(config_dic["ip"]) + ":" + str(config_dic["port"])
        self.client = Minio(endpoint=end_point,
                            access_key=config_dic["username"],
                            secret_key=config_dic["password"],
                            secure=False)

    def upload_file(self, bucket_name, object_name, data, length):
        if self.client.bucket_exists(bucket_name):
            self.client.put_object(bucket_name=bucket_name,
                                   object_name=object_name,
                                   data=data,
                                   length=length)
            url = self.client.presigned_get_object(bucket_name, object_name)
            print(url)
        else:
            pass


if __name__ == '__main__':
    test_minio_module = MinioModule()
    print(test_minio_module.client)
    with open("test.png", "rb") as f:
        bytes_length = os.path.getsize("test.png")
    test_minio_module.upload_file(bucket_name="crawled",
                                  object_name="test.png",
                                  data=f,
                                  length=bytes_length)


