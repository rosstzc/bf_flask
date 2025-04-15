import pip
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


from store_management import * 

# 1 打开input目录“已合作达人列表_带url_test.xlsx”，用rpa更新该表。  RPA项目名称：存量达人名称管理

# 2 执行下脚本，更新达人列表，生成darenlist文件在output目录 
# df = get_daren_list()

# 3 通过RPA抓取数据并生成 笔记exel表，手工放入input目录

# 4 执行下脚本，读取笔记exel表分析并更新darenlist文件
df = process_biji()