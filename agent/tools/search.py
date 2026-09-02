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

from pathlib import Path
import sqlite3

from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek



# 数据库路径
# ============================================================

# search.py 位于：
# agent/tools/search.py
#
# parent      -> agent/tools
# parent.parent -> agent
#
# 所以数据库位于：
# agent/orders.db

DB_PATH = Path(__file__).resolve().parent.parent / "orders.db"


# ============================================================
# Text-to-SQL 模型
# ============================================================

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.0
)


# ============================================================
# 数据库结构
# ============================================================

DATABASE_SCHEMA = """
SQLite数据库中只有一张订单表：
表名：orders
字段：
id
- 类型：INTEGER
- 含义：订单记录唯一编号

image_name
- 类型：TEXT
- 含义：订单图片文件名

customer_company
- 类型：TEXT
- 含义：顾客公司名称

order_date
- 类型：TEXT
- 含义：发注日期
- 格式类似：2024年05月09日

source_company
- 类型：TEXT
- 含义：源公司名称

project
- 类型：TEXT
- 含义：订单中的项目/商品名称

quantity
- 类型：INTEGER
- 含义：商品数量

unit_price
- 类型：REAL
- 含义：商品单价，单位为日元

total_amount
- 类型：REAL
- 含义：该条记录的总金额，等于 quantity × unit_price
"""


# ============================================================
# Text → SQL
# ============================================================

def generate_sql(query: str) -> str:
    """
    使用大模型将用户自然语言问题转换成 SQLite SELECT SQL。
    """

    prompt = f"""
你是一个SQLite数据库查询SQL语言生成器。

你的任务是：
根据用户的问题生成可以直接在SQLite数据库中实现用户意图并执行的SQL查询语句。

数据库结构如下：
{DATABASE_SCHEMA}
用户问题：
{query}

要求：
1. 只能生成SELECT查询。
2. 不允许生成INSERT、UPDATE、DELETE、DROP、ALTER、CREATE等语句。
3. 只能查询orders表。
4. 如果需要模糊查询字符串，优先使用LIKE。
5. 用户查询某个公司、项目或订单时，应使用合理的WHERE条件。
6. 如果用户询问数量，可以使用SUM(quantity)。
7. 如果用户询问订单数量，可以使用COUNT(*)。
8. 如果用户询问金额，可以使用SUM(total_amount)。
9. 如果用户询问单条订单信息，可以查询相关字段。
10. 如果没有明确要求返回全部数据，尽量限制返回数量。
11. SQL必须兼容SQLite。
12. 只返回SQL语句。
13. 不要返回Markdown代码块。
14. 不要解释SQL，也不要在语句前后添加任何其他内容或标点。

只输出可执行的SQL语句。

"""

    response = llm.invoke(prompt)

    sql = response.content.strip()

    # 防止模型返回 ```sql ... ```
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql


# ============================================================
# SQL安全检查
# ============================================================

def validate_sql(sql: str) -> bool:
    """
    对LLM生成的SQL进行最基本的安全检查。
    """
    normalized_sql = sql.strip().lower()
    # 必须以SELECT开头
    if not normalized_sql.startswith("select"):
        return False
    # 禁止危险操作
    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "replace",
        "truncate",
        "attach",
        "detach",
        "pragma",
    ]

    for keyword in forbidden_keywords:
        if keyword in normalized_sql:
            return False

    # 只能访问orders表
    if "orders" not in normalized_sql:
        return False

    return True
# ============================================================
# 执行SQL
# ============================================================
def execute_sql(sql: str):
    """
    在SQLite数据库中执行SELECT查询。
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"数据库不存在：{DB_PATH}"
        )
    conn = sqlite3.connect(DB_PATH)  # 连接数据库
    try:
        cursor = conn.execute(sql)   # 数据库接口
        columns = [
            description[0]
            for description in cursor.description   #结果对应表头
        ]
        rows = cursor.fetchall()      # 结果内容
        return columns, rows

    finally:
        conn.close()



@tool
def search_orders(query: str) -> str:
    """
    查询企业订单数据库中的历史订单信息。

    当用户询问订单、货物数量、商品数量、
    订单记录、历史订单、顾客公司、
    项目、发注日期等信息或进行了相关订单查询需求但语义模糊时使用此工具。

    参数：
        query: 用户希望查询的订单信息。

    返回：
        SQLite数据库查询结果。
    """

    print("\n========== search_orders ==========")
    print("用户查询：", query)

    try:
    # 自然语言 → SQL

        sql = generate_sql(query)

     #   print("生成SQL：")
     #   print(sql)


    # SQL安全检查

        if not validate_sql(sql):

            print("SQL安全检查失败")

            return (
                "无法执行该数据库查询："
                "生成的SQL不是合法的只读查询。"
            )
        columns, rows = execute_sql(sql)

        print("查询结果数量：", len(rows))

        if not rows:
            return "数据库中没有找到符合条件的订单记录。"

    # 格式化结果

        result_lines = []

        for row in rows:

            item = []

            for column, value in zip(columns, row):

                item.append(
                    f"{column}: {value}"
                )

            result_lines.append(
                " | ".join(item)
            )

        result = "\n".join(result_lines)

        # print("返回结果：")
        # print(result)

        # print("==================================")

        return result

    except Exception as e:

        print("search_orders执行失败：")
        print(e)

        return f"数据库查询失败：{e}"