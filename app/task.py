import json
import logging
import uuid
from app.chatgpt.client import analyze_text, run_conversation
from app.chatgpt.tokens import limit_tokens_in_messages
from app.sql import crud
from app.sql.database import SessionLocal
from app.sql.models import Messages
from app.whatsapp_api.chat import send_text
import config
logger = logging.getLogger("whatsapp")

def generate_html_table(csv_data: str):
    data = [line.split(',') for line in csv_data.split('\n')]
    html = "<table>\n"
    for i, row in enumerate(data):
        if i == 0:
            html += "  <tr class='header'>\n"
            for col in row:
                html += f"    <th>{col}</th>\n"
            html += "  </tr>\n"
        else:
            html += "  <tr>\n"
            for col in row:
                html += f"    <td>{col}</td>\n"
            html += "  </tr>\n"
    html += "</table>"
    
    css = """
    <style>
    table {
      border-collapse: collapse;
      width: 100%;
    }

    th, td {
      text-align: left;
      padding: 8px;
    }

    tr:nth-child(even) {
      background-color: #f2f2f2;
    }

    .header {
      background-color: #333;
      color: white;
    }
    </style>
    """
    
    unique_filename = f"{uuid.uuid4()}"
    
    with open(f"table_html/{unique_filename}.html", "w", encoding="utf-8") as html_file:
        html_file.write((css + html))
    
    url = f"{config.FILE_URL}/table/{unique_filename}"
    return url
def proccess_message_task(message_from: str, message_body: str):
    db = SessionLocal()
    phone_number = message_from.split("@")[0]
    try:
        send_text(message_from, "我正在思考，请稍等！")
        message = {"role": "user", "content": message_body}
        db_chat_history = crud.get_chat_history_by_number(db, phone_number)
        if db_chat_history:
            messages: list[dict] = json.loads(str(db_chat_history.messages))
            messages.append(message)
        else:
            messages: list[dict] = []
            messages.append(message)
            crud.creat_chat_history(db, phone_number, messages)
        messages = limit_tokens_in_messages(messages, 4096 * 2)
        res = run_conversation(messages)
        chatgpt_reply = res.chat_completion.choices[0].message.content
        if chatgpt_reply:
            send_text(message_from, chatgpt_reply)
            messages.append({"role": "assistant", "content": chatgpt_reply})
        if res.func_data:
            url = generate_html_table(res.func_data)
            send_text(message_from, f"👇点击链接查看查询详情\n🔗{url}")
        crud.update_chat_history(db, phone_number, messages)
    finally:
        db.close()


def save_goods_info(message: Messages):
    db = SessionLocal()
    logger.info(f"{message.id}号消息开始分析数据")
    message_content_list = str(message.message_content).split("\n")
    max_lines = 30
    count = 0
    try:
        for index in range(0, len(message_content_list), max_lines):
            count = count + 1
            chunk_list = message_content_list[
                index : min(index + max_lines, len(message_content_list))
            ]
            chunk_text = "\n".join(chunk_list)
            goods_info = analyze_text(chunk_text)

            if goods_info.is_include_commodity_information == True:
                logger.info(f"{message.id}号消息第{count}轮分析包含商品信息")
                for info in goods_info.information:
                    existing_info = crud.get_goods_information_by_detail(
                        db, info.detail
                    )
                    if existing_info is None:
                        crud.create_goods_information(
                            db, info.detail, info.price, int(str(message.id))
                        )
            else:
                logger.info(f"{message.id}号消息第{count}轮分析不包含商品信息")
    finally:
        logger.info(f"{message.id}号消息分析数据结束")
        db.close()


def delate_chat_history_task(message_from: str, message_body: str):
    db = SessionLocal()
    phone_number = message_from.split("@")[0]
    messages = []
    try:
        crud.update_chat_history(db, phone_number, messages)
        send_text(message_from, "聊天记录已删除。")
    finally:
        db.close()


def delete_expired_information(message_from: str, message_body: str):
    db = SessionLocal()
    try:
        res = crud.delete_expired_goods_information(db, 30)
        send_text(message_from, f"已删除{res.expiration_date}前的{res.count}条信息。")
    finally:
        db.close()

def show_log(message_from: str, message_body: str):
    url = f"{config.FILE_URL}/logs?secret_key={config.SECRET_KEY}"
    send_text(message_from, f"👇点击链接查看日志\n🔗{url}")

def change_proxy(message_from: str, message_body: str):
    send_text(message_from, f"请进入clash面板操作\n\nhttp://101.126.71.169:9090/ui\n\n1fab91cf8aa2c79b3c2b2305d87568a5757e4cca23346b12454e7355223d5082")

def show_help(message_from: str, message_body: str):
    send_text(message_from, f"#帮助\n#删除聊天记录\n#删除过期信息\n#日志\n#代理")
command_dict = {
    "#帮助": show_help,
    "#删除聊天记录": delate_chat_history_task,
    "#删除过期信息": delete_expired_information,
    "#日志":show_log,
    "#代理":change_proxy,
}