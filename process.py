import pip
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

from function import * # type: ignore

#隐藏警告
import warnings
warnings.filterwarnings("ignore")               #忽略警告信息
plt.rcParams['font.family'] = 'sans-serif' # 用来正常显示中文标签
plt.rcParams['font.sans-serif'] = ['SimHei', 'KaiTi', 'FangSong']
plt.rcParams['axes.unicode_minus'] = False      # 用来正常显示负号
plt.rcParams['figure.dpi']  = 100        #分辨率



# df_product = pd.read_excel('./input/2025夏2——商品-宝贝管理-我的宝贝 (12).xlsx') 
# print(df_product.head(5))

#处理导出淘宝后台下载的商品列表
def productID_to_list(df_product):
    # 按“类目名称”分组，将“商品ID”合并为一个列表
    df_grouped = df_product.groupby('类目名称')['商品ID'].agg(list).reset_index()
    #去掉 商品ID 少于4的行
    df_grouped = df_grouped[df_grouped['商品ID'].apply(lambda x: len(x) >= 4)]

    # 随机选取商品ID内4个id，保存到新列“随机商品ID”
    import random
    def select_random_ids(ids):
        if len(ids) > 4:
            return random.sample(ids, 4)
        else:
            return ids  
    df_grouped['随机商品ID'] = df_grouped['商品ID'].apply(select_random_ids)

    # 创建一个新df，重复执行5次上一行代码，把结果保存到新df中
    df_combined = pd.DataFrame()
    for i in range(5):
        df_grouped['随机商品ID'] = df_grouped['商品ID'].apply(select_random_ids)
        df_grouped['第几天'] = i + 1 
        df_combined = pd.concat([df_combined, df_grouped], ignore_index=True)


    # 修改代码以确保拆分后的值为字符串格式
    df_combined[['商品ID1', '商品ID2', '商品ID3', '商品ID4']] = pd.DataFrame(
        df_combined['随机商品ID'].apply(lambda x: list(map(str, x))).tolist(), 
        index=df_combined.index
    )
    return df_combined




# 按频率调用api取值，并做数据处理，注意需要prompt的配合
def get_results_api(cal_list, prompt_template, num):
    # 假设 analyze_review_sentiments 是已经定义的函数
    results = []
    import time
    # 将 cal_list 拆分为每5个元素一组
    for i in range(0, len(cal_list), num):
        chunk = cal_list[i:i + num]  # 获取当前的10个元素
        result = analyze_review_sentiments(chunk, prompt_template)  # 执行分析
        #results.extend(result)  # 将结果添加到总结果中
        import re
        # 使用正则表达式提取列表内容
        matches = re.findall(r'\[(.*?)\]', result, re.DOTALL)
        # 将匹配的内容转换为列表
        if matches:
            # 去除空格和换行符，分割为单个元素
            result2 = [item.strip().strip("'") for item in matches[0].split(",")]
        else:
            result2 = []    
        print(result2)
        print(len(result2))
            # 合并结果到 all_results
        results.extend(result2)
        time.sleep(4)  # 延时4秒
    return results




# 关注信息流 - 营销标题
def get_follow_title(df_combined):
    # 关注信息流 - 营销标题
    cal_list = df_combined['类目名称'].tolist()

    #后续增加文案文案，方便
    prompt_template = """请对以下用","分隔的产品分类,先统计下面数组长度,然后针对每个分类生成一个营销文案，
    1)文案内容在10个中文字符以内,带“夏上新”类似字眼
    2）请使用小红书爆文风格文案，可适当加emoji，
    3）回复的内容不能有重复，开头不要带序号、分类名称或特殊符号，
    4）回复内容的行数应与之前数组统计长度相同，不要回复除营销标题以外的任何内容，
    5）不要有多余换行或空行,请务必检查，务必检查以上条件再回复我。
    6) 请用一个list的格式返回,不要带python等信息，仅返回对应分类的营销文案
    ----
    "{reviews}"
    """
    
    #热销模板
    prompt_template2 = """请对以下用","分隔的产品分类,先统计下面数组长度,然后针对每个分类生成一个营销文案，
    1)文案内容在10个中文字符以内, 带“热销”类似字眼。
    2）请使用小红书爆文风格文案，可适当加emoji，
    3）回复的内容不能有重复，开头不要带序号、分类名称或特殊符号，
    4）回复内容的行数应与之前数组统计长度相同，不要回复除营销标题以外的任何内容，
    5）不要有多余换行或空行,请务必检查，务必检查以上条件再回复我。
    6) 请用一个list的格式返回,不要带python等信息，仅返回对应分类的营销文案
    ----
    "{reviews}"
    """



    results = get_results_api(cal_list, prompt_template, 10)
    print(results)
    print(len(results))
    df_combined['营销标题'] = results
    return df_combined


# 关注信息流 - 营销正文
def get_follow_content(df_combined):
    # 关注信息流 - 营销正文
    cal_list = df_combined['类目名称'].tolist()

    prompt_template = """请对以下用","分隔的产品分类,先统计下面数组长度,然后针对每个分类生成一个营销文案，
    1)文案内容在60~80个中文字符以内,
    2）请使用小红书爆文风格文案，可以带些emoji，
    3）回复的内容不能有重复，开头不要带序号、分类名称或特殊符号，
    4）回复内容的行数应与之前数组统计长度相同，不要回复除营销标题以外的任何内容，
    5）不要有多余换行或空行,请务必检查，务必检查以上条件再回复我。
    6) 文案后面增加引导客户互动的语句，随便你发挥，内容与穿搭，风格，场景等相关
    7) 请用一个list的格式返回,不要带python等信息，仅返回对应分类的营销文案
    ----
    "{reviews}"
    """

    prompt_template2 = """请对以下用","分隔的产品分类,先统计下面数组长度,然后针对每个分类生成一个营销文案，
    1)文案内容在60~80个中文字符以内,
    2）请使用小红书爆文风格文案，可以带些emoji，
    3）回复的内容不能有重复，开头不要带序号、分类名称或特殊符号，
    4）回复内容的行数应与之前数组统计长度相同，不要回复除营销标题以外的任何内容，
    5）不要有多余换行或空行,请务必检查，务必检查以上条件再回复我。
    6) 文案后面增加引导客户互动的语句，比如：你觉得怎么样？你喜欢吗？你觉得好看吗？你觉得适合什么场景穿？你觉得适合微胖，高瘦，个子小的人穿吗，，等等
    7) 请用一个list的格式返回,不要带python等信息，仅返回对应分类的营销文案
    ----
    "{reviews}"
    """

    results = get_results_api(cal_list, prompt_template, 10)
    print(results)
    print(len(results))
    df_combined['营销正文'] = results
    return df_combined


#关注信息流（标题+正文）-上新/预上新/清单
def get_follow_new(df_combined, type):
    df_combined = get_follow_title(df_combined)
    df_combined = get_follow_content(df_combined)
    path = './output/'
    if type == '上新':
        df_combined['信息类型'] = '上新'
        df_combined.to_excel(path+'关注信息流-上新组合列表.xlsx', index=False)    
    if type == '预上新':
        df_combined['信息类型'] = '预上新'
        df_combined.to_excel(path+'关注信息流-预上新组合列表.xlsx', index=False)    
    if type == '清单':
        df_combined['信息类型'] = '清单'
        df_combined.to_excel(path+'关注信息流-清单组合列表.xlsx', index=False)    
    return df_combined


# 淘宝群 - 群清单信息
def get_group_list(df_combined):
    # 淘宝群 - 群清单信息
    cal_list = df_combined['类目名称'].tolist()

    #直接再上新或预上新的表， 增加定时日期和时间，就可以用， 每天最多3天

    #在df combined 增加一个"群发日期"列、“群发时间”列
    from datetime import datetime, timedelta

    # 获取明天的日期
    tomorrow = pd.Timestamp(datetime.now() + timedelta(days=0))
    # 创建新列并填充值
    df_combined['群发日期'] = ''
    df_combined['群发时间'] = ''

    for i in range(len(df_combined)):
        if i < 3:
            df_combined.loc[i, '群发日期'] = tomorrow.strftime('%Y-%m-%d')
            if i == 0:
                df_combined.loc[i, '群发时间'] = '08:03:00'
            elif i == 1:
                df_combined.loc[i, '群发时间'] = '12:02:00'
            else:
                df_combined.loc[i, '群发时间'] = '19:01:00'
        else:
            df_combined.loc[i, '群发日期'] = (tomorrow + timedelta(days=(i//3))).strftime('%Y-%m-%d')
            if i % 3 == 0:
                df_combined.loc[i, '群发时间'] = '08:04:00'
            elif i % 3 == 1:
                df_combined.loc[i, '群发时间'] = '12:03:00'
            else:
                df_combined.loc[i, '群发时间'] = '19:02:00'

    #因为群营销文案中文仅支持20中文字，所以要修改。
    prompt_template = """请对以下用","分隔的产品分类,先统计下面数组长度,然后针对每个分类生成一个营销文案，
    1)文案内容在19个中文字符以内,
    2）请使用小红书爆文风格文案，可以带些emoji，
    3）回复的内容不能有重复，开头不要带序号、分类名称或特殊符号，
    4）回复内容的行数应与之前数组统计长度相同，不要回复除营销标题以外的任何内容，
    5）不要有多余换行或空行,请务必检查，务必检查以上条件再回复我。
    6) 请用一个list的格式返回,不要带python等信息，仅返回对应分类的营销文案
    ----
    "{reviews}"
    """

    results = get_results_api(cal_list, prompt_template, 10)
    print(results)
    print(len(results))
    df_combined['营销正文'] = results


    df_combined['信息类型'] = '群清单'
    path = './output/'
    df_combined.to_excel(path+'淘宝群-清单组合列表.xlsx', index=False)  
    return df_combined



# 淘宝群 - 群消息信息
def  get_group_message():
    #在df combined 增加一个"群发日期"列、“群发时间”列
    from datetime import datetime, timedelta

    #创建一个空df
    df = pd.DataFrame()
 

    #群消息-预上新文案模板： 边缝夏3波于4.14日晚7:00直播上新，
    #因为群营销文案中文仅支持20中文字，所以要修改。
    prompt_template = """帮我写一个文案，吸引客户关注，，大概内容如右边：边缝夏3波于4.14日晚7:00直播上新，提前预览...
    1）请给我20个不同的文案版本，把结果存放在一个list返回给我。
    2）除了list不用回复任何内容。
    3）下面的内容可以忽略。
    ----
    "{reviews}"
    """
    result = analyze_review_sentiments([], prompt_template)  # 执行分析
    # 现在可以导入
    #from function import get_list_from_text
    results = get_list_from_text(result)    
    df['营销正文'] = results
    msg = '会员领券,提前准备-> https://market.m.taobao.com/app/sj/member-center-rax/pages/pages_index_index?wh_weex=true&source=ShopSelfUse&sellerId=232107310'
    home_url = 'https://shop58053041.taobao.com/'
    df['营销正文'] = df['营销正文'] + home_url + '\n' +'\n' + msg
    print(results)
    print(len(results))

    df['信息类型'] = '文本'
    # 获取明天的日期
    tomorrow = pd.Timestamp(datetime.now() + timedelta(days=0))
    # 创建新列并填充值
    df['群发日期'] = ''
    df['群发时间'] = ''

    for i in range(len(df)):
        if i < 3:
            df.loc[i, '群发日期'] = tomorrow.strftime('%Y-%m-%d')
            if i == 0:
                df.loc[i, '群发时间'] = '09:03:00'
            elif i == 1:
                df.loc[i, '群发时间'] = '17:02:00'
            else:
                df.loc[i, '群发时间'] = '21:01:00'
        else:
            df.loc[i, '群发日期'] = (tomorrow + timedelta(days=(i//3))).strftime('%Y-%m-%d')
            if i % 3 == 0:
                df.loc[i, '群发时间'] = '09:04:00'
            elif i % 3 == 1:
                df.loc[i, '群发时间'] = '17:03:00'
            else:
                df.loc[i, '群发时间'] = '21:02:00'

    path = './output/'
    df.to_excel(path+'淘宝群-群营销消息.xlsx', index=False)  
    return results

    # print(result)