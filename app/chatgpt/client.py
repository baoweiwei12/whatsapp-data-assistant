from datetime import datetime
import logging
from typing import List
import httpx
from openai import OpenAI
import json
from pydantic import BaseModel
import config
from app.sql import crud
from app.sql.database import SessionLocal
import csv
import io
import base64
from app.whatsapp_api.chat import send_file

logger = logging.getLogger("whatsapp")
if config.HTTP_PROXY is not None:
    # Clash 代理地址
    custom_http_client = httpx.Client(timeout=10.0, proxies=config.HTTP_PROXY)
else:
    custom_http_client = None
client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL,http_client=custom_http_client)


class GoodsData(BaseModel):
    csv_data: str | None
    csv_base64_data: bytes | None


class FuncGoodsInfoResponse(BaseModel):
    is_matched_info: bool
    goods_data: GoodsData
    message: str | None


def get_goods_info_from_db_to_csv(
    limit: int = 500,
    start_timestamp: str | None = None,
    end_timestamp: str | None = None,
    key_words: str | None = None,
    sender_phone_number: str | None = None,
    sender_display_name: str | None = None,
):
    try:
        logger.info(
            f"正在查询聊天记录 - {limit} - {start_timestamp} - {end_timestamp} - {key_words} - {sender_phone_number} - {sender_display_name}"
        )
        db = SessionLocal()
        goods_infomation = crud.get_goods_information(
            db,
            limit,
            start_timestamp,
            end_timestamp,
            key_words,
            sender_phone_number,
            sender_display_name,
        )
        if len(goods_infomation) == 0:
            return FuncGoodsInfoResponse(
                is_matched_info=False,
                goods_data=GoodsData(csv_data=None, csv_base64_data=None),
                message="没有查询到任何信息",
            )
        # 使用内存中的缓冲区来构建CSV格式的数据
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入列名
        writer.writerow(
            [
                "商品信息发布时间",
                "发布者手机号",
                "发布者昵称",
                "商品详情",
                "价格",
            ]
        )

        # 写入每条群组消息的数据
        for good_info in goods_infomation:
            writer.writerow(
                [
                    good_info.message.timestamp,
                    good_info.message.sender_phone_number,
                    good_info.message.sender_display_name,
                    good_info.detail,
                    good_info.price,
                ]
            )

        # 获取CSV格式的字符串并返回
        output.seek(0)
        csv_data = output.getvalue()
        base64_csv_data = base64.b64encode(csv_data.encode("utf-8"))
        logger.info(f"查询成功")
        return FuncGoodsInfoResponse(
            is_matched_info=True,
            goods_data=GoodsData(csv_data=csv_data, csv_base64_data=base64_csv_data),
            message=None,
        )
    except Exception as e:
        logger.error(f"函数运行失败:{e}")
        return FuncGoodsInfoResponse(
            is_matched_info=False,
            goods_data=GoodsData(csv_data=None, csv_base64_data=None),
            message=f"函数运行失败:{e}",
        )
    finally:
        db.close()


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_goods_info_from_db_to_csv",
            "description": "Retrieve group messages based on specified filters such as date range, content, sender's phone number, and sender's display name",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of goods information (default is 500)",
                    },
                    "start_timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The start timestamp in the format %Y-%m-%d %H:%M:%S for goods information",
                    },
                    "end_timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The end timestamp in the format %Y-%m-%d %H:%M:%S for goods information",
                    },
                    "key_words": {
                        "type": "string",
                        "description": "The keywords to search within goods information detail",
                    },
                    "sender_phone_number": {
                        "type": "string",
                        "description": "The phone number of the goods information sender for filtering information",
                    },
                    "sender_display_name": {
                        "type": "string",
                        "description": "The display name of the goods information sender for filtering information",
                    },
                },
            },
            "required": [],
        },
    }
]

available_functions = {
    "get_goods_info_from_db_to_csv": get_goods_info_from_db_to_csv,
}

system_prompt = f"现在的时间是{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},你是ChatGPT手表商品查询助手，你需要在数据库中检索商品数据，这些商品数据都是关于手表的，函数会为你返回CSV格式的手表商品信息，你需要根据这些手表商品信息回答用户的问题，回答时需要附带商品信息发布时间,发布者手机号,发布者昵称,商品详情,价格,以清晰的方式呈现,商品详情请原样展示，不要省略任何。"

from openai.types.chat import ChatCompletion


class RunConResponese(BaseModel):
    func_data: str | None
    chat_completion: ChatCompletion


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
            if function_response.is_matched_info:
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response.goods_data.csv_data,
                    }
                )
            else:
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response.message,
                    }
                )
        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return RunConResponese(
            func_data=function_response.goods_data.csv_data,
            chat_completion=second_response,
        )
    else:
        return RunConResponese(func_data=None, chat_completion=response)


class AnalyzeDataError(Exception):
    pass


class Info(BaseModel):
    detail: str
    price: int | None


class GoodsInfo(BaseModel):
    is_include_commodity_information: bool
    information: List[Info]


def analyze_text(text: str):
    model = "gpt-3.5-turbo-0125"
    system_prompt = """
作为一个助手，你的任务是从消息中提取商品信息。如果消息中不包含商品信息，请将 "is_include_commodity_information" 设置为 false，并确保 "information" 属性为空数组。如果消息中包含商品信息，请提取所有商品信息并放入 "information" 数组中。务必筛选出所有可能的商品信息，并尽可能多地提取商品信息,有些商品可能只有折扣没有价格，你也需要提取出来，设置price为null即可。以下是需要返回的 JSON 消息示例。注意：不要漏掉任何一条可能的商品信息。

<json消息示例>
{
    "is_include_commodity_information": true,
    "information": [
        {
            "detail": "4962/200R $208000 1/2024",
            "price":208000
        },
        {
            "detail": "126720vtnr jub n2🏷$141000",
            "price": 141000
        },
        {
            "detail": "5100-1140-52A - 38%",
            "price": null
        },
        {
            "detail": "42410402001003 - 38%",
            "price": null
        },
        {
            "detail": "311.92.44.30.01.001 $84,600 -8%",
            "price": 84600
        },
        {
            "detail": "116244 Rhodium Floral Motif Both Tag Warranty Card 2014 $77,800",
            "price": 77800
        }
    ]
}
</json消息示例>
"""

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0,
        max_tokens=4096,
    )
    json_message = response.choices[0].message.content
    if json_message is None:
        raise AnalyzeDataError("json_message为空")
    message_dict = json.loads(json_message)

    return GoodsInfo(**message_dict)
