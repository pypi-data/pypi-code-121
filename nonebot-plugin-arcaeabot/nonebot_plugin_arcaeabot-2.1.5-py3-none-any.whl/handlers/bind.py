from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.params import CommandArg
from ..data import ArcInfo, UserInfo
from ..matcher import arc
from ..AUA import get_user_info


async def bind_handler(bot: Bot, event: MessageEvent, args=CommandArg()):
    args: list = str(args).split()

    if args[0] == "bind":
        if len(args) == 1:
            await arc.finish(MessageSegment.reply(event.message_id) + "缺少参数 arcaea_id！")
        arc_id = args[1]

        arc_info = ArcInfo.get_or_none(ArcInfo.arcaea_name == arc_id)
        arc_info2 = ArcInfo.get_or_none(ArcInfo.arcaea_id == arc_id)
        # get 2 info and check them
        if arc_info:
            arc_id = arc_info.arcaea_id
            arc_name = arc_info.arcaea_name

        elif arc_info2:
            arc_id = arc_info2.arcaea_id
            arc_name = arc_info2.arcaea_name

        elif not arc_id.isdigit() or (arc_id.isdigit() and len(arc_id) != 9):
            await arc.finish(
                MessageSegment.reply(event.message_id) + f"找不到 Arc_id: {arc_id} 的玩家"
            )

        else:
            res = await get_user_info(arcaea_id=arc_id)
            if res["status"] != 0:
                await arc.finish(str(res["status"]) + ": " + res["message"])

            arc_name = res["content"]["account_info"]["name"]
            ArcInfo.replace(
                arcaea_id=arc_id,
                arcaea_name=arc_name,
                ptt=res["content"]["account_info"]["rating"],
            ).execute()

        UserInfo.delete().where(UserInfo.user_qq == event.user_id).execute()
        UserInfo.replace(user_qq=event.user_id, arcaea_id=arc_id).execute()
        await arc.finish(
            MessageSegment.reply(event.message_id)
            + f"绑定成功, 用户名: {arc_name}, id: {arc_id}"
        )
