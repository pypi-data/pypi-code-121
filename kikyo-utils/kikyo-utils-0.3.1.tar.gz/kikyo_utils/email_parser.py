import base64
import logging
from email.utils import getaddresses
from typing import Optional

import mailparser
from mailparser import MailParser

from kikyo_utils.file import normalize_file_content
from kikyo_utils.selector import Selector

log = logging.getLogger(__name__)


class BaseEmailParser:
    def parse_email(self, file_content: bytes) -> dict:
        data = {}
        mail = mailparser.parse_from_bytes(file_content)
        try:
            self._parse_headers(mail, data)
            self._parse_content(mail, data)
        except Exception as e:
            log.error('Parse email error: %s', e)
        return data

    def _parse_headers(self, mail: MailParser, data: dict):
        data['subject'] = mail.headers.get('Subject')
        data['mail_from'] = mail.headers.get('From')
        data['mail_to'] = mail.headers.get('To')
        data['mail_cc'] = mail.headers.get('Cc')
        data['reply_to'] = mail.headers.get('Reply-To')
        for i in ['mail_from', 'mail_to', 'mail_cc', 'reply_to']:
            data[i] = self.parse_address(data[i])

    def parse_address(self, address_str: str):
        if not address_str:
            return
        result = []
        s = getaddresses([address_str])
        for a in s:
            if a and a[1]:
                result.append(a[1])
        if len(result) == 0:
            return
        if len(result) == 1:
            return result[0]
        return result

    def _parse_content(self, mail: MailParser, data: dict):
        if 'content' not in data:
            data['content'] = ''
        if 'attachments' not in data:
            data['attachments'] = []

        for i in mail.text_plain:
            data['content'] += _read_index_content('plain', i)
        for i in mail.text_html:
            data['content'] += _read_index_content('html', i)

        for i in mail.attachments:
            content = base64.b64decode(i['payload'])
            filepath = self._save_attachment(i.get('filename'), i.get('mail_content_type'), content)
            data['attachments'].append({
                'filename': i.get('filename'),
                'filepath': filepath,
                'content_type': i.get('mail_content_type'),
            })

    def _save_attachment(self, filename: str, content_type: str, content: bytes) -> Optional[str]:
        pass


def _read_index_content(subtype, body) -> str:
    content = ''
    if subtype == 'html':
        content = _get_text_from_html(body)
        if content:
            content = normalize_file_content(content)
    elif subtype == 'plain':
        content = body
        if content:
            content = normalize_file_content(content)
    return content


def _get_text_from_html(html):
    try:
        selector = Selector(html)
        return selector.css('body').text[0]
    except Exception:
        return ''
