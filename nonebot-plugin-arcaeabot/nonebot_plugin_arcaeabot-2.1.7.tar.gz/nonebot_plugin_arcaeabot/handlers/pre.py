from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.log import logger
from ..matcher import arc
from ..config import config
from ..draw_text import draw_help


async def pre_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    args: list = str(args).split()
    if len(args) == 0:
        await arc.finish(MessageSegment.reply(event.message_id) + draw_help())

    aua_ua = config.get_config("aua_ua")
    aua_url = config.get_config("aua_url")
    if aua_ua == "SECRET" or aua_url == "URL":
        logger.error("ArcaeaUnlimitedApi is not configured!")
        await arc.finish("ArcaeaUnlimitedApi is not configured!")
