from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from ..main import arc
from ..draw_text import draw_song
from .._RHelper import RHelper
from typing import Dict
from ..AUA.request import get_song_info
from ..AUA.schema.api.another.song_info_detail import SongInfoDetail
from ..AUA.schema.utils import diffstr2num

root = RHelper()


async def song_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    args: list = str(args).split()
    args: Dict = {i: v for i, v in enumerate(args)}
    if args.get(0, None) == "song":
        # get args
        songname = args.get(1, None)
        difficulty = args.get(2, "ALL")
        difficulty = diffstr2num(difficulty.upper())
        resp = await get_song_info(songname, difficulty)
        data = SongInfoDetail(**resp)
        if error_message := data.message:
            await arc.finish(
                MessageSegment.reply(event.message_id) + str(error_message)
            )
        await arc.finish(
            MessageSegment.reply(event.message_id) + draw_song(data.content)
        )
