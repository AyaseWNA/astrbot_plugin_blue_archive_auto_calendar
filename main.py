import asyncio
import os
from .generate_pic.genetate import generate_day_schedule
from datetime import datetime, timedelta
import json

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger # 使用 astrbot 提供的 logger 接口
from astrbot.api.event import MessageChain
from astrbot.api import AstrBotConfig

# def _get_platform_id(context):
#     """获取平台ID"""
#     try:
#         if hasattr(context.bot_manager, '_context') and context.bot_manager._context:
#             bot_manager = context.bot_manager
#             if hasattr(bot_manager, '_context') and bot_manager._context:
#                 context_obj = bot_manager._context
#                 if hasattr(context_obj, 'platform_manager') and hasattr(context_obj.platform_manager, 'platform_insts'):
#                     platforms = context_obj.platform_manager.platform_insts
#                     for platform in platforms:
#                         if hasattr(platform, 'metadata') and hasattr(platform.metadata, 'id'):
#                             platform_id = platform.metadata.id
#                             return platform_id
#         return "aiocqhttp"  # 默认值
#     except Exception as e:
#         return "aiocqhttp"  # 默认值

         
@register("schaledb_calendar", "author", "一个简单的 Hello World 插件", "1.0.0", "repo url")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # 设置定时任务
        asyncio.create_task(self.set_schedule())

    @filter.command("日历")
    async def send_calendar(self, event: AstrMessageEvent, server: str):
        umo = event.unified_msg_origin
        # 生成并保存图片
        img = await generate_day_schedule(server)
        temp_dir = ".temp"
        os.makedirs(temp_dir, exist_ok=True)

        img_path = os.path.join(temp_dir, f"{server}_pic.png")
        img.save(img_path,"PNG")
        logger.info(umo)
        # 发送图片
        message_chain = MessageChain().file_image(img_path)
        await self.context.send_message(umo, message_chain)
        logger.info(f" {umo} 图片发送成功")
    
    @filter.command("启用日历")
    async def switch_on(self, event: AstrMessageEvent,server: str):
        """
        启用日历命令，获取对话umo并持久保存在../plugin_data/schaledb_calendar/umo.json中

        Args:
            server: 服务器名称，cn/jp/global
        """
        try:
            # 确保路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            plugin_root = os.path.join(current_dir, "..", "..")
            file_path = os.path.join(plugin_root, "plugin_data", "schaledb_calendar", "umo.json")
            file_path = os.path.normpath(file_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 创建数据字典并继承旧数据
            data_dict = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data_dict = json.load(f)
                except json.JSONDecodeError:
                    data_dict = {}

            # 组合umo以及服务器名称
            umo = event.unified_msg_origin
            data_dict[umo] = server
            logger.info({umo: server})

            # 保存数据
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"启用日历出错：{e}")
        else:
            yield event.plain_result(f"已启用本聊天{server}日历推送")
    
    @filter.command("禁用日历")
    async def switch_off(sel ,event: AstrMessageEvent,):
        """
        禁用日历命令，删除对话umo
        """
        # 确保路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_root = os.path.join(current_dir, "..", "..")
        file_path = os.path.join(plugin_root, "plugin_data", "schaledb_calendar", "umo.json")
        file_path = os.path.normpath(file_path)

        umo = event.unified_msg_origin
        data_dict = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)

        try:
            del data_dict[umo]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"已禁用umo: {umo}")
        except Exception as e:
            logger.error(f"禁用umo出错: {e}")
        else:
            yield event.plain_result(f"已禁用{umo}日历推送")
    async def send(self, umo, server):
        # 生成并保存图片
        img = await generate_day_schedule(server)
        temp_dir = ".temp"
        os.makedirs(temp_dir, exist_ok=True)

        img_path = os.path.join(temp_dir, f"{server}_pic.png")
        img.save(img_path,"PNG")

        # 发送图片
        message_chain = MessageChain().file_image(img_path)
        await self.context.send_message(umo, message_chain)
        logger.info(f" {umo} 图片发送成功")
    

    async def set_schedule(self):
        """
        获取配置并设置定时任务
        """
        auto_send_time = self.config["auto_send_time"]

        # 确保路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_root = os.path.join(current_dir, "..", "..")
        file_path = os.path.join(plugin_root, "plugin_data", "schaledb_calendar", "umo.json")
        file_path = os.path.normpath(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 读取持久化配置文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                group_ids_and_servers = json.load(f)
        except Exception as e:
            logger.error(f"读取持久化配置文件出错: {e}")
            group_ids_and_servers = {}
        else:
            logger.info(f"读取持久化配置文件成功")

        # 调用函数设置定时任务
        try:
            await self.schedule_send_loop(auto_send_time, group_ids_and_servers)
            logger.info(f"定时任务已启动，目标时间: {auto_send_time}")
        except Exception as e:
            logger.info(f"定时任务启动失败 {e}")

    

    async def schedule_send_loop(self, auto_send_time, group_ids_and_servers):
        """
        定时触发发送函数
        
        Args:
            auto_send_time: 定时执行的目标时间字符串，格式为("%H:%M")
            group_ids_and_servers: 包含目标group_id的列表
        """
        while True:
            try:
                now = datetime.now()
                target_time = datetime.strptime(auto_send_time, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day
                )


                if now >= target_time:
                    target_time += timedelta(days=1)
                    
                wait_seconds = (target_time - now).total_seconds()
                logger.info(f"将在 {target_time} 发送消息到群组 ，等待 {wait_seconds:.0f} 秒")
                
                await asyncio.sleep(wait_seconds)
                
                # TODO 添加错误验证功能
                # 循环遍历group_ids_and_servers列表并执行发送操作
                for umo, servers in group_ids_and_servers.items():
                    servers_list = servers.split("/")
                    for server in servers_list:
                        await self.send(umo, server)
                        logger.info(f"定时消息发送完成，umo: {umo}, Server: {server}")
                    
            except Exception as e:
                logger.error(f"定时发送错误: {e}")
                await asyncio.sleep(300)

