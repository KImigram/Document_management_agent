import base64
import requests

from langchain_core.tools import tool


# InternVL API 地址
INTERNVL_API_URL = "http://localhost:5006/v1/chat/completions"


def image_to_base64(image_path):
    """
    将本地图片转换成 Base64 字符串。
    """

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return base64.b64encode(image_bytes).decode("utf-8")


def get_image_mime_type(image_path):
    """
    根据图片扩展名判断 MIME 类型。
    """

    image_path = image_path.lower()

    if image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
        return "image/jpeg"

    if image_path.endswith(".png"):
        return "image/png"

    if image_path.endswith(".webp"):
        return "image/webp"

    if image_path.endswith(".gif"):
        return "image/gif"

    raise ValueError("不支持的图片格式")


@tool
def parse_order_image(image_path: str):
    """
    识别订单/单据图像中的具体内容。

    输入：
        image_path: 本地图片路径

    输出：
        InternVL 图像识别结果
    """

    print("调用 InternVL3 模型进行图像识别")

    mime_type = get_image_mime_type(image_path)
    image_base64 = image_to_base64(image_path)
    payload = {
        "model": "vl",

        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一名专业的图像识别与信息提取专家。"
                    "你的任务是准确分析用户提供的订单或单据图片，"
                    "识别图片中的公司、日期、商品、数量、单价、金额等信息。"
                    "请以客观、准确、清晰的方式回答。"
                    "对于无法从图像中确定的信息，应明确说明无法确认。"
                    "不要随意编造图像中的内容，一切结果都应该一图像内容为准。"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "请识别这张订单图片中的信息。"
                            "重点提取顾客公司、发注日、源公司、"
                            "项目、商品名称、数量、单价以及金额等信息。"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                f"data:{mime_type};base64,"
                                f"{image_base64}"
                            )
                        }
                    }
                ]
            }
        ],

        "stream": False,
        "temperature": 0.2,
        "max_tokens": 1024
    }

# 调用 InternVL4 api
    response = requests.post(
        INTERNVL_API_URL,
        json=payload,
        timeout=120
    )

    # HTTP错误直接抛出
    response.raise_for_status()
    result = response.json()
    content = result["choices"][0]["message"]["content"]

    print("识别结果：")
    print(content)
    return content

if __name__ == "__main__":
    image_path = input("请输入图片路径：\n")

    result = parse_order_image.invoke({
        "image_path": image_path
    })

    print("\n========== 识别结果 ==========")
    print(result)