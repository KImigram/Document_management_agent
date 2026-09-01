import base64
import mimetypes
import requests


# ============================================================
# 配置
# ============================================================

API_URL = "http://localhost:5006/v1/chat/completions"

# 修改成你的图片路径
IMAGE_PATH = "test.png"


# ============================================================
# 图片转 Base64
# ============================================================

def image_to_base64(image_path):
    # 自动判断图片 MIME 类型
    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None:
        raise ValueError("无法识别图片格式，请使用 JPG、JPEG 或 PNG 图片。")

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    return mime_type, image_base64


# ============================================================
# 调用 API
# ============================================================

def call_api(image_path):
    print("正在读取图片...")

    mime_type, image_base64 = image_to_base64(image_path)

    print(f"图片格式: {mime_type}")
    print(f"Base64 长度: {len(image_base64)}")
    print("正在调用 API...")

    # OpenAI Chat Completions 格式
    data = {
        "model": "vl",
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一名专业的图像识别与信息提取专家。"
                    "你的任务是准确分析用户提供的图像，识别图像中的物体、"
                    "场景、文字及其他有价值的信息，并根据用户的要求提取和整理关键信息。"
                    "请以客观、准确、清晰的方式回答，避免主观臆测；"
                    "对于无法从图像中确定的信息，应明确说明无法确认。"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请分析这张图片，识别其中的主要内容，并提取图片中的关键信息。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "stream": False,
        "temperature": 0.2,
        "max_tokens": 1024
    }

    try:
        response = requests.post(
            API_URL,
            json=data,
            timeout=300
        )

        # 检查 HTTP 状态码
        response.raise_for_status()

        result = response.json()

        # ====================================================
        # OpenAI 标准返回格式：
        #
        # {
        #     "choices": [
        #         {
        #             "message": {
        #                 "role": "assistant",
        #                 "content": "模型回答"
        #             }
        #         }
        #     ]
        # }
        # ====================================================

        content = result["choices"][0]["message"]["content"]

        print("\n" + "=" * 60)
        print("模型分析结果：")
        print("=" * 60)
        print(content)
        print("=" * 60)

        return content

    except requests.exceptions.RequestException as e:
        print("\nAPI 请求失败：")
        print(e)

    except (KeyError, IndexError, TypeError):
        print("\nAPI 返回格式异常：")
        print(response.text)

    except Exception as e:
        print("\n发生未知错误：")
        print(e)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    call_api(IMAGE_PATH)