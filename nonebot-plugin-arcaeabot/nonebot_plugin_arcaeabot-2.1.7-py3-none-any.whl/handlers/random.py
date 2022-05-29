from typing import Dict
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from ..main import arc
from ..draw_text import draw_song
from .._RHelper import RHelper
from ..AUA.request import get_song_random
from ..AUA.schema.api.another.song_random import SongRandom
from ..AUA.schema.utils import diffstr2num


root = RHelper()


async def random_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    args: list = str(args).split()
    args: Dict = {i: v for i, v in enumerate(args)}
    if args.get(0, None) == "random":
        # get args
        start = args.get(1, 0)
        end = args.get(2, 20)
        difficulty = args.get(3, "ALL")
        difficulty = diffstr2num(difficulty.upper())
        resp = await get_song_random(start, end, difficulty)
        data = SongRandom(**resp)
        if error_message := data.message:
            await arc.finish(
                MessageSegment.reply(event.message_id) + str(error_message)
            )
        await arc.finish(
            MessageSegment.reply(event.message_id) + draw_song(data.content)
        )
