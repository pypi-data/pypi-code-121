from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from ..data import UserInfo
from ..main import arc
from ..draw_image import UserArcaeaInfo
from .._RHelper import RHelper
from ..AUA.request import get_song_alias
from ..AUA.schema.utils import diffstr2num
from ..AUA.schema.api.another.song_alias import SongAlias

root = RHelper()


async def best_handler(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    args: list = str(args).split()
    """
        /arc best Fracture Ray ftr
    """
    if len(args) >= 2 and args[0] == "best":
        user_info = UserInfo.get_or_none(UserInfo.user_qq == event.user_id)
        # get args
        if difficulty := diffstr2num(args[-1].upper()):
            songname = " ".join(args[1:-1])
        else:
            difficulty = 2
            songname = " ".join(args[1:])
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
