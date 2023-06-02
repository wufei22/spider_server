import logging
from app.main.public_method import *


class DatabaseModule(object):
    """
    爬虫数据的增删改查
    """
    def __init__(self):
        database_conn = database.DatabaseConn()
        self.conn = database_conn.conn_database()

    def add_data(self, sql_sentence):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="ERROR")
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence)
            self.conn.commit()
            my_cursor.close()
            self.conn.close()
            logging.shutdown()
            return True
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()
            my_cursor.close()
            self.conn.close()
            return False

    def delete_data(self, sql_sentence):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="ERROR")
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence)
            self.conn.commit()
            my_cursor.close()
            self.conn.close()
            logging.shutdown()
            return True
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()
            my_cursor.close()
            self.conn.close()
            return False

    def select_data(self, sql_sentence):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="ERROR")
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence)
            my_data = my_cursor.fetchall()
            my_cursor.close()
            self.conn.close()
            logging.shutdown()
            return my_data
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()
            my_cursor.close()
            self.conn.close()
            return False

    def update_data(self, sql_sentence):
        crawled_logging = logging_module.CrawledLogging()
        crawled_dir_path = crawled_logging.make_log_dir(log_dir_name="crawled_log")
        crawled_log_filename = crawled_logging.get_log_filename(dir_path=crawled_dir_path)
        crawled_logger = crawled_logging.log(log_filename=crawled_log_filename, level="ERROR")
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence)
            self.conn.commit()
            my_cursor.close()
            self.conn.close()
            logging.shutdown()
            return True
        except Exception as e:
            # print(e)
            crawled_logger.error(msg=e)
            logging.shutdown()
            my_cursor.close()
            self.conn.close()
            return False
