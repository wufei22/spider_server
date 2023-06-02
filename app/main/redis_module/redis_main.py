import time

import redis
import os
import json
from multiprocessing import Pool


class RedisModule(object):

    def __init__(self):
        local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\..\.."))
        dic_path = os.path.join(local_path, "config.json")
        with open(dic_path, "r") as f:
            dic_data = json.load(f)
        self.config_dic = dic_data["dependencies"]["redis_config"]

    def publish_theme(self, channel_name, send_message):
        conn = redis.Redis(host=self.config_dic["ip"],
                           port=self.config_dic["port"])
        conn.publish(channel=channel_name, message=send_message)

    def subscribe_theme(self, channel_name):
        conn = redis.Redis(host=self.config_dic["ip"],
                           port=self.config_dic["port"])
        my_pubsub = conn.pubsub()
        my_pubsub.subscribe(channel_name)
        msg_stream = my_pubsub.listen()
        # print(msg_stream)
        for msg in msg_stream:
            # print(msg["data"], type(msg["data"]))
            if isinstance(msg["data"], bytes):
                # print(123456798)
                if json.loads(msg["data"]) == 0:
                    return True
            # return msg["data"]
            # print(json.loads(msg))
        #     if msg["type"] == "message":
        #         print(str(msg["channel"], encoding="utf-8") + ":" + str(msg["data"], encoding="utf-8"))
        #     elif msg["type"] == "subscribe":
        #         print(str(msg["channel"], encoding="utf-8"), '订阅成功')

    # def quit_redis(self):
    #     self.conn.close()


if __name__ == '__main__':
    test_redis_module = RedisModule()
    test_pool = Pool()
    test_pool.apply_async(test_redis_module.publish_theme, args=("python_test", 1,))
    test_pool.apply_async(test_redis_module.subscribe_theme, args=("python_test",))
    time.sleep(2)
    test_pool.apply_async(test_redis_module.publish_theme, args=("python_test", 1,))
    time.sleep(3)
    test_pool.apply_async(test_redis_module.publish_theme, args=("python_test", 1,))
    # test_pool.terminate()
    # time.sleep(4)
    test_pool.close()
    test_pool.join()
    # time.sleep(4)
    # test_pool.terminate()
    # test_redis_module.quit_redis()
    # test_redis_module.publish_theme(channel_name="python_test", send_message=json.dumps({"test": 1}))
    # test_redis_module.subscribe_theme(channel_name="python_test")
