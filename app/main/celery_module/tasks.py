import time

from celery import Celery

# 通过使用本机redis且没有密码，使用远程redis有密码格式为
# 'redis://:密码@ip:6379/1'
# redis://:username:passowrd@host:port/db
broker = 'redis://127.0.0.1:6379/1'  # 任务储存
backend = 'redis://127.0.0.1:6379/2'  # 结果存储，执行完之后结果放在这

# 创建出app对象
app = Celery(__name__, broker=broker, backend=backend)


# 任务通过装饰器@app.task进行装饰
@app.task(name="func")
def func(x, y):
    time.sleep(3)
    print("已经运行。。。")
    return x + y
