import logging
import requests
import config
from app.logger import logger

def send_text(chatId: str, text: str, session: str = "default"):
    """
    发送文本消息到指定聊天ID

    参数:
    chatId : str - 聊天ID，指定消息发送的目标
    text : str - 要发送的文本内容
    session : str - 会话标识，默认为 "default"，用于标识不同的会话或对话

    返回值:
    bool - 消息是否成功发送，True为成功，False为失败
    """
    # 准备请求数据，包含聊天ID、文本内容和会话标识
    data = {"chatId": chatId, "text": text, "session": session}
    # 向指定API发送POST请求，发送文本消息
    response = requests.post(f"{config.WHATSAPP_API_BASE_URL}/api/sendText", data=data)
    # 判断请求响应状态，记录日志并返回发送结果
    if response.status_code == 201:
        logger.info(f"消息发送成功 - {chatId} ")
        return True
    logger.warning(f"消息发送失败 - {response.text}")
    return False


def send_file(
    chatId: str,
    mimetype: str,
    filename: str,
    base64_data: bytes,
    caption: str,
    session: str = "default",
):
    data = {
        "chatId": chatId,
        "file": {
            "mimetype": mimetype,
            "filename": filename,
            "data": base64_data,
        },
        "caption": caption,
        "session": session,
    }
    response = requests.post(f"{config.WHATSAPP_API_BASE_URL}/api/sendFile", data=data)
    if response.status_code == 201:
        logger.info(f"文件发送成功 - {chatId} - {filename}")
        return True
    logger.warning(f"文件发送失败 - {response.text}")
    return False
