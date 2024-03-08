import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import requests
import config

router = APIRouter()


@router.get("/start")
def start_whatsapp():
    data = {
        "name": "default",
        "config": {
            "proxy": None,
            "webhooks": [
                {
                    "url": config.WEBHOOKS_URL,
                    "events": ["message", "session.status"],
                    "hmac": None,
                    "retries": None,
                    "customHeaders": None,
                }
            ],
        },
    }

    response = requests.post(
        f"{config.WHATSAPP_API_BASE_URL}/api/sessions/start", json=data
    )
    return response.json()


@router.get("/stop")
def stop_whatsapp():
    data = {"logout": False, "name": "default"}

    response = requests.post(
        f"{config.WHATSAPP_API_BASE_URL}/api/sessions/stop", json=data
    )
    return response.json


@router.get("/qr_code")
def get_qr_code():
    response = requests.get(f"{config.WHATSAPP_API_BASE_URL}/api/default/auth/qr")
    if response.status_code == 200:
        image_stream = io.BytesIO(response.content)
        return StreamingResponse(image_stream, media_type="image/png")
    raise HTTPException(response.status_code, detail=response.text)


@router.get("/screenshot")
def screenshot():
    params = {"session": "default"}
    response = requests.get(
        url=f"{config.WHATSAPP_API_BASE_URL}/api/screenshot", params=params
    )
    if response.status_code == 200:
        image_stream = io.BytesIO(response.content)
        return StreamingResponse(image_stream, media_type="image/png")
    raise HTTPException(response.status_code, detail=response.text)
