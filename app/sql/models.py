
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from app.sql.database import Base

#
# 定义消息模型
#
class Messages(Base):
    __tablename__ = "messages"  # 指定表名为messages

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键，自动增长的ID
    timestamp = Column(TIMESTAMP)  # 消息时间戳
    sender_phone_number = Column(String(255))  # 发送者手机号码
    sender_display_name = Column(String(255))  # 发送者显示名称
    message_type = Column(String(255))  # 消息类型
    message_content = Column(Text)  # 消息内容
    is_group_message = Column(Boolean)  # 是否为群组消息
    group_id = Column(String(255), nullable=True)  # 群组ID，可为空
    goods_information = relationship("GoodsInformation", back_populates="message")

class GoodsInformation(Base):
    __tablename__ = "goods_information"  # 指定表名为goods_information
    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键，自动增长的ID
    detail = Column(String(255))  # 商品详情
    price = Column(Integer, nullable=True)  # 商品价格，可为空
    message_id = Column(Integer, ForeignKey("messages.id"))  # 消息ID，外键关联到消息表
    message = relationship("Messages", back_populates="goods_information")  # 定义与消息的关联关系


class ChatHistory(Base):
    __tablename__ = "chat_history"  # 指定表名为chat_history
    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键，自动增长的ID
    phone_number = Column(String(255), unique=True)  # 用户手机号码，唯一约束
    messages = Column(JSON)  # 聊天消息的JSON格式数据



class ErrorMessageRecords(Base):
    __tablename__ = 'error_message_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    error_message = Column(Integer, ForeignKey('messages.id'))
    error_reason = Column(String)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    message = relationship("Messages")

