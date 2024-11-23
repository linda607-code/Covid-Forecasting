import pandas as pd
import re

# 输入数据
DATA_PATH = r"../data/DXYArea.csv"
# 输出数据
OUTPUT_PATH = r"../data/data_converted.csv"

org_data = pd.read_csv(DATA_PATH, encoding='utf-8')  # 初始数据
org_data = org_data[['countryName', 'provinceName', 'province_confirmedCount' , 'updateTime']]
p_data = org_data[org_data['countryName'] == '中国']
p_data = p_data[p_data['provinceName'] != '中国'][['provinceName', 'province_confirmedCount' , 'updateTime']]
org_data = p_data
org_data['updateTime'] = org_data['updateTime'].apply(lambda x: re.match(r'([0-9]+\/[0-9]+\/[0-9]+)(.*)', x).group(1))
org_data.drop_duplicates(subset=['provinceName', 'updateTime'], inplace=True)
org_data.reset_index(drop=True, inplace=True)
org_data.to_csv(OUTPUT_PATH, encoding='gbk', index=False)
