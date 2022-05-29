from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from ..main import arc
from ..draw_text import draw_song
from .._RHelper import RHelper
from ..AUA.request import get_song_info
from ..AUA.schema.api.another.song_info_detail import SongInfoDetail
from ..AUA.schema.utils import diffstr2num

root = RHelper()


async def song_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    args: list = str(args).split()
    """
        /arc song Fracture Ray ftr
    """
    if len(args) >= 2 and args[0] == "song":
        # get args
        if difficulty := diffstr2num(args[-1].upper()):
            songname = " ".join(args[1:-1])
        else:
            difficulty = -1
            songname = " ".join(args[1:])
        # query
        resp = await get_song_info(songname, difficulty)
        data = SongInfoDetail(**resp)
        if error_message := data.message:
            await arc.finish(
                MessageSegment.reply(event.message_id) + str(error_message)
            )
        await arc.finish(
            MessageSegment.reply(event.message_id) + draw_song(data.content)
        )
