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

PageBlock = Union[raw.types.PageBlockAnchor, raw.types.PageBlockAudio, raw.types.PageBlockAuthorDate, raw.types.PageBlockBlockquote, raw.types.PageBlockChannel, raw.types.PageBlockCollage, raw.types.PageBlockCover, raw.types.PageBlockDetails, raw.types.PageBlockDivider, raw.types.PageBlockEmbed, raw.types.PageBlockEmbedPost, raw.types.PageBlockFooter, raw.types.PageBlockHeader, raw.types.PageBlockKicker, raw.types.PageBlockList, raw.types.PageBlockMap, raw.types.PageBlockOrderedList, raw.types.PageBlockParagraph, raw.types.PageBlockPhoto, raw.types.PageBlockPreformatted, raw.types.PageBlockPullquote, raw.types.PageBlockRelatedArticles, raw.types.PageBlockSlideshow, raw.types.PageBlockSubheader, raw.types.PageBlockSubtitle, raw.types.PageBlockTable, raw.types.PageBlockTitle, raw.types.PageBlockUnsupported, raw.types.PageBlockVideo]


# noinspection PyRedeclaration
class PageBlock:  # type: ignore
    """This base type has 29 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageBlockAnchor <telectron.raw.types.PageBlockAnchor>`
            - :obj:`PageBlockAudio <telectron.raw.types.PageBlockAudio>`
            - :obj:`PageBlockAuthorDate <telectron.raw.types.PageBlockAuthorDate>`
            - :obj:`PageBlockBlockquote <telectron.raw.types.PageBlockBlockquote>`
            - :obj:`PageBlockChannel <telectron.raw.types.PageBlockChannel>`
            - :obj:`PageBlockCollage <telectron.raw.types.PageBlockCollage>`
            - :obj:`PageBlockCover <telectron.raw.types.PageBlockCover>`
            - :obj:`PageBlockDetails <telectron.raw.types.PageBlockDetails>`
            - :obj:`PageBlockDivider <telectron.raw.types.PageBlockDivider>`
            - :obj:`PageBlockEmbed <telectron.raw.types.PageBlockEmbed>`
            - :obj:`PageBlockEmbedPost <telectron.raw.types.PageBlockEmbedPost>`
            - :obj:`PageBlockFooter <telectron.raw.types.PageBlockFooter>`
            - :obj:`PageBlockHeader <telectron.raw.types.PageBlockHeader>`
            - :obj:`PageBlockKicker <telectron.raw.types.PageBlockKicker>`
            - :obj:`PageBlockList <telectron.raw.types.PageBlockList>`
            - :obj:`PageBlockMap <telectron.raw.types.PageBlockMap>`
            - :obj:`PageBlockOrderedList <telectron.raw.types.PageBlockOrderedList>`
            - :obj:`PageBlockParagraph <telectron.raw.types.PageBlockParagraph>`
            - :obj:`PageBlockPhoto <telectron.raw.types.PageBlockPhoto>`
            - :obj:`PageBlockPreformatted <telectron.raw.types.PageBlockPreformatted>`
            - :obj:`PageBlockPullquote <telectron.raw.types.PageBlockPullquote>`
            - :obj:`PageBlockRelatedArticles <telectron.raw.types.PageBlockRelatedArticles>`
            - :obj:`PageBlockSlideshow <telectron.raw.types.PageBlockSlideshow>`
            - :obj:`PageBlockSubheader <telectron.raw.types.PageBlockSubheader>`
            - :obj:`PageBlockSubtitle <telectron.raw.types.PageBlockSubtitle>`
            - :obj:`PageBlockTable <telectron.raw.types.PageBlockTable>`
            - :obj:`PageBlockTitle <telectron.raw.types.PageBlockTitle>`
            - :obj:`PageBlockUnsupported <telectron.raw.types.PageBlockUnsupported>`
            - :obj:`PageBlockVideo <telectron.raw.types.PageBlockVideo>`
    """

    QUALNAME = "telectron.raw.base.PageBlock"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.telectron.org/telegram/base/page-block")
