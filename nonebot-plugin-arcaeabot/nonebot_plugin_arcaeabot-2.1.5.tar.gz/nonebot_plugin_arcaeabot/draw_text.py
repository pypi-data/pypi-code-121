from nonebot.adapters.onebot.v11 import MessageSegment
from ._RHelper import RHelper
from .AUA.schema.api.another.song_random import Content as SongRandomContent
from .AUA.schema.api.v5.song_info import SongInfo

root = RHelper()


def draw_help():
    return "\n".join(
        [
            "/arc bind <arcaea id> 进行绑定",
            "/arc unbind 解除绑定",
            "/arc info 查看绑定信息",
            "/arc recent 查询上一次游玩记录",
            "/arc b30 查询 best 30 记录",
            "/arc assets_update 更新曲绘与立绘资源",
            "/arc best <曲名> [难度] 查询单曲最高分",
            "/arc song <曲名> [难度] 查询信息",
            "/arc random [难度] 随机指定难度的歌曲",
            "/arc random [难度min] [难度max] 随机指定难度区间的歌曲",
        ]
    )


def draw_song(content: SongRandomContent):
    if not isinstance(content.song_info, SongInfo):
        image = "file:///" + root.assets.song / content.song_id / ("base.jpg")
        result = "\n".join(
            [
                f"Name: {content.song_info[0].name_en}",
                f"[Past]: {content.song_info[0].rating/10}",
                f"[Present]: {content.song_info[1].rating/10}",
                f"[Future]: {content.song_info[2].rating/10}",
            ]
        )
        result += (
            f"\n[Beyond]: {content.song_info[3].rating/10}"
            if len(content.song_info) > 3
            else ""
        )
        result += "\n获取详细信息请在添加难度后缀"
    else:
        difficulty = ["Past", "Present", "Future", "Beyond"][content.difficulty]
        cover_name = "3.jpg" if content.song_info.jacket_override else "base.jpg"
        image = "file:///" + root.assets.song / content.song_id / cover_name
        result = "\n".join(
            [
                f"曲名: {content.song_info.name_en}[{difficulty}]",
                f"曲师: {content.song_info.artist}",
                f"曲绘: {content.song_info.jacket_designer}",
                f"时长: " + "%02d:%02d" % divmod(content.song_info.time, 60),
                f"BPM:  {content.song_info.bpm}",
                f"谱师: {content.song_info.chart_designer}",
                f"Note数: {content.song_info.note}",
                f"Rating: {content.song_info.rating/10}",
                f"隶属曲包: {content.song_info.set_friendly}",
                "上线时间: " + content.song_info.date.strftime("%Y-%m-%d"),
            ]
        )
        result += "\n需要世界模式解锁" if content.song_info.world_unlock is True else ""
        result += "\n需要下载" if content.song_info.remote_download is True else ""
    return MessageSegment.image(image) + "\n" + result
