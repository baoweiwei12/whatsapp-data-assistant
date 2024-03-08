from datetime import datetime
import io
import json
import logging
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
import config
from app.chatgpt.client import analyze_text, run_conversation
from app.chatgpt.tokens import limit_tokens_in_messages
from app.dependencies import get_db
from app.sql import crud
from app.sql.database import SessionLocal
from app.sql.models import Messages
from app.whatsapp_api.chat import send_text
from PIL import Image

router = APIRouter()
logger = logging.getLogger("whatsapp")


class WhatsappEvent(BaseModel):
    event: str
    session: str
    payload: dict


def proccess_message_task(message_from: str, message_body: str):
    db = SessionLocal()
    phone_number = message_from.split("@")[0]
    try:
        send_text(message_from, "我正在思考，请稍等！")
        message = {"role": "user", "content": message_body}
        db_chat_history = crud.get_chat_history_by_number(db, phone_number)
        if db_chat_history:
            messages: list[dict] = json.loads(str(db_chat_history.messages))
            messages.append(message)
        else:
            messages: list[dict] = []
            messages.append(message)
            crud.creat_chat_history(db, phone_number, messages)
        messages = limit_tokens_in_messages(messages, 4096 * 2)
        res = run_conversation(messages)
        chatgpt_reply = res.chat_completion.choices[0].message.content
        if chatgpt_reply:
            send_text(message_from, chatgpt_reply)
            messages.append({"role": "assistant", "content": chatgpt_reply})
        if res.func_data:
            send_text(message_from, res.func_data)
        crud.update_chat_history(db, phone_number, messages)
    finally:
        db.close()


def save_goods_info(message: Messages):
    db = SessionLocal()
    logger.info("开始分析数据")
    message_content_list = str(message.message_content).split("\n")
    max_lines = 30
    count = 0
    try:
        for index in range(0, len(message_content_list), max_lines):
            count = count + 1
            chunk_list = message_content_list[
                index : min(index + max_lines, len(message_content_list))
            ]
            chunk_text = "\n".join(chunk_list)
            goods_info = analyze_text(chunk_text)

            if goods_info.is_include_commodity_information == True:
                logger.info(f"{message.id}号消息第{count}轮分析包含商品信息")
                for info in goods_info.information:
                    crud.create_goods_information(
                        db, info.detail, info.price, int(str(message.id))
                    )
            else:
                logger.info(f"{message.id}号消息第{count}轮分析不包含商品信息")
    finally:
        logger.info("分析数据结束")
        db.close()


def delate_chat_history_task(message_from: str, message_body: str):
    db = SessionLocal()
    phone_number = message_from.split("@")[0]
    messages = []
    try:
        crud.update_chat_history(db, phone_number, messages)
        send_text(message_from, "聊天记录已删除。")
    finally:
        db.close()


def delete_expired_information(message_from: str, message_body: str):
    db = SessionLocal()
    try:
        res = crud.delete_expired_goods_information(db, 30)
        send_text(message_from, f"已删除{res.expiration_date}前的{res.count}条信息。")
    finally:
        db.close()


command_dict = {
    "#删除聊天记录": delate_chat_history_task,
    "#删除过期信息": delete_expired_information,
}


def process_staring_status():
    logger.info("WhatsApp正在启动......")


def process_scan_qr_code_status():
    logger.info("请使用手机扫描二维码")
    response = requests.get(f"{config.WHATSAPP_API_BASE_URL}/api/default/auth/qr")
    if response.status_code == 200:
        image_stream = io.BytesIO(response.content)
    image = Image.open(image_stream)
    image.show()


def process_working_status():
    logger.info("WhatsApp正在运行中......")


def process_stopped_status():
    logger.info("WhatsApp已停止运行")


def process_failed_status():
    logger.info("失败")


STATUS_FUNC_MAP = {
    "STARTING": process_staring_status,
    "SCAN_QR_CODE": process_scan_qr_code_status,
    "WORKING": process_working_status,
    "STOPPED": process_stopped_status,
    "FAILED": process_failed_status,
}


@router.post("/webhooks")
def whatsapp_webhook(
    whatsapp_event: WhatsappEvent,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    event_type = whatsapp_event.event
    if event_type == "session.status":
        try:
            STATUS_FUNC_MAP[whatsapp_event.payload["status"]]()
        except KeyError as e:
            logger.error(e)
            logger.info(whatsapp_event.payload)

    elif event_type == "message":
        try:
            event_data = whatsapp_event.payload["_data"]
            message_body = str(event_data["body"])
            message_type = str(event_data["type"])
            message_time = datetime.fromtimestamp(int(event_data["t"])).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            message_notify_name = str(event_data["notifyName"])
            message_from = str(event_data["from"])
            if message_from.endswith("@g.us"):
                message_author = str(event_data["author"])
                new_message = crud.create_whatsapp_message(
                    db=db,
                    timestamp=message_time,
                    sender_phone_number=message_author.split("@")[0],
                    sender_display_name=message_notify_name,
                    message_type=message_type,
                    message_content=message_body,
                    is_group_message=True,
                    group_id=message_from.split("@")[0],
                )
                logger.info(
                    f"收到群组消息 - 群组ID: {message_from.split('@')[0]} - 发送人: {message_author.split('@')[0]} {message_notify_name} "
                )
                background_tasks.add_task(save_goods_info, new_message)

            else:
                crud.create_whatsapp_message(
                    db=db,
                    timestamp=message_time,
                    sender_phone_number=message_from.split("@")[0],
                    sender_display_name=message_notify_name,
                    message_type=message_type,
                    message_content=message_body,
                    is_group_message=False,
                )
                logger.info(
                    f"收到个人消息 - 发送人: {message_from.split('@')[0]} {message_notify_name} "
                )
                if message_from.split("@")[0] in config.USER_PHONE_NUMBER:

                    for command, task in command_dict.items():
                        if message_body.startswith(command):
                            background_tasks.add_task(task, message_from, message_body)
                            break
                    else:
                        background_tasks.add_task(
                            proccess_message_task, message_from, message_body
                        )
        except KeyError as e:
            logger.error(f"消息解析失败: {e}")
    else:
        logger.info(whatsapp_event)
    return "OK"
