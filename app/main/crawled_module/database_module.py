from app.main.public_method import *


class DatabaseModule(object):
    """
    爬虫数据的增删改查
    """
    def __init__(self):
        database_conn = database.DatabaseConn()
        self.conn = database_conn.conn_database()

    def add_data(self, sql_sentence, field_list):
        crawled_logging = logging_module.CrawledLogging()
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence, field_list)
            self.conn.commit()
            my_cursor.close()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            crawled_logging.error_log_main(message=e)
            my_cursor.close()
            self.conn.close()
            return False

    def delete_data(self, sql_sentence):
        crawled_logging = logging_module.CrawledLogging()
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence)
            self.conn.commit()
            my_cursor.close()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            crawled_logging.error_log_main(message=e)
            my_cursor.close()
            self.conn.close()
            return False

    def select_data(self, sql_sentence):
        crawled_logging = logging_module.CrawledLogging()
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence)
            my_data = my_cursor.fetchall()
            my_cursor.close()
            self.conn.close()
            return my_data
        except Exception as e:
            print(e)
            crawled_logging.error_log_main(message=e)
            my_cursor.close()
            self.conn.close()
            return False

    def update_data(self, sql_sentence, field_list):
        crawled_logging = logging_module.CrawledLogging()
        my_cursor = self.conn.cursor()
        try:
            my_cursor.execute(sql_sentence, field_list)
            self.conn.commit()
            my_cursor.close()
            self.conn.close()
            return True
        except Exception as e:
            print(e)
            crawled_logging.error_log_main(message=e)
            my_cursor.close()
            self.conn.close()
            return False
