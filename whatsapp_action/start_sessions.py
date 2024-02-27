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

pprint(response.json())
