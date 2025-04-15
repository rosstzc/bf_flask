import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from function import *  # 现在能成功导入 flask_app 目录下的 function.py

import os
print("当前工作目录:", os.getcwd())

#隐藏警告
import warnings
warnings.filterwarnings("ignore")               #忽略警告信息
plt.rcParams['font.family'] = 'sans-serif' # 用来正常显示中文标签
plt.rcParams['font.sans-serif'] = ['SimHei', 'KaiTi', 'FangSong']
plt.rcParams['axes.unicode_minus'] = False      # 用来正常显示负号
plt.rcParams['figure.dpi']  = 100        #分辨率


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# 设置不换行显示DataFrame
pd.set_option('display.expand_frame_repr', False)

# 获取当前脚本所在路径
base_dir = os.path.dirname(os.path.abspath(__file__))

# # 构造 Excel 路径
# excel_file_path = os.path.join(base_dir, './input/已合作达人列表_带url_test.xlsx')
# base_file_path = os.path.join(base_dir, './input/2025-1-4基线列表.xlsx')

# 生成达人list，方便影刀抓数据
def get_daren_list(
    excel_file_path = os.path.join(base_dir, './input/已合作达人列表_带url_test.xlsx'),
    base_file_path = os.path.join(base_dir, './input/2025-1-4基线列表.xlsx'),
    pr_names=['楚', '丹', '静', '兰', '玲'],
    base_sheet='Sheet1',
    skip_counts=[1993, 1782, 1775, 2051, 1988]
):
    
    # 读取全部页签
    all_data = pd.read_excel(excel_file_path, sheet_name=None)
    df_base = pd.read_excel(base_file_path, sheet_name=base_sheet)
    df_base = df_base[df_base['颜值达人'] != 1]


    dfs = []
    for i, (sheet_name, df) in enumerate(all_data.items()):
        df.insert(0, 'pr', pr_names[i])
        print(f"{sheet_name} 原始行数:", df.shape)

        # 跳过已基线的部分
        df = df[skip_counts[i]:]
        print(f"{sheet_name} 跳过后行数:", df.shape)

        dfs.append(df)

    # 合并多个页签
    conca_df = pd.concat(dfs).reset_index(drop=True)
    print(conca_df.head(10))

    # 提取 ID 和构造 URL
    conca_df['id'] = conca_df.iloc[:, 2].str.extract(r"user/profile/([^?]+)")
    conca_df['id'] = conca_df['id'].fillna('')
    conca_df.loc[conca_df['id'] != '', 'xhu_url'] = 'https://www.xiaohongshu.com/user/profile/' + conca_df['id']
    conca_df.loc[conca_df['id'] != '', 'zxh_url'] = 'https://data.zhiyitech.cn/xhs/up/overview?id=' + conca_df['id']

    # 只保留需要的列
    conca_df = conca_df[['pr', '博主', 'id', 'xhu_url', 'zxh_url']]
    df_base = df_base[['pr', '博主', 'id', 'xhu_url', 'zxh_url']]

    # 合并基线数据
    conca_df = pd.concat([df_base, conca_df], axis=0)
    print("合并后总数据量:", conca_df.shape)

    # 删除重复 ID 行
    print("空 ID 数量:", conca_df['id'].isnull().sum())
    print("重复 ID 数量:", conca_df['id'].duplicated().sum())
    conca_df.drop_duplicates(subset=['id'], inplace=True)
    conca_df = conca_df.reset_index(drop=True)

    conca_df.to_excel(os.path.join(base_dir, './output/daren_list.xlsx')) #这个表用在影刀抓取
    return conca_df


#处理笔记数据
def process_biji(
    path_biji = os.path.join(base_dir, './input/达人笔记列表12-30.xlsx'),
    daren_list = os.path.join(base_dir, './output/daren_list.xlsx'),
):
    
    #df_biji30 = pd.read_excel('达人笔记列表-合并_知小红.xlsx')
    df_biji30 = pd.read_excel(path_biji) 
    #根据第4列的内容，删除重复笔记
    df_biji30 = df_biji30.drop_duplicates(subset=[df_biji30.columns[3]])
    print(df_biji30.shape)

    df_biji30 = df_biji30.drop(df_biji30.columns[[1,2]], axis=1)  #删除第2,3列，即pr和名称
    df_biji30.columns = ['达人序号', '笔记全文']
    #print(df_biji30)


    ## 识别在知小红搜不到的达人
    df_account_notfound = df_biji30[df_biji30['笔记全文'].str.contains('没找到该档案')]
    df_account_nobiji = df_biji30[df_biji30['笔记全文'].str.contains('该达人最近30天没笔记')]
    print(df_account_notfound.shape)
    print(df_account_nobiji.shape)
    # 从 df_biji30 中删除 df_account_notfound 的行 
    df_biji30 = df_biji30[~df_biji30.index.isin(df_account_notfound.index)]
    df_biji30 = df_biji30[~df_biji30.index.isin(df_account_nobiji.index)]
    print(df_biji30.shape)


        #拆分笔记文本
    df_split = df_biji30['笔记全文'].str.split('\n', expand=True)
    #print(df_split)


    #合并到原df
    df_combine = pd.concat([df_biji30, df_split], axis=1)
    df_combine.columns = ['达人序号', '笔记全文' , '标题', '达人', '日期', '赞', '收藏', '评论', '1', '1']
    #print(df_combine)


    ##计算笔记平均点赞等

    #先把赞、收藏、评论中有“万”的单位转化数字
    df_combine['赞2'] = df_combine['赞'].apply(convert)
    df_combine['赞2'] = df_combine['赞2'].astype(int)

    #计算点赞平均值
    df_group1 = df_combine.groupby('达人序号')['赞2'].mean().reset_index()
    df_group2 = df_combine.groupby('达人序号').size().reset_index()


    ## 笔记点赞数区间统计
    bins = [0, 100, 200, 500, 1000, 1500, 2500, 5000, 1000000]
    labels = ['0-100', '101-200','201-500', '501-1000', '1001-1500', '1501-2500', '2501-5000', '5001-1000000']
    df_combine['区间'] = pd.cut(df_combine['赞2'], bins=bins, labels=labels, right=True)

    df_group = df_combine.groupby('达人序号')['区间'].value_counts().reset_index()
    df_group_dict = df_group.groupby('达人序号').apply(lambda x: dict(zip(x['区间'], x['count']))).reset_index()
    df_group_dict = df_group_dict.rename(columns={0:'点赞分层'})



    #点赞分层按照labels进行排序
    df_group_dict['点赞分层'] = df_group_dict['点赞分层'].apply(lambda x: dict(sorted(x.items(), key=lambda item: labels.index(item[0]))))
    #用比例显示
    df_group_dict['点赞分层'] = df_group_dict['点赞分层'].apply(lambda x: {k: round((v / sum(x.values())),2) if sum(x.values()) != 0 else 0 for k, v in x.items()})
    print(df_group_dict)



    #点赞分层按照labels进行排序
    df_group_dict['点赞分层'] = df_group_dict['点赞分层'].apply(lambda x: dict(sorted(x.items(), key=lambda item: labels.index(item[0]))))
    #用比例显示
    df_group_dict['点赞分层'] = df_group_dict['点赞分层'].apply(lambda x: {k: round((v / sum(x.values())),2) if sum(x.values()) != 0 else 0 for k, v in x.items()})
    print(df_group_dict)


    # 把统计结果合并到原df
    conca_df = pd.read_excel(daren_list)  #读取达人列表
    conca_df['达人序号'] = conca_df.index  #把索引赋值到一列，然后用该列作merge标记
    df_merge = pd.merge(conca_df, df_group1, left_on='达人序号', right_on='达人序号', how='left' )
    df_merge = pd.merge(df_merge, df_group2, left_on='达人序号', right_on='达人序号', how='left' )
    df_merge = df_merge.rename(columns={'赞2':'平均赞', 0:'30天笔记数'})
    df_merge['平均赞'] = df_merge['平均赞'].fillna(0).astype(int)
    df_merge['30天笔记数'] = df_merge['30天笔记数'].fillna(0).astype(int)

    #再处理一下点赞数区间逻辑
    df_merge = pd.merge(df_merge, df_group_dict, left_on='达人序号', right_on='达人序号', how='left')
    df_merge = df_merge.join(df_merge['点赞分层'].apply(pd.Series))
    df_merge = df_merge.drop('点赞分层', axis=1)
    print(df_merge)


    ## 达人分级
    # 级别	爆文率	无效率	不论篇数	10+篇数	15+篇数	
    # S	30%+	30%-	148	105	80	选款达人
    # A	20%-29.9%	40%-	84	79	71	
    # B	10%-19.9%	40%-	125	119	111	

    #爆文： 1000+
    #无效：200-

    df_merge['c1'] = df_merge[['1001-1500', '1501-2500',  '2501-5000',  '5001-1000000']].sum(axis=1).round(2)
    df_merge['c2'] = df_merge[['0-100',  '101-200']].sum(axis=1).round(2)
    #condition_c = df_merge['30天笔记数']

    #标记A类或B类达人
    df_merge['class'] = ''
    df_merge.loc[(df_merge['c1'] >= 0.3) & (df_merge['c2'] < 0.3), 'class'] = 'S'
    df_merge.loc[(df_merge['c1'] >= 0.2) & (df_merge['c1'] < 0.3) & (df_merge['c2'] <= 0.4), 'class'] = 'A'
    df_merge.loc[(df_merge['c1'] >= 0.1) & (df_merge['c1'] < 0.2) & (df_merge['c2'] <= 0.4), 'class'] = 'B'

        #增加日期
    import datetime
    import os
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f'合作达人最近30天笔记-点赞分层统计_{date_str}.xlsx'


    #标记是否是重名的达人


    #df_merge.to_excel(filename)
    df_merge.to_excel(os.path.join(base_dir, './output/'+ filename))

   
    return