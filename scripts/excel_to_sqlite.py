import sqlite3


import pandas as pd


# ============================================================
# Excel → SQLite
# 将企业订单 Excel 数据导入 SQLite 数据库
# ============================================================
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

EXCEL_FILE = BASE_DIR / "data" / "output_label.xlsx"

DB_FILE = BASE_DIR / "agent" / "orders.db"


def clean_price(value):
    """将 Excel 中类似 ¥14,781.00 的单价转换为 float。"""
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    # 去掉货币符号、千位分隔符和空格
    value = (
        value.replace("¥", "")
        .replace(",", "")
        .replace(" ", "")
    )

    try:
        return float(value)
    except ValueError:
        print(f"警告：无法解析单价：{value!r}")
        return None


def clean_quantity(value):
    """将数量转换为整数。"""
    if pd.isna(value):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        print(f"警告：无法解析数量：{value!r}")
        return None


def create_table(conn):
    """创建订单表。"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            customer_company TEXT,
            order_date TEXT,
            source_company TEXT,
            project TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL
        )
    """)

    conn.commit()


def import_excel():
    """读取 Excel 并导入 SQLite。"""

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"找不到 Excel 文件：{EXCEL_FILE}\n"
            f"请将 Excel 文件放到 data/ 目录下。"
        )

    # 读取 Excel
    df = pd.read_excel(EXCEL_FILE)

    print(f"读取 Excel 成功，共 {len(df)} 条数据。")
    print(f"Excel 列名：{list(df.columns)}")

    # 检查必要字段
    required_columns = [
        "图像名",
        "顾客公司",
        "发注日",
        "源公司",
        "项目",
        "数量",
        "单价",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Excel 缺少以下字段：{missing_columns}"
        )

    # 创建数据库目录
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 如果数据库已经存在，询问是否重新创建
    if DB_FILE.exists():
        answer = input(
            f"\n数据库 {DB_FILE} 已存在，是否删除并重新导入？(y/n): "
        ).strip().lower()

        if answer == "y":
            DB_FILE.unlink()
            print("已删除旧数据库。")
        else:
            print("取消导入。")
            return

    # 连接 SQLite
    conn = sqlite3.connect(DB_FILE)

    try:
        create_table(conn)

        rows = []

        for _, row in df.iterrows():
            image_name = (
                str(row["图像名"]).strip()
                if not pd.isna(row["图像名"])
                else None
            )

            customer_company = (
                str(row["顾客公司"]).strip()
                if not pd.isna(row["顾客公司"])
                else None
            )

            # 日期按照用户要求直接作为字符串保存
            order_date = (
                str(row["发注日"]).strip()
                if not pd.isna(row["发注日"])
                else None
            )

            source_company = (
                str(row["源公司"]).strip()
                if not pd.isna(row["源公司"])
                else None
            )

            project = (
                str(row["项目"]).strip()
                if not pd.isna(row["项目"])
                else None
            )

            quantity = clean_quantity(row["数量"])
            unit_price = clean_price(row["单价"])

            # 数量 × 单价
            total_amount = (
                quantity * unit_price
                if quantity is not None and unit_price is not None
                else None
            )

            rows.append((
                image_name,
                customer_company,
                order_date,
                source_company,
                project,
                quantity,
                unit_price,
                total_amount,
            ))

        conn.executemany("""
            INSERT INTO orders (
                image_name,
                customer_company,
                order_date,
                source_company,
                project,
                quantity,
                unit_price,
                total_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

        conn.commit()

        # 基本检查
        cursor = conn.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]

        print("\n========================================")
        print("Excel → SQLite 导入完成")
        print("========================================")
        print(f"Excel 数据量：{len(df)}")
        print(f"数据库记录数：{count}")
        print(f"数据库位置：{DB_FILE}")

        # 查看前 3 条数据
        print("\n前 3 条数据：")

        cursor = conn.execute("""
            SELECT
                id,
                image_name,
                customer_company,
                order_date,
                source_company,
                project,
                quantity,
                unit_price,
                total_amount
            FROM orders
            LIMIT 3
        """)

        for record in cursor.fetchall():
            print(record)

    finally:
        conn.close()


if __name__ == "__main__":
    import pandas as pd

    import_excel()
