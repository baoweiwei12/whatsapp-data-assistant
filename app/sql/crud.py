from sqlalchemy import desc
from sqlalchemy.orm import Session
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
