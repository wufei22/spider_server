import os
import re
import pandas as pd


# file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data.xlsx")
# # print(file_path)
# test_data_frame = pd.read_excel(file_path, names=["序号", "省", "城市", "机构", "URL", "关键字", "备注"])
# # print(test_data_frame)
# url_data = test_data_frame["URL"]
# # print(url_data)
# test_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
# for i in url_data:
#     # print(i)
#     compiled_url = re.match(pattern=test_pattern, string=i).group()
#     print(compiled_url)

# a = "核定申请、税收政策、创新"
# if "、" in a:
#     b = a.split("、")
#     print(b, type(b))
#
#     # //form/div/a[@class='btn ariaskiptheme']
#     #
#     # // *[@ id="searchForm"] / div / a
#     a = [{'id': 1,
#           'searched_url_list':
#               ['http://search.gd.gov.cn/search/mall/755018?keywords=%E6%A0%B8%E5%AE%9A%E7%94%B3%E8%AF%B7',
#                'http://search.gd.gov.cn/search/mall/755018?keywords=%E7%A8%8E%E6%94%B6%E6%94%BF%E7%AD%96',
#                'http://search.gd.gov.cn/search/mall/755018?keywords=%E5%88%9B%E6%96%B0']},
#          {'id': 2,
#           'searched_url_list':
#               ['http://search.gd.gov.cn/search/mall/755529?keywords=%E7%94%B3%E6%8A%A5',
#                'http://search.gd.gov.cn/search/mall/755529?keywords=%E6%89%B6%E6%8C%81']}]




