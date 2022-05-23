from nonebot.adapters.onebot.v11 import MessageSegment
from .AUA.schema.api.v5.user_best30 import UserBest30
from . import image_generator
from io import BytesIO
from .AUA import get_user_best, get_user_b30, get_user_recent, UserRecent, UserBest


class UserArcaeaInfo:
    querying = list()

    @staticmethod
    def is_querying(arcaea_id: str) -> bool:
        return arcaea_id in UserArcaeaInfo.querying

    @staticmethod
    async def draw_user_b30(arcaea_id: str):
        UserArcaeaInfo.querying.append(arcaea_id)
        try:
            resp = await get_user_b30(arcaea_id=arcaea_id, overflow=10)
            data = UserBest30(**resp)
            if error_message := data.message:
                return error_message
            image = image_generator.draw_user_b30(data=data.content)
            buffer = BytesIO()
            image.save(buffer, "png")
            return MessageSegment.image(buffer)
        except Exception as e:
            return str(e)
        finally:
            UserArcaeaInfo.querying.remove(arcaea_id)

    @staticmethod
    async def draw_user_recent(arcaea_id: str):
        UserArcaeaInfo.querying.append(arcaea_id)
        try:
            resp = await get_user_recent(arcaea_id=arcaea_id)
            data = UserRecent(**resp)
            if error_message := data.message:
                return error_message
            image = image_generator.draw_single_song(data=data.content)
            buffer = BytesIO()
            image.save(buffer, "png")
            return MessageSegment.image(buffer)
        except Exception as e:
            return str(e)
        finally:
            UserArcaeaInfo.querying.remove(arcaea_id)

    @staticmethod
    async def draw_user_best(arcaea_id: str, song_id: str, difficulty: str):
        UserArcaeaInfo.querying.append(arcaea_id)
        try:
            resp = await get_user_best(
                arcaea_id=arcaea_id, song_id=song_id, difficulty=difficulty
            )
            data = UserBest(**resp)
            if error_message := data.message:
                return error_message
            image = image_generator.draw_single_song(data=data.content)
            buffer = BytesIO()
            image.save(buffer, "png")
            return MessageSegment.image(buffer)
        except Exception as e:
            return str(e)
        finally:
            UserArcaeaInfo.querying.remove(arcaea_id)
