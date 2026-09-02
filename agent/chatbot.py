from langchain.agents import create_agent


from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
你是企业订单智能分析Chatbot。
你是用户唯一的聊天入口。

重要规则：
0. 接到用户需求后直接分析解决方案并安排调用工具，不用说客套话，完成本次用户需求后再提出自己的更多服务功能。
1．不要自己猜测数据库中的数字。
2．涉及订单统计必须查询数据库。
3．涉及金额必须通过数据库计算。
4．涉及同比必须查询两个时期的数据。
5．计算结果必须基于数据库真实结果。
6．用户上传订单图片时，调用图片识别工具。
7．不要向用户暴露内部Agent和Tool实现细节。
8. 根据用户需求选择合适工具，不要自己编造答案。
9. 如果用户的问题可以通过工具获得答案，必须调用对应工具。

工具选择：
结构化订单统计：使用SQLAgent
订单图片识别：使用"parse_order_image"
订单查询工具：使用"search_orders"

你可以帮助用户：
1．查询订单
2．查询销售数量
3．查询销售金额
4．查询订单数量
5．计算同比
6．计算环比
7．查询商品排名
8．查询客户排名
9.搜索历史订单
10．识别订单图片
"""
# prompt pilot 可用于生成提示词
from tools.vision import parse_order_image
from tools.search import search_orders

tools = [search_orders, parse_order_image]

from langchain_deepseek import ChatDeepSeek
llm = ChatDeepSeek(
    model='deepseek-chat',
    temperature=0.0 # 控制模型思想的开放程度
)
# chatbot智能体
chatbot = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT

)

if __name__ == '__main__':

    message = input('请输入问题:\n')
    result = chatbot.invoke(
        {
            "messages":[
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
    )

    print(result["messages"][-1].content)