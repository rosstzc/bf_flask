import pip
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

from function import * 
from process import * 

#隐藏警告
import warnings
warnings.filterwarnings("ignore")               #忽略警告信息
plt.rcParams['font.family'] = 'sans-serif' # 用来正常显示中文标签
plt.rcParams['font.sans-serif'] = ['SimHei', 'KaiTi', 'FangSong']
plt.rcParams['axes.unicode_minus'] = False      # 用来正常显示负号
plt.rcParams['figure.dpi']  = 100        #分辨率



# df_product = pd.read_excel('./input/2025夏2——商品-宝贝管理-我的宝贝 (12).xlsx') 
df_product = pd.read_excel('./input/2025夏2——商品-宝贝管理-我的宝贝 (12).xlsx') 
df_combined = productID_to_list(df_product)

#输出关注信息的内容
result = get_follow_new(df_combined, '上新')
# result = get_follow_new(df_combined, '预上新')
# result = get_follow_new(df_combined, '清单')


#输出淘宝群-清单的内容，需要结合“上新列表使用”
follow_new = pd.read_excel('./output/关注信息流-上新组合列表.xlsx') 
group_list = get_group_list(follow_new)

#输出淘宝群-消息的内容
