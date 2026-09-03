from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import uuid

from conversation import Conversation


app = Flask(__name__)

# session_id -> Conversation
conversations = {}

# 图片上传目录
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def get_conversation(session_id):
    """
    获取当前用户的 Conversation。
    """

    if session_id not in conversations:
        conversations[session_id] = Conversation()

    return conversations[session_id]


@app.route("/")
def index():
    """
    返回前端页面。
    """

    return send_from_directory(
        app.root_path,
        "index.html"
    )


@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat API。

    接收：
        message
        image
        session_id

    返回：
        Agent 最终回答
    """

    message = request.form.get(
        "message",
        ""
    ).strip()

    session_id = request.form.get(
        "session_id",
        ""
    ).strip()

    image = request.files.get("image")

    # 没有 session 就创建一个
    if not session_id:
        session_id = str(uuid.uuid4())

    # 文字和图片都没有
    if not message and not image:
        return jsonify({
            "error": "消息不能为空"
        }), 400

    # ==========================
    # 保存图片
    # ==========================

    image_path = None

    if image:

        allowed_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp"
        }

        suffix = Path(
            image.filename or ""
        ).suffix.lower()

        if suffix not in allowed_extensions:

            return jsonify({
                "error": "只支持 PNG、JPG、JPEG、WEBP 图片"
            }), 400

        # 使用随机文件名
        filename = (
            uuid.uuid4().hex
            + suffix
        )

        image_path = (
            UPLOAD_DIR / filename
        )

        image.save(image_path)

    # ==========================
    # 交给 Conversation
    # ==========================

    try:

        conversation = get_conversation(
            session_id
        )

        answer = conversation.chat(
            message,
            image_path=str(image_path)
            if image_path else None
        )

        return jsonify({
            "session_id": session_id,
            "reply": answer
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/clear", methods=["POST"])
def clear():
    """
    清空当前会话。
    """

    data = request.get_json(
        silent=True
    ) or {}

    session_id = data.get(
        "session_id",
        ""
    ).strip()

    if session_id in conversations:

        conversations[
            session_id
        ].clear()

        del conversations[
            session_id
        ]

    return jsonify({
        "message": "对话已清空"
    })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )