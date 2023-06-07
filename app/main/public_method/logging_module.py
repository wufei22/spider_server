import logging
import os
import time
import shutil


class CrawledLogging(object):
    """
    日志模块
    """
    def __init__(self):
        self.local_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

    def make_log_dir(self, log_dir_name):
        """
        创建日志文件夹
        :param log_dir_name:日志保存的文件夹名
        :return:日志文件夹绝对路径
        """
        path = os.path.join(self.local_path, log_dir_name)
        path = os.path.normpath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @staticmethod
    def get_log_filename(dir_path):
        """
        创建日志文件名，格式类似2022-11-07.log
        :param dir_path:日志文件夹的绝对路径
        :return:日志绝对路径
        """
        filename = "{}.log".format(time.strftime("%Y-%m-%d", time.localtime()))
        filename = os.path.join(dir_path, filename)
        filename = os.path.normpath(filename)
        return filename

    @staticmethod
    def log(log_filename, level):
        """
        生成日志的主方法,传入对选定级别及以上的日志进行处理
        :param log_filename: 日志绝对路径
        :param level: 选定级别
        :return: 返回日志器
        """
        logger = logging.getLogger()  # 创建日志器
        level = getattr(logging, level)  # 获取日志模块的的级别对象属性
        logger.setLevel(level)  # 设置日志级别
        if not logger.handlers:  # 作用,防止重新生成处理器
            sh = logging.StreamHandler()  # 创建控制台日志处理器
            fh = logging.FileHandler(filename=log_filename, mode='a', encoding="utf-8")  # 创建日志文件处理器
            # 创建格式器
            fmt = logging.Formatter("{logging_time}\n%(levelname)s %(filename)s Line:%(lineno)d \nMessage:%(message)s".format(logging_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            # 给处理器添加格式
            sh.setFormatter(fmt=fmt)
            fh.setFormatter(fmt=fmt)
            # 给日志器添加处理器，过滤器一般在工作中用的比较少，如果需要精确过滤，可以使用过滤器
            logger.addHandler(sh)
            logger.addHandler(fh)
        return logger

    def regular_cleaning(self, log_path_name):
        """
        清理日志功能
        :param
        :return:
        """
        try:
            shutil.rmtree(os.path.join(self.local_path, log_path_name))
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    crawled_logging = CrawledLogging()
    test_dir_path = crawled_logging.make_log_dir(log_dir_name="test_log")
    test_log_filename = crawled_logging.get_log_filename(dir_path=test_dir_path)
    test_logger = crawled_logging.log(log_filename=test_log_filename, level="DEBUG")
    test_logger.error(msg="test1")
    logging.shutdown()
    # crawled_logging.regular_cleaning(log_path_name="test_log")
