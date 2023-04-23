import pymysql
import json
import os


class DatabaseConn(object):
    """
    数据库连接，执行sql语句
    """
    def __init__(self):
        # realpath方法即使是在其他地方调用也可以获取真实的绝对路径
        local_path = os.path.abspath(os.path.join(os.path.realpath(__file__), r"..\..\..\.."))
        dic_path = os.path.join(local_path, "config.json")
        with open(dic_path, "r") as f:
            dic_data = json.load(f)
        self.config_dic = dic_data["dependencies"]["database_config"]

    def conn_database(self):
        conn = pymysql.connect(host=self.config_dic["ip"],
                               user=self.config_dic["username"],
                               password=self.config_dic["password"],
                               port=self.config_dic["port"],
                               database=self.config_dic["database"],
                               charset="utf8")
        return conn


if __name__ == '__main__':
    database_test = DatabaseConn()
    conn_test = database_test.conn_database()
    print(conn_test)
    conn_test.close()
