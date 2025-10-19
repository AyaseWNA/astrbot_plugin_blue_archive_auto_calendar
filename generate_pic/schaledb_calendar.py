import datetime
import asyncio
import json
import logging
import os
import base64
from io import BytesIO
import aiohttp

def get_base_dir():
    return os.path.dirname(__file__)


def get_config():
    with open(os.path.join(get_base_dir(), 'config.json'), encoding='utf8') as f:
        config = json.load(f)
    return config


def get_base_url():
    try:
        config = get_config()
        return config["base_url"]
    except Exception as e:
        logging.error("配置获取失败，请检查插件目录下的config.json文件")
        logging.error(e)
        return "http://124.223.25.80:40000/"


def img_to_base64str(img):
    io = BytesIO()
    img.save(io, 'png')
    base64_str = f"base64://{base64.b64encode(io.getvalue()).decode()}"
    return base64_str


def img_content_to_base64str(content):
    return f"base64://{base64.b64encode(content).decode()}"


def img_content_to_cqcode(content):
    return f"[CQ:image,file={img_content_to_base64str(content)}]"


async def get_json_data(url, proxies=None):
    for i in range(2):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15, proxy=proxies) as res:
                    if res.status == 200:
                        data = await res.json()
                        return data
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(3)
            continue
    return None


async def get_img_content(url, proxies=None):
    for i in range(2):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as r:
                    content = await r.read()
                    if r.status == 200:
                        return content
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(3)
            continue
    return None

# 修复查询语句
def get_item(dic, key, value):
    # 如果是字典结构（键值对），遍历值
    if isinstance(dic, dict):
        for item in dic.values():
            if isinstance(item, dict) and item.get(key) == value:
                return item
    # 如果是列表结构，保持原有逻辑
    elif isinstance(dic, list):
        for item in dic:
            if isinstance(item, dict) and item.get(key) == value:
                return item
    return None

def get_default_server(gid):
    try:
        path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(path, encoding='utf8') as f:
            group_data = json.load(f)
    except Exception as e:
        logging.error(e)
        return "jp"
    if str(gid) not in group_data or len(group_data[str(gid)]["server_list"]) == 0:
        return "jp"
    server = group_data[str(gid)]["server_list"][0]
    if "jp" in server:
        return "jp"
    elif server == "cn":
        return "cn"
    elif "global" in server:
        return "global"
    
#-----------------------------------------------------------------------------------------------------------------------

base_url = get_base_url()
common = base_url + "SchaleDB/data/config.json"
localization = base_url + "SchaleDB/data/cn/localization.json"
raids = base_url + "SchaleDB/data/cn/raids.min.json"
student_cn = base_url + "SchaleDB/data/cn/students.min.json"
student_jp = base_url + "SchaleDB/data/jp/students.min.json"

# 获取日历数据并输出
async def extract_calendar_data(server):
    event_list = []

    common_data = await get_json_data(common)
    student_data = await get_json_data(student_cn)
    localization_data = await get_json_data(localization)
    raid_data = await get_json_data(raids)
    if common_data is None or student_data is None or localization_data is None or raid_data is None:
        return None

    if server == "jp":
        data = common_data["Regions"][0]
    else:
        data = common_data["Regions"][1]

    # gacha 正常
    for gacha in data["CurrentGacha"]:
        characters = gacha["characters"]
        for character in characters:
            stu_info = get_item(student_data, "Id", character)
            title = "本期卡池: " + stu_info["Name"]
            start_time = datetime.datetime.fromtimestamp(gacha["start"]).strftime("%Y/%m/%d %H:%M")
            end_time = datetime.datetime.fromtimestamp(gacha["end"]).strftime("%Y/%m/%d %H:%M")
            event_list.append({'title': title, 'start': start_time, 'end': end_time})

    # event
    for event in data["CurrentEvents"]:
        event_rerun = ""
        event_id = event["event"]
        # 复刻活动似乎是在原id前面加上10
        if event_id > 1000:
            event_id = str(event_id)[2:]
            event_rerun = "(复刻)"
        event_name = localization_data["EventName"][str(event_id)] + event_rerun
        start_time = datetime.datetime.fromtimestamp(event["start"]).strftime("%Y/%m/%d %H:%M")
        end_time = datetime.datetime.fromtimestamp(event["end"]).strftime("%Y/%m/%d %H:%M")
        event_list.append({'title': event_name, 'start': start_time, 'end': end_time})

    # raid
    for raid in data["CurrentRaid"]:
        raid_tpye = raid["type"]
        raid_id = raid["raid"]
        title = ""

        # 总力 
        if raid_tpye == "Raid":
            raid_info = get_item(raid_data["Raid"], "Id", raid_id)
            title = "总力战: " + raid_info["Name"]
            if "terrain" in raid:
                title = title + f'({raid["terrain"]})'
        # 演习
        if raid_tpye == "TimeAttack":
            dungeon_types = {"Shooting": "射击", "Defense": "防御", "Destruction": "突破"}
            raid_info = get_item(raid_data["TimeAttack"], "Id", raid_id)
            title = raid_info["DungeonType"]
            if raid_info["DungeonType"] in dungeon_types:
                title = dungeon_types[raid_info["DungeonType"]]
            title += "演习"
            if "Terrain" in raid_info:
                title = title + f'({raid_info["Terrain"]})'
        # 世界boss
        if raid_tpye == "WorldRaid":
            raid_info = get_item(raid_data["WorldRaid"], "Id", raid_id)
            title = raid_info["Name"]

        # TODO 爬塔
        if raid_tpye == 'MultiFloorRaid':
            pass

        # 处理时间
        if title != "":
            start_time = datetime.datetime.fromtimestamp(raid["start"]).strftime("%Y/%m/%d %H:%M")
            end_time = datetime.datetime.fromtimestamp(raid["end"]).strftime("%Y/%m/%d %H:%M")
            event_list.append({'title': title, 'start': start_time, 'end': end_time})
    return event_list

async def transform_schaledb_calendar(server):
    data = await extract_calendar_data(server)
    return data

if __name__ == '__main__':
    print(asyncio.run(extract_calendar_data("jp")))

