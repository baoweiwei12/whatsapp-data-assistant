from fastapi import APIRouter, Query, Request
from pprint import pprint
from pydantic import BaseModel
from typing import List

router = APIRouter()


@router.get("/webhooks")
async def verify_webhook(verify_request: Request):
    verify_query_params = verify_request.query_params
    hub_challenge = verify_query_params.get("hub.challenge")
    if hub_challenge is not None:
        return int(hub_challenge)
    else:
        return "Fail"


@router.post("/webhooks")
async def whatsapp_webhook(whatsapp_event: Request):
    body = await whatsapp_event.body()
    pprint(body)
    return "OK"
