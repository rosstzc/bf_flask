import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown
import os
from dotenv import load_dotenv
from store_management import * 
load_dotenv()

#df = search_files_in_directory('D:\Backup\Downloads\社媒助手\小红书')
#上一行代码的路径可以这样写吗， 请修改
df = search_files_in_directory('D:\\Backup\\Downloads\\社媒助手\\小红书')

