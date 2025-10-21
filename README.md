<h1 style="text-align:center; font-size: 2em; color: #4A90E2; margin-top: 20px;">
    自动发送ba日历插件
</h1>


## 功能特色
-  **定时发送日历**: 📅 每日定时自动发送目标群组的日历。
-  **服务器选择**: 🌐 可以为每个群聊自定义发送的服务器日历。
-  **可靠的数据源**: 🔍 使用gamekee和SchaleDB公共数据库，提供准确而可靠的数据。
-  **即时查询功能**: ⌛ 输入`/日历 [服务器名]`即可快速获取并发送指定服务器的日历。



## 效果展示
<img src="assets\show.png" width="500">

## 配置项目
| 配置项                           | 说明                                               | 备注                                     |
|----------------------------------|--------------------------------------------------|------------------------------------------|
| 启用日历功能的QQ群与服务器对列表 | 填入允许使用日历功能的“QQ群号:服务器”，例如"114514:cn,jp,global"，服务器可以按需随意组合 | 记得删除默认配置，以及使用英文冒号        |
| 发送日历时间                     | 每日发送日历时间，格式HH:MM                       | 使用东八区基准，默认为早上9点            |


## 使用方法
1. 下载插件
<img src="assets/guider1.jpg" width="500">
2. 在控制面板进入配置项，删除默认配置并填入自己的配置
<img src="assets/guider2.jpg" width="500">
## 使用注意事项
- 消息平台兼容问题：自动发送的时候使用的时候default的消息平台，使用多个消息平台时可能会出现问题，目前只能确保单独使用aiocqhttp不出现问题
- 数据切换：gamekee 出现问题时会自动切换到 SchaleDB 数据库，此时会缺少大决战数据（因为修这个查询函数好麻烦我还找不到这个数据库的说明文档😭）。


## 🙏 致谢
- 本项目参考了[astrbot-qq-group-daily-analysis](https://github.com/SXP-Simon/astrbot-qq-group-daily-analysis/)的定时调度和消息平台处理
- 查询逻辑来自隔壁的HoshinoBot插件
[Blue_Archive_HoshinoBot](https://github.com/Cosmos01/Blue_Archive_HoshinoBot)，该项目似乎由于SchaleDB的数据格式更新所以对SchaleDB查询存在问题，我修补了一下，不过只要gamekee不出问题应该就没事
- 数据来源：[gamekee](https://www.gamekee.com/ba/)，[SchaleD](|https://schaledb.com/home) 


## 后续更新计划
- [ ] 添加活动结束提醒功能
- [ ] 加入cron格式时间
- [ ] 添加项目数据流图
- [ ] 添加错误处理


## 更新日志

### 2025-10-21
v1.0
- 推送正式版本