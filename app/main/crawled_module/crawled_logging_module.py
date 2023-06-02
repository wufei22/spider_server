import datetime
from app.main.crawled_module import database_module


class CrawledLoggingModule(object):
    @staticmethod
    def start_task_log():
        my_database_module = database_module.DatabaseModule()
        task_id_data = my_database_module.select_data(sql_sentence="SELECT MAX(task_id) FROM crawled_log_info")
        # print(task_id_data)
        if task_id_data:
            task_id = task_id_data[0][0] + 1
            # print(task_id)
        else:
            task_id = 1
        task_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_log_info( log_type, task_id, start_time, task_status) VALUES (1, %d, '%s', 0)" % (task_id, task_start_time)
        print(sql_sentence)
        my_database_module.add_data(sql_sentence=sql_sentence)

    @staticmethod
    def end_task_log(task_status):
        my_database_module = database_module.DatabaseModule()
        task_id_data = my_database_module.select_data(sql_sentence="SELECT MAX(task_id) FROM crawled_log_info")
        task_id = task_id_data[0][0]
        task_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "UPDATE crawled_log_info SET end_time='%s',task_status=%d WHERE log_type=1 AND task_id=%d" % (task_end_time, task_status, task_id)
        my_database_module.update_data(sql_sentence=sql_sentence)

    @staticmethod
    def start_website_log(website_id):
        my_database_module = database_module.DatabaseModule()
        task_id_data = my_database_module.select_data(sql_sentence="SELECT MAX(task_id) FROM crawled_log_info")
        task_id = task_id_data[0][0]
        task_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_log_info( log_type, task_id, website_id, start_time, task_status) VALUES (2, %d, %d, '%s', 0)" % (task_id, website_id, task_start_time)
        my_database_module.add_data(sql_sentence=sql_sentence)

    @staticmethod
    def end_website_log(website_id, task_status):
        my_database_module = database_module.DatabaseModule()
        task_id_data = my_database_module.select_data(sql_sentence="SELECT MAX(task_id) FROM crawled_log_info")
        task_id = task_id_data[0][0]
        task_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "UPDATE crawled_log_info SET end_time='%s',task_status=%d WHERE log_type=2 AND task_id=%d AND website_id=%d" % (task_end_time, task_status, task_id, website_id)
        my_database_module.update_data(sql_sentence=sql_sentence)

    @staticmethod
    def start_article_log(website_id, article_id):
        my_database_module = database_module.DatabaseModule()
        task_id_data = my_database_module.select_data(sql_sentence="SELECT MAX(task_id) FROM crawled_log_info")
        task_id = task_id_data[0][0]
        task_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_log_info( log_type, task_id, website_id, article_id, start_time, task_status) VALUES (3, %d, %d, %d, '%s', 0)" % (task_id, website_id, article_id, task_start_time)
        my_database_module.add_data(sql_sentence=sql_sentence)

    @staticmethod
    def end_article_log(website_id, article_id, task_status):
        my_database_module = database_module.DatabaseModule()
        task_id_data = my_database_module.select_data(sql_sentence="SELECT MAX(task_id) FROM crawled_log_info")
        task_id = task_id_data[0][0]
        task_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "UPDATE crawled_log_info SET end_time='%s',task_status=%d WHERE log_type=2 AND task_id=%d AND website_id=%d AND article_id=%d" % (task_end_time, task_status, task_id, website_id, article_id)
        my_database_module.update_data(sql_sentence=sql_sentence)


if __name__ == '__main__':
    test_crawled_logging_module = CrawledLoggingModule()
    test_crawled_logging_module.start_task_log()
