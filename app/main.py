import logging
from fastapi import FastAPI
from app.routers import webhooks, whatsapp_control,html
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="WhatsAppBot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.include_router(whatsapp_control.router, tags=["WhatsApp"])


app.include_router(webhooks.router, tags=["webhooks"])
app.include_router(html.router, tags=["html"])
app.include_router(whatsapp_control.router, tags=["WhatsApp"])


