from app import app
import os
import sys


# 1.获取当前绝对路径
filepath = os.path.realpath(__file__)
# print(os.path.dirname(filepath))
sys.path.append(os.path.dirname(filepath))


# 定义开启服务的主函数
def server_main():
    app.debug = False
    app.config["JSON_AS_ASCII"] = False
    app.run(host='0.0.0.0', port=5080, threaded=True)


if __name__ == '__main__':
    server_main()
