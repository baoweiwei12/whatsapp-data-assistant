import requests
import config

params = {"session": "default"}
response = requests.get(
    url=f"{config.WHATSAPP_API_BASE_URL}/api/screenshot", params=params
)

# 检查响应是否成功
if response.status_code == 200:
    with open("whatsapp_action/screenshot.jpg", "wb") as f:
        f.write(response.content)
        print("图片保存成功")
else:
    print("请求失败:", response.text)
