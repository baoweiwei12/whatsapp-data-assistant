from datetime import datetime
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.sql import crud

router = APIRouter()
logger = logging.getLogger("whatsapp")


class WhatsappEvent(BaseModel):
    event: str
    session: str
    payload: dict


@router.post("/webhooks")
def whatsapp_webhook(whatsapp_event: WhatsappEvent, db: Session = Depends(get_db)):

    event_type = whatsapp_event.event
    if event_type == "message":
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
                crud.create_whatsapp_message(
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
                    f"群组消息 - 群组ID: {message_from.split('@')[0]} - 发送人: {message_author.split('@')[0]} {message_notify_name} - 消息内容: {message_body}"
                )

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
                    f"个人消息 - 发送人: {message_from.split('@')[0]} {message_notify_name} - 消息内容: {message_body}"
                )
        except KeyError as e:
            logger.error(f"消息解析失败: {e}")
    else:
        logger.info(whatsapp_event)
    return "OK"
