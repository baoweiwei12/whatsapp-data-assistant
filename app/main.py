import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from app.routers import webhooks
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks.router, tags=["webhooks"])

# 配置全局的logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(asctime)s   %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("log.txt", encoding="utf-8"),
    ],
)

# 使用logger实例
logger = logging.getLogger("whatsapp")
