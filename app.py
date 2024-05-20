import json
import os
import re
from datetime import datetime
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import requests
import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import dashscope
from apscheduler.schedulers.asyncio import AsyncIOScheduler

CAIYUN_API_KEY = os.environ.get("CAIYUN_API_KEY", "abc")

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
app = FastAPI()
origins = [
    "http://localhost:8080",  # 你的前端应用地址
    # "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()


class ConfItem(BaseModel):
    username: str
    cityname: str
    concern: str
    scheduler: Optional[str]
    rate: Optional[int]


class TriggerItem(BaseModel):
    username: str
    coordinate: str
    datetime: str
    nowcast: str
    forecast: str
    alert: str


def sample_sync_call(prompt_text, model="qwen-plus"):
    resp = dashscope.Generation.call(model=model, prompt=prompt_text)
    if resp.status_code == HTTPStatus.OK:
        print(f"resp: {resp}")
        return resp.output


def push_message(queue_name, message):
    """
    将消息压入 Redis 队列。

    参数:
    queue_name -- 队列的名字
    message -- 要压入的消息
    """
    try:
        r.rpush(queue_name, message)
    except Exception as e:
        print(f"push_message error: {e}")
        return False
    return True


def pop_message(queue_name):
    """
    从 Redis 队列中取出消息。

    参数:
    queue_name -- 队列的名字

    返回:
    取出的消息，如果队列为空，则返回 None
    """
    message = r.lpop(queue_name)
    if message is not None:
        return message


@app.get("/")
async def smoke():
    return {"message": "Hello World"}


def worker():
    task_data_str = pop_message("task")
    if task_data_str is not None:
        task_data = json.loads(task_data_str)
        username = task_data["username"]
        key = f"conf:{username}"
        data = r.get(key)
        if data:
            conf_data = json.loads(data)
        print(f"conf_data: {conf_data}")
        if conf_data:
            concern = conf_data["concern"]
            scheduler = conf_data["scheduler"]
            cityname = conf_data["cityname"]
            sense_rate = int(conf_data["rate"])

        if cityname == "自动定位":
            coordinate_str = task_data["coordinate"]
            lon, lat = coordinate_str.split(",")
        else:
            url = f"https://api.caiyunapp.com/fcgi-bin/v1/text2coord.py?address={cityname}"
            resp = requests.get(url)
            if resp.ok:
                result = resp.json()
                lon, lat = result["coord"]["lng"], result["coord"]["lat"]

        now_time_str = task_data["datetime"]
        now_time = datetime.fromisoformat(now_time_str).replace(
            tzinfo=timezone(timedelta(hours=8))
        )
        nowcast_str = task_data.get("nowcast")
        forecast_str = task_data.get("forecast")
        alert_str = task_data.get("alert")
        print(
            f"nowcast_str: {type(nowcast_str)}, forecast_str: {type(forecast_str)}, alert_str: {type(alert_str)}"
        )
        result_text = ask_ai(
            lon,
            lat,
            concern,
            scheduler,
            nowcast_str,
            forecast_str,
            alert_str,
            now_time,
            username,
        )
        # 风险等级1：今天下午到明天中午多云转晴，无降水，打车上班畅通无阻。保持好心情，出行注意防晒。
        match = re.search(r"风险等级(\d+)", result_text)
        if match:
            risk_level_str = match.group(1)
            risk_level = int(risk_level_str)
            record_log(username, f"AI识别的风险等级: {risk_level}")
        else:
            print("没有找到匹配的风险等级")
            risk_level = -1

        queue_name = f"notification:{username}"
        noti_level = 5 - sense_rate
        print(f"risk_level: {risk_level}, noti_level: {noti_level}")
        record_log(username, f"根据用户的设置，通知的等级阈值: {noti_level}")
        if risk_level > noti_level:
            final_text = result_text.replace(f"风险等级{risk_level_str}：", "").replace(
                f"风险等级{risk_level_str}:", ""
            )
            record_log(username, f"最终通知文本：{final_text}")
            push_message(queue_name, final_text)
            record_log(username, "已将消息推送到队列中")
            print(f"Pushed message to {queue_name}: {final_text}")
        else:
            record_log(username, "风险等级低于通知等级，不推送消息")
            print(f"Risk level is lower than notification level, no message pushed")


@app.on_event("startup")
async def start_scheduler():
    # 如果计划任务还没有启动，则启动它
    if not scheduler.running:
        scheduler.add_job(worker, "interval", seconds=1)
        scheduler.start()


def record_log(username, message, level="INFO"):
    """
    将消息记录到 Redis 的日志中。

    参数:
    message -- 要记录的消息
    """
    dt = datetime.now(tz=timezone(timedelta(hours=8))).isoformat()
    text = f"{dt} [{level}] {message}"
    r.rpush(f"log:{username}", text)


@app.get("/log/")
def get_log(username: str):
    """
    从 Redis 日志中取出所有消息。

    返回:
    所有消息的列表
    """
    record = r.lpop(f"log:{username}")
    print("record log", record)
    return {"message": record}


@app.get("/notification/")
async def get_notification(username: str):
    queue_name = f"notification:{username}"
    message = pop_message(queue_name)
    if message is None:
        return {"message": "No message"}, 404
    return {"message": message}


@app.post("/trigger")
async def trigger_notification(item: TriggerItem):
    """发送通知任务"""

    task_queue_name = "task"
    task_data = {
        "username": item.username,
        "coordinate": item.coordinate,
        "datetime": item.datetime,
        "nowcast": item.nowcast,
        "forecast": item.forecast,
        "alert": item.alert,
    }
    task_data_str = json.dumps(task_data, ensure_ascii=False)
    res = push_message(task_queue_name, task_data_str)
    if res:
        return {"message": "Task submitted"}
    else:
        return {"message": "Task failed"}, 500


@app.post("/submit_info/")
async def submit_info(item: ConfItem):
    data = {
        "username": item.username,
        "cityname": item.cityname,
        "concern": item.concern,
        "scheduler": item.scheduler,
        "rate": item.rate,
    }

    key = f"conf:{item.username}"
    r.set(key, json.dumps(data, ensure_ascii=False))
    return {"message": "Success"}


@app.get("/info")
async def get_info(username):
    key = f"conf:{username}"
    data = r.get(key)
    if data:
        return json.loads(data)
    return None


def ask_ai(
    lon,
    lat,
    concern,
    scheduler=None,
    minutely=None,
    hourly=None,
    alerts=None,
    dtnow: datetime = None,
    username="Clarmy",
):
    url = f"https://api.caiyunapp.com/v2.6/{CAIYUN_API_KEY}/{lon},{lat}/weather.json?dailysteps=3&alert=true&hourlysteps=24&unit=metric:v2"

    response = requests.get(url)
    if response.ok:
        api_result = response.json()
        server_time = api_result["server_time"]
        if not dtnow:
            dt = datetime.fromtimestamp(server_time, timezone(timedelta(hours=8)))
        else:
            dt = dtnow
        result = api_result["result"]
        if not alerts:
            alerts = result["alert"]["content"]
            if alerts:
                alert_texts = [alert["description"] for alert in alerts]
                alert_all_text = ";".join(alert_texts)
            else:
                alert_all_text = "无预警"
        else:
            alert_all_text = alerts

        if not minutely:
            minutely = result["minutely"]["description"]
            print(f"minutely: {minutely}")
        if not hourly:
            hourly = result["hourly"]["description"]

        data_text = f"当前时间:{dt.isoformat()};分钟级降水预报:{minutely};小时级降水预报:{hourly};预警信息:{alert_all_text}"

    record_log(username, f"收集到的数据: {data_text}")

    base_text = "你是一个风险提示助手,主要根据天气信息以及用户的一些个性化的信息,提供各种与天气相关的风险提示,请根据我发送的相关信息,给出一条简要结论和建议,全部文案内容要压缩在140个字以内。文案中不要提及我的个人职业信息。根据气象信息的危险程度按0-5划分等级,文案的最开头以级别开始,例如'风险等级5'。\n"

    if scheduler is None:
        scheduler = "无"

    prompt_text = base_text + f"我的关注:{concern};我的日程:{scheduler};{data_text}"
    record_log(username, f"提示词: {prompt_text}")
    result = sample_sync_call(prompt_text, "qwen-plus")
    record_log(username, f"返回值: {result}")
    return result["text"]


# 异常处理示例
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"error": exc.detail}


# 运行应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8848)
