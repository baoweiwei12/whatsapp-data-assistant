import requests
import config

data = {"logout": False, "name": "default"}

response = requests.post(f"{config.WHATSAPP_API_BASE_URL}/api/sessions/stop", json=data)

if response.status_code == 201:
    print(f"whatsapp会话停止成功,是否退出登录？:{response.json()['logout']}")
else:
    print(f"whatsapp会话停止失败:{response.text}")
