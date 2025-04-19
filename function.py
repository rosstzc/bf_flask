import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown
import os
from dotenv import load_dotenv
load_dotenv()

# 显示为markdown格式（可选）
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# 配置API（请勿泄露 API KEY）
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

#print("API KEY:", GOOGLE_API_KEY)

# 初始化模型（可切换不同模型）
# model = genai.GenerativeModel("gemini-2.0-flash-lite")
model = genai.GenerativeModel("gemini-1.5-flash")
# model = genai.GenerativeModel("gemini-1.5-pro")

# ===============================
# 封装的主方法
# ===============================


def get_list_from_text(result):
    import re
    # 使用正则表达式提取列表内容
    matches = re.findall(r'\[(.*?)\]', result, re.DOTALL)
    # 将匹配的内容转换为列表
    if matches:
        # 去除空格和换行符，分割为单个元素
        result2 = [item.strip().strip("'") for item in matches[0].split(",")]
    else:
        result2 = []    
    return result2






def analyze_review_sentiments(reviews, prompt_template, output_markdown=False):
    """
    输入一组评论和一个prompt模板，返回每条评论的情感倾向。
    
    参数:
        reviews (list[str]): 用户评论列表
        prompt_template (str): 提示词模板，使用 {reviews} 占位
        output_markdown (bool): 是否以Markdown方式展示结果（用于Notebook）
    返回:
        str: 模型生成的结果
    """
    reviews_joined = ",".join(reviews)
    prompt = prompt_template.format(reviews=reviews_joined)
    response = model.generate_content(prompt)
    
    if output_markdown:
        display(to_markdown(response.text))
    return response.text



# ===============================
# 示例调用
# ===============================
if __name__ == "__main__":
    reviews = [
        "不错",
        "发货慢",
        "臭味",
        "一定一定要配上马甲！",
        "非常喜欢边缝的衣服，质量很好，价格不贵，每次包装都很用心。家里已经积累了好多麻布袋，收纳很实用。希望你家可以一直保持，会持续购入"
    ]

    prompt_template = """下面内容是多个用户评价，每一个是用","分隔的。请逐个分析以下评价的情感倾向（负面/中性/正面），
请仅返回三个选项之一，仅回答: 负面/中性/正面。有多少个用户评价就回复多少个，每行一个：
"{reviews}"
"""

    result = analyze_review_sentiments(reviews, prompt_template)
    print(result)



def extract_id(url):
    import re  
    match = re.search(r'id=(\d+)', url)
    if match:
        return match.group(1)
    else:
        return None

#定义一个函数来处理“万”
def convert(value):
    if isinstance(value, str) and "万" in value:
        return float(value.replace('万','')) * 10000
    else:
        return value
    


def convert2(value):
    if isinstance(value, str):
        if "万" in value:
            return float(value.replace('万', '')) * 10000
        elif "w" in value.lower():  # 检查 "w" 或 "W"
            return float(value.lower().replace('w', '')) * 10000
    return value




