"""
This is Asterisk PBX Salt module
"""
import base64
import ipaddress
import logging
import re
import os
from salt.utils import json
import salt.utils.event
from salt.ext.tornado import ioloop
from salt.ext.tornado import locks
from salt.ext.tornado.gen import sleep
import time
import subprocess
import uuid
try:
    from ipsetpy import ipset_list, ipset_create_set, ipset_add_entry
    from ipsetpy import ipset_del_entry, ipset_test_entry, ipset_flush_set
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False
try:
    from google.cloud import texttospeech
    HAS_TTS_LIBS = True
except ImportError:
    HAS_TTS_LIBS = False

__virtualname__ = 'asterisk'

log = logging.getLogger(__name__)


RE_IPSET_ENTRY = re.compile(
    r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?) '
    'timeout ([0-9]+) packets ([0-9]+) bytes ([0-9]+)( comment "(.+)")?$')


def __virtual__():
    '''
    Only load if celery libraries exist.
    '''
    if not HAS_LIBS:
        msg = 'ipsetpy lib not found, asterisk module not available.'
        log.warning(msg)
        return False, msg
    return True


def manager_action(action, timeout=5, no_wait=False, as_list=None):
    """
    Send AMI action and wait for reply if required.
    CLI Examples:
        salt-call asterisk.manager_action '{"Action":"Ping"}'

    """
    # Update action for timeout
    action.update({
        'timeout': timeout,
        'as_list': as_list,
    })
    # First check it is fire and forget case.
    if no_wait:
        __salt__['event.fire'](action, 'ami_action')
        return True
    # Fire an action event to asterisk_ami engine and wait for a reply event.
    async def fire():
        # Wait for waiter to start waiting :-))
        await waiter.wait()
        await sleep(0.01)
        # Ok we started a reply channel listening, fire!
        __salt__['event.fire'](action, 'ami_action')
    # Start a reply event listener before sending.
    async def wait_reply():
        event = salt.utils.event.MinionEvent(__opts__)
        # Generate a random reply channel
        reply_channel = action['reply_channel'] = uuid.uuid4().hex
        started = time.time()
        # Now send s signal to fire!
        waiter.set()
        # Wait until timeout.
        while started + timeout > time.time():
            ret = event.get_event(
                no_block=True, full=True,
                tag='ami_reply/{}'.format(reply_channel))
            if ret is None:
                await sleep(0.01)
            else:
                # Get a reply from the other side and return it.
                return ret['data']['Reply']
    # Synchronize callbacks not to miss a reply if it comes too quick.
    waiter = locks.Event()
    loop = ioloop.IOLoop(make_current=False)
    loop.spawn_callback(fire)
    res = loop.run_sync(wait_reply)
    return res


def put_file(path, data):
    """
    Save a local file from data.
    """
    log.info('Download from Odoo file %s.', path)
    open(path, 'wb').write(base64.b64decode(data.encode()))
    return True


def delete_file(path):
    log.info('Delete file %s.', path)
    os.unlink(path)
    return True


def get_file(path):
    log.info('Upload to Odoo file %s.', path)
    file_data = open(path, 'rb').read()
    return {
        'file_data': base64.b64encode(file_data).decode(),
    }


# Configuration files management
def _get_etc_dir():
    return __salt__['config.get']('asterisk_etc_dir', '/etc/asterisk/')


def get_config(file):
    res = get_file(os.path.join(_get_etc_dir(), file))
    return res


def put_config(file, data):
    res = put_file(os.path.join(_get_etc_dir(), file), data)
    return res


def delete_config(files):
    if type(files) is not list:
        files = list(files)
    for file in files:
        delete_file(os.path.join(_get_etc_dir(), file))
    return True


def get_all_configs():
    files = {}
    etc_dir = _get_etc_dir()
    for file in [k for k in os.listdir(
            etc_dir) if os.path.isfile(
            os.path.join(etc_dir, k)) and k.endswith('.conf')]:
        files[file] = get_file(os.path.join(etc_dir, file))
    log.info('Get %s configs.', len(files.keys()))
    return files


def put_all_configs(data):
    etc_dir = _get_etc_dir()
    for filename, filedata in data.items():
        put_file(os.path.join(etc_dir, filename), filedata)
    log.info('Put %s configs.', len(data.keys()))
    return True


# Voice prompts management
def _get_odoo_sounds_dir():
    data_dir = __salt__['config.get'](
        'asterisk_data_dir', '/var/lib/asterisk/')
    odoo_sounds_dir = os.path.join(data_dir, 'sounds', 'odoo')
    if not os.path.isdir(odoo_sounds_dir):
        os.mkdir(odoo_sounds_dir)
    return odoo_sounds_dir


def get_prompt(file):
    return get_file(os.path.join(_get_odoo_sounds_dir(), file))


def put_prompt(file, data):
    return put_file(
        os.path.join(_get_odoo_sounds_dir(), file), data)


def delete_prompt(file):
    delete_file(os.path.join(_get_odoo_sounds_dir(), file))
    return True


############### SECURITY FUNCTIONS ##################################

def get_banned():
    """
    Get banned IP addresses.

    CLI Example: salt asterisk asterisk.get_banned
    """
    result = []
    data = ipset_list('banned')
    lines = data.split('\n')
    for line in lines:
        # Try IP style
        found = RE_IPSET_ENTRY.search(line)
        if found:
            address, timeout, packets, bytes, comment = found.group(1), \
                found.group(2), found.group(3), \
                found.group(4), found.group(5)
            result.append({
                'address': found.group(1),
                'timeout': int(found.group(2)),
                'packets': int(found.group(3)),
                'bytes': int(found.group(4)),
                'comment': found.group(6)
            })
    log.debug('Banned entries: {}'.format(json.dumps(
        ['{}: {}'.format(k['address'], k['comment']) for k in result],
        indent=2)))
    return result


def remove_banned_address(address):
    """
    Remove banned IP address.

    CLI example: salt asterisk asterisk.remove_banned_address 1.2.3.4
    """
    log.info('Remove ban address %s', address)
    return ipset_del_entry('banned', address, exist=True)


def remove_banned_addresses(address_list):
    """
    Remove banned IP addresses.

    CLI example: salt asterisk asterisk.remove_banned_addressed [1.2.3.4,2.3.4.5]
    """
    for address in address_list:
        remove_banned_address(address)
    return True


def update_access_rules(rules):
    """
    Update Asterisk access rules e.g. re-create black and white lists.
    """
    # Destroy ipset lists as it will be re-filled.
    ipset_flush_set('whitelist')
    ipset_flush_set('blacklist')
    errors = []
    # Add new rules
    for rule in rules:
        try:
            ip_netmask = rule['address'] if rule['address_type'] == 'ip' \
                else '{}/{}'.format(
                    rule['address'],
                    str(ipaddress.IPv4Network(
                        rule['address'] + '/' + rule['netmask'])).split(
                        '/')[1])
        except (ipaddress.NetmaskValueError,
                ipaddress.AddressValueError) as e:
            error_message = ('Cannot convert netmask {} for '
                             'address: {}').format(rule['netmask'],
                                                   rule['address'])
            log.error(error_message)
            errors.append(error_message)
            continue
        if rule['access_type'] == 'deny':
            log.info('Adding {} to blacklist ipset'.format(ip_netmask))
            try:
                comment = rule['comment'] or 'Admin added'
                subprocess.check_output(
                    f'ipset add blacklist {ip_netmask} '
                    '--exist '
                    f'--comment "{comment}"', shell=True)
            except subprocess.CalledProcessError as e:
                log.error(f'ipset add error {e}')
                errors.append(str(e))
        elif rule['access_type'] == 'allow':
            log.info('Adding {} to whitelist ipset'.format(ip_netmask))
            ipset_add_entry('whitelist', ip_netmask, exist=True)
    if errors:
        raise Exception('\n'.join(errors))
    return True


def tts_create_sound(result_file_name,
                     text,
                     language='en-US',
                     voice='en-US-Wavenet-A',
                     pitch=0,
                     speaking_rate=1,
                     tts_key_file_path=None,
                     result_file_dir=None):
    """
    Crate sound file from text.

    CLI example: salt-call asterisk.tts_create_sound hello_world 'Hello world!' language='en-US' voice='en-US-Wavenet-A'  pitch=0 speaking_rate=1 tts_key_file_path=/srv/odoopbx/google_key.json result_file_dir='/var/lib/asterisk/sounds'
    You can fine hello_world.wav /var/lib/asterisk/sounds folder.
    """
    if not HAS_TTS_LIBS:
        log.error('TTS API not available, install with pip3 install google-cloud-texttospeech.')
        return
    if not tts_key_file_path:
        tts_key_file_path = __salt__['config.get'](
            'tts_google_key_file', '/srv/odoopbx/google_key.json')
    if not os.path.isfile(tts_key_file_path):
        raise Exception('File {} not found'.format(tts_key_file_path))
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = tts_key_file_path
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=voice,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        pitch=float(pitch),
        speaking_rate=float(speaking_rate),
        sample_rate_hertz=8000)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config)
    # The response's audio_content is binary.
    if not result_file_dir:
        result_file_dir = __salt__['config.get']('asterisk_sounds_dir',
                                                 '/var/lib/asterisk/sounds')
    file_path = os.path.join(
        result_file_dir, '{}.wav'.format(result_file_name))
    if not os.path.isdir(os.path.dirname(file_path)):
        log.warning('tts_create_sound: creating %s', os.path.dirname(file_path))
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
    return True
