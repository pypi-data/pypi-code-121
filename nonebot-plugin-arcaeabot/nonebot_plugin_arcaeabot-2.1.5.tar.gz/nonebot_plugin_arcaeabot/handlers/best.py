from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from ..data import UserInfo
from ..main import arc
from ..draw_image import UserArcaeaInfo
from .._RHelper import RHelper
from typing import Dict
from ..AUA.request import get_song_alias
from ..AUA.schema.utils import diffstr2num
from ..AUA.schema.api.another.song_alias import SongAlias

root = RHelper()


async def best_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    args: list = str(args).split()
    args: Dict = {i: v for i, v in enumerate(args)}
    if args.get(0, None) == "best":
        user_info = UserInfo.get_or_none(UserInfo.user_qq == event.user_id)
        # get args
        songname = args.get(1, None)
        difficulty = args.get(2, "FTR")
        difficulty = diffstr2num(difficulty.upper())
        # Exception
        if not user_info:
            await arc.finish(MessageSegment.reply(event.message_id) + "你还没绑定呢！")

        if UserArcaeaInfo.is_querying(user_info.arcaea_id):
            await arc.finish(
                MessageSegment.reply(event.message_id) + "您已在查询队列, 请勿重复发起查询。"
            )

        # Query
        resp = await get_song_alias(songname)
        data = SongAlias(**resp)
        if error_message := data.message:
            await arc.finish(
                MessageSegment.reply(event.message_id) + str(error_message)
            )
        result = await UserArcaeaInfo.draw_user_best(
            arcaea_id=user_info.arcaea_id,
            song_id=data.content.song_id,
            difficulty=str(difficulty),
        )
        await arc.finish(MessageSegment.reply(event.message_id) + result)
