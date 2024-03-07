from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    JSON,
)
from sqlalchemy.orm import relationship
from app.sql.database import Base


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP)
    sender_phone_number = Column(String)
    sender_display_name = Column(String)
    message_type = Column(String)
    message_content = Column(Text)
    is_group_message = Column(Boolean)
    group_id = Column(String, nullable=True)

    goods_information = relationship("GoodsInformation", back_populates="message")


class GoodsInformation(Base):
    __tablename__ = "goods_information"
    id = Column(Integer, primary_key=True, autoincrement=True)
    detail = Column(String)
    price = Column(Integer, nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    message = relationship("Messages", back_populates="goods_information")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String, unique=True)
    messages = Column(JSON)
