from agent.chatbot import chat_with_agent


class Conversation:
    """
    管理一次多轮对话。

    职责：
    1. 保存对话历史
    2. 接收 Web 层传入的文字和图片信息
    3. 将消息交给主 Agent
    4. 返回 Agent 最终回答

    不负责：
    - 判断调用哪个 Tool
    - 调用 Vision
    - 调用数据库
    - 业务逻辑判断
    """

    def __init__(self):
        self.messages = []

    def chat(self, user_message, image_path=None):
        """
        接收用户消息。

        参数：
            user_message: 用户输入的文字
            image_path: 用户上传的图片路径，可为空

        返回：
            Agent 最终回答
        """

        # ==========================
        # 组装用户消息
        # ==========================

        content = user_message.strip()

        if image_path:
            if content:
                content += "\n\n"

            content += (
                "用户同时上传了一张图片。\n"
                f"图片路径：{image_path}\n"
                "请根据用户需求自行判断是否需要使用图片识别工具。"
            )

        user_message_data = {
            "role": "user",
            "content": content
        }

        # 保存用户消息
        self.messages.append(user_message_data)

        # ==========================
        # 调用主 Agent
        # ==========================

        answer = chat_with_agent(self.messages)

        # ==========================
        # 保存 Agent 回复
        # ==========================

        self.messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    def clear(self):
        """
        清空当前对话历史。
        """
        self.messages.clear()

"""
if __name__ == "__main__":

    conversation = Conversation()

    while True:

        message = input("请输入问题：")

        if message == "exit":
            break

        if message == "clear":
            conversation.clear()
            print("对话已清空")
            continue

        answer = conversation.chat(message)

        print("\nAgent：")
        print(answer)
        print()
"""