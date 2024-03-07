from pprint import pprint
import requests
import config

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
if response.status_code == 201:
    print(f"whatsapp会话启动成功,状态:{response.json()['status']}")
else:
    print(f"whatsapp会话启动失败:{response.text}")
