"""This package contains tools to annotate transform outputs with a content type."""
from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from typing import Any, Dict, TypedDict

from typing_extensions import NotRequired  # Python 3.11


@dataclass(frozen=True)
class ContentType:
    """The Content Type class."""

    mimetype: str

    @classmethod
    def from_ext(cls, ext: str) -> ContentType:
        """Content factory from file extension.

        Parameters:
            extension: The file extension for which the MIME type is requested.

        Returns:
            The ContentType instance associated with the extension.

        Examples:
            >>> ContentType.from_ext('wav')
            ContentType(mimetype='audio/wav')
        """
        ext = ext.lower()
        mimetype, _ = mimetypes.guess_type(f'http://file.{ext}')
        if mimetype is None:
            raise ValueError(f'No MIME type known for extension {ext!r}')
        return ContentType(mimetype)


MediaTypeAnnotations = TypedDict(
    'MediaTypeAnnotations',
    {
        'contentMediaType': str,
        'x-contentMediaEncoding': NotRequired[Dict[str, Any]],
    },
)


def media_type(type_name: str, **media_encoding: Any) -> MediaTypeAnnotations:
    """Returns JSON schema annotations to describe a media type.

    Parameters:
        type_name: Either the generic media type (`audio`, `image` or `video`)
            or the file extension for which the MIME type is requested.
        **media_encoding: The intrinsic parameters of the transform output when
            it is of generic type (ex: audio/*). These parameters should not
            be provided when the transform output is a BytesIO encoding a
            defined MIME subtype (ex: audio/x-wav) because this information is
            already encoded in the output.

    Returns:
        The JSON annotations as a dict:
            * `contentMediaType`: The generic MIME type or the mimetype inferred
                from the file extension.
            * `x-contentMediaEncoding`: Optional, intrinsic parameters of
                the transform output which are required to encode into a
                concrete MIME type.

    Raises:
        TypeError: When the media encoding is specified and the media type is
            not generic ('*').
        ValueError: When the MIME type cannot be inferred from the file
            extension.

    Examples:
        >>> content_type('wav')
        {'contentMediaType': 'audio/x-wav'}
        >>> media_type('audio', rate=44100, range='int16')
        {
            'contentMediaType': 'audio/*',
            'x-contentMediaEncoding': {'rate': 44100, 'range': 'int16'},
        }
    """
    if type_name in {'audio', 'image', 'video'}:
        type_name += '/*'
    else:
        type_name = ContentType.from_ext(type_name).mimetype

    result: MediaTypeAnnotations = {'contentMediaType': type_name}
    if media_encoding:
        if not type_name.endswith('/*'):
            raise TypeError(
                'Media encoding parameters should only be specified for generic'
                " medias, such as 'image/*'."
            )
        result['x-contentMediaEncoding'] = media_encoding

    return result
