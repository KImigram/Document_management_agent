from langchain_core.tools import tool

@tool

def search_orders(query):
    """
    查询企业订单数据库中的历史订单信息。

    当用户询问订单、货物数量、商品数量、
    订单记录、模糊语义查询、历史订单等信息时使用此工具。
    使用text_to_sql

    参数：
        query: 用户希望查询的订单信息。

    返回：
        数据库查询结果。

    """
    from langchain_deepseek import ChatDeepSeek
    llm = ChatDeepSeek(
        model='deepseek-chat',
        temperature=0.0  # 控制模型思想的开放程度
    )

    PROMPT="""
    我使用的是SQLite数据库
    我的数据库结构及含义是什么
    # 给出表定义的sql语句或自然语言描述我的表定义以及对应语段代表含义
    表1名为user
    
    用户的问题：
    统计系统中有多少用户
    
    请注意：结果只返回sql的查询语句，不要添加任何其他解释说明、注释、markdown标记以及其他无关标点符号
    """

    output = llm.invoke(PROMPT)
    print(output)
    print('调用了查询订单的工具')
    # 查询数据库中的信息：关系型数据库MySQL/SQLite 或 向量数据库（用于语义检索）

    return{
        '货物名称': '笔记本',
        '数量': 200
    }