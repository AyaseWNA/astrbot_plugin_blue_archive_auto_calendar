<div align="center">
# 自动发送ba日历插件
</div>

## 功能特色
能够在每日定时在目标群聊中发送日历，可以设置每个群聊发送哪个服务器的日历
使用了gamekee和schaledb公共数据库作为数据源，可靠
也可以使用``/日历 [服务器名]``来直接发送目标日历至当年聊天
## 效果展示
<img src="" width="500">

## 配置项目
| 配置项 | 说明 | 备注 ||-----|-----|-----|| 启用日历功能的QQ群与服务器对列表 | 填入允许使用日历功能的“QQ群号:服务器”，例如"114514:cn,jp,global"，服务器可以按需随意组合 | 记得删除默认配置，以及使用英文冒号 || 发送日历时间 | 每日发送日历时间，格式HH:MM | 使用东八区基准，默认为早上9点 |

## 使用注意事项
- 消息平台兼容问题：自动发送的时候使用的时候default的消息平台，使用多个消息平台时可能会出现问题，目前只能确保单独使用aiocqhttp不出现问题
- 数据切换：gamekee 出现问题时会自动切换到 SchaleDB 数据库，此时会缺少大决战数据（因为修这个查询函数好麻烦我还找不到这个数据库的说明文档😭）。

## 贡献者
本项目参考了[https://github.com/SXP-Simon/astrbot-qq-group-daily-analysis/tree/master]的定时调度和消息平台处理，
查询逻辑来自隔壁的HoshinoBot插件
[Blue_Archive_HoshinoBot|https://github.com/Cosmos01/Blue_Archive_HoshinoBot]，该项目似乎由于SchaleDB的数据格式更新所以对SchaleDB查询存在问题，我修补了一下，不过只要gamekee不出问题应该就没事
数据来源：[gamekee|https://www.gamekee.com/ba/]，[SchaleDB|https://schaledb.com/home]

## 后续更新计划
- [ ] 加入cron格式时间
- [ ] 添加项目数据流图
- [ ] 添加错误处理

## 更新日志

### 2025-10-19
v0.9.114515
- 完成了基础功能