from sqlalchemy import Column, Integer, String, Text, Boolean
from app.sql.database import Base


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String)
    sender_phone_number = Column(String)
    sender_display_name = Column(String)
    message_type = Column(String)
    message_content = Column(Text)
    is_group_message = Column(Boolean)
    group_id = Column(String, nullable=True)
