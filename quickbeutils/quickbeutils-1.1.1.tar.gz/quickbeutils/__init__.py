import os
import json
import random
from time import sleep
from datetime import timedelta, datetime
from quickbelog import Log
import quickbeutils.gmail as gmail
import quickbeutils.aws_ses as aws_ses
import quickbeutils.slack as slack
from email.utils import formataddr
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SEND_EMAIL_VIA_GMAIL = 'GMAIL'
SEND_EMAIL_VIA_SMTP = 'SMTP'
SEND_EMAIL_VIA_AWS_SES = 'AWS_SES'


def send_email(
        sender: str, recipient: str,
        subject: str = None, sender_name: str = None,
        body_text: str = '',
        body_html: str = None,
        send_via: str = SEND_EMAIL_VIA_SMTP) -> bool:
    """

    :param body_html:
    :param body_text:
    :param sender: "From" address
    :param recipient: "To" address.
    :param subject: The subject line of the email.
    :param sender_name: Sender name is optional.
    :param send_via: One of the following: SMTP, AWS_SES, GMAIL
    :return:
    """

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr((sender_name, sender))
    msg['To'] = recipient

    if body_html is None:
        txt = body_text.replace('\n', '<br>')
        body_html = f"<html><head><title>{subject}</title></head><body>{txt}</body></html>"

    # Record the MIME types of both parts - text/plain and text/html
    # According to RFC 2046, the last part of a multipart message, in this case the HTML message is preferred.
    msg.attach(MIMEText(body_text, 'plain'))
    msg.attach(MIMEText(body_html, 'html'))

    send_via = send_via.upper().strip()

    try:
        if send_via == SEND_EMAIL_VIA_AWS_SES:
            aws_ses.send(sender=sender, recipient=recipient, msg=msg)
        elif send_via == SEND_EMAIL_VIA_GMAIL:
            gmail.send(sender=sender, recipient=recipient, msg=msg)
        else:
            raise ValueError(f'Sending method: {send_via} is not supported.')
        return True

    except SMTPException as e:
        Log.exception(f'Failed sending email from {sender} to {recipient} ({e.__class__.__name__} {e})')
        return False


def send_slack_message(recipient_id: str, text: str):
    slack.send_message(recipient_id=recipient_id, text=text)


def send_slack_attachment(recipient_id: str, text: str, file_path: str, file_name: str = None):
    slack.upload_file(recipient_id=recipient_id, comment=text, file_path=file_path, file_name=file_name)


def get_env_var_as_int(key: str, default: int = 0) -> int:
    value = os.getenv(key)
    try:
        default = int(default)
        value = int(float(value))
    except (TypeError, ValueError):
        value = default
    return value


def get_env_var_as_list(key: str, default: list = [], delimiter: str = ' ') -> list:
    value = os.getenv(key, '')
    try:
        tokens = [token.strip() for token in value.strip().split(delimiter)]
        return tokens
    except (TypeError, ValueError):
        return default


def get_env_var_as_dict(key: str, default: dict = {}) -> dict:
    try:
        if default is not None:
            default = json.dumps(default)
        return dict(json.loads(os.getenv(key).replace("'", '"')))
    except (TypeError, ValueError):
        return default


RETRY_PATTERN_INCREASING = 'INCREASING'
RETRY_PATTERN_FIX = 'FIX'
RETRY_PATTERN_RANDOM = 'RANDOM'


def retry(
        func, *args,
        retries: int = 2,
        delay: float = 2.0,
        time_limit: float = 0,
        delay_pattern: str = RETRY_PATTERN_INCREASING):
    """

    :param func: Function to execute. Function has to return rais any exception or error if it fails.
    :param args: Arguments for this function has to follow the function
    :param retries: Number of retries, if the last attempt will fail TimeoutError will be raised.
    :param delay: Delay period (in seconds) between retries.
    :param time_limit: Time limit for all retries.
    :param delay_pattern: Delay pattern
    :return:
    """

    sw_id = Log.start_stopwatch(f'Retry loop for {func}')
    sleep_time = delay
    delay_pattern = delay_pattern.upper()
    for i in range(1, retries+1):
        try:
            result = func(*args)
            return result
        except Exception as e:
            func_args = list(args)
            Log.warning(
                f'Failed the #{i} attempt ({e.__class__.__name__}: {e}). '
                f'Function: {func.__name__}, Arguments: {func_args}'
            )
            time_passed = Log.stopwatch_seconds(stopwatch_id=sw_id, print_it=False)
            if i < retries and (time_limit <= 0 or time_passed < time_limit):
                if delay_pattern in ['RAND', RETRY_PATTERN_RANDOM]:
                    sleep_time = random.uniform(delay/3, delay)
                elif delay_pattern in ['FIXED', RETRY_PATTERN_FIX]:
                    sleep_time = delay
                Log.debug(f'Retrying within {sleep_time} seconds.')

                sleep(sleep_time)
                sleep_time *= 1.625
            else:
                raise TimeoutError(
                    f'Failed {i} attempts for function {func.__name__}, aborting after {time_passed}.'
                )


def remove_from_string(s: str, characters_to_remove: str) -> str:
    """

    :param s: Base string.
    :param characters_to_remove: All characters  in this str will be removed from base string.
    :return: New string without these characters.
    """
    return s.translate(str.maketrans("", "", characters_to_remove))


TIME_UNITS_SECONDS = 'seconds'
VALID_TIME_UNITS_SECONDS = [TIME_UNITS_SECONDS, 'sec', 's']
TIME_UNITS_MILLISECOND = 'millisecond'
VALID_TIME_UNITS_MILLISECOND = [TIME_UNITS_MILLISECOND, 'msec', 'ms']
VALID_TIME_UNITS = VALID_TIME_UNITS_SECONDS + VALID_TIME_UNITS_MILLISECOND


def time_to_string(value: int, units: str = TIME_UNITS_SECONDS) -> str:
    units = units.lower()
    valid_units = VALID_TIME_UNITS
    if units not in valid_units:
        raise ValueError(f'Time unit {units} is not supported, please use one of these {VALID_TIME_UNITS}')

    if units in VALID_TIME_UNITS_MILLISECOND:
        value = value / 1000
        if value == int(value):
            value = int(value)

    delta = timedelta(seconds=value)

    minutes, seconds = divmod(value, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    seconds_label = f'{seconds} seconds' if seconds > 0 else ''
    minutes_label = f'{int(minutes)} minutes, ' if minutes > 0 else ''
    hours_label = f'{int(hours)} hours, ' if hours > 0 else ''
    days_label = f'{int(delta.days)} days, ' if delta.days > 0 else ''

    human = f'{days_label}{hours_label}{minutes_label}{seconds_label}'.strip().strip(',')

    return ' and'.join(human.rsplit(',', 1))
