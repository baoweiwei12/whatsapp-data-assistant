from datetime import datetime
import logging
from openai import OpenAI
import json
from app import config
from app.sql import crud
from app.sql.database import SessionLocal
import csv
import io

logger = logging.getLogger("whatsapp")
client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)


def get_group_messages_from_db_to_csv(
    limit: int = 20,
    start_timestamp: str | None = None,
    end_timestamp: str | None = None,
    search_content: str | None = None,
    sender_phone_number: str | None = None,
    sender_display_name: str | None = None,
):
    try:
        logger.info(f"正在查询聊天记录")
        db = SessionLocal()
        group_messages = crud.get_group_messages(
            db,
            limit,
            start_timestamp,
            end_timestamp,
            search_content,
            sender_phone_number,
            sender_display_name,
        )

        # 使用内存中的缓冲区来构建CSV格式的数据
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入列名
        writer.writerow(
            [
                "timestamp",
                "sender_phone_number",
                "sender_display_name",
                "message_content",
                "group_id",
            ]
        )

        # 写入每条群组消息的数据
        for group_message in group_messages:
            writer.writerow(
                [
                    group_message.timestamp,
                    group_message.sender_phone_number,
                    group_message.sender_display_name,
                    group_message.message_content,
                ]
            )

        # 获取CSV格式的字符串并返回
        output.seek(0)
        csv_data = output.getvalue()
        logger.info(f"查询成功")
        return csv_data
    except Exception as e:
        logger.error(f"函数运行失败:{e}")
        return f"函数运行失败:{e}"
    finally:
        db.close()


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_group_messages_from_db_to_csv",
            "description": "Retrieve group messages based on specified filters such as date range, content, sender's phone number, and sender's display name",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of messages to retrieve (default is 20)",
                    },
                    "start_timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The start timestamp in the format %Y-%m-%d %H:%M:%S for filtering messages",
                    },
                    "end_timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The end timestamp in the format %Y-%m-%d %H:%M:%S for filtering messages",
                    },
                    "search_content": {
                        "type": "string",
                        "description": "The keyword to search within message content",
                    },
                    "sender_phone_number": {
                        "type": "string",
                        "description": "The phone number of the message sender for filtering messages",
                    },
                    "sender_display_name": {
                        "type": "string",
                        "description": "The display name of the message sender for filtering messages",
                    },
                },
            },
            "required": [],
        },
    }
]

available_functions = {
    "get_group_messages_from_db_to_csv": get_group_messages_from_db_to_csv,
}

system_prompt = f"现在的时间是{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},你是ChatGPT，你需要在群组的历史消息中检索数据，函数会为你返回CSV格式的历史聊天记录，你需要根据这些聊天记录回答用户的问题，你需要关注和商品信息有关的聊天记录。"


def run_conversation(messages: list):
    model = config.OPENAI_MODEL
    messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,  # type: ignore
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return second_response
    else:
        return response
