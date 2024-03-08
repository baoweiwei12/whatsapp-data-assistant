from urllib.parse import quote_plus
from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

username = config.SQL_NAME
password = config.SQL_PSWD
hostname = config.SQL_HOST
database_name = config.SQL_DB_NAME
# 对用户名和密码进行 URL 编码
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# 构建编码后的连接字符串
SQLALCHEMY_DATABASE_URL = (
    f"mysql://{encoded_username}:{encoded_password}@{hostname}/{database_name}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # 设置连接池大小为10
    max_overflow=20,  # 设置允许的最大连接数（超出连接池大小时）
    pool_timeout=30,  # 设置获取连接的超时时间（秒）
    pool_recycle=3600,  # 设置连接的回收时间（秒）
    pool_pre_ping=True,  # 启用连接保活机制，自动检查连接是否有效
    echo=False,  # 当为True时，将打印所有与数据库交互的SQL语句
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
