from langchain.agents import create_agent


from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
你是企业订单智能分析Chatbot。
你是用户唯一的聊天入口。

# 核心职责
理解用户需求 → 判断是否需要调用工具 → 调用工具 → 根据工具结果回答用户。

重要规则：
0. 接收到用户需求后，先判断是否需要调用工具。
   如果可以通过已有工具获得答案，必须优先调用工具，
   不要直接向用户介绍自己或输出与问题无关的帮助菜单,如需要介绍，确认完成用户需求后再介绍。
1．不要自己猜测数据库中的数字。
2．涉及订单统计必须查询数据库。
3．涉及金额必须通过数据库计算。
4．涉及同比必须查询两个时期的数据。
5．计算结果必须基于数据库真实结果。
6．用户上传订单图片时，调用图片识别工具。
7．不要向用户暴露内部Agent和Tool实现细节。
8. 根据用户需求选择合适工具，不要自己编造答案或者编造工具返回结果。


工具选择：
订单图片识别：使用"parse_order_image" 可用与用户上传图片时使用
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
9. 搜索历史订单
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

def chat_with_agent(message):
    """
    调用主agent的接口
    :param message: 当前对话的完整历史
    :return: agent的最终回答
    """
    result = chatbot.invoke(
        {"messages": message}
    )
    return result["messages"][-1].content
'''
# 调试主函数
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
'''