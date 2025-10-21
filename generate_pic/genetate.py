

import asyncio
import datetime
import math
import time

import aiohttp
from .gamekee_calendar import transform_gamekee_calendar
from .schaledb_calendar import transform_schaledb_calendar
from .draw import create_image, draw_item, draw_rec, draw_text, draw_title
from astrbot.api import logger


event_data = {
    'jp': [],
    'cn': [],
    'global': [],
    'en-jp': [],
    'db-jp': [],
    'db-global': []
}

lock = {
    'jp': asyncio.Lock(),
    'cn': asyncio.Lock(),
    'global': asyncio.Lock(),
    'en-jp': asyncio.Lock(),
    'db-jp': asyncio.Lock(),
    'db-global': asyncio.Lock(),
}

event_updated = {
    'jp': '',
    'cn': '',
    'global': '',
    'en-jp': '',
    'db-jp': '',
    'db-global': ''
}

data_source = {
    'jp': 'gamekee',
    'cn': 'gamekee',
    'global': 'gamekee',
    'en-jp': 'schaledb',
    'db-jp': 'schaledb',
    'db-global': 'schaledb'
}

gamekee_server = {
    '日服': 15,
    '国服': 16,
    '国际服': 17
}

server_name = {
    'jp': '日服',
    'cn': '国服',
    'global': '国际服',
    'en-jp': '日服',
    'db-jp': '日服',
    'db-global': '国际服'
}

# schaledb载入活动数据并存入全局event_data[server]
async def load_event_schaledb(server):
    data = ''
    try:
        data = await transform_schaledb_calendar(server)
        if data == None:
            print('解析ba日程表失败')
            return 1
    except:
        print('解析ba日程表失败')
        return 1
    if data:
        if server == "jp":
            event_data['db-jp'] = []
        else:
            event_data['db-global'] = []
        for item in data:
            start_time = datetime.datetime.strptime(item['start'], r"%Y/%m/%d %H:%M")
            end_time = datetime.datetime.strptime(item['end'], r"%Y/%m/%d %H:%M")
            event = {'title': item['title'], 'start': start_time, 'end': end_time, 'type': 1}
            if '倍' in event['title']:
                event['type'] = 2
            elif '总力战' in event['title'] or '演习' in event['title'] or '演習' in event['title']:
                event['type'] = 3
            if server == "jp":
                event_data['db-jp'].append(event)
            else:
                event_data['db-global'].append(event)
        return 0
    return 1

# gamekee载入活动数据并存入全局event_data[server]
async def load_event_gamekee(server):
    try:
        gamekee_data = []
        async with aiohttp.ClientSession() as session:
            session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            session.headers['Game-Alias'] = 'ba'
            async with session.get('https://ba.gamekee.com/v1/wiki/index') as resp:
                res = await resp.json()
                for item in res["data"]:
                    if item["module"]["name"] == "活动周历":
                        gamekee_data = item["list"]
                        break
            for sn, sid in gamekee_server.items():
                pool_dic = {}
                async with session.get(f'https://www.gamekee.com/v1/cardPool/query-list?order_by=-1&card_tag_id'
                                       f'=&keyword=&kind_id=6&status=0&serverId={sid}') as resp:
                    res = await resp.json()
                    gacha_data = res["data"]
                    for pool in gacha_data:
                        if pool["end_at"] > time.time():
                            if str(pool["end_at"]) in pool_dic:
                                pool_dic[str(pool["end_at"])].append(pool)
                            else:
                                pool_dic[str(pool["end_at"])] = [pool]
                        else:
                            break
                    for pools in pool_dic.values():
                        pool_title = []
                        for pool in pools:
                            pool_title.append(pool["name"])
                        if len(pool_title) == 0:
                            continue
                        gamekee_data.append(
                            {
                                "title": f"{sn}卡池：{'、'.join(pool_title)}",
                                "begin_at": pools[0]["start_at"],
                                "end_at": pools[0]["end_at"],
                                "pub_area": sn
                            }
                        )
        if gamekee_data == []:
            print('gamekee数据错误')
            return 1
        data = transform_gamekee_calendar(server, gamekee_data)
        if data == None:
            print('解析ba日程表失败')
            return 1
    except Exception as e:
        print('解析ba日程表失败: ', e)
        return 1
    if data:
        if server == "jp":
            event_data['jp'] = []
        elif server == "cn":
            event_data['cn'] = []
        else:
            event_data['global'] = []
        for item in data:
            start_time = datetime.datetime.fromtimestamp(item["start"])
            end_time = datetime.datetime.fromtimestamp(item["end"])
            event = {'title': item['title'], 'start': start_time, 'end': end_time, 'type': 1}
            if '倍' in event['title']:
                event['type'] = 2
            elif '总力' in event['title'] or '演习' in event['title']:
                event['type'] = 3
            if server == "jp":
                event_data['jp'].append(event)
            elif server == "cn":
                event_data['cn'].append(event)
            else:
                event_data['global'].append(event)
        return 0
    return 1

# TODO应用逻辑 记得修复测试逻辑
# TODO 添加日志信息
async def load_event(server):

    if server == 'jp':
        flag =  await load_event_gamekee("jp")
        if flag == 0 and event_data['jp']:
            data_source['jp'] = 'gamekee'
            logger.info("获取gamekee日服信息成功")
        else:
            logger.info("gamekee信息异常，启用schaledb信息")
            flag = await load_event_schaledb("jp")
            if flag == 0 and event_data['db-jp']:
                data_source['jp'] = 'schaledb'
            else:
                logger.info("schaledb信息异常，所有信息源获取失败")
        
    if server == 'cn':
        flag =  await load_event_gamekee("cn")
        if flag == 0 and event_data['cn']:
            data_source['cn'] = 'gamekee'
            logger.info("获取gamekee国服信息成功")
        else:
            logger.info("gamekee信息异常，获取失败")

    
    elif server == 'global':
        flag =  await load_event_gamekee("global")
        if flag == 0 and event_data['global']:
            data_source['global'] = 'gamekee'
            logger.info("获取gamekee国际服信息成功")
        else:
            logger.info("gamekee信息异常，启用schaledb信息")
            flag = await load_event_schaledb("global")
            if flag == 0 and event_data['db-global']:
                data_source['global'] = 'schaledb'
            else:
                logger.info("schaledb信息异常，所有信息源获取失败")

    
# 计算活动时间并返回处理好的活动列表
async def get_events(server, offset, days):
    events = []
    ba_now = datetime.datetime.now()
    if ba_now.hour < 4:
        ba_now -= datetime.timedelta(days=1)
    ba_now = ba_now.replace(hour=18, minute=0, second=0, microsecond=0)  # 用晚6点做基准

    await lock[server].acquire()
    try:
        t = ba_now.strftime('%y%m%d')
        if event_updated[server] != t:
            if await load_event(server) == 0:
                event_updated[server] = t
    finally:
        lock[server].release()

    start = ba_now + datetime.timedelta(days=offset)
    end = start + datetime.timedelta(days=days)
    end -= datetime.timedelta(hours=8)

    for event in event_data[server]:
        if end > event['start'] and start < event['end']:  # 在指定时间段内 已开始 且 未结束
            event['start_days'] = math.ceil((event['start'] - start) / datetime.timedelta(days=1))  # 还有几天开始
            event['left_days'] = math.floor((event['end'] - start) / datetime.timedelta(days=1))  # 还有几天结束
            events.append(event)
    events.sort(key=lambda item: item["type"] * 100 - item['left_days'], reverse=True)  # 按type从大到小 按剩余天数从小到大
    return events

def get_ba_now(offset):
    ba_now = datetime.datetime.now()
    if ba_now.hour < 4:
        ba_now -= datetime.timedelta(days=1)
    ba_now = ba_now.replace(hour=18, minute=0, second=0, microsecond=0)  # 用晚6点做基准
    ba_now = ba_now + datetime.timedelta(days=offset)
    return ba_now

# 生成日活动image
async def generate_day_schedule(server='jp'):
    """
    用来生成不同服务器的日历图片
    参数:
        server (str): 服务器区域代码，可选值包括：
                      'jp' - 日服
                      'cn' - 国服
                      'global' - 国际服

    返回:
        PIL.Image.Image: 生成的活动日程图片对象，可进一步保存或展示。
    """
    events = await get_events(server, 0, 7)
    
    logger.info(f"获取到 {len(events)} 个活动")

    has_prediction = False
    title_len = 25
    for event in events:
        if event['start_days'] > 0:
            has_prediction = True
        title_len = max(title_len, len(event['title']) + 5)
    
    # 计算图片行数：标题行(1) + 活动行数 + 预测标题行(0或1) + 信息行(1)
    if has_prediction:
        total_rows = 1 + len(events) + 1 + 1
    else:
        total_rows = 1 + len(events) + 1
    
    logger.info(f"has_prediction={has_prediction}, total_rows={total_rows}, title_len={title_len}")
    im = create_image(total_rows, title_len)

    title = f'碧蓝档案{server_name[server]}活动'
    ba_now = get_ba_now(0)
    draw_title(im, 0, title, ba_now.strftime('%Y/%m/%d'), '正在进行')

    if len(events) == 0:
        draw_item(im, 1, 1, '无数据', 0)
        i = 2
    else:
        i = 1
        for event in events:
            if event['start_days'] <= 0:
                logger.info(f"绘制活动 {i}: {event['title']}")
                draw_item(im, i, event['type'], event['title'], event['left_days'])
                i += 1
        
        if has_prediction:
            logger.info(f"绘制预测标题行 {i}")
            draw_title(im, i, right='即将开始')
            for event in events:
                if event['start_days'] > 0:
                    i += 1
                    logger.info(f"绘制预测活动 {i}: {event['title']}")
                    draw_item(im, i, event['type'], event['title'], -event['start_days'])
    
    # 添加数据来源和bot信息行
    logger.info(f"绘制信息行 {i}, 数据来源：{data_source[server]}")
    draw_title(im, i, left=f'data by {data_source[server]}', right='bot by astrbot')
    
    return im

if __name__ == '__main__':
    # 方法1：直接运行并保存图片
    async def main():
        im = await generate_day_schedule("jp")
        im.save(r"C:\Users\18367\Downloads\schedule.png", "PNG")
        print("图片已保存为 schedule.png")
    
    asyncio.run(main())
    
    # 或者方法2：分别测试
    # print(asyncio.run(get_events("global", 0, 7)))
    # asyncio.run(main())

    # print(event_data)