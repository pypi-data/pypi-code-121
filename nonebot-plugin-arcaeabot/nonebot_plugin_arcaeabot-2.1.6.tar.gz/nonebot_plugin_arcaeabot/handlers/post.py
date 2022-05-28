from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from ..matcher import arc


async def post_handler(bot: Bot, event: MessageEvent):
    await arc.finish(MessageSegment.reply(event.message_id) + "不支持的命令参数")
