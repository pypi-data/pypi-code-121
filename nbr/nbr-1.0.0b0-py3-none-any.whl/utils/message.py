from typing import Optional, Union

from nbr.schemas.message import Content, Header, Message, Metadata


def create_message(
    channel: str,
    msg_type: str,
    session: str,
    content: Optional[Union[Content, dict]] = None,
    metadata: Optional[Union[Metadata, dict]] = None,
) -> str:
    """Generate a message using a template."""
    if not content:
        content = {}

    if not metadata:
        metadata = {}

    header = Header(msg_type=msg_type, session=session)

    message_data = {
        "channel": channel,
        "header": header,
        "content": content,
        "metadata": metadata,
    }

    message = Message(**message_data)

    return message.json()
