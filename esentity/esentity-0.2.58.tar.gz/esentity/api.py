#coding: utf-8
from flask import request, url_for, session, make_response
from flask import current_app
from flask_restful import Resource
from flask_login import current_user, login_required
from flask_uploads import UploadNotAllowed
import os
import hashlib
import pycountry 
import ipaddress
from datetime import date, datetime, timedelta
from slugify import slugify 
from loguru import logger
from werkzeug import Response
from werkzeug.routing import BuildError
from functools import wraps
from json import dumps, loads
from utils import geo_context
from PIL import Image
from resizeimage import resizeimage
from pydantic import ValidationError
from cryptography.fernet import Fernet
from esentity.models import BaseEntity, ElasticEntity, TdsPostback
from esentity.models import Page, Actor, Activity, TdsCampaign, TdsDomain, TdsHit, CasinoCommit, TelegramBot, TelegramChat, TelegramMessage
from esentity.models import AuthModel, SignupModel, SignupModelInvite, UserModel, ManagerModel, CasinoModel, CasinoProxyModel, DomainModel, CampaignModel, ActivityFeedbackModel, ActivitySubscribeModel, ActivityTicketModel , TelegramBotModel, TelegramChatModel, TelegramMessageModel, ActivityComplaintModel, ComplaintModel, ComplaintReplyModel
from esentity.tasks import send_email, send_notify, tdscampaign_clear, tdscampaign_bots, add_vote
from esentity.telegram import *
from esentity.encoder import TelegramContentParser
from boto3 import session as boto_session
from boto3.s3.transfer import TransferConfig
import tempfile
from oauth2client.service_account import ServiceAccountCredentials
import httplib2


def su_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view


def zone_required(zone):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if zone not in current_user.zones and not current_user.is_admin:
                return current_app.login_manager.unauthorized()
            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_page_url(obj, full_path=False):
    url = None

    kw = {
        'alias': obj['alias']
    }
    if current_app.config.get('CORE_PREFIX'):
        kw['lang_code'] = obj['locale']

    if obj['category'] == 'slot':
        url = url_for('{0}slot'.format(current_app.config.get('CORE_PREFIX', '')), **kw)
    elif obj['category'] == 'provider':
        url = url_for('{0}casino'.format(current_app.config.get('CORE_PREFIX', '')), **kw)
    else:
        url = url_for('{0}path'.format(current_app.config.get('CORE_PREFIX', '')), **kw)

    if url and full_path:
        url = f"{current_app.config['PREFERRED_URL_SCHEME']}://{current_app.config['DOMAIN']}{url}"

    return url


def get_tags(item):
    _tags = []
    if item.category == 'provider':
        _tags.append({'title': 'Casino', 'class': 'casino'})
        if item.is_draft:
            _tags.append({'title': 'Draft', 'class': 'draft'})
        if item.owner:
            actors, found = Actor.get(_id=item.owner)
            if found == 1:
                actor = actors.pop()
                _tags.append({'title': actor.username, 'class': 'owner'})

    elif item.category == 'slot':
        _tags.append({'title': 'Slot', 'class': 'slot'})
    elif item.category == 'collection':
        _tags.append({'title': 'Collection', 'class': 'collection'})

    if not item.is_active:
        _tags.append({'title': 'Not Active', 'class': 'is-disabled'})
    if not item.is_searchable:
        _tags.append({'title': 'Not Searchable', 'class': 'not-searchable'})
    if item.is_redirect:
        _tags.append({'title': 'Redirect', 'class': 'is-redirected'})

    _tags.append({'title': item.locale.upper(), 'class': 'locale'})

    return _tags


def process_casino(item, actors={}, check_commit=False):
    _doc = item['_source']
    _doc['id'] = item['_id']
    _doc['full_path'] = get_page_url(_doc, True)
    if _doc.get('owner') and len(actors.keys()):
        _doc['owner'] = {'id': _doc['owner'], 'username': actors.get(_doc['owner'])}

    if check_commit and _doc['status'] in ['draft', 'published']:
        _, found = CasinoCommit.get(
            source_id=_doc['id'],
            actor_id=current_user.id
        )
        if found:
            _doc['status'] = 'unpublished_changes'

    return _doc


def get_timerange(timeframe, custom=None):
    # today
    start = "now/d"
    end = start

    if timeframe == 'Custom':
        _custom = custom.split(' to ')
        if len(_custom) == 1:
            start = f'{_custom[0]}||/d' 
            end = start
        elif (len(_custom) == 2):
            start = f'{_custom[0]}||/d' 
            end = f'{_custom[1]}||/d' 
    elif timeframe == "Yesterday":
        start = "now-1d/d"
        end = start
    elif timeframe == "Last 24 hours":
        start = "now-24h/m"
        end = "now/m"
    elif timeframe == "Last 7 days":
        start = "now-6d/d"
        end = "now/d"
    elif timeframe == "Last 60 days":
        start = "now-60d/d"
        end = "now/d"
    elif timeframe == "This Month":
        start = "now/M"
        end = start
    elif timeframe == "Prev Month":
        start = "now-1M/M"
        end = start

    return start, end


class ApiPing(Resource):
    def get(self):
        return {'ok': True, 'pong': True}


class ApiResourceSlug(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSlug: {0}'.format(data))
    
        _attrs = {'alias': slugify(data.get('title'))}

        return {'ok': True, 'attrs': _attrs}


class ApiResourceGet(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json(silent=True)
        logger.info(u'Data ApiResourceGet: {0}'.format(data))

        if data:
            objs, total = Page.get(_id=data['key'])
            if total == 1:
                obj = objs.pop()
                doc = obj.to_dict()
                doc['updatedon'] = datetime.utcnow()
                resp = {
                    'ok': True,
                    'resource': doc,
                }
                return resp
        else:
            resp = {
                'ok': True,
                'resource': {
                    'alias': Page.get_random_string(10).lower(),
                    'category': 'page',
                    'is_active': True,
                    'is_searchable': True,
                    'publishedon': datetime.utcnow().date(),
                    'updatedon': datetime.utcnow(),
                    'order': 0,
                    'locale': current_app.config['BABEL_DEFAULT_LOCALE']
                },
            }
            return resp
        return {'ok': False}


class ApiResourceSearch(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSearch: {0}'.format(data))

        objs, total = Page.get(path=data['key'], locale=data.get('locale', current_app.config['BABEL_DEFAULT_LOCALE']))
        if total:
            obj = objs.pop()


            data = [{
                'key': obj._id, 
                'title': obj.title or obj.path, 
                'url': get_page_url(obj.to_dict(), True)
            }]
            resp = {
                'ok': True,
                'found': data, 
                'resource_key': data[0],
            }
        else:
            resp = {
                'ok': True,
                'found': [], 
                'resource_key': None
            }
        return resp


class ApiResourceSearchPage(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSearchPage: {0}'.format(data))

        objs = [{
            'key': item._id, 
            'title': item.title or item.path, 
            'url': get_page_url(item.to_dict(), True),
            'tags': get_tags(item)
        } for item in Page.query(data['query'], True)]
        return {'ok': True, 'items': objs}


class ApiResourceGeo(Resource):
    @login_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceGeo: {0}'.format(data))

        _c, _e, _v = Page.get_countries(data.get('w', '') or '', data.get('b', '') or '')
        if _v:
            _c = []

        return {'ok': True, 'countries': _c, 'errors': _e, 'valid': not _v}


class ApiResourceUpload(Resource):
    @login_required
    def post(self):
        logger.info(u'Data ApiResourceUpload: {0}'.format(request.form))

        _e = None
        try:
            resp = {}
            file = request.files['file']
            basename = slugify(u'.'.join(file.filename.split('.')[:-1])).lower() + '.'

            rename = request.form['rename']
            if rename in ['entity']:
                basename = slugify(request.form['title'] or basename).lower() + '.'
            if rename in ['hash']:
                basename = hashlib.md5(file.read()).hexdigest() + '.'
                file.seek(0)
            
            filename = current_app.images.save(file, None, basename)
            resp['origin'] = current_app.images.url(filename)

            path = current_app.images.path(filename)
            image = Image.open(path) 
            image = image.convert('RGBA')            
            w, h = image.size

            _w = None
            _h = None

            preset = request.form['preset'].split('_')
            for item in preset:
                if 'w' in item:
                    _w = int(item.replace('w', ''))
                elif 'h' in item:
                    _h = int(item.replace('h', ''))

            if len(preset) > 1:
                tfname = '{0}.' + preset[0] + '.png'
                filename = '.'.join(filename.split('.')[:-1])

                if _w and _h:
                    if w > _w and h > _h: 
                        image = resizeimage.resize_cover(image, [_w, _h])
                else:
                    if w > _w:
                        image = resizeimage.resize_width(image, _w)

                png = current_app.images.path(tfname.format(filename))
                image.save(png, 'PNG')
                resp['png'] = current_app.images.url(tfname.format(filename))

                image.save("{0}.webp".format(png), 'WEBP')
                resp['webp'] = "{0}.webp".format(resp['png'])
            else:
                image.save("{0}.webp".format(path), 'WEBP')
                resp['webp'] = "{0}.webp".format(resp['origin'])

            resp['ok'] = True
            return resp
        except UploadNotAllowed:
            _e = 'Not allowed'
        return {'ok': False, 'error': _e}


class ApiResourceSave(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSave: {0}'.format(data))

        _errors = dict()
        entity = data['entity']

        # to cerberus
        if not entity.get('alias'):
            _errors['alias'] = ['Mandatory field']

        if not _errors:
            if entity['category'] in ['slot', 'provider']:
                entity['alias'] = slugify(entity['alias'].strip()).lower()

            resource_key = data['key']

            try:
                path = get_page_url(entity)
            except BuildError:
                _errors['category'] = ['Endpoint not found']

            if not _errors:
                if current_app.config.get('CORE_PREFIX'):
                    path = path.replace('/{0}'.format(entity['locale']), '')

                _, total = Page.get(path=path, locale=entity['locale'])

                if total > 0 and (not resource_key or (resource_key and resource_key.get('key') != _.pop()._id)):
                    _errors['alias'] = ['Page already exist: {0}'.format(path)]
                else:
                    if not resource_key:
                        _id = Page.generate_id(path, entity['locale'])

                        if not current_user.is_admin and entity['category'] in ['provider']:
                            entity['ref_link'] = None
                            entity['ref_link_tc'] = None
                            entity['ref_link_geo'] = []
                    else:
                        _id = resource_key.get('key')

                        if not current_user.is_admin and entity['category'] in ['provider']:
                            bl_attrs = ['ref_link', 'ref_link_tc', 'ref_link_geo']

                            pages, total = Page.get(_id=_id)
                            if total == 1:
                                _page = pages.pop()
                                if _page.category in ['provider']:
                                    _d = _page.to_dict()
                                    for _a in bl_attrs:
                                        entity[_a] = _d.get(_a)
                                        logger.info(f'Get attr {_a} from source: {_d.get(_a)}')

                    entity['path'] = path
                    entity['suggest'] = entity.get('title', '')
                    entity['project'] = os.environ.get('PROJECT', 'app')

                    # TODO fix errors data by script
                    if entity['category'] not in ['provider']:
                        entity['geo'] = []
                        

                    if current_app.config.get('CORE_PREFIX') and entity['category'] in ['page', 'collection'] and entity.get('bulk_create') and not resource_key:
                        _locales = entity['locale_available']
                        entity['locale_available'] = []
                        for _locale in _locales:
                            pages, found = Page.get(path=path, locale=_locale)
                            if found == 0:
                                entity['locale'] = _locale
                                resp, _ = Page.put(Page.generate_id(path, _locale), entity)
                                logger.info(f'Page with locale {_locale} saved: {resp}')
                            else:
                                page = pages.pop()
                                logger.info(f'Page with locale {_locale} already exists: {page.title}')
                    else:
                        resp, obj = Page.put(_id, entity)
                        logger.info(f'Page saved: {resp}')

                        # send notify for owner on publicate (checkbox)
                        if entity.get('is_send_notify') and obj.owner and obj.category == 'provider' and obj.is_active and not obj.is_draft and obj.status == 'published':
                            actors, found = Actor.get(_id=obj.owner)
                            if found:
                                actor = actors.pop()
                                if actor.actor_is_active:
                                    url = get_page_url(obj.to_dict(), True)
                                    tv = {"brand": obj.title, "url": url}
                                    send_email.apply_async(args=['approved', actor.username, 'Hey, we have approved your casino!', tv])

                                    msg = f':bell: Send approving notify: {obj.title}, to: {actor.username}'
                                    send_notify.apply_async(args=[msg])

                    return {'ok': True}

        return {'ok': False, 'errors': _errors}


class ApiResourceHistory(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        history, _ = Page.get(_count=20, _sort=[{"updatedon": {"order": "desc"}}])
        objs = [{
            'key': item._id, 
            'title': item.title or item.path, 
            'url': get_page_url(item.to_dict(), True),
            'tags': get_tags(item)
        } for item in history]
        return {'ok': True, 'history': objs}


class ApiResourceAPISearch(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceAPISearch: {0}'.format(data))
        return {'ok': True, 'items': []}


class ApiResourceImportPush(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceImportPush: {0}'.format(data))

        _attrs = {}
        success = 'Complete!'

        entity = data['entity']
        raw = entity.get('raw')
        if raw:

            try:
                _attrs = loads(raw)
                _attrs['alias'] = None
                _attrs['is_active'] = False
                _attrs['is_searchable'] = False

                _attrs['raw'] = success
            except Exception:
                logger.info(f'Not JSON: {raw}')

                _data = [item.strip() for item in raw.split('\n')]
                if len(_data) == 1:
                    _data = _data[0].split(';')

                    if entity.get('category') == 'slot' and len(_data) == 11:
                        _attrs = {
                            'title': _data[0],
                            'software': [_data[1]],
                            'releasedon': date(int(_data[2]), 1, 1) if _data[2].isdigit() and len(_data[2]) == 4 else _data[2],
                            'layout': _data[3],
                            'lines': _data[4],
                            'volatility': [_data[5]],
                            'rtp': _data[6],
                            'default_currency': _data[7],
                            'min_bet': _data[8],
                            'max_bet': _data[9],
                            'alias': None,
                            'raw': success
                        }
                    elif entity.get('category') == 'provider' and len(_data) == 1:
                        _attrs = {
                            'title': _data[0],
                            'alias': None,
                            'raw': success
                        }

        return {'ok': True, 'attrs': _attrs}


class ApiResourceExport(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceExport: {0}'.format(data))

        pages, found = Page.get(_id=data['key']['key'])
        if found:
            page = pages.pop()
            _doc = page.to_dict()

            return {
                'ok': True, 
                'doc': _doc, 
                'filename': f'{page.title}.json', 
                'content_type': 'application/json;charset=utf-8'
            }

        return {'ok': False}

class ApiSearchCasinos(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiSearchCasinos: {0}'.format(data))

        _afields = ['software', 'licences', 'deposits', 'withdrawal', 'games']
        payload = data['payload']
        _n = payload
        for k, v in payload.items():
            if k in _afields and isinstance(v, list):
                _a = []
                for item in v:
                    _a.append(item['item'] if isinstance(item, dict) else item)
                _n[k] = _a
        data['payload'] = _n
        logger.info(u'Processed Data ApiSearchCasinos: {0}'.format(data))

        _res = None
        _found = None

        # _aggs_primary = {}

        ## experiment
        _cached = current_app.redis.hget('aggs', data['hash'])
        _aggs_primary = loads(_cached) if _cached else {}
        ## experiment

        if data.get('is_init'):
            # _cached = current_app.redis.hget('aggs', data['hash'])
            # _aggs_primary = loads(_cached) if _cached else {}

            ## experiment
            current_app.redis.hset('aggs_history', data['hash'] + '123', _cached)
            ## experiment
        else:
            _aggs = {
                item: {
                    "terms": {
                        "field": "{0}.keyword".format(item),
                        "size": 500,
                        "order": {"_key": "asc"}
                    }
                } for item in _afields
            }

            payload = data['payload']
            logger.info(u'Filters for search: {0}'.format(payload))

            _sorting = None
            if 'sorting' in payload:
                if payload['sorting'] == 'Rating Highest first':
                    _sorting = [{'rating': {'order': 'desc'}}]
                elif payload['sorting'] == 'Newest sites first':
                    _sorting = [{'establishedon': {'order': 'desc'}}]
                elif payload['sorting'] == 'Oldest sites first':
                    _sorting = [{'establishedon': {'order': 'asc'}}]
                elif payload['sorting'] == 'Most traffic first':
                    _sorting = [{'rank_alexa': {'order': 'asc'}}]
                elif payload['sorting'] == 'Last added':
                    _sorting = [{'publishedon': {'order': 'desc'}}]
                elif payload['sorting'] == 'Sort A-Z':
                    _sorting = [{'title.keyword': {'order': 'asc'}}]

            # args: service
            pages, _found, _aggs_primary_filtered, id = Page.provider_by_context(
                is_searchable=True,
                is_redirect=False,
                country=current_user.country_full if payload.get('is_geo', True) else None,
                services=data['category'],
                provider_tags=data['tags'],
                **payload,
                _locale=current_app.config['BABEL_DEFAULT_LOCALE'],
                _source = [
                    "title", 
                    "alias", 
                    "logo", 
                    "logo_white",
                    "logo_small",
                    "external_id", 
                    "theme_color", 
                    "welcome_package", 
                    "welcome_package_note",
                    "provider_pros",
                    "services",
                    "welcome_package_max_bonus",
                    "default_currency",
                    "rating",
                    "rank",
                    "user_rating",
                    "is_sponsored",
                    "website",
                    "provider_pros",
                    "licences",
                    "ref_link",
                    "geo",
                    "category",
                ] + _afields, 
                _count=int(payload.get('cpp', 10)),
                _page=int(data.get('page', 1)),
                _aggs = _aggs,
                _sorting = _sorting
            )

            ## experiment
            def to_dict(items):
                return {item['item']: item['count'] for item in items}

            _cached_prev = current_app.redis.hget('aggs_history', data['hash'] + '123')
            _aggs_prev = loads(_cached_prev) if _cached_prev else {}

            _aggs_diff = {}
            for k, v in _aggs_primary.items():
                _diff = []
                prev = to_dict(_aggs_prev.get(k, []))
                current = to_dict(_aggs_primary_filtered[k])
                for j in v:
                    _name = j['item']
                    if len(payload[k]):
                        if _name in payload[k]:
                            _diff.append({'item': _name, 'count': ''})
                        else:
                            _cnt = j['count']
                            if _name in current:
                                _cnt = _cnt - current[_name]
                            else:
                                if _name in prev:
                                    _cnt = prev[_name]
                                else:
                                    _cnt = 0
                            _diff.append({'item': _name, 'count': '+{0}'.format(_cnt)})
                    else:
                        _diff.append({'item': _name, 'count': current.get(_name, 0)})
                _aggs_diff[k] = _diff

            _aggs_primary = _aggs_diff
            if _found > 0:
                current_app.redis.hset('aggs_history', data['hash'] + '123', dumps(_aggs_primary_filtered))
            ## experiment

            # _aggs_primary = _aggs_primary_filtered

            _template = '_rating-grid.html' if payload.get('is_grid', False) else '_rating-rows.html'
            t = current_app.jinja_env.get_template(_template)
            deposits_primary, langs_primary, currency_primary = geo_context(current_user.country_full)
            _res = t.render(pages=pages, deposits_primary=deposits_primary)
            
        _aggs_secondary = {
            'sorting': [
                'Legal in my region', 
                'Rating Highest first', 
                'Newest sites first',
                'Oldest sites first',
                'Most traffic first',
                'Last added',
                'Sort A-Z',
            ],
            'cpp': [10, 25, 50, 100, 200],
        }
        _aggs = dict(_aggs_primary, **_aggs_secondary)

        return {
            'ok': True, 
            'aggs': _aggs,
            'found': _found,
            'data': _res
        }
    

class ApiSearchSlots(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiSearchSlots: {0}'.format(data))

        _afields = ['software', 'volatility', 'themes', 'slot_features']

        payload = data['payload']
        _n = payload
        for k, v in payload.items():
            if k in _afields and isinstance(v, list):
                _a = []
                for item in v:
                    _a.append(item['item'] if isinstance(item, dict) else item)
                _n[k] = _a
        data['payload'] = _n
        logger.info(u'Processed Data ApiSearchSlots: {0}'.format(data))

        _res = None
        _found = None

        # _aggs_primary = {}

        ## experiment
        _cached = current_app.redis.hget('aggs', data['hash'])
        _aggs_primary = loads(_cached) if _cached else {}
        ## experiment

        if data.get('is_init'):
            # _cached = current_app.redis.hget('aggs', data['hash'])
            # _aggs_primary = loads(_cached) if _cached else {}

            ## experiment
            current_app.redis.hset('aggs_history', data['hash'] + '123', _cached)
            ## experiment
        else:
            _aggs = {
                item: {
                    "terms": {
                        "field": "{0}.keyword".format(item),
                        "size": 500,
                        "order": {"_key": "asc"}
                    }
                } for item in _afields
            }

            payload = data['payload']
            logger.info(u'Filters for search: {0}'.format(payload))

            _sorting = None
            if 'sorting' in payload:
                if payload['sorting'] == 'Rating Highest first':
                    _sorting = [{'rating': {'order': 'desc'}}]
                elif payload['sorting'] == 'RTP Highest first':
                    _sorting = [{'rtp': {'order': 'desc'}}]
                elif payload['sorting'] == 'Newest slots first':
                    _sorting = [{'releasedon': {'order': 'desc'}}]
                elif payload['sorting'] == 'Oldest slots first':
                    _sorting = [{'releasedon': {'order': 'asc'}}]
                elif payload['sorting'] == 'Last added':
                    _sorting = [{'publishedon': {'order': 'desc'}}]
                elif payload['sorting'] == 'Sort A-Z':
                    _sorting = [{'title.keyword': {'order': 'asc'}}]

            # args: service
            pages, _found, _aggs_primary_filtered, id = Page.slots_by_context(
                is_searchable=True,
                is_redirect=False,
                **payload,
                _locale=current_app.config['BABEL_DEFAULT_LOCALE'],
                _source=[
                    'alias', 
                    'title', 
                    'cover', 
                    'software'
                ] + _afields, 
                _count=int(payload.get('cpp', 10)),
                _page=int(data.get('page', 1)),
                _aggs=_aggs,
                _sorting=_sorting
            )

            ## experiment
            def to_dict(items):
                return {item['item']: item['count'] for item in items}

            _cached_prev = current_app.redis.hget('aggs_history', data['hash'] + '123')
            _aggs_prev = loads(_cached_prev) if _cached_prev else {}

            _aggs_diff = {}
            for k, v in _aggs_primary.items():
                _diff = []
                prev = to_dict(_aggs_prev.get(k, []))
                current = to_dict(_aggs_primary_filtered[k])
                for j in v:
                    _name = j['item']
                    if len(payload[k]):
                        if _name in payload[k]:
                            _diff.append({'item': _name, 'count': ''})
                        else:
                            _cnt = j['count']
                            if _name in current:
                                _cnt = _cnt - current[_name]
                            else:
                                if _name in prev:
                                    _cnt = prev[_name]
                                else:
                                    _cnt = 0
                            _diff.append({'item': _name, 'count': '+{0}'.format(_cnt)})
                    else:
                        _diff.append({'item': _name, 'count': current.get(_name, 0)})
                _aggs_diff[k] = _diff

            _aggs_primary = _aggs_diff
            if _found > 0:
                current_app.redis.hset('aggs_history', data['hash'] + '123', dumps(_aggs_primary_filtered))
            ## experiment

            # _aggs_primary = _aggs_primary_filtered

            t = current_app.jinja_env.get_template('_rating-slots.html')
            _res = t.render(pages=pages)
            
        _aggs_secondary = {
            'sorting': [
                'Sort A-Z',
                'Rating Highest first', 
                'RTP Highest first',
                'Newest slots first',
                'Oldest slots first',
                'Last added',
            ],
            'cpp': [24, 48, 72, 96, 192],
        }
        _aggs = dict(_aggs_primary, **_aggs_secondary)

        return {
            'ok': True, 
            'aggs': _aggs,
            'found': _found,
            'data': _res
        }


class ApiGeo(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiGeo: {0}'.format(data))

        _c = []

        if 'query' in data:
            try:
                res = pycountry.countries.search_fuzzy(data['query'])
                _c = [{'iso': item.alpha_2.lower(), 'country': item.name} for item in res]
            except Exception as e:
                logger.warning('Pycountry exception: {0}'.format(e))
        else:
            _c = [{'iso': item.alpha_2.lower(), 'country': item.name} for item in pycountry.countries]

        return {
            'ok': True, 
            'countries': _c,
        }


class ApiAuthLogin(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAuth: {0}'.format(data))

        _errors = {}

        try:
            obj = AuthModel(**data)

            objs, found = Actor.get(username=obj.login.lower())
            if found == 1:
                actor = objs.pop()
                if hashlib.sha256(obj.password.encode()).hexdigest() == actor.password:
                    if actor.actor_is_active:
                        _doc = actor.to_dict()
                        _doc['last_auth'] = datetime.utcnow()
                        _doc['last_country'] = current_user.location_iso
                        _doc['ip'] = request.remote_addr
                        _doc['ua'] = str(request.user_agent)
                        # _doc['zones'] = ['admin']
                        # _doc['actor_is_admin'] = True
                        resp, obj = Actor.put(actor._id, _doc)

                        session['actor'] = obj.to_dict()

                        msg = ':man: Auth success: {0}, IP: {1} [{2}]'.format(obj.username, current_user.ip, current_user.location_iso.upper())
                        send_notify.apply_async(args=[msg])

                        return {'ok': True, 'user': obj.to_dict()}
                    else:
                        _errors['login'] = 'Your account is disabled'
                else:
                    _errors['password'] = 'Incorrect password'
            else:
                _errors['login'] = 'Account not found'

            msg = ':lock: Auth error: {0}, IP: {1} [{2}]'.format(obj.login, current_user.ip, current_user.location_iso.upper())
            send_notify.apply_async(args=[msg])

        except ValidationError as e:
            logger.warning('ApiAuth validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.email': 'E-mail is not valid'
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}, 401


class ApiAuthLogout(Resource):
    @login_required
    def get(self):
        if 'actor' in session:
            del session['actor']
            logger.info('ApiLogout complete')
            return {'ok': True}

        return {'ok': False}
            

class ApiAuthSignup(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAuthSignup: {0}'.format(data))

        _errors = {}

        try:
            if current_app.config['DASHBOARD_INVITE']:
                obj = SignupModelInvite(**data)
            else:
                obj = SignupModel(**data)

            objs, found = Actor.get(username=obj.login.lower())
            if found == 0:
                password = Actor.get_random_string(8)
                logger.info('{0} new password: {1}'.format(obj.login.lower(), password))

                _id = Actor.generate_id(obj.login.lower(), request.remote_addr, datetime.utcnow().isoformat())
                _doc = {
                    'id': _id,
                    'username': obj.login.lower(),
                    'password': hashlib.sha256(password.encode()).hexdigest(),
                    'actor_is_active': True,
                    'actor_is_admin': False,
                    'zones': current_app.config.get('DASHBOARD_DEFAULT_ZONES') or [],
                    'ip': request.remote_addr,
                    'ua': str(request.user_agent),
                    'sign_date': datetime.utcnow(),
                    'skype': obj.skype
                }
                resp, actor = Actor.put(_id, _doc)

                tv = {"password": password, "login": actor.username}
                send_email.apply_async(args=['sign', actor.username, 'Welcome on board', tv])

                msg = ':id: Signup: {0}, IP: {1} [{2}]'.format(actor.username, current_user.ip, current_user.location_iso.upper())
                send_notify.apply_async(args=[msg])

                if obj.invite_code:
                    logger.info(f'Process attach by token: {obj.invite_code}')
                    try:
                        f = Fernet(current_app.config['FERNET_KEY'])
                        _obj = f.decrypt(obj.invite_code.encode())
                        _token = loads(_obj)
                        if isinstance(_token, dict):
                            _ts = datetime.timestamp(datetime.utcnow())
                            if _ts > _token['expired']:
                                logger.info(f'Token expired: {_token}, now: {_ts}')
                            else:
                                logger.info(f'Token valid: {_token}')
                                objs, total = Page.get(_id=_token['key'])
                                if total == 1:
                                    casino = objs.pop()
                                    if casino.category == 'provider':
                                        casino.owner = actor._id
                                        resp, casino = Page.put(casino._id, casino.to_dict(), _signal=False)

                                        msg = ':man: Casino {0} attached to {1}'.format(casino.title, actor.username)
                                        send_notify.apply_async(args=[msg])

                    except Exception as e:
                        logger.error(f'Exception encrypt token: {e}')

                return {'ok': True}
            else:
                _errors['login'] = 'Account already exist'

        except ValidationError as e:
            logger.warning('ApiAuthSignup validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.email': 'E-mail is not valid',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}     


class ApiAuthReset(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAuthReset: {0}'.format(data))

        _errors = {}

        try:
            obj = UserModel(**data)

            objs, found = Actor.get(username=obj.login.lower())
            if found == 1:
                actor = objs.pop()

                if actor.actor_is_active:
                    password = Actor.get_random_string(8)
                    logger.info('{0} update password: {1}'.format(obj.login.lower(), password))

                    _doc = actor.to_dict()
                    _doc['password'] = hashlib.sha256(password.encode()).hexdigest()
                    resp, obj = Actor.put(actor._id, _doc)

                    tv = {"password": password}
                    send_email.apply_async(args=['reset', obj.username, 'Reset Password', tv])

                    msg = ':man: Reset password: {0}, IP: {1} [{2}]'.format(obj.username, current_user.ip, current_user.location_iso.upper())
                    send_notify.apply_async(args=[msg])

                    return {'ok': True}
                else:
                    _errors['login'] = 'Your account is disabled'
            else:
                _errors['login'] = 'Account not found'
        except ValidationError as e:
            logger.warning('ApiAuthReset validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.email': 'E-mail is not valid',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}     


class ApiAuthActor(Resource):
    @login_required
    def get(self):
        _doc = current_user.to_dict()
        _doc.pop('comment', None)
        _doc.pop('password', None)
        _doc.pop('project', None)
        return {'ok': True, 'user': _doc}


class ApiManagerUpdate(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerUpdate: {0}'.format(data))

        _errors = {}

        try:
            obj = ManagerModel(**data)

            _doc = current_user.to_dict()
            _doc['skype'] = obj.skype

            email_updated = False

            if current_user.username != obj.login.lower():
                objs, found = Actor.get(username=obj.login.lower())
                if found == 0:
                    logger.info('{0} update e-mail: {1}'.format(current_user.username, obj.login.lower()))

                    password = Actor.get_random_string(8)
                    logger.info('{0} update password: {1}'.format(obj.login.lower(), password))

                    _doc['username'] = obj.login.lower()
                    _doc['password'] = hashlib.sha256(password.encode()).hexdigest()

                    # send email with password to new address
                    tv = {"password": password, "login": obj.login.lower()}
                    send_email.apply_async(args=['update', obj.login.lower(), 'You have updated your login', tv])

                    email_updated = True
                else:
                    _errors['login'] = 'E-mail already used'

            if not _errors:
                resp, obj = Actor.put(current_user._id, _doc)
                session['actor'] = obj.to_dict()

                return {'ok': True, 'updated': email_updated, 'email': obj.username}

        except ValidationError as e:
            logger.warning('ApiManagerUpdate validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.email': 'E-mail is not valid'
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}   


class ApiAdminUsers(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsers: {0}'.format(data))

        _sort = [{'username.keyword': {'order': 'asc'}}]
        if data['sorting'] in ['last_auth', 'sign_date']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        users, total = Actor.get(
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'id', 
                'username', 
                'last_auth', 
                'last_country',
                'actor_is_active', 
                'actor_is_admin', 
                'ip', 
                'sign_date', 
                'skype', 
                'comment', 
                'zones'
            ]
        )

        def process_user(item):
            _doc = item['_source']
            return _doc

        return {'ok': True, 'users': [process_user(item) for item in users], 'total': total}


class ApiAdminUsersGet(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsersGet: {0}'.format(data))

        actors, found = Actor.get(_id=data['id'])
        if found == 1:
            actor = actors.pop()

            _sort = [{'updatedon': {'order': 'desc'}}]
            casinos, total = Page.get(
                owner=actor.id,
                category='provider',
                is_redirect=False, 
                locale=current_app.config['BABEL_DEFAULT_LOCALE'],
                _all=True,
                _process=False,
                _sort=_sort,
                _source=[
                    'id', 
                    'updatedon',
                    'publishedon',
                    'title',
                    'path',
                    'is_active', 
                    'is_searchable', 
                    'is_draft', 
                    'status',
                    'alias',
                    'category',
                ]
            )

            return {
                'ok': True, 
                'actor': {
                    'id': actor.id,
                    'username': actor.username,
                    'actor_is_active': actor.actor_is_active,
                    'actor_is_admin': actor.actor_is_admin,
                    'skype': actor.skype,
                    'comment': actor.comment,
                    'zones': actor.zones,
                },
                'casinos': [process_casino(item) for item in casinos],
                'zones': [
                    'manager',
                    'admin',
                    'content',
                    'tds',
                    'telegram',
                    'tools',
                ],
                'total': total                
            }

        return {'ok': False}


class ApiAdminUsersUpdate(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsersUpdate: {0}'.format(data))

        actors, found = Actor.get(_id=data['id'])
        if found == 1:
            actor = actors.pop()

            raw = data['actor']
            actor.username = raw['username']
            actor.actor_is_active = raw['actor_is_active']
            actor.skype = raw['skype']
            actor.comment = raw['comment']

            # only SU
            if current_user.is_admin:
                actor.actor_is_admin = raw['actor_is_admin']
                actor.zones = sorted(raw['zones'])

            Actor.put(actor._id, actor.to_dict())
            return {'ok': True}

        return {'ok': False}


class ApiAdminUsersRemove(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsersRemove: {0}'.format(data))

        actors, found = Actor.get(_id=data['id'])
        if found == 1:
            actor = actors.pop()

            # not admin and only disabled
            if not actor.actor_is_admin and not actor.actor_is_active:
                # check related entities (owner casino)
                casinos, found = Page.get(
                    category='provider',
                    owner=actor._id
                )
                for item in casinos:
                    item.owner = None
                    Page.put(item._id, item.to_dict(), _signal=False)
                    logger.info(f'Owner removed: {item.title}')

                Actor.delete(actor._id)
                return {'ok': True}

        return {'ok': False}


class ApiContentCasinos(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentCasinos: {0}'.format(data))

        kwargs = {}
        if data['table'] == 'requests':
            kwargs = {'is_draft': True, 'status': 'on_review'}
        elif data['table'] == 'drafts':
            kwargs = {'is_draft': True, 'status': 'draft'}
        elif data['table'] == 'casinos':
            kwargs = {'is_draft': False}

        _sort = [{'updatedon': {'order': 'desc'}}]
        if data['sorting'] in ['title', 'casino']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['publishedon', 'rating', 'user_rating', 'boost', 'establishedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]
        elif data['sorting'] in ['rank_alexa']:
            _sort = [{data['sorting']: {'order': 'asc'}}]

        if data['table'] == 'commits':
            commits, _ = CasinoCommit.get(_all=True, _process=False, _sort=_sort)

            _res = []
            for item in commits:
                casinos, found = Page.get(_id=item['_source']['source_id'])
                if found == 1:
                    casino = casinos.pop()
                    _casino = casino.to_dict()
                    _casino['updatedon'] = item['_source']['updatedon']

                    obj_casino = CasinoProxyModel(**_casino)
                    obj_casino_attrs = obj_casino.dict()
                    if casino.establishedon:
                        obj_casino_attrs['year'] = casino.establishedon.year

                    obj_commit = CasinoModel(**item['_source'])
                    obj_commit_attrs = obj_commit.dict()

                    _fields = []
                    for k, v in obj_commit_attrs.items():
                        if k in obj_casino_attrs:
                            if v != obj_casino_attrs[k]:
                                _fields.append({
                                    'attr': k,
                                    'casino':  obj_casino_attrs[k],
                                    'commit': v
                                })

                    _doc = {
                        '_id': casino._id,
                        '_source': _casino,
                    }
                    _doc['_source']['commit'] = _fields
                    _doc['_source']['commit_id'] = item['_id']
                    _doc['_source']['casino_id'] = casino._id
                    _res.append(_doc)

            casinos = _res
        else:
            casinos, _ = Page.get(
                category='provider',
                **kwargs,
                _all=True,
                _process=False,
                _sort=_sort,
                _source=[
                    'id', 
                    'updatedon',
                    'publishedon',
                    'category',
                    'title',
                    'alias',
                    'path',
                    'is_active', 
                    'is_searchable', 
                    'is_redirect',
                    'is_sponsored',
                    'redirect',
                    'is_draft', 
                    'status',
                    'owner',
                    'ref_link',
                    'website',
                    'provider_tags',
                    'rank_alexa',
                    'rating',
                    'user_rating',
                    'boost',
                    'meta_title',
                    'meta_description',
                    'intro',
                    'welcome_package',
                    'welcome_package_wager',
                    'welcome_package_note',
                    'min_deposit',
                    'min_withdrawal',
                    'default_currency',
                    'establishedon',
                    'locale',
                    'locale_available',
                    'source_chain',
                    'affiliate_contact',
                    'affiliate_email',
                ]
            )

        owners = [item['_source'].get('owner') for item in casinos if item['_source'].get('owner')]
        actors, _ = Actor.get(id=owners, _count=len(casinos))
        actors = {item.id: item.username for item in actors}
        logger.info('Actors found: {0}'.format(actors))

        return {
            'ok': True,
            'items': [process_casino(item, actors) for item in casinos],
        }


class ApiContentPages(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentPages: {0}'.format(data))

        _sort = [{'updatedon': {'order': 'desc'}}]
        if data['sorting'] in ['title', 'category', 'path']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['publishedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        pages, _ = Page.get(
            category=['page', 'collection'],
            _all=True,
            _process=False,
            _sort=_sort,
            _source=[
                'id', 
                'updatedon',
                'publishedon',
                'category',
                'title',
                'alias',
                'path',
                'is_active', 
                'is_searchable', 
                'is_redirect',
                'redirect',
                'category',
                'meta_title',
                'collection_mode',
                'locale',
                'tags',
            ]
        )

        def process_page(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            _doc['title'] = _doc['title'] or _doc['path']
            _doc['full_path'] = get_page_url(_doc, True)
            return _doc

        return {
            'ok': True,
            'items': [process_page(item) for item in pages],
        }


class ApiContentSlots(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentSlots: {0}'.format(data))

        _sort = [{'updatedon': {'order': 'desc'}}]
        if data['sorting'] in ['title', 'software']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['publishedon', 'releasedon', 'rtp', 'lines', 'max_win', 'rating']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        pages, _ = Page.get(
            category=['slot'],
            _all=True,
            _process=False,
            _sort=_sort,
            _source=[
                'id', 
                'updatedon',
                'publishedon',
                'category',
                'title',
                'alias',
                'path',
                'is_active', 
                'is_searchable', 
                'is_redirect',
                'redirect',
                'software',
                'meta_title',
                'releasedon',
                'is_new',
                'is_featured',
                'rating',
                'themes',
                'volatility',
                'rtp',
                'slot_features',
                'layout',
                'lines',
                'is_coins',
                'default_currency',
                'min_bet',
                'max_bet',
                'max_win',
                'is_freeplay',
                'freeplay_url',
                'locale',
                'locale_available',
                'source_chain',
            ]
        )

        def process_page(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            _doc['full_path'] = get_page_url(_doc, True)
            return _doc

        return {
            'ok': True,
            'items': [process_page(item) for item in pages],
        }


class ApiContentTickets(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminTickets: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['contacts', 'subject']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        users, total = Activity.get(
            activity='ticket',
            _all=True,
            _sort=_sort,
            _source=[
                'id', 
                'createdon', 
                'subject', 
                'contacts',
                'name',
                'message',
                'ip', 
                'country', 
                'cid'
            ]
        )

        def process_ticket(_doc, _id):
            _doc['message'] = '<br />'.join(_doc['message'].split('\n'))   
            _doc['id'] = _id      
            return _doc

        return {'ok': True, 'tickets': [process_ticket(item.to_dict(), item._id) for item in users], 'total': total}


class ApiContentFeedback(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminFeedback: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['casino', 'ip']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        if data['sorting'] in ['rate']:
            _sort = [{data['sorting']: {'order': 'asc'}}]

        users, total = Activity.get(
            activity='feedback',
            _all=True,
            _sort=_sort,
            _source=[
                'id', 
                'createdon', 
                'name',
                'ip', 
                'country', 
                'country_iso',
                'cid',
                'casino',
                'rate',
                'casino_id',
                'pros',
                'cons',
            ]
        )

        def process_feedback(_doc, _id):
            _doc['pros'] = '<br />'.join(_doc['pros'].split('\n'))   
            _doc['cons'] = '<br />'.join(_doc['cons'].split('\n'))   
            _doc['id'] = _id       
            return _doc

        casinos, _ = Page.get(
            category='provider',
            is_redirect=False, 
            locale=current_app.config['BABEL_DEFAULT_LOCALE'],
            _process=False,
            _all=True,
            _source=[
                'alias', 
                'title',
                'comments',
                'category',
                'locale',
            ]
        )

        def process_approved(_doc):
            if 'comment_pros' in _doc:
                _doc['comment_pros'] = '<br />'.join(_doc['comment_pros'].split('\n'))   
            if 'comment_cons' in _doc:
                _doc['comment_cons'] = '<br />'.join(_doc['comment_cons'].split('\n'))   
            _doc['country'] = _doc['country'].upper()
            return _doc

        _approved = []
        for item in casinos:
            if len(item['_source']['comments']):
                _d2 = {
                    'casino': item['_source']['title'], 
                    'full_path': get_page_url(item['_source'], True)
                }
                _approved += [process_approved(dict(_d1, **_d2)) for _d1 in item['_source']['comments']]

        return {
            'ok': True, 
            'feedback': [process_feedback(item.to_dict(), item._id) for item in users], 
            'total_feedback': total,
            'approved': sorted(_approved, key=lambda d: d['publishedon'], reverse=True),
            'total_approved': len(_approved),
        }


class ApiContentSubscribers(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminSubscribers: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['email', 'ip']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        users, total = Activity.get(
            activity='subscribe',
            _all=True,
            _sort=_sort,
            _source=[
                'id', 
                'createdon', 
                'email',
                'ip', 
                'country', 
                'cid',
            ]
        )

        def process_subscriber(_doc, _id):
            _doc['id'] = _id   
            return _doc

        return {'ok': True, 'subscribers': [process_subscriber(item.to_dict(), item._id) for item in users], 'total': total}


class ApiContentComplaints(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentComplaints: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['email', 'ip', 'casino']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['rate']:
            _sort = [{data['sorting']: {'order': 'asc'}}]

        users, total = Activity.get(
            activity='complaint',
            _all=True,
            _sort=_sort,
            _source=[
                'id', 
                'createdon', 
                'completedon',
                'email',
                'ip', 
                'country', 
                'cid',
                'name',
                'username',
                'status',
                'is_active',
                'casino',
                'amount',
                'currency',
                'rate',
                'replies',
                'subject',
            ]
        )

        def process_subscriber(_doc, _id):
            _doc['id'] = _id   
            return _doc

        return {'ok': True, 'complaints': [process_subscriber(item.to_dict(), item._id) for item in users], 'total': total}


class ApiContentComplaintsGet(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentComplaintsGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            complaints, found = Activity.get(_id=data['id'])
            if found == 1:
                complaint = complaints.pop()
                _attrs = complaint.to_dict()

                _attrs['casino_selected'] = {'id': _attrs['casino_id'], 'title': _attrs['casino']}  
                if '\n' in _attrs['message']:
                    _attrs['message'] = ''.join([f'<p>{item}</p>' for item in _attrs['message'].split('\n')])

                obj = ComplaintModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Complaint found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404

        options = Page.get_options()

        _sort = [{'title.keyword': {'order': 'asc'}}]
        casinos, _ = Page.get(
            category='provider',
            is_active=True,
            is_searchable=True,
            is_redirect=False, 
            is_draft=False,
            locale=current_app.config['BABEL_DEFAULT_LOCALE'],
            _all=True,
            _process=False,
            _sort=_sort,
            _source=[
                'id', 
                'title',
                'alias',
            ]
        )

        def process_casino(item):
            return {'id': item['_id'], 'title': item['_source']['title']}

        _opts = {
            'countries': [item.name for item in pycountry.countries],
            'currencies': options['currency'],
            'casinos': [process_casino(item) for item in casinos],
            'status_list': [
                'draft',
                'confirmed',
                'opened',
                'not_solved',
                'solved',
                'rejected'
            ],
            'author_list': [
                'manager',
                'editor',
            ],
            'subject_list': current_app.config['COMPLAINT_SUBJECTS'],
        }

        return {'ok': True, 'options': _opts, 'complaint': _doc}


class ApiContentComplaintsSave(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentComplaintsSave: {0}'.format(data))

        _errors = {}
        try:
            obj = ComplaintModel(**data['payload'])
            _doc = obj.dict()

            if 'id' in data:
                complaints, found = Activity.get(_id=data['id'])
                if found == 1:
                    complaint = complaints.pop()

                    _attrs = complaint.to_dict()
                    _attrs.update(_doc)

                    _cn = pycountry.countries.get(name=_attrs['country'])
                    if _cn:
                        _attrs['country_iso'] = _cn.alpha_2.lower()

                    if _attrs['casino_selected']:
                        _attrs['casino'] = _attrs['casino_selected']['title']
                        _attrs['casino_id'] = _attrs['casino_selected']['id']

                    logger.info(f'Doc for update complaint: {_attrs}')
                    resp, obj = Activity.put(complaint._id, _attrs, _signal=False)
                else:
                    return {'ok': False}, 404

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiContentComplaintsSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.list.min_items': 'Required field',
                'type_error.none.not_allowed': 'Required field',
                'type_error.integer': 'Only integer value accepted',
                'value_error.number.not_le': 'Invalid range (1-5)',
                'value_error.number.not_ge': 'Invalid range (1-5)',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiAdminActivity(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        _d = request.get_json()
        logger.info(u'Data ApiAdminActivity: {0}'.format(_d))

        data = _d['payload']

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['country', 'ip', 'casino', 'ua']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['createdon_asc']:
            _sort = [{'createdon': {'order': 'asc'}}]

        cpp = int(data['cpp'])
        start, end = get_timerange(data['range'], data['custom_range'])

        items, total = Activity.get(
            activity='click',
            _sort=_sort,
            _process=False,
            _count=cpp,
            _offset=int(_d['offset'])*cpp,
            _range=('createdon', start, end, _d.get('timezone', 'UTC')),
            _source=[
                'id', 
                'createdon', 
                'ip', 
                'country', 
                'country_iso',
                'cid',
                'ua',
                'is_bot',
                'casino',
                'url',
                'landing',
            ]
        )

        def process_activity(item):
            _doc = item['_source']
            _doc['id'] = item['_id']      
            return _doc

        return {'ok': True, 'items': [process_activity(item) for item in items], 'total': total}


class ApiContentActivityRemove(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminActivityRemove: {0}'.format(data))

        actions, found = Activity.get(_id=data['id'])
        if found == 1:
            action = actions.pop()
            Activity.delete(action._id)
            return {'ok': True}

        return {'ok': False}


class ApiContentFeedbackAccept(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentFeedbackAccept: {0}'.format(data))

        actions, found = Activity.get(_id=data['id'])
        if found == 1:
            action = actions.pop()

            if action.activity == 'feedback' and action.casino_id:
                add_vote.apply_async(args=[action.to_dict()])
                Activity.delete(action._id)
                logger.info(f'Feedback accepted')
                return {'ok': True}

        return {'ok': False}


class ApiContentFeedbackReject(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentFeedbackReject: {0}'.format(data))

        actions, found = Activity.get(_id=data['id'])
        if found == 1:
            action = actions.pop()

            if action.activity == 'feedback' and action.casino_id:
                # remove from casino comments
                casinos, total = Page.get(_id=action.casino_id)
                if total == 1:
                    casino = casinos.pop()

                    hash = Activity.generate_id(action.ip, action.ua, action.cid)
                    hash_dt = Activity.generate_id(action.createdon, action.ip, action.ua, action.cid)

                    _res = []
                    for item in casino.comments:
                        if 'hash' in item and item['hash'] in [hash, hash_dt]:
                            logger.info(f'Comment by hash {hash} found')
                        else:
                            _res.append(item)                

                    casino.comments = sorted(_res, key=lambda d: d['publishedon'])
                    resp, obj = Page.put(casino._id, casino.to_dict(), _signal=False)
                    logger.info('Update casino [{1}]: {0}'.format(resp, obj.title))

                    Activity.delete(action._id)
                    return {'ok': True}

        return {'ok': False}


class ApiContentCommit(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentCommit: {0}'.format(data))

        commits, commits_found = CasinoCommit.get(_id=data['commit_id'])
        casinos, casinos_found = Page.get(_id=data['casino_id'])

        if commits_found and casinos_found:
            commit = commits.pop()
            casino = casinos.pop()

            if data['action'] == 'reject':
                resp = CasinoCommit.delete(commit._id)
                logger.info(f'Commit for {commit.casino} rejected: {resp}')
                
                casino.status = 'published'
                resp, _ = Page.put(casino._id, casino.to_dict())
                logger.info(f'Casino status updated: {resp}')

                return {'ok': True, 'rejected': True}
            elif data['action'] == 'accept':
                _commit = commit.to_dict()
                _casino = casino.to_dict()
                if 'attr' in data:
                    _attr = data['attr']
                    if _attr in _commit:
                        if _attr == 'year':
                            if _commit[_attr]:
                                _casino['establishedon'] = datetime(year=int(_commit[_attr]), month=1, day=1)
                        else:
                            _casino[_attr] = _commit[_attr]
                        resp, _ = Page.put(casino._id, _casino)
                        logger.info(f'Casino attr {_attr} updated: {resp}')
                else:
                    # accept all
                    if _commit['year']:
                        _commit['establishedon'] = datetime(year=int(_commit['year']), month=1, day=1)

                    _casino.update(_commit)
                    _casino['status'] = 'published'

                    resp, _ = Page.put(casino._id, _casino)
                    logger.info(f'Casino attrs and status updated: {resp}')

                    resp = CasinoCommit.delete(commit._id)
                    logger.info(f'Commit for {commit.casino} accepted: {resp}')

                    return {'ok': True, 'accepted': True}

            return {'ok': True}

        return {'ok': False}, 404


class ApiManagerCasinos(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerCasinos: {0}'.format(data))

        _sort = [{'publishedon': {'order': 'desc'}}]
        if data['sorting'] in ['title']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['updatedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        casinos, total = Page.get(
            owner=current_user.id,
            category='provider',
            is_redirect=False, 
            locale=current_app.config['BABEL_DEFAULT_LOCALE'],
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'id', 
                'publishedon',
                'updatedon', 
                'title',
                'path',
                'is_active', 
                'is_draft', 
                'status',
                'alias',
                'category',
            ]
        )

        return {'ok': True, 'casinos': [process_casino(item, {}, True) for item in casinos], 'total': total}


class ApiManagerComplaints(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerComplaints: {0}'.format(data))

        casinos, _ = Page.get(
            is_active=True,
            is_redirect=False, 
            owner=current_user.id,
            category='provider',
            locale=current_app.config['BABEL_DEFAULT_LOCALE'],
            _all=True,
            _process=False,
            _source=[
                'path',
                'alias',
                'locale',
                'category',
            ]
        )

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['casino', 'username']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['rate']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        _attrs = [
            'rate',
            'username',
            'amount',
            'currency',
            'message',
            'casino_id',
            'casino',
            'createdon',
            'country',
            'country_iso',
            'replies'
        ]

        items, _ = Activity.get(
            is_active=True,
            casino_id=[casino['_id'] for casino in casinos],
            status='published',
            activity='complaint',
            _all=True,
            _sort=_sort,
            _source=_attrs
        )

        def process_activity(item):
            _doc = {k: v for k, v in item.to_dict().items() if k in _attrs}
            _doc['id'] = item._id
            _doc['replies_length'] = len([item for item in _doc['replies'] if item.get('is_active', False) and item.get('author') == 'manager'])
            del _doc['replies']
            return _doc

        return {
            'ok': True, 
            'items': [process_activity(item) for item in items], 
            'casinos': {casino['_id']: get_page_url(casino['_source'], True) for casino in casinos}
        }


class ApiManagerComplaintsReplyGet(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerComplaintsReplyGet: {0}'.format(data))

        _res = ''
        if data and 'id' in data:
            complaints, found = Activity.get(_id=data['id'])
            if found == 1:
                complaint = complaints.pop()
                _replies = [item.get('message') for item in complaint.replies if item.get('author') in ['manager'] and item.get('is_active', False)]
                if len(_replies) > 0:
                    _res = _replies[0] or ''

        return {'ok': True, 'reply': _res}


class ApiManagerComplaintsReplySave(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerComplaintsReplySave: {0}'.format(data))

        _errors = {}
        try:
            obj = ComplaintReplyModel(**data['payload'])

            if 'id' in data:
                complaints, found = Activity.get(_id=data['id'])
                if found == 1:
                    complaint = complaints.pop()

                    _res = []
                    _found = False
                    
                    for item in complaint.replies:
                        if item.get('is_active') and item.get('author') == 'manager':
                            item['message'] = obj.reply
                            _found = True
                        if item['message'] and item['message'] != '<p></p>':   
                            _res.append(item)

                    if not _found and obj.reply:
                        _res.append({
                            'is_active': True,
                            'message': obj.reply,
                            'author': 'manager',
                        })

                    complaint.replies = _res

                    _doc = complaint.to_dict()
                    logger.info(f'Doc for update complaint (set manager reply): {_doc}')
                    resp, obj = Activity.put(complaint._id, _doc, _signal=False)
                else:
                    return {'ok': False}, 404

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiManagerComplaintsReplySave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'type_error.none.not_allowed': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiManagerActivity(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        _d = request.get_json()
        logger.info(u'Data ApiManagerActivity: {0}'.format(_d))

        data = _d['payload']

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['country', 'ip', 'casino', 'ua']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['createdon_asc']:
            _sort = [{'createdon': {'order': 'asc'}}]

        cpp = int(data['cpp'])
        start, end = get_timerange(data['range'], data['custom_range'])

        casinos, total = Page.get(
            owner=current_user.id,
            category='provider',
            is_redirect=False, 
            locale=current_app.config['BABEL_DEFAULT_LOCALE'],
            _all=True,
            _source=[
                'id', 
                'publishedon',
                'updatedon', 
                'title',
                'path',
                'is_active', 
                'is_draft', 
            ]
        )

        casino_list = [item.title for item in casinos]
        logger.info('Casinos: {0}'.format(casino_list))

        users, total = Activity.get(
            activity='click',
            casino=casino_list,
            is_bot=False,
            _sort=_sort,
            _process=False,
            _count=cpp,
            _offset=int(_d['offset'])*cpp,
            _range=('createdon', start, end, _d.get('timezone', 'UTC')),
            _source=[
                'id', 
                'createdon', 
                'ip', 
                'country', 
                'country_iso',
                'ua',
                'is_bot',
                'casino',
            ]
        )

        def process_activity(item):
            _doc = item['_source']
            _doc['id'] = item['_id']         
            return _doc

        return {'ok': True, 'items': [process_activity(item) for item in users], 'total': total}


class ApiManagerCasinosGet(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json(silent=True)
        logger.info(u'Data ApiManagerCasinosGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            casinos, found = Page.get(_id=data['id'])
            if found == 1:
                casino = casinos.pop()
                if casino.owner == current_user.id and casino.status in ['draft', 'published']:
                    _attrs = casino.to_dict()

                    if casino.establishedon:
                        _attrs['year'] = casino.establishedon.year

                    if casino.status == 'published':
                        commits, found = CasinoCommit.get(
                            source_id=casino._id,
                            actor_id=current_user.id
                        )
                        if found == 1:
                            commit = commits.pop()
                            _attrs.update(commit.to_dict())
                            logger.info(f'Data from commit {commit._id} loaded')

                    obj = CasinoProxyModel(**_attrs)
                    _doc = obj.dict()
                    logger.info(u'Casino found: {0}'.format(_doc))
                else:
                    return {'ok': False}, 401
            else:
                return {'ok': False}, 404

        support = current_app.config['DASHBOARD_SUPPORT']

        options = Page.get_options()
        wl = [
            'services',
            'languages', 
            'payment_methods',
            'software',
            'currency',
            'games',
            'licences',
            'countries_name'
        ]
        _res = {}
        for k, v in options.items():
            if k in wl:
                _res[k] = sorted(v)

        return {'ok': True, 'support': support, 'options': _res, 'casino': _doc}


class ApiManagerCasinosSave(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerCasinosSave: {0}'.format(data))

        _errors = {}
        try:
            obj = CasinoModel(**data['payload'])
            _doc = obj.dict()

            if _doc['year']:
                _doc['establishedon'] = datetime(year=int(_doc['year']), month=1, day=1)

            if 'id' in data:
                casinos, found = Page.get(_id=data['id'])
                if found == 1:
                    casino = casinos.pop()
                    if casino.owner == current_user.id and casino.status in ['draft', 'published']:
                        if casino.status and casino.status == 'draft':
                            _attrs = casino.to_dict()
                            _attrs.update(_doc)

                            _attrs['suggest'] = _doc['title']
                            _attrs['alt_title'] = _doc['title']
                            _attrs['updatedon'] = datetime.utcnow()

                            if data.get('publish'):
                                _attrs['status'] = 'on_review'

                            logger.info(f'Doc for update casino: {_attrs}')
                            resp, obj = Page.put(casino._id, _attrs)
                        elif casino.status == 'published':
                            commits, found = CasinoCommit.get(
                                source_id=casino._id,
                                actor_id=current_user.id
                            )
                            if found == 1:
                                commit = commits.pop()
                                _attrs = commit.to_dict()
                                _attrs.update(_doc)

                                _attrs['updatedon'] = datetime.utcnow()
                                _doc['casino'] = casino.title

                                resp, obj = CasinoCommit.put(commit._id, _attrs)
                                logger.info(f'Commit updated: {resp}')
                            elif found == 0:
                                _doc['updatedon'] = datetime.utcnow()
                                _doc['source_id'] = casino._id
                                _doc['actor_id'] = current_user.id
                                _doc['casino'] = casino.title

                                resp, obj = CasinoCommit.put(CasinoCommit.generate_id([casino._id, current_user.id]), _doc)
                                logger.info(f'Commit created: {resp}')

                        if data.get('publish'):
                            casino.status = 'on_review'
                            casino.updatedon = datetime.utcnow()

                            resp, obj = Page.put(casino._id, casino.to_dict())
                            logger.info(f'Casino updated: {resp}')
                    else:
                        return {'ok': False}, 401
                else:
                    return {'ok': False}, 404

            else:
                alias = Page.get_random_string(10).lower()
                _meta = {
                    'category': 'provider',
                    'locale': current_app.config['BABEL_DEFAULT_LOCALE'],
                    'is_active': False,
                    'is_searchable': False,
                    'is_draft': True,
                    'alias': alias,
                    'suggest': _doc['title'],
                    'alt_title': _doc['title'],
                    'publishedon': datetime.utcnow().date(),
                    'updatedon': datetime.utcnow(),
                    'owner': current_user.id,
                    'status': 'draft',
                    'theme_color': '#6B8794',
                }

                _doc.update(_meta)
                _doc['path'] = get_page_url(_doc)

                if data.get('publish'):
                    _doc['status'] = 'on_review'

                logger.info(f'Doc for create casino: {_doc}')
                resp, obj = Page.put(Page.generate_id(_doc['path'], _doc['locale']), _doc)

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiManagerCasinosSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'type_error.none.not_allowed': 'Required field',
                'value_error.list.min_items': 'Required field',
                'type_error.integer': 'Only integer value accepted',
                'value_error.url.scheme': 'Not a valid URL',
                'value_error.email': 'Not a valid e-mail',
                'value_error.any_str.max_length': 'Too many chars'
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiManagerCasinosPublish(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerCasinosPublish: {0}'.format(data))

        if 'id' in data:
            casinos, found = Page.get(_id=data['id'])
            if found == 1:
                casino = casinos.pop()
                if casino.owner == current_user.id:
                    _doc = casino.to_dict()
                    _doc['status'] = 'on_review'
                    _doc['updatedon'] = datetime.utcnow()
                    resp, obj = Page.put(casino._id, _doc)
                    return {'ok': True}
                else:
                    return {'ok': False}, 401

        return {'ok': False}, 404


class ApiTdsDomains(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsDomains: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['domain']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        domains, _ = TdsDomain.get(
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'domain', 
                'endpoint', 
                'createdon',
                'is_https'
            ]
        )

        def process_domain(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            return _doc

        return {'ok': True, 'items': [process_domain(item) for item in domains]}


class ApiTdsDomainsGet(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json(silent=True)
        logger.info(u'Data ApiTdsDomainsGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            domains, found = TdsDomain.get(_id=data['id'])
            if found == 1:
                domain = domains.pop()
                _attrs = domain.to_dict()
                obj = DomainModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Domain found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404

        return {'ok': True, 'options': {}, 'domain': _doc}


class ApiTdsDomainsSave(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsDomainsSave: {0}'.format(data))

        _errors = {}
        try:
            obj = DomainModel(**data['payload'])
            _doc = obj.dict()

            if 'id' in data:
                domains, found = TdsDomain.get(_id=data['id'])
                if found == 1:
                    domain = domains.pop()

                    _attrs = domain.to_dict()
                    _attrs.update(_doc)

                    logger.info(f'Doc for update domain: {_attrs}')
                    resp, obj = TdsDomain.put(domain._id, _attrs)
                else:
                    return {'ok': False}, 404

            else:
                _meta = {
                    'createdon': datetime.utcnow(),
                }

                _doc.update(_meta)

                logger.info(f'Doc for create domain: {_doc}')
                resp, obj = TdsDomain.put(Page.generate_id(_doc['domain'], _doc['endpoint']), _doc)

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiTdsDomainsSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiTdsStats(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        _d = request.get_json()
        logger.info(u'Data ApiTdsStats: {0}'.format(_d))

        data = _d['payload']

        cpp = int(data['cpp'])
        start, end = get_timerange(data['range'], data['custom_range'])

        items = []
        total = 0
        aggs_name = None
        aggs_fields = ['campaign_alias', 'campaign_name', 'stream_name', 'stream', 'country', 'is_bot', 'is_uniq']

        kwargs = {}
        if 'filters' in data:
            for attr in aggs_fields:
                if attr in data['filters'] and data['filters'][attr]:
                    kwargs[attr] = data['filters'][attr]

        if data['mode'] == 'Clicks':
            _sort = [{'createdon': {'order': 'desc'}}]

            if data['sorting'] in ['click_id', 'ip', 'country', 'ua', 'campaign_name', 'stream_name']:
                _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
            elif data['sorting'] in ['createdon_asc']:
                _sort = [{'createdon': {'order': 'asc'}}]

            items, total = TdsHit.get(
                **kwargs,
                _sort=_sort,
                _process=False,
                _count=cpp,
                _offset=int(_d['offset'])*cpp,
                _range=('createdon', start, end, _d.get('timezone', 'UTC')),
                _source=[
                    'createdon',
                    'stream',
                    'stream_name',
                    'campaign_name',
                    'campaign_alias',
                    'click_id',
                    'ip',
                    'country',
                    'country_iso',
                    'ua',
                    'is_bot',
                    'is_uniq',
                    'action',
                    'url',
                    'subid',
                ]
            )

            def process_hit(item):
                _doc = item['_source']
                _doc['id'] = item['_id']    
                _doc['country_iso'] = _doc['country_iso'].lower()     
                return _doc

            items = [process_hit(item) for item in items]
        else:
            field = None
            if data['mode'] == 'By Day':
                aggs_name = 'Days'
                field = 'createdon'
            elif data['mode'] == 'By Campaign':
                aggs_name = 'Campaigns'
                field = 'campaign_id'
            elif data['mode'] == 'By Stream':
                aggs_name = 'Streams'
                field = 'stream'
            elif data['mode'] == 'By Stream Key':
                aggs_name = 'Streams'
                field = 'stream_key'
            elif data['mode'] == 'By Geo':
                aggs_name = 'Countries'
                field = 'country'
            elif data['mode'] == 'By Link':
                aggs_name = 'Links'
                field = 'url'
            elif data['mode'] == 'By User-Agent':
                aggs_name = 'User-Agents'
                field = 'ua'
            elif data['mode'] == 'By IP':
                aggs_name = 'IP'
                field = 'ip'
            elif data['mode'] == 'By Sub-ID':
                aggs_name = 'Sub-ID'
                field = 'subid'
            elif data['mode'] == 'By Action':
                aggs_name = 'Actions'
                field = 'action'

            if field:
                items, total = TdsHit.aggs_stats(
                    field, 
                    _range=('createdon', start, end, _d.get('timezone', 'UTC')),
                    _filters=kwargs
                )

        return {
            'ok': True, 
            'items': items, 
            'total': total, 
            'aggs_name': aggs_name,
            'filters': TdsHit.aggs(aggs_fields, _range=('createdon', start, end, _d.get('timezone', 'UTC')))
        }


class ApiTdsCampaigns(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaigns: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['name', 'alias']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        kwargs = {}
        if 'filters_group' in data['payload'] and data['payload']['filters_group']:
            kwargs['groups'] = data['payload']['filters_group']

        campaigns, _ = TdsCampaign.get(
            **kwargs,
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'name', 
                'alias',
                'createdon',
                'updatedon',
                'is_active',
                'is_split',
                'groups',
                'domain',
                'streams',
            ]
        )

        start, end = get_timerange(data['payload']['range'], data['payload']['custom_range'])
        stats, _ = TdsHit.aggs_stats('stream', _range=('createdon', start, end, data.get('timezone', 'UTC')))
        stats = {item['term']: {'hits': item['hits'], 'uc': item['uc']} for item in stats}

        def process_campaign(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            _doc['url'] = '{0}{1}'.format(_doc['domain'], _doc['alias'])
            return _doc

        return {
            'ok': True, 
            'items': [process_campaign(item) for item in campaigns], 
            'stats': stats,
            'filters': TdsCampaign.aggs(['groups'])
        }


class ApiTdsCampaignsGet(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json(silent=True)
        logger.info(u'Data ApiTdsCampaignsGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            campaigns, found = TdsCampaign.get(_id=data['id'])
            if found == 1:
                campaign = campaigns.pop()
                _attrs = campaign.to_dict()
                obj = CampaignModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Campaign found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404
        else:
            _doc['alias'] = BaseEntity.get_urlsafe_string(6)
            _doc['groups'] = []
            _doc['ttl'] = 86400

        domains, _ = TdsDomain.get(
            _all=True,
            _process=False,
            _source=[
                'domain', 
                'endpoint',
                'is_https',
            ]
        )

        campaigns, _ = TdsCampaign.get(
            _all=True,
            _process=False,
            _source=[
                'name', 
                'groups',
            ]
        )

        def process_campaign(_doc):
            return {
                'id': _doc['_id'],
                'name': _doc['_source']['name']
            }

        _groups = []
        for item in campaigns:
            _groups += item['_source'].get('groups', [])

        _opts = {
            'countries': [{'iso': item.alpha_2, 'country': item.name} for item in pycountry.countries],
            'domains': ['{2}://{0}{1}'.format(item['_source']['domain'], item['_source']['endpoint'], 'https' if item['_source']['is_https'] else 'http') for item in domains],
            'campaigns': [process_campaign(item) for item in campaigns if not data or (data and data.get('id') != item['_id'])],
            'groups': sorted(list(set(_groups))),
            'actions': [
                {'key': '404', 'value': '404 NotFound'},
                {'key': 'http', 'value': 'HTTP Redirect'},
                {'key': 'js', 'value': 'JS Redirect'},
                {'key': 'meta', 'value': 'Meta Redirect'},
                {'key': 'curl', 'value': 'cURL'},
                {'key': 'remote', 'value': 'Remote URL'},
                {'key': 'campaign', 'value': 'Send to Campaign'},
                {'key': 'html', 'value': 'Show as HTML'},
            ],
            'processors': [
                'softswiss',
                'pelican'
            ]
        }

        if data:
            _doc['postback_url'] = f"{_doc['domain']}postback/{data['id']}"

        return {'ok': True, 'options': _opts, 'campaign': _doc}


class ApiTdsCampaignsSave(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsSave: {0}'.format(data))

        _errors = {}
        try:
            obj = CampaignModel(**data['payload'])
            _doc = obj.dict()

            def process_streams(_s):
                # check all streams
                _res = []
                for stream in _s:
                    if 'id' not in stream:
                        stream['id'] = BaseEntity.get_urlsafe_string(6)
                    if stream.get('is_default'):
                        stream['position'] = None
                        stream['is_bot'] = False
                        stream['advanced_mode'] = False
                        stream['is_unique'] = False
                        stream['is_mobile'] = False
                        stream['is_empty_referrer'] = False
                        stream['is_ipv6'] = False
                        stream['geo'] = []
                        stream['ip'] = None
                        stream['ua'] = None
                        stream['subid'] = None
                    if stream.get('is_bot'):
                        stream['advanced_mode'] = False
                        stream['is_unique'] = False
                        stream['is_mobile'] = False
                        stream['is_empty_referrer'] = False
                        stream['is_ipv6'] = False
                        stream['geo'] = []
                        stream['ip'] = None
                        stream['ua'] = None
                        stream['subid'] = None

                    if stream['action'] in ['http', 'js', 'meta', 'curl', 'remote']:
                        stream['campaign'] = None
                        stream['html'] = None
                    elif stream['action'] in ['404']:
                        stream['url'] = None
                        stream['campaign'] = None
                        stream['html'] = None
                    elif stream['action'] in ['campaign']:
                        stream['url'] = None
                        stream['html'] = None
                    elif stream['action'] in ['html']:
                        stream['url'] = None
                        stream['campaign'] = None

                    _res.append(stream)
                return sorted(_res, key = lambda i: int(i.get('position') or 1000))

            if 'id' in data:
                campaigns, found = TdsCampaign.get(_id=data['id'])
                if found == 1:
                    campaign = campaigns.pop()

                    _attrs = campaign.to_dict()
                    _attrs.update(_doc)

                    _attrs['streams'] = process_streams(_attrs['streams'])
                    _attrs['updatedon'] = datetime.utcnow()

                    logger.info(f'Doc for update campaign: {_attrs}')
                    resp, obj = TdsCampaign.put(campaign._id, _attrs)
                else:
                    return {'ok': False}, 404

            else:
                _meta = {
                    'createdon': datetime.utcnow(),
                    'updatedon': datetime.utcnow(),
                }

                _doc.update(_meta)
                _doc['streams'] = process_streams(_doc['streams'])

                logger.info(f'Doc for create campaign: {_doc}')
                resp, obj = TdsCampaign.put(Page.generate_id(_doc['alias'], _doc['domain']), _doc)

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiTdsCampaignsSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.list.min_items': 'Required field',
                'type_error.none.not_allowed': 'Required field',
                'type_error.integer': 'Only integer value accepted',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiTdsCampaignsClone(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsClone: {0}'.format(data))

        if 'id' in data:
            campaigns, found = TdsCampaign.get(_id=data['id'])
            if found == 1:
                campaign = campaigns.pop()

                _doc = campaign.to_dict()

                # check all streams
                _res = []
                for stream in _doc['streams']:
                    stream['id'] = BaseEntity.get_urlsafe_string(6)
                    _res.append(stream)

                _doc['streams'] = _res
                _doc['alias'] = BaseEntity.get_urlsafe_string(6)
                _doc['name'] = '{0} [{1}]'.format(campaign.name, _doc['alias'])
                _doc['createdon'] = datetime.utcnow()
                _doc['updatedon'] = datetime.utcnow()

                logger.info(f'Doc for clone campaign: {_doc}')
                TdsCampaign.put(ElasticEntity.generate_id(_doc['alias'], _doc['domain']), _doc)

                return {'ok': True}

        return {'ok': False}, 404


class ApiTdsCampaignsClear(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsClear: {0}'.format(data))

        if 'id' in data:
            campaigns, found = TdsCampaign.get(_id=data['id'])
            if found == 1:
                campaign = campaigns.pop()
                if campaign.is_active:
                    return {'ok': False}
                else:
                    tdscampaign_clear.apply_async(args=[campaign._id])
                    return {'ok': True}

        return {'ok': False}, 404


class ApiTdsCampaignsToggle(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsToggle: {0}'.format(data))

        campaigns, found = TdsCampaign.get(_id=data['campaign'])
        if found == 1:
            campaign = campaigns.pop()

            _c = None
            _s = None
            _status = False

            if 'stream' in data:
                _s = data['stream']

                _res = []
                for stream in campaign.streams:
                    if stream['id'] == _s:
                        _status = not stream.get('is_active', False)
                        stream['is_active'] = _status                        
                    _res.append(stream)

                campaign.streams = _res
                TdsCampaign.put(campaign._id, campaign.to_dict())
            else:
                _status = not campaign.is_active
                campaign.is_active = _status
                TdsCampaign.put(campaign._id, campaign.to_dict())
                _c = campaign.alias

            return {'ok': True, 'status': _status, 'campaign': _c, 'stream': _s}

        return {'ok': False}, 404


class ApiTdsBotsUpload(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        logger.info(u'Data ApiTdsBotsUpload: {0}'.format(request.form))
        file = request.files['file']
        data = [item.strip().decode() for item in file.readlines()]
        tdscampaign_bots.apply_async(args=[data, request.form['section']])
        return {'ok': True}


class ApiTdsSettings(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json(silent=True)
        logger.info(u'Data ApiTdsBots: {0}'.format(data))
        ip_count = current_app.redis.scard(f'tds_bots_ip')
        ua_count = current_app.redis.scard(f'tds_bots_ua')

        _sort = [{'createdon': {'order': 'desc'}}]
        campaigns, _ = TdsCampaign.get(
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'name', 
                'alias',
            ]
        )

        def process_uniq(s):
            _doc = s['_source']
            _doc['id'] = s['_id']
            _doc['count'] = current_app.redis.hlen(f'tds_uniq_{_doc["alias"]}')
            return _doc

        uniq = [process_uniq(item) for item in campaigns]

        return {'ok': True, 'ip_count': ip_count, 'ua_count': ua_count, 'uniq': uniq}


class ApiTdsPostbacks(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsPostbacks: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['campaign_name', 'postback_id']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        postbacks, _ = TdsPostback.get(
            _all=True,
            _sort=_sort,
            _process=False
        )

        def process_postback(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            # term, process data on post request
            _args = loads(_doc['args'])
            if _args['a'] == 'reg':
                _doc['action'] = 'Signup'
                _doc['tag'] = 'is-disable'
            if _args['a'] in ['dep', 'first_dep']:
                _doc['action'] = 'Deposit'
                _doc['tag'] = 'is-active'
            return _doc

        return {'ok': True, 'items': [process_postback(item) for item in postbacks]}


class ApiTdsBotsClear(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsBotsClear: {0}'.format(data))
        current_app.redis.delete(f'tds_bots_{data["section"]}')
        return {'ok': True}


class ApiTdsBotsDownload(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsBotsDownload: {0}'.format(data))
        _data = current_app.redis.smembers(f'tds_bots_{data["section"]}')

        def process_item(s):
            s = s.decode()
            if data["section"] == 'ip' and s.isdigit():
                s = ipaddress.ip_address(int(s))
            return str(s)

        return {
            'ok': True, 
            'content': '\n'.join(sorted([process_item(item) for item in list(_data)])), 
            'content_type': 'plain/text', 
            'filename': f'export-{data["section"]}-{len(_data)}.txt'
        }


class ApiTdsCampaignUniqClear(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignUniqClear: {0}'.format(data))

        campaigns, total = TdsCampaign.get(_id=data['id'])
        if total == 1:
            campaign = campaigns.pop()
            current_app.redis.delete(f"tds_uniq_{campaign.alias}")
            return {'ok': True}

        return {'ok': False}


class ApiResourceIndexate(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceIndexate: {0}'.format(data))

        if 'key' in data:
            pages, found = Page.get(_id=data['key']['key'])
            if found == 1:
                page = pages.pop()

                if page.is_active and page.is_searchable and not page.is_redirect:
                    SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
                    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
                    
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(current_app.config['GOOGLE_API_CREDENTIALS'], scopes=SCOPES)
                    http = credentials.authorize(httplib2.Http())
                    
                    url = get_page_url(page.to_dict(), True)
                    logger.info(f'URL for indexate: {url}')

                    content = {
                        'url': url,
                        'type': 'URL_UPDATED'
                    }
                    response, content = http.request(ENDPOINT, method="POST", body=dumps(content))
                    result = loads(content.decode())
                    logger.info(f'Indexing API response: {result}')

                    msg = None
                    if response['status'] in ['200']:
                        msg = f":mag: Indexing complete: {result['urlNotificationMetadata']['url']}"
                    else:
                        msg = f":mag: Indexing error: {result['error']['code']}, {result['error']['status']}"

                    if msg:
                        send_notify.apply_async(args=[msg])
                    return {'ok': response['status'] in ['200']}

        return {'ok': False}

class ApiResourceSignupLink(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSignupLink: {0}'.format(data))

        f = Fernet(current_app.config['FERNET_KEY'])
        _token = {
            'key': data['key'],
            'expired': datetime.timestamp(datetime.utcnow() + timedelta(days=1))
        }
        token = f.encrypt(dumps(_token).encode())
        url = f"https://{current_app.config['DASHBOARD_DOMAIN']}/signup?invite=" + token.decode()
        logger.info(f'URL generated: {url}')

        return {'ok': True, 'url': url}


class ApiActivity(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiActivity: {0}'.format(data))

        _res = None
        _errors = {}
        _result = False

        try:
            _id = None
            obj = None

            _doc = {
                'project': os.environ.get('PROJECT', 'project'),
                'ip': current_user.ip,
                'country': current_user.location,
                'country_iso': current_user.location_iso,
                'ua': str(current_user.user_agent),
                'is_bot': current_user.user_agent.is_bot,
                'cid': current_user.client_id,
                'createdon': datetime.utcnow().replace(microsecond=0)
            }
            core = data.get('core')
            if core == 'Ticket':
                obj = ActivityTicketModel(**data)

                _doc['activity'] = 'ticket'
                _doc['subject'] = obj.subject
                _doc['contacts'] = obj.contacts
                _doc['name'] = obj.name
                _doc['message'] = obj.message

                _res = 'Ticket has been sent'
                _id = Activity.generate_id(*_doc.values())
            elif core == 'Subscribe':
                obj = ActivitySubscribeModel(**data)

                _doc['activity'] = 'subscribe'
                _doc['email'] = obj.email

                _res = 'You are subscribed to the newsletter'
                _id = Activity.generate_id(*_doc.values())
            elif core == 'Vote':
                obj = ActivityFeedbackModel(**data)

                _doc['activity'] = 'feedback'
                _doc['rate'] = obj.rate
                _doc['casino'] = obj.casino
                _doc['casino_id'] = obj.casino_id

                _res = 'Your rate has been sent'
                _id = Activity.generate_id(*_doc.values())
            elif core == 'Complaint':
                obj = ActivityComplaintModel(**data)

                _doc['activity'] = 'complaint'

                if obj.casino_selected.get('title') and obj.casino_selected.get('id'):
                    _doc['casino'] = obj.casino_selected['title']
                    _doc['casino_id'] = obj.casino_selected['id']

                _doc['country'] = obj.country
                _cn = pycountry.countries.get(name=_doc['country'])
                if _cn:
                    _doc['country_iso'] = _cn.alpha_2.lower()

                _doc['message'] = obj.message
                _doc['subject'] = obj.subject
                _doc['name'] = obj.name
                _doc['amount'] = obj.amount
                _doc['currency'] = obj.currency
                _doc['username'] = obj.username
                _doc['email'] = obj.email
                _doc['reply'] = []
                _doc['status'] = 'draft'
                _doc['is_active'] = False

                _res = 'Your complaint has been sent'
                _id = Activity.generate_id(*_doc.values())

            if _id:
                resp, obj = Activity.put(_id, _doc)
                logger.info('Activity: {0}'.format(resp))
                _result = True

        except ValidationError as e:
            logger.warning('ApiActivity validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.email': 'Enter your email address',
                'type_error.none.not_allowed': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {
            'ok': _result, 
            'data': data,
            'errors': _errors,
            'message': _res,
        }


class ApiComplaintOptions(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiComplaintOptions: {0}'.format(data))

        options = Page.get_options()

        _sort = [{'title.keyword': {'order': 'asc'}}]
        casinos, _ = Page.get(
            category='provider',
            is_active=True,
            is_searchable=True,
            is_redirect=False, 
            is_draft=False,
            locale=current_app.config['BABEL_DEFAULT_LOCALE'],
            _all=True,
            _process=False,
            _sort=_sort,
            _source=[
                'id', 
                'title',
                'alias',
            ]
        )

        def process_casino(item):
            return {'id': item['_id'], 'title': item['_source']['title']}

        casino = None
        if data.get('casino_id') and data.get('casino'):
            casino = {'id': data['casino_id'], 'title': data['casino']}            

        return {
            'ok': True, 
            'countries': [item.name for item in pycountry.countries],
            'currencies': options['currency'],
            'casinos': [process_casino(item) for item in casinos],
            'subject_list': current_app.config['COMPLAINT_SUBJECTS'],
            'payload': {
                'casino_selected': casino,
                'currency': 'EUR',
                'country': current_user.country_full
            }
        }

class ApiTelegramBots(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramBots: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['username']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        bots, _ = TelegramBot.get(
            _all=True,
            _sort=_sort,
            _process=False,
        )

        def process_domain(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            return _doc

        return {'ok': True, 'items': [process_domain(item) for item in bots]}


class ApiTelegramBotsGet(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramBotsGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            bots, found = TelegramBot.get(_id=data['id'])
            if found == 1:
                bot = bots.pop()
                _attrs = bot.to_dict()
                obj = TelegramBotModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Bot found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404
        else:
            _doc = {
                'tags': []
            }

        _aggs = TelegramBot.aggs(['tags'])

        domains, _ = TdsDomain.get(
            _all=True,
            _process=False,
            _source=['domain']
        )

        _opts = {
            'tags': _aggs.get('tags', []),
            'domains': [item['_source']['domain'] for item in domains],
            'modules': [
                'spectator',
                'users',
                'balance',
                'referral',
            ]
        }
        logger.info(f'Options found: {_opts}')

        return {'ok': True, 'options': _opts, 'bot': _doc}


class ApiTelegramBotsSave(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramBotsSave: {0}'.format(data))

        _errors = {}
        try:
            obj = TelegramBotModel(**data['payload'])
            _doc = obj.dict()

            if 'id' in data:
                bots, found = TelegramBot.get(_id=data['id'])
                if found == 1:
                    bot = bots.pop()

                    _attrs = bot.to_dict()
                    _attrs.update(_doc)
                    _attrs.update(telegram_getMe(_attrs['token']))
                    _attrs.update({'updatedon': datetime.utcnow()})

                    logger.info(f'Doc for update bot: {_attrs}')
                    resp, obj = TelegramBot.put(bot._id, _attrs)

                    telegram_setWebhook(obj.token, f'https://{obj.domain}/webhook/{obj._id}')
                else:
                    return {'ok': False}, 404

            else:
                _meta = {
                    'createdon': datetime.utcnow(),
                }

                _doc.update(_meta)
                _doc.update(telegram_getMe(_doc['token']))

                logger.info(f'Doc for create bot: {_doc}')
                resp, obj = TelegramBot.put(Page.generate_id(_doc['token']), _doc)

                telegram_setWebhook(obj.token, f'https://{obj.domain}/webhook/{obj._id}')

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiTelegramBotsSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'type_error.none.not_allowed': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}        


class ApiTelegramChats(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChats: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['username', 'type', 'title']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['updatedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        chats, _ = TelegramChat.get(
            _all=True,
            _sort=_sort,
            _process=False,
        )

        def process_chat(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            return _doc

        return {'ok': True, 'items': [process_chat(item) for item in chats]}


class ApiTelegramChatsGet(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            chats, found = TelegramChat.get(_id=data['id'])
            if found == 1:
                chat = chats.pop()
                _attrs = chat.to_dict()
                obj = TelegramChatModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Chat found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404
        else:
            _doc = {
                'tags': []
            }

        _aggs = TelegramChat.aggs(['tags'])

        bots, _ = TelegramBot.get(
            _all=True,
            _process=False,
        )

        _opts = {
            'tags': _aggs.get('tags', []),
            'bots': [item['_source']['username'] for item in bots],
        }
        logger.info(f'Options found: {_opts}')

        return {'ok': True, 'options': _opts, 'chat': _doc}


class ApiTelegramChatsSave(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsSave: {0}'.format(data))

        _errors = {}
        try:
            data['payload']['photo'] = data['photo']
            obj = TelegramChatModel(**data['payload'])
            _doc = obj.dict()

            if 'id' in data:
                chats, found = TelegramChat.get(_id=data['id'])
                if found == 1:
                    chat = chats.pop()

                    _attrs = chat.to_dict()
                    _attrs.update(_doc)

                    _chat, _errors = telegram_checkChat(_attrs)

                    if not _errors:
                        _attrs.update(_chat)
                        _attrs.update({'updatedon': datetime.utcnow()})
                        logger.info(f'Doc for update chat: {_attrs}')
                        resp, obj = TelegramChat.put(chat._id, _attrs)
                else:
                    return {'ok': False}, 404

            else:
                _meta = {
                    'createdon': datetime.utcnow(),
                }

                _doc.update(_meta)

                _chat, _errors = telegram_checkChat(_doc)

                if not _errors:
                    _doc.update(_chat)
                    logger.info(f'Doc for create chat: {_doc}')
                    resp, obj = TelegramChat.put(Page.generate_id(_doc['chat_id'], _doc['username'], _doc['createdon']), _doc)

            if not _errors:
                return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiTelegramChatsSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}          


class ApiTelegramChatsUsers(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsUsers: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        chats, _ = TelegramChat.get(
            _all=True,
            _sort=_sort,
            _process=False,
        )

        def process_chat(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            return _doc

        return {'ok': True, 'items': [process_chat(item) for item in chats]}        


class ApiTelegramChatsMessages(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsMessages: {0}'.format(data))

        _items = []
        chats, found = TelegramChat.get(_id=data['chat_id'])
        if found:
            chat = chats.pop()

            _sort = [{'createdon': {'order': 'desc'}}]

            if data['sorting'] in ['status']:
                _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
            elif data['sorting'] in ['message_id']:
                _sort = [{data['sorting']: {'order': 'desc'}}]

            messages, _ = TelegramMessage.get(
                recipients=chat.username,
                _all=True,
                _sort=_sort,
                _process=False,
            )

            def process_message(item):
                _doc = item['_source']
                _doc['id'] = item['_id']
                return _doc

            _items = [process_message(item) for item in messages]

        return {'ok': True, 'items': _items}        


class ApiTelegramChatsMessagesGet(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsMessagesGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            messages, found = TelegramMessage.get(_id=data['id'])
            if found == 1:
                message = messages.pop()
                _attrs = message.to_dict()
                obj = TelegramMessageModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Message found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404
        else:
            chats, found = TelegramChat.get(_id=data['chat_id'])
            _chats = []
            if found:
                chat = chats.pop()
                _chats = [chat.username]

            _doc = {
                'recipients': _chats,
                'send_without_notify': True,
                'tags': [],
                'photo': None
            }

        _aggs = TelegramMessage.aggs(['tags'])

        chats, _ = TelegramChat.get(
            is_active=True,
            _all=True,
            _process=False,
        )

        _opts = {
            'tags': _aggs.get('tags', []),
            'chats': [item['_source']['username'] for item in chats],
            'types': ['photo', 'text', 'forward', 'copy']
        }
        logger.info(f'Options found: {_opts}')

        return {'ok': True, 'options': _opts, 'message': _doc}


class ApiTelegramChatsMessagesSave(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsMessagesSave: {0}'.format(data))

        _errors = {}
        try:
            if data['photo']:
                data['payload']['photo'] = data['photo']

            obj = TelegramMessageModel(**data['payload'])
            _doc = obj.dict()

            if 'id' in data:
                messages, found = TelegramMessage.get(_id=data['id'])
                if found == 1:
                    message = messages.pop()

                    _attrs = message.to_dict()
                    _attrs.update(_doc)

                    s = boto_session.Session()
                    config = TransferConfig(use_threads=False)
                    client = s.client('s3', 
                        endpoint_url=current_app.config['MINIO_ENDPOINT'], 
                        aws_access_key_id=current_app.config['MINIO_ACCESS_KEY'],
                        aws_secret_access_key=current_app.config['MINIO_SECRET_KEY']
                    )
                    bucket = current_app.config['MINIO_BUCKET']

                    if _attrs['status'] == 'published' or (_doc['send_task'] and _attrs['status'] == 'draft'):
                        i = 0
                        for chat in _doc['recipients']:
                            chats, found_chats = TelegramChat.get(username=chat)
                            if found_chats:
                                obj_chat = chats.pop()
                                if obj_chat.is_active:
                                    logger.info(f'Send to chat: @{chat}, chat_id: {obj_chat.chat_id}')
                                    bots, found_bots = TelegramBot.get(username=obj_chat.bot_admin)
                                    if found_bots:
                                        bot = bots.pop()
                                        if bot.is_active:

                                            parser = TelegramContentParser()
                                            parser.feed(_attrs['content'])
                                            _text = '\n'.join(parser.content)

                                            # html = Html()
                                            # dom = html.feed(_attrs['content'])
                                            # # _text = dom.join('\n\n', 5)

                                            # _res = []
                                            # for item in dom.find('p'):
                                            #     _res.append(str(item).replace('<p >', '').replace('</p>', ''))

                                            # _text = '\n'.join(_res)

                                            if _doc['type'] == 'text' and _doc['photo']:
                                                url = f"{current_app.config['PREFERRED_URL_SCHEME']}://{current_app.config['DOMAIN']}/api/v3/media/{_doc['photo']}"
                                                _text = f'<a href="{url}">&#8205;</a>' + _text

                                            if _doc['send_task'] and _doc['status'] == 'draft':
                                                
                                                if _doc['type'] == 'text':
                                                    _attrs.update(telegram_sendMessage(bot.token, int(obj_chat.chat_id), _text, _attrs['send_without_notify'], _attrs['send_without_link_preview']))
                                                elif _doc['type'] == 'photo':
                                                    with tempfile.NamedTemporaryFile() as tmp:
                                                        client.download_fileobj(bucket, _doc['photo'], tmp, Config=config)
                                                        tmp.seek(0)
                                                        _attrs.update(telegram_sendPhoto(bot.token, int(obj_chat.chat_id), _text, tmp, _attrs['send_without_notify']))

                                                _attrs.update({'status': 'published', 'recipients': [chat]})                            
                                            elif _doc['status'] == 'published':

                                                if _attrs['type'] == 'text':
                                                    _attrs.update(telegram_editMessageText(bot.token, int(obj_chat.chat_id), _attrs['message_id'], _text, _attrs['send_without_notify'], _attrs['send_without_link_preview']))
                                                elif _doc['type'] == 'photo':
                                                    #### change photo attr - key
                                                    _id = message._id if i == 0 else Page.generate_id(message._id, i)
                                                    resp, obj = TelegramMessage.put(_id, _attrs)
                                                    ####
                                                    with tempfile.NamedTemporaryFile() as tmp:
                                                        client.download_fileobj(bucket, obj.photo, tmp, Config=config)
                                                        tmp.seek(0)
                                                        _attrs.update(telegram_editMessageMedia(bot.token, int(obj_chat.chat_id), _attrs['message_id'], tmp, _text))

                                            logger.info(f'Doc for update message: {_attrs}')
                                            _id = message._id if i == 0 else Page.generate_id(message._id, i)
                                            logger.info(f'Save as ID: {_id}')
                                            resp, obj = TelegramMessage.put(_id, _attrs)
                                            i += 1
                    else:
                        logger.info(f'Doc for update message: {_attrs}')
                        resp, obj = TelegramMessage.put(message._id, _attrs)
                else:
                    return {'ok': False}, 404

            else:
                _meta = {
                    'createdon': datetime.utcnow(),
                    'status': 'draft',
                }

                _doc.update(_meta)
                logger.info(f'Doc for create message: {_doc}')
                resp, obj = TelegramMessage.put(Page.generate_id(_doc['type'], _doc['content'], _doc['createdon']), _doc)

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiTelegramChatsMessagesSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.list.min_items': 'Required field'
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}          


class ApiTelegramChatsMessagesDelete(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsMessagesDelete: {0}'.format(data))

        if 'id' in data:
            messages, found = TelegramMessage.get(_id=data['id'])
            if found == 1:
                message = messages.pop()

                if message.status == 'published':
                    for chat in message.recipients:
                        chats, found_chats = TelegramChat.get(username=chat)
                        if found_chats:
                            obj_chat = chats.pop()
                            if obj_chat.is_active:
                                bots, found_bots = TelegramBot.get(username=obj_chat.bot_admin)
                                if found_bots:
                                    bot = bots.pop()
                                    if bot.is_active:
                                        telegram_api(bot.token, 'deleteMessage', json={'chat_id': message.chat_id, 'message_id': message.message_id})

                                        message.status = 'draft'
                                        message.publishedon = None
                                        message.chat_id = None
                                        message.chat_username = None
                                        message.message_id = None
                                        message.sender_id = None
                                        message.sender_username = None
                                        message.raw = None

                                        TelegramMessage.put(message._id, message.to_dict())
                                        return {'ok': True}

        return {'ok': False}, 404


class ApiTelegramChatsMessagesRemove(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsMessagesRemove: {0}'.format(data))

        if 'id' in data:
            messages, found = TelegramMessage.get(_id=data['id'])
            if found == 1:
                message = messages.pop()

                if message.status == 'draft':
                    TelegramMessage.delete(message._id)
                    return {'ok': True}

        return {'ok': False}, 404


class ApiTelegramChatsMessagesClone(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsMessagesClone: {0}'.format(data))

        if 'id' in data:
            messages, found = TelegramMessage.get(_id=data['id'])
            if found == 1:
                message = messages.pop()

                if message.status in ['published', 'scheduled']:

                    message.createdon = datetime.utcnow()
                    message.status = 'draft'
                    message.publishedon = None
                    message.chat_id = None
                    message.chat_username = None
                    message.message_id = None
                    message.sender_id = None
                    message.sender_username = None
                    message.raw = None

                    TelegramMessage.put(Page.generate_id(message._id, message.createdon, Page.get_urlsafe_string(12)), message.to_dict())
                    return {'ok': True}

        return {'ok': False}, 404        


class ApiTelegramChatsMessagesPreview(Resource):
    @login_required
    @zone_required(zone='telegram')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTelegramChatsMessagesPreview: {0}'.format(data))

        payload = data['payload']

        s = boto_session.Session()
        config = TransferConfig(use_threads=False)
        client = s.client('s3', 
            endpoint_url=current_app.config['MINIO_ENDPOINT'], 
            aws_access_key_id=current_app.config['MINIO_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['MINIO_SECRET_KEY']
        )

        if data['photo'] and 'data:' in data['photo']:
            _hash = TelegramMessage.generate_id(datetime.utcnow(), TelegramMessage.get_urlsafe_string(12))
            file_key = f'messages/{datetime.utcnow().strftime("%Y%m%d")}/{_hash}'

            with tempfile.NamedTemporaryFile() as tmp:
                meta, raw = data['photo'].split(',')
                tmp.write(decodebytes(raw.encode()))
                tmp.seek(0)

                client.upload_fileobj(tmp, current_app.config['MINIO_BUCKET'], file_key, Config=config, ExtraArgs={'ContentType': meta.replace('data:', '').replace('base64', '')})
                payload['photo'] = file_key

        parser = TelegramContentParser()
        parser.feed(payload.get('content', ''))
        _text = '\n'.join(parser.content)

        # html = Html()
        # dom = html.feed(payload.get('content', ''))

        # _res = []
        # for item in dom.find('p'):
        #     _res.append(str(item).replace('<p >', '').replace('</p>', ''))

        # _text = '\n'.join(_res)

        if payload['type'] == 'text' and payload['photo']:
            url = f"{current_app.config['PREFERRED_URL_SCHEME']}://{current_app.config['DOMAIN']}/api/v3/media/{payload['photo']}"
            _text = f'<a href="{url}">&#8205;</a>' + _text

        logger.info(f'Message for preview: {_text}')

        _resp = {}
        for chat_id in current_app.config['TELEGRAM_RECIPIENTS']:
            if payload['type'] == 'text':
                _resp = telegram_sendMessage(current_app.config['TELEGRAM_TOKEN'], int(chat_id), _text, payload.get('send_without_notify', False), payload.get('send_without_link_preview', False))
            elif payload['type'] == 'photo':
                if payload['photo']:
                    with tempfile.NamedTemporaryFile() as tmp:
                        client.download_fileobj(current_app.config['MINIO_BUCKET'], payload['photo'], tmp, Config=config)
                        tmp.seek(0)
                        _resp = telegram_sendPhoto(current_app.config['TELEGRAM_TOKEN'], int(chat_id), _text, tmp, payload.get('send_without_notify', False))

        return {'ok': bool(_resp)}


class ApiMedia(Resource):
    def get(self, file_key):
        logger.info(f'Get ApiMedia: {file_key}')
        try:
            s = boto_session.Session()
            config = TransferConfig(use_threads=False)
            client = s.client('s3', 
                endpoint_url=current_app.config['MINIO_ENDPOINT'], 
                aws_access_key_id=current_app.config['MINIO_ACCESS_KEY'],
                aws_secret_access_key=current_app.config['MINIO_SECRET_KEY']
            )
            bucket = current_app.config['MINIO_BUCKET']
            with tempfile.NamedTemporaryFile() as tmp:
                meta = client.head_object(Bucket=bucket, Key=file_key)
                logger.info(f'Meta found: {meta}')
                client.download_fileobj(bucket, file_key, tmp, Config=config)
                tmp.seek(0)
                response = make_response(tmp.read())
                response.headers['content-type'] = meta['ContentType']
                return response
        except Exception as e:
            logger.error(f'Exception ApiMedia: {e}')
            return {'ok': False}, 404