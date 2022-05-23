#coding: utf-8
import requests
from loguru import logger
from base64 import b64encode, decodebytes
from esentity.models import TelegramBot
import tempfile
from datetime import datetime
from json import dumps


def telegram_api(token, method, json={}):
    # logger.info(f'Telegram {method} request data: {json}')
    r = requests.post(f'https://api.telegram.org/bot{token}/{method}', json=json)
    if r.status_code == 200:
        _res = r.json()
        logger.info(f'Telegram {method} response: {_res}')
        return _res
    else:
        logger.info(f'Telegram {method} response code: {r.status_code}, response: {r.content}')
    return {}


def telegram_getMe(token):
    res = telegram_api(token, 'getMe')
    if res['ok']:
        return {
            'bot_id': res['result']['id'],
            'first_name': res['result']['first_name'],
            'username': res['result']['username'],
            'can_join': res['result']['can_join_groups'],
            'can_read': res['result']['can_read_all_group_messages'],
        }                
    return {}


def telegram_setWebhook(token, url):
    res = telegram_api(token, 'setWebhook', {'url': url, 'drop_pending_updates': True})


def telegram_getChatAdministrators(token, chat):
    res = telegram_api(token, 'getChatAdministrators', {'chat_id': chat})
    if 'ok' in res and res['ok']:
        return [str(item['user']['id']) for item in res['result'] if item['user']['is_bot']]
    return []


def telegram_getChat(token, chat):
    res = telegram_api(token, 'getChat', {'chat_id': chat})
    if res.get('ok'):
        _res = {
            'chat_id': res['result']['id'],
            'title': res['result']['title'],
            'type': res['result']['type'],
            'linked_chat': res['result'].get('linked_chat_id'),
        }
        if 'permissions' in res['result']:
            _res['can_send'] = res['result']['permissions']['can_send_messages']
            _res['can_invite'] = res['result']['permissions']['can_invite_users']
        if 'photo' in res['result']:
            res_photo = telegram_api(token, 'getFile', {'file_id': res['result']['photo']['small_file_id']})
            if res_photo.get('ok'):
                r = requests.get(f"https://api.telegram.org/file/bot{token}/{res_photo['result']['file_path']}")
                if r.status_code == 200:
                    _res['photo'] = b64encode(r.content).decode()
        return _res                
    return {}


def telegram_checkChat(_doc):
    _res = {}
    _err = {}
    bots, found = TelegramBot.get(username=_doc['bot_admin'])
    if found == 1:
        bot = bots.pop()

        chat_id = f"@{_doc['username']}"
        _admins = telegram_getChatAdministrators(bot.token, chat_id)
        if bot.bot_id in _admins:
            telegram_api(bot.token, 'setChatTitle', {'chat_id': chat_id, 'title': _doc['title']})
            telegram_api(bot.token, 'setChatDescription', {'chat_id': chat_id, 'description': _doc['description'] or ''})
            if _doc['photo']:
                telegram_setChatPhoto(bot.token, chat_id, _doc['photo'])
            telegram_api(bot.token, 'setChatPermissions', {'chat_id': chat_id, 'permissions': {
                'can_send_messages': _doc['can_send'],
                'can_invite_users': _doc['can_invite'],
            }})
            _res = telegram_getChat(bot.token, chat_id)
            _res.update(telegram_getChatMemberCount(bot.token, chat_id))
        else:
            _err = {
                'username': 'No access to chat'
            }
    else:
        _err = {
            'bot_admin': 'Bot not found'
        }
    return _res, _err


def telegram_getChatMemberCount(token, chat):
    res = telegram_api(token, 'getChatMemberCount', {'chat_id': chat})
    if 'ok' in res and res['ok']:
        _res = {
            'count': res['result'],
        }
        return _res                
    return {}


def telegram_setChatPhoto(token, chat, photo):
    with tempfile.NamedTemporaryFile() as tmp:
        raw = photo.split(',')[-1]
        tmp.write(decodebytes(raw.encode()))
        tmp.seek(0)

        r = requests.post(f'https://api.telegram.org/bot{token}/setChatPhoto', {'chat_id': chat}, files={'photo': tmp})
        if r.status_code == 200:
            _res = r.json()
            logger.info(f'Telegram setChatPhoto response: {_res}')
            return _res
        else:
            logger.info(f'Telegram setChatPhoto response code: {r.status_code}, response: {r.content}')


def telegram_sendMessage(token, chat, text, disable_notify=True, disable_preview=False):
    res = telegram_api(token, 'sendMessage', {'chat_id': chat, 'text': text, 'parse_mode': 'HTML', 'disable_notification': disable_notify, 'disable_web_page_preview': disable_preview})
    if res.get('ok'):
        _res = {
            'publishedon': datetime.utcfromtimestamp(res['result']['date']),
            'chat_id': res['result']['chat']['id'],
            'chat_username': res['result']['chat']['username'],
            'message_id': res['result']['message_id'],
            'raw': res['result']['text'],
        }
        if 'from' in res['result']:
            _res['sender_id'] = res['result']['from']['id']
            _res['sender_username'] = res['result']['from']['username']
        elif 'sender_chat' in res['result']:
            _res['sender_id'] = res['result']['sender_chat']['id']
            _res['sender_username'] = res['result']['sender_chat']['username']

        return _res                
    return {}


def telegram_editMessageText(token, chat, message, text, disable_notify=True, disable_preview=False):
    res = telegram_api(token, 'editMessageText', {'chat_id': chat, 'message_id': message, 'text': text, 'parse_mode': 'HTML', 'disable_notification': disable_notify, 'disable_web_page_preview': disable_preview})
    if res.get('ok'):
        _res = {
            'publishedon': datetime.utcfromtimestamp(res['result']['date']),
            'chat_id': res['result']['chat']['id'],
            'chat_username': res['result']['chat']['username'],
            'message_id': res['result']['message_id'],
            'raw': res['result']['text'],
        }
        if 'from' in res['result']:
            _res['sender_id'] = res['result']['from']['id']
            _res['sender_username'] = res['result']['from']['username']
        elif 'sender_chat' in res['result']:
            _res['sender_id'] = res['result']['sender_chat']['id']
            _res['sender_username'] = res['result']['sender_chat']['username']

        return _res                
    return {}


def telegram_sendPhoto(token, chat, caption, photo, disable_notify=True):
    r = requests.post(f'https://api.telegram.org/bot{token}/sendPhoto', {'chat_id': chat, 'caption': caption, 'parse_mode': 'HTML', 'disable_notification': disable_notify}, files={'photo': photo})
    if r.status_code == 200:
        res = r.json()
        logger.info(f'Telegram sendPhoto response: {res}')
        if res.get('ok'):
            _res = {
                'publishedon': datetime.utcfromtimestamp(res['result']['date']),
                'chat_id': res['result']['chat']['id'],
                'chat_username': res['result']['chat']['username'],
                'message_id': res['result']['message_id'],
                'raw': res['result'].get('caption'),
            }
            if 'from' in res['result']:
                _res['sender_id'] = res['result']['from']['id']
                _res['sender_username'] = res['result']['from']['username']
            elif 'sender_chat' in res['result']:
                _res['sender_id'] = res['result']['sender_chat']['id']
                _res['sender_username'] = res['result']['sender_chat']['username']
            return _res                
    else:
        logger.info(f'Telegram sendPhoto response code: {r.status_code}, response: {r.content}')
    return {}


def telegram_editMessageMedia(token, chat, message, photo, text):
    media = {'type': 'photo', 'caption': text, 'parse_mode': 'HTML', 'media': 'attach://photo'}
    r = requests.post(f'https://api.telegram.org/bot{token}/editMessageMedia', {'chat_id': chat, 'message_id': message, 'media': dumps(media)}, files={'photo': photo})
    if r.status_code == 200:
        res = r.json()
        logger.info(f'Telegram editMessageMedia response: {res}')
        if res.get('ok'):
            _res = {
                'publishedon': datetime.utcfromtimestamp(res['result']['date']),
                'chat_id': res['result']['chat']['id'],
                'chat_username': res['result']['chat']['username'],
                'message_id': res['result']['message_id'],
                'raw': res['result'].get('caption'),
            }
            if 'from' in res['result']:
                _res['sender_id'] = res['result']['from']['id']
                _res['sender_username'] = res['result']['from']['username']
            elif 'sender_chat' in res['result']:
                _res['sender_id'] = res['result']['sender_chat']['id']
                _res['sender_username'] = res['result']['sender_chat']['username']
            return _res   
    else:
        logger.info(f'Telegram editMessageMedia response code: {r.status_code}, response: {r.content}')
    return {}
