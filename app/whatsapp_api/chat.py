import logging
import requests
from app import config

logger = logging.getLogger("whatsapp")


def send_text(chatId: str, text: str, session: str = "default"):
    data = {"chatId": chatId, "text": text, "session": session}
    response = requests.post(f"{config.WHATSAPP_API_BASE_URL}/api/sendText", data=data)
    if response.status_code == 201:
        logger.info(f"消息发送成功 - {chatId} - {text}")
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
