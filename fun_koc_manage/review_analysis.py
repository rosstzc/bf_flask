import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from function import *  # 现在能成功导入 flask_app 目录下的 function.py

import os
#print("当前工作目录:", os.getcwd())


# 设置你的文件夹路径（建议传入参数）
folder_path = r'D:\Backup\Downloads\社媒助手\小红书-BAK'

# 获取所有 Excel 文件（包含 .xls 和 .xlsx）
excel_files = [f for f in os.listdir(folder_path) if f.endswith(('.xls', '.xlsx'))]

# 用于存储所有 DataFrame 的列表
df_list = []


#单个excel表的数据处理
def process_review(df):
    #df删除重复行
    df = df.drop_duplicates()
    #判断"评论内容"列是否包含“边缝”，如果有就在列“出现关键字”列标记为1
    df['评论出现关键字'] = df['评论内容'].apply(lambda x: '1' if '边缝' in str(x) else '')
    
    #给第一级评论编号
    # 初始化计数器
    counter = 1

    # 确保“出现位置”列存在（如果没有就创建）
    if '1级评论编号' not in df.columns:
        df['1级评论编号'] = ''

    # 遍历每一行，如果“子评论数”不为空，就写入编号
    for index, row in df.iterrows():
        if pd.notna(row['子评论数']):
            df.at[index, '1级评论编号'] = counter
            counter += 1

    print(df[[ '出现关键字', '1级评论编号']].head(20))
    fdf
    return df

# 遍历每个 Excel 文件
for file in excel_files:
    file_path = os.path.join(folder_path, file)
    
    # 读取 Excel（默认第一张表）
    df = pd.read_excel(file_path)
    df = process_review(df)
    
    # 插入文件名列作为第一列
    df.insert(0, '来源文件', file)
    
    # 添加到列表中
    df_list.append(df)

# 合并所有 DataFrame
final_df = pd.concat(df_list, ignore_index=True)
print(final_df.head(20))

# 可选：保存到本地或返回给影刀使用
final_df.to_excel('合并结果.xlsx', index=False)



