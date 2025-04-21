import pip
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

from function import * 
from process import * 

print("当前工作目录:", os.getcwd())


#统计关注信息流曝光与店铺访客、信息数的关系



# #关注信息流-上新
# df_product = pd.read_excel('./input/2025-夏3-商品-宝贝管理-我的宝贝 (13).xlsx') 
# df_combined = productID_to_list(df_product)
# result = get_follow_new(df_combined, '上新')

#关注信息流-预上新
# df_product = pd.read_excel('./input/2025-夏4-商品-宝贝管理-我的宝贝 (13).xlsx') 
# df_combined = productID_to_list(df_product)
# result = get_follow_new(df_combined, '预上新')

#关注信息流-清单
# df_product = pd.read_excel('./input/2025-4-13-月销排序_商品-宝贝管理-我的宝贝 (13).xlsx') 
# df_combined = productID_to_list(df_product)
# result = get_follow_new(df_combined, '清单')

# print(result.head(5))
# print(result)

#--------下面是群相关----

#输出淘宝群-清单的内容，需要结合“上新列表使用”
# follow_new = pd.read_excel('./output/关注信息流-清单组合列表.xlsx') 
# group_list = get_group_list(follow_new)



#群营销消息, 上新通知之类的
group_message = get_group_message()


