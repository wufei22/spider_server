import json
import flask
from app import app


# 时间计算接口
@app.route('/application/data_spider', methods=['POST'])
def person_add():
    # 1. 获取时间参数
    param_dic = flask.request.args
    start_date = param_dic["start_date"]
    end_date = param_dic["end_date"]



