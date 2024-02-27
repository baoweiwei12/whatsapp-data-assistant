from pprint import pprint
import requests
import config

data = {"logout": False, "name": "default"}

response = requests.post(f"{config.WHATSAPP_API_BASE_URL}/api/sessions/stop", json=data)

pprint(response.json())
