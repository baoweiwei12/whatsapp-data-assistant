from app.chatgpt.client import run_conversation


messages = [
    {
        "role": "user",
        "content": "最近有什么比较便宜的商品？我应该找谁购买,告诉我电话号码",
    }
]
reply = run_conversation(messages).choices[0].message.content
print(reply)
