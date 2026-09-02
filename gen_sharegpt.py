import pandas as pd

# 提示词
PROMPT = """
# 任务描述
你需要对图像中的销售信息进行结构化信息提取，按以下所说的销售字段对应的信息种类输出一个标准CSV格式的数据。

# 销售内容字段定义
desc:表示接收货物的顾客公司的名称
date:表示发生销售行为的日期
from:表示发货公司的名称
item:表示被销售以及被接收的货物的名称
amount:表示销售的货物的数量
price:表示销售货物的单价

# 输入的图像
<image>

"""

# 读取Excel数据
data = pd.read_excel('data/output_label.xlsx')

TRAIN_RANGE = (0, 800)  # 训练数据范围
VAL_RANGE = (850, 1000)  # 评估数据范围
PATH_PREF = '/workspace/team1/LLaMA-Factory/data/doc_agent' # 训练数据的服务器路径前缀

def create_conversation(image_rows, image_path):# 为单个图片生成Share_gpt格式的对话数据
    csv_line = " "
    for _, row in image_rows.iterrows():
        csv_line += f'{row['顾客公司']}, {row['发注日']}, {row['源公司']}, {row['项目']}, {str(row['数量'])}, {row['单价'].replace('￥', '').replace(',', '')}\n'
    conversation = {
        "conversations": [
          {
            "from": "human",
            "value": PROMPT
          },
          {
            "from": "gpt",
            "value": csv_line
          }
        ],
        "system": "你是一个专业的图像文本信息提取与分析助手。",
        "images": [
          PATH_PREF+f"/{image_path}",
        ]
    }
    return conversation


from tqdm import trange
import json

def main():

    with open('train.jsonl', 'w', encoding= 'utf-8') as f:
        for i in trange(*TRAIN_RANGE):
            image_name = f'Sample{i}.png'
            # 提取Excel中所有的对应数据行
            image_rows = data[data['图像名'] == f'output_image\\{image_name}']
             # 生成对话
            conversation = create_conversation(image_rows, f'train/{image_name}')

            f.write(json.dumps(conversation, ensure_ascii=False) + '\n')

    with open('val.jsonl', 'w', encoding= 'utf-8') as f:
        for i in trange(*VAL_RANGE):
            image_name = f'Sample{i}.png'
            # 提取Excel中所有的对应数据行
            image_rows = data[data['图像名'] == f'output_image\\{image_name}']
             # 生成对话
            conversation = create_conversation(image_rows, f'val/{image_name}')

            f.write(json.dumps(conversation, ensure_ascii=False) + '\n')

# print(data.shape)
# 生成训练数据'data/train/Sample0.png-Sample149.png' csv内容，不同内容用，拼接，不同行用//分割

if __name__ == "__main__":
    main()
