import json
import uuid
from app.chatgpt.billing import BillingQuery
from app.chatgpt.client import analyze_text, run_conversation
from app.chatgpt.tokens import limit_tokens_in_messages
from app.sql import crud
from app.sql.database import SessionLocal
from app.sql.models import Messages
from app.whatsapp_api.chat import send_text
import config
from app.logger import logger

def generate_html_table(csv_data: str):
    """
    生成HTML表格，将CSV数据转换为带有样式的HTML表格，并将其保存为HTML文件。
    
    参数:
    csv_data: str - 包含CSV数据的字符串，每行为一个记录，记录内部字段以逗号分隔。
    
    返回值:
    str - 生成表格的HTML文件的访问URL。
    """
    # 将CSV数据解析为二维列表
    data = [line.split(',') for line in csv_data.split('\n')]
    # 初始化HTML字符串
    html = "<table>\n"
    # 遍历数据行，生成HTML表格
    for i, row in enumerate(data):
        if i == 0:
            # 为表头行添加样式
            html += "  <tr class='header'>\n"
            for col in row:
                html += f"    <th>{col}</th>\n"
            html += "  </tr>\n"
        else:
            # 为数据行添加样式
            html += "  <tr>\n"
            for col in row:
                html += f"    <td>{col}</td>\n"
            html += "  </tr>\n"
    html += "</table>"
    
    # 定义内嵌CSS样式，用于美化表格
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
    
    # 生成唯一的文件名，以避免文件覆盖
    unique_filename = f"{uuid.uuid4()}"
    
    # 将HTML内容保存到文件中
    with open(f"table_html/{unique_filename}.html", "w", encoding="utf-8") as html_file:
        html_file.write((css + html))
    
    # 构造并返回HTML文件的访问URL
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
    """
    保存商品信息到数据库。
    
    参数:
    - message: Messages 类型，包含需要分析的消息内容。
    
    无返回值。
    """
    db = SessionLocal()  # 建立数据库会话
    logger.info(f"{message.id}号消息开始分析数据")
    
    # 将消息内容按行分割
    message_content_list = str(message.message_content).split("\n")
    max_lines = 30  # 每次处理的最大行数
    count = 0  # 记录处理的轮数
    
    try:
        # 分块处理消息内容，并分析每块文本中的商品信息
        for index in range(0, len(message_content_list), max_lines):
            count = count + 1
            chunk_list = message_content_list[
                index : min(index + max_lines, len(message_content_list))
            ]
            chunk_text = "\n".join(chunk_list)  # 将分块的文本重新组合
            
            # 分析文本中是否包含商品信息
            goods_info = analyze_text(chunk_text)

            if goods_info.is_include_commodity_information == True:
                logger.info(f"{message.id}号消息第{count}轮分析包含商品信息")
                # 遍历分析出的商品信息，并将其保存到数据库中
                for info in goods_info.information:
                    existing_info = crud.get_goods_information_by_detail(
                        db, info.detail
                    )
                    if existing_info is None:
                        crud.create_goods_information(
                            db, info.detail, info.price, int(str(message.id))
                        )
                logger.info(f"{message.id}号消息第{count}轮商品信息已添加至数据库")
            else:
                logger.info(f"{message.id}号消息第{count}轮分析不包含商品信息")
    except Exception as e:
        logger.error(f"处理商品信息时发生错误: {e}")
        crud.creat_error_message_record(db, int(str(message.id)), str(e))
        send_text("85292988566@c.us", f"处理{int(str(message.id))}号商品信息时发生错误: {e}")
        send_text("8619871547694@c.us", f"处理{int(str(message.id))}号商品信息时发生错误: {e}")
    finally:
        # 结束消息分析，并关闭数据库会话
        logger.info(f"{message.id}号消息分析数据结束")
        db.close()


def delate_chat_history_task(message_from: str, message_body: str):
    """
    删除指定用户的聊天历史记录。

    参数:
    - message_from: 发送消息的用户标识，格式为"电话号码@域名"。
    - message_body: 消息正文，本函数未使用此参数。

    返回值:
    - 无
    """
    db = SessionLocal()  # 建立数据库会话
    phone_number = message_from.split("@")[0]  # 从用户标识中提取电话号码
    messages = []  # 准备一个空列表，用于存储（此处未使用的）消息
    try:
        crud.update_chat_history(db, phone_number, messages)  # 更新数据库，删除指定用户的聊天记录
        send_text(message_from, "聊天记录已删除。")  # 发送文本消息，通知用户聊天记录已删除
    finally:
        db.close()  # 关闭数据库会话


def delete_expired_information(message_from: str, message_body: str):
    """
    从数据库中删除过期的信息，并向指定用户发送删除成功的文本消息。
    
    参数:
    - message_from: 发送消息的用户标识
    - message_body: 消息的内容，本函数未使用该参数
    
    返回值:
    - 无
    """
    db = SessionLocal()  # 建立数据库会话
    
    try:
        # 删除30天前的过期商品信息，并返回删除结果
        res = crud.delete_expired_goods_information(db, 30)
        # 向用户发送删除成功的消息
        send_text(message_from, f"已删除{res.expiration_date}前的{res.count}条信息。")
    finally:
        # 确保最后关闭数据库会话
        db.close()

def show_log(message_from: str, message_body: str):
    url = f"{config.FILE_URL}/logs?secret_key={config.SECRET_KEY}"
    send_text(message_from, f"👇点击链接查看日志\n🔗{url}")

def change_proxy(message_from: str, message_body: str):
    send_text(message_from, f"👇请进入clash面板操作\n\nhttp://101.126.71.169:9090/ui")

def show_help(message_from: str, message_body: str):
    send_text(message_from, f"#帮助\n#删除聊天记录\n#删除过期信息\n#日志\n#代理")

def query_billing(message_from: str, message_body: str):
    query = BillingQuery(http_proxy=config.HTTP_PROXY)
    result = query.query_one(api_key=config.OPENAI_API_KEY)
    if result.success :
        send_text(message_from, f"当前额度：{result.data.total_available} \n 总额度：{result.data.total_granted} \n 使用量：{result.data.total_used} \n 开始时间：{result.data.start_date} \n 结束时间：{result.data.end_date} ") #type: ignore
    else:
        send_text(message_from, f"查询失败：{result.messsage}")
command_dict = {
    "#帮助": show_help,
    "#删除聊天记录": delate_chat_history_task,
    "#删除过期信息": delete_expired_information,
    "#日志":show_log,
    "#代理":change_proxy,
    "#查询余额":query_billing,
}