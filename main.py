import asyncio
import os
from .generate_pic.genetate import generate_day_schedule
from datetime import datetime, timedelta

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
    async def send(self, group_id, server):
        # 获取平台ID并组合为发送umo（似乎新版本直接整合了消息平台为default，Soulter我的超人！！！）
        # platform_id = _get_platform_id(self.context)
        umo = f"default:GroupMessage:{group_id}" if group_id else None
        
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
        group_ids_and_servers = self.config["group_ids_and_servers"]

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
            group_ids: 包含目标group_id的列表
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
                
                # 循环遍历group_ids_and_servers列表并执行发送操作
                for group_and_servers_info in group_ids_and_servers:
                    group_info = group_and_servers_info.split(":")
                    group_id = group_info[0]
                    servers = group_info[1].split(",")
                
                    for server in servers:
                        await self.send(group_id, server)
                        logger.info(f"定时消息发送完成，Group ID: {group_id}, Server: {server}")
                    
            except Exception as e:
                logger.error(f"定时发送错误: {e}")
                await asyncio.sleep(300)  # 错误后5分钟重试

if __name__ == "__main__":
    try:
        img = asyncio.run(MyPlugin.send("974502961","cn"))
    except Exception as e:
        print(e)

