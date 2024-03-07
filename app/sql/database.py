from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app import config

username = config.SQL_NAME
password = config.SQL_PSWD
# hostname = config.SQL_HOST
hostname = "47.99.70.58"
database_name = config.SQL_DB_NAME
# 对用户名和密码进行 URL 编码
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# 构建编码后的连接字符串
SQLALCHEMY_DATABASE_URL = (
    f"mysql://{encoded_username}:{encoded_password}@{hostname}/{database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
