import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



# 设置最大列数和最大宽度，防止换行
pd.set_option('display.max_columns', None)     # 显示所有列
pd.set_option('display.width', 200)            # 一行最多显示200字符
pd.set_option('display.max_colwidth', None)    # 列内容完整显示


from function import *  # 现在能成功导入 flask_app 目录下的 function.py

import os
# 获取当前脚本所在路径
base_dir = os.path.dirname(os.path.abspath(__file__))


# 设置你的文件夹路径（建议传入参数）
folder_path = r'D:\Backup\Downloads\社媒助手\小红书'

# 获取所有 Excel 文件（包含 .xls 和 .xlsx）
excel_files = [f for f in os.listdir(folder_path) if f.endswith(('.xls', '.xlsx'))]

# 用于存储所有 DataFrame 的列表
df_list = []


#单个excel表的数据处理
def process_review(df):

    #df删除重复行
    df = df.drop_duplicates().copy()
    #判断"评论内容"列是否包含“边缝”，如果有就在列“出现关键字”列标记为1
    df['评论出现关键字'] = df['评论内容'].apply(lambda x: '1' if '边缝' in str(x) else '')
    
    #给第一级评论编号
    # 初始化计数器
    counter = 1  #一级评论计数
    counter2 = 1  #二级评论计数

    # 确保“出现位置”列存在（如果没有就创建）
    if '1级评论编号' not in df.columns:
        df['1级评论编号'] = ''
    if '2级评论编号' not in df.columns:
        df['2级评论编号'] = ''
    if '关键字在1级/2级' not in df.columns:
        df['关键字在1级/2级'] = ''

    # 遍历每一行，如果“子评论数”不为空，就写入编号
    for index, row in df.iterrows():
        if pd.notna(row['子评论数']): #不为空，表示是一级评论
            df.at[index, '1级评论编号'] = counter
            counter += 1
            counter2 = 1
            
        else: #为空表示是二级评论
            #df.at[index, '1级评论编号'] = counter
            df.at[index, '2级评论编号'] = str(counter2)
            counter2 += 1



    #如果“评论出现关键字”=1 和 “1级评论编号”不为空，那么“”关键字在1级/2级”=1；如果“评论出现关键字”=1 和 “2级评论编号”不为空，那么“”关键字在1级/2级”=2
    df['关键字在1级/2级'] = df.apply(lambda x: '1' if x['评论出现关键字'] == '1' and x['1级评论编号'] != '' else ('2' if x['评论出现关键字'] == '1' and x['2级评论编号'] != '' else ''), axis=1)

    #fill 补全
    df['1级评论编号'] = df['1级评论编号'].replace('', pd.NA).ffill().infer_objects(copy=False)
    #用字符形式合并1、2列
    df['合并编号'] = df['1级评论编号'].astype(str) + '_' + df['2级评论编号'].astype(str)

    #print(df[[ '评论出现关键字', '1级评论编号','2级评论编号','关键字在1级/2级']].head(20))

    return df


#把所有笔记的评论合并到一个表中
def get_all_reviews(folder_path):
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

    # 合并所有评论的df
    final_df = pd.concat(df_list, ignore_index=True)
    final_df['来源文件'] = final_df['来源文件'].str.replace('.0.xlsx', '', regex=False)
    print(final_df.head(20))


    # 可选：保存到本地或返回给影刀使用
    final_df.to_excel(os.path.join(base_dir, 'output', '评论_合并结果.xlsx'), index=False)

    return final_df


url = file_path = os.path.join(base_dir, 'input', 'test_URL.xlsx')
df_notes = pd.read_excel(url)
url = file_path = os.path.join(base_dir, 'output', '评论_合并结果.xlsx')
df_reviews = pd.read_excel(url)
#print(df_reviews.head(20))

#按单个笔记继续评论统计
filtered_df = df_reviews[df_reviews['评论出现关键字'] == 1]
# 按“来源文件”分组并统计 关键字出现的次数
keyword_count_list = filtered_df.groupby('来源文件').size().reset_index(name='次数')
# print(keyword_count_list.head(20))  
# 统计关键字出现的在1级还是2级评论
keyword_level_list = filtered_df.groupby('来源文件')['关键字在1级/2级'].apply(list).reset_index(name='层级列表')
# print(keyword_level_list)
keyword_position_list = filtered_df.groupby('来源文件')['合并编号'].apply(list).reset_index(name='位置列表')
#print(keyword_position_list)

#把上面三个df合并到df_notes, 依据“来源文件”列
df_notes = df_notes.merge(keyword_count_list, how='left', left_on='线上表编号', right_on='来源文件').drop(columns=['来源文件'])
df_notes = df_notes.merge(keyword_level_list, how='left', left_on='线上表编号', right_on='来源文件').drop(columns=['来源文件'])
df_notes = df_notes.merge(keyword_position_list, how='left', left_on='线上表编号', right_on='来源文件').drop(columns=['来源文件'])
print(df_notes.head(10))


df_notes.to_excel(
    os.path.join(base_dir, 'output', '笔记评论_【边缝】关键字统计分析.xlsx'), 
    index=False
)



#从所有评论找出带有“边缝”的评论是笔记
#从一个文件夹读取所有excel文件，1）把文件名存入一个df 2）读取每个excel文件的内容，搜索是否包含"边缝"这个词，在刚才df对应行的第二列标记1
def search_files_in_directory(directory):
    import pandas as pd
    import os
    import re

    # 创建一个空的 DataFrame 来存储文件名和搜索结果
    df = pd.DataFrame(columns=['文件名', '包含边缝'])

    # 获取所有 .xlsx 文件的完整路径，并按创建时间排序
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith('.xlsx')
    ]
    files.sort(key=lambda x: os.path.getctime(x))  # 按创建时间排序（越早越前）

    # 遍历排序后的文件列表
    for file_path in files:
        filename = os.path.basename(file_path)
        try:
            df_excel = pd.read_excel(file_path)
            text = df_excel.to_string()
            if re.search(r'边缝', text):
                df.loc[len(df)] = [filename, 1]
            else:
                df.loc[len(df)] = [filename, 0]
        except Exception as e:
            print(f"读取失败：{filename}，原因：{e}")

    # 保存结果
    result_path = os.path.join(directory, '搜索结果.xlsx')
    df.to_excel(result_path, index=False)
    print(f"已保存到: {result_path}")
    return df

