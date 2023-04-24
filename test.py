import os
import re
import pandas as pd


file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data.xlsx")
# print(file_path)
test_data_frame = pd.read_excel(file_path, names=["序号", "省", "城市", "机构", "URL", "关键字", "备注"])
# print(test_data_frame)
url_data = test_data_frame["URL"]
# print(url_data)
test_pattern = re.compile("(http://[^/]*)|(https://[^/]*)")
for i in url_data:
    # print(i)
    compiled_url = re.match(pattern=test_pattern, string=i).group()
    print(compiled_url)





