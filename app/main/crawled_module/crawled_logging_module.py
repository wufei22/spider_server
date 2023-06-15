import datetime
from app.main.crawled_module import database_module


class CrawledLoggingModule(object):
    @staticmethod
    def start_task_log():
        my_database_module = database_module.DatabaseModule()
        task_id_data = my_database_module.select_data(sql_sentence="SELECT MAX(task_id) FROM crawled_log_info")
        # print(task_id_data[0][0])
        field_list = []
        if task_id_data[0][0]:
            task_id = task_id_data[0][0] + 1
            # print(task_id)
        else:
            task_id = 1
        field_list.append(task_id)
        task_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        field_list.append(task_start_time)
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "INSERT INTO crawled_log_info( log_type, task_id, start_time, task_status) VALUES (1, %s, %s, 0)"
        # print(sql_sentence)
        my_database_module.add_data(sql_sentence=sql_sentence, field_list=field_list)
        return task_id

    @staticmethod
    def end_task_log(task_status, task_id, remarks):
        field_list = []
        task_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        field_list.append(task_end_time)
        field_list.append(task_status)
        field_list.append(remarks)
        field_list.append(task_id)
        my_database_module = database_module.DatabaseModule()
        sql_sentence = "UPDATE crawled_log_info SET end_time=%s,task_status=%s, remarks=%s WHERE log_type=1 AND task_id=%s"
        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)

    @staticmethod
    def start_website_log(website_id, task_id):
        field_list = []
        task_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        field_list.append(task_id)
        field_list.append(website_id)
        field_list.append(task_start_time)
        sql_sentence = "INSERT INTO crawled_log_info( log_type, task_id, website_id, start_time, task_status) VALUES (2, %s, %s, %s, 0)"
        my_database_module.add_data(sql_sentence=sql_sentence, field_list=field_list)

    @staticmethod
    def end_website_log(website_id, task_status, task_id, remarks):
        field_list = []
        task_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        field_list.append(task_end_time)
        field_list.append(task_status)
        field_list.append(remarks)
        field_list.append(task_id)
        field_list.append(website_id)
        sql_sentence = "UPDATE crawled_log_info SET end_time=%s, task_status=%s , remarks=%s WHERE log_type=2 AND task_id=%s AND website_id=%s"
        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)

    @staticmethod
    def start_article_log(website_id, article_id, task_id):
        field_list = []
        task_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        field_list.append(task_id)
        field_list.append(website_id)
        field_list.append(article_id)
        field_list.append(task_start_time)
        sql_sentence = "INSERT INTO crawled_log_info( log_type, task_id, website_id, article_id, start_time, task_status) VALUES (3, %s, %s, %s, %s, 0)"
        my_database_module.add_data(sql_sentence=sql_sentence, field_list=field_list)

    @staticmethod
    def end_article_log(website_id, article_id, task_status, task_id, remarks):
        field_list = []
        task_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        my_database_module = database_module.DatabaseModule()
        field_list.append(task_end_time)
        field_list.append(task_status)
        field_list.append(remarks)
        field_list.append(task_id)
        field_list.append(website_id)
        field_list.append(article_id)
        sql_sentence = "UPDATE crawled_log_info SET end_time=%s, task_status=%s, remarks=%s WHERE log_type=2 AND task_id=%s AND website_id=%s AND article_id=%s"
        my_database_module.update_data(sql_sentence=sql_sentence, field_list=field_list)


if __name__ == '__main__':
    test_crawled_logging_module = CrawledLoggingModule()
    test_crawled_logging_module.start_task_log()
