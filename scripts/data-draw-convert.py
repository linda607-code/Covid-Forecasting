import csv
import pandas as pd
import numpy as np

area = 'Shanghai'  # 筛选数据的取遇
option = 2  # 筛选数据的选项，1代表area是国家名称 2代表area是省份名称

data = pd.read_csv('datasets/DXYArea.csv', encoding="gbk")
data = np.array(data)
data = data[::-1]  # 翻转顺序
tmp = ''
index = 1
with open('datasets/data_' + area + '.csv', 'w', encoding='utf8', newline='') as f:
    writer = csv.writer(f)
    if option == 1:  # 筛选国家的数据
        for i in data:
            i = np.insert(i, 7, index)
            if i[3] == area:  # 匹配地区
                i[12] = i[12][0:9]  # 保留日期
                if i[12] != tmp:  # 去除重复日期
                    writer.writerow(i[7:9])
                    index = index + 1
                    tmp = i[12]
    elif option == 2:  # 筛选省份的数据
        for i in data:
            i = np.insert(i, 7, index)
            if i[5] == area:  # 匹配地区
                i[12] = i[12][0:9]  # 保留日期
                if i[12] != tmp:  # 去除重复日期
                    writer.writerow(i[7:9])
                    index = index + 1
                    tmp = i[12]
