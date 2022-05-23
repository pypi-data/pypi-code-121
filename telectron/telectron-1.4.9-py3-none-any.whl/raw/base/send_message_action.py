#  telectron - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2021 Dan <https://github.com/delivrance>
#
#  This file is part of telectron.
#
#  telectron is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  telectron is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with telectron.  If not, see <http://www.gnu.org/licenses/>.

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from telectron import raw
from telectron.raw.core import TLObject

SendMessageAction = Union[raw.types.SendMessageCancelAction, raw.types.SendMessageChooseContactAction, raw.types.SendMessageChooseStickerAction, raw.types.SendMessageEmojiInteraction, raw.types.SendMessageEmojiInteractionSeen, raw.types.SendMessageGamePlayAction, raw.types.SendMessageGeoLocationAction, raw.types.SendMessageHistoryImportAction, raw.types.SendMessageRecordAudioAction, raw.types.SendMessageRecordRoundAction, raw.types.SendMessageRecordVideoAction, raw.types.SendMessageTypingAction, raw.types.SendMessageUploadAudioAction, raw.types.SendMessageUploadDocumentAction, raw.types.SendMessageUploadPhotoAction, raw.types.SendMessageUploadRoundAction, raw.types.SendMessageUploadVideoAction, raw.types.SpeakingInGroupCallAction]


# noinspection PyRedeclaration
class SendMessageAction:  # type: ignore
    """This base type has 18 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SendMessageCancelAction <telectron.raw.types.SendMessageCancelAction>`
            - :obj:`SendMessageChooseContactAction <telectron.raw.types.SendMessageChooseContactAction>`
            - :obj:`SendMessageChooseStickerAction <telectron.raw.types.SendMessageChooseStickerAction>`
            - :obj:`SendMessageEmojiInteraction <telectron.raw.types.SendMessageEmojiInteraction>`
            - :obj:`SendMessageEmojiInteractionSeen <telectron.raw.types.SendMessageEmojiInteractionSeen>`
            - :obj:`SendMessageGamePlayAction <telectron.raw.types.SendMessageGamePlayAction>`
            - :obj:`SendMessageGeoLocationAction <telectron.raw.types.SendMessageGeoLocationAction>`
            - :obj:`SendMessageHistoryImportAction <telectron.raw.types.SendMessageHistoryImportAction>`
            - :obj:`SendMessageRecordAudioAction <telectron.raw.types.SendMessageRecordAudioAction>`
            - :obj:`SendMessageRecordRoundAction <telectron.raw.types.SendMessageRecordRoundAction>`
            - :obj:`SendMessageRecordVideoAction <telectron.raw.types.SendMessageRecordVideoAction>`
            - :obj:`SendMessageTypingAction <telectron.raw.types.SendMessageTypingAction>`
            - :obj:`SendMessageUploadAudioAction <telectron.raw.types.SendMessageUploadAudioAction>`
            - :obj:`SendMessageUploadDocumentAction <telectron.raw.types.SendMessageUploadDocumentAction>`
            - :obj:`SendMessageUploadPhotoAction <telectron.raw.types.SendMessageUploadPhotoAction>`
            - :obj:`SendMessageUploadRoundAction <telectron.raw.types.SendMessageUploadRoundAction>`
            - :obj:`SendMessageUploadVideoAction <telectron.raw.types.SendMessageUploadVideoAction>`
            - :obj:`SpeakingInGroupCallAction <telectron.raw.types.SpeakingInGroupCallAction>`
    """

    QUALNAME = "telectron.raw.base.SendMessageAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/send-message-action")
