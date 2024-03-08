from datetime import datetime, timedelta
import json
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from app.sql import models


def create_whatsapp_message(
    db: Session,
    timestamp: str,
    sender_phone_number: str,
    sender_display_name: str,
    message_type: str,
    message_content: str,
    is_group_message: bool,
    group_id: str | None = None,
):
    try:
        new_message = models.Messages(
            timestamp=timestamp,
            sender_phone_number=sender_phone_number,
            sender_display_name=sender_display_name,
            message_type=message_type,
            message_content=message_content,
            is_group_message=is_group_message,
            group_id=group_id,
        )

        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message
    except Exception as e:
        db.rollback()
        raise e


def get_group_messages(
    db: Session,
    limit: int = 20,
    start_timestamp: str | None = None,
    end_timestamp: str | None = None,
    search_content: str | None = None,
    sender_phone_number: str | None = None,
    sender_display_name: str | None = None,
):
    query = db.query(models.Messages).filter(models.Messages.is_group_message == True)

    if start_timestamp:
        query = query.filter(models.Messages.timestamp >= start_timestamp)

    if end_timestamp:
        query = query.filter(models.Messages.timestamp <= end_timestamp)

    if search_content:
        query = query.filter(
            models.Messages.message_content.ilike(f"%{search_content}%")
        )

    if sender_phone_number:
        query = query.filter(models.Messages.sender_phone_number == sender_phone_number)

    if sender_display_name:
        query = query.filter(models.Messages.sender_display_name == sender_display_name)

    group_messages = query.order_by(desc(models.Messages.id)).limit(limit).all()

    return group_messages


def create_goods_information(
    db: Session, detail: str, price: int | None, message_id: int
):
    try:
        new_goods_info = models.GoodsInformation(
            detail=detail, price=price, message_id=message_id
        )
        db.add(new_goods_info)
        db.commit()
        db.refresh(new_goods_info)
        return new_goods_info
    except Exception as e:
        db.rollback()
        raise e


class DeleteExpiredInfo(BaseModel):
    count: int
    expiration_date: str


def get_goods_information_by_detail(db: Session, detail: str):
    db_goods_info = (
        db.query(models.GoodsInformation)
        .filter(models.GoodsInformation.detail == detail)
        .first()
    )
    return db_goods_info


def delete_expired_goods_information(db: Session, valid_days: int = 30):

    current_datetime = datetime.now()

    expiration_date_str = (current_datetime - timedelta(days=valid_days)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    count = 0
    try:

        query = db.query(models.GoodsInformation).options(
            joinedload(models.GoodsInformation.message)
        )
        expired_goods = query.join(models.GoodsInformation.message).filter(
            models.Messages.timestamp <= expiration_date_str
        )
        for goods in expired_goods:
            db.delete(goods)
            count += 1

        db.commit()
        return DeleteExpiredInfo(count=count, expiration_date=expiration_date_str)
    except Exception as e:
        db.rollback()
        raise e


def get_goods_information(
    db: Session,
    limit: int = 100,
    start_timestamp: str | None = None,
    end_timestamp: str | None = None,
    key_words: str | None = None,
    sender_phone_number: str | None = None,
    sender_display_name: str | None = None,
):

    query = db.query(models.GoodsInformation).options(
        joinedload(models.GoodsInformation.message)
    )

    if start_timestamp:
        query = query.join(models.GoodsInformation.message).filter(
            models.Messages.timestamp >= start_timestamp
        )
    if end_timestamp:
        query = query.join(models.GoodsInformation.message).filter(
            models.Messages.timestamp <= end_timestamp
        )
    if sender_phone_number:
        query = query.join(models.GoodsInformation.message).filter(
            models.Messages.sender_phone_number == sender_phone_number
        )
    if sender_display_name:
        query = query.join(models.GoodsInformation.message).filter(
            models.Messages.sender_display_name == sender_display_name
        )
    if key_words:
        query = query.filter(models.GoodsInformation.detail.ilike(f"%{key_words}%"))

    results = query.order_by(desc(models.GoodsInformation.id)).limit(limit).all()

    return results


def get_chat_history_by_number(db: Session, phone_number: str):
    try:
        db_chat_history = (
            db.query(models.ChatHistory)
            .filter(models.ChatHistory.phone_number == phone_number)
            .first()
        )
        return db_chat_history
    except Exception as e:
        db.rollback()
        raise e


def creat_chat_history(db: Session, phone_number: str, messages: list[dict]):
    try:
        new_chat_history = models.ChatHistory(
            phone_number=phone_number, messages=json.dumps(messages)
        )
        db.add(new_chat_history)
        db.commit()
        db.refresh(new_chat_history)
        return new_chat_history
    except Exception as e:
        db.rollback()
        raise e


def update_chat_history(db: Session, phone_number: str, messages: list[dict]):
    try:
        # 查询要更新的记录
        chat_history = (
            db.query(models.ChatHistory)
            .filter(models.ChatHistory.phone_number == phone_number)
            .first()
        )

        if chat_history:
            # 更新 messages 列
            chat_history.messages = json.dumps(messages)  # type: ignore

            db.commit()
            db.refresh(chat_history)
            return chat_history
        else:
            new_chat_history = models.ChatHistory(
                phone_number=phone_number, messages=json.dumps(messages)
            )
            db.add(new_chat_history)
            db.commit()
            db.refresh(new_chat_history)
            return new_chat_history
    except Exception as e:
        db.rollback()
        raise e
