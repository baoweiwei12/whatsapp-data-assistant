
from datetime import datetime
import logging
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.task import proccess_message_task, save_goods_info,command_dict
import config
from app.dependencies import get_db
from app.sql import crud


router = APIRouter()
logger = logging.getLogger("whatsapp")


class WhatsappEvent(BaseModel):
    event: str
    session: str
    payload: dict


def process_staring_status():
    logger.info("WhatsApp正在启动......")


def process_scan_qr_code_status():
    logger.info("请使用手机扫描二维码")


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
            message_body = str(whatsapp_event.payload["body"])
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
                    sender_phone_number=f"+{message_author.split('@')[0]}",
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
                    sender_phone_number=f"+{message_from.split('@')[0]}",
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
