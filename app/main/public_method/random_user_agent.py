import random
import os
import json


class RandomUserAgent(object):
    def __init__(self):
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        self.local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\..\.."))

    # 返回随机的user-agent
    def main_process(self):
        user_agent_file_path = os.path.join(self.local_path, r"app\static\user_agent.json")
        with open(user_agent_file_path, "r") as f:
            user_agent_dic = json.load(f)
            # print(user_agent_dic)
        user_agent_list = user_agent_dic["user_agent_list"]
        user_agent = user_agent_list[random.randint(0, (len(user_agent_list) - 1))]
        # print(user_agent)
        return user_agent


if __name__ == '__main__':
    random_user_agent = RandomUserAgent()
    random_user_agent.main_process()
