"""Implements twitter."""

import argparse
import logging

import tweepy

from utils import timex
from utils.cache import cache

MAX_LEN_TWEET = 280
MAX_MEDIA_FILES = 4
log = logging.getLogger('twitter-wrapper')
logging.basicConfig(level=logging.INFO)


def _update_status(api, tweet_text, media_ids, in_reply_to_status_id):
    if len(media_ids) > 0 and in_reply_to_status_id:
        return api.update_status(
            tweet_text,
            media_ids=media_ids,
            in_reply_to_status_id=in_reply_to_status_id,
        )

    if len(media_ids) > 0:
        return api.update_status(tweet_text, media_ids=media_ids)

    if in_reply_to_status_id:
        return api.update_status(
            tweet_text, in_reply_to_status_id=in_reply_to_status_id
        )

    return api.update_status(tweet_text)


def _upload_media(api, image_files):
    media_ids = []
    for image_file in image_files:
        media_id = api.media_upload(image_file).media_id
        media_ids.append(media_id)
        log.info(
            'Uploaded status image %s to twitter as %s',
            image_file,
            media_id,
        )
    return media_ids


def _update_profile_description(api):
    date_with_timezone = timex.format_current_date_with_timezone()
    description = 'Automatically updated at {date_with_timezone}'.format(
        date_with_timezone=date_with_timezone
    )
    api.update_profile(description=description)
    log.info('Updated profile description to: %s', description)


class Twitter:
    """Implements Twitter wrapper."""

    def __init__(
        self,
        twtr_api_key,
        twtr_api_secret_key,
        twtr_access_token,
        twtr_access_token_secret,
    ):
        """Construct Twitter."""
        if twtr_api_key:
            auth = tweepy.OAuthHandler(twtr_api_key, twtr_api_secret_key)
            auth.set_access_token(twtr_access_token, twtr_access_token_secret)
            self.api = tweepy.API(auth)
            api_me = self.api.me()
            log.info(
                'Created Twitter for @%s (%s).',
                api_me.screen_name,
                api_me.id_str,
            )
        else:
            log.error('Missing twitter API Key etc. Cannot create Twitter.')
            self.api = None

    @staticmethod
    def from_args(description=''):
        """Construct Twitter from Args."""
        parser = argparse.ArgumentParser(description=description)
        for twtr_arg_name in [
            'twtr_api_key',
            'twtr_api_secret_key',
            'twtr_access_token',
            'twtr_access_token_secret',
        ]:
            parser.add_argument(
                '--' + twtr_arg_name,
                type=str,
                required=False,
                default=None,
            )
        args = parser.parse_args()
        return Twitter(
            args.twtr_api_key,
            args.twtr_api_secret_key,
            args.twtr_access_token,
            args.twtr_access_token_secret,
        )

    def tweet(
        self,
        tweet_text,
        status_image_files=None,
        update_user_profile=False,
        profile_image_file=None,
        banner_image_file=None,
        in_reply_to_status_id=None,
    ):
        """Tweet."""
        if status_image_files is None:
            status_image_files = []

        log.info('tweet_text: %s', tweet_text)
        log.info('status_image_files: %s', str(status_image_files))
        log.info('update_user_profile: %s', str(update_user_profile))
        log.info('profile_image_file: %s', str(profile_image_file))
        log.info('banner_image_file: %s', str(banner_image_file))

        tweet_text_for_length_list = []
        for tweet_text_line in tweet_text.split('\n'):
            if 'http' not in tweet_text_line:
                tweet_text_for_length_list.append(tweet_text_line)
        n_tweet_text = len('\n'.join(tweet_text_for_length_list))

        if n_tweet_text > MAX_LEN_TWEET:
            log.error(
                'Tweet text is too long (%d chars). Not tweeting.',
                n_tweet_text,
            )
            return None
        else:
            log.info('Tweet Length: %d', n_tweet_text)

        if len(status_image_files) > MAX_MEDIA_FILES:
            log.warning('Too many (%d) status image files. Truncating.')
            status_image_files = status_image_files[:MAX_MEDIA_FILES]

        if not self.api:
            log.error('Missing API. Cannot tweet')
            return None

        media_ids = _upload_media(self.api, status_image_files)
        update_status_result = _update_status(
            self.api, tweet_text, media_ids, in_reply_to_status_id
        )

        if update_user_profile:
            _update_profile_description(self.api)

        if profile_image_file:
            self.api.update_profile_image(profile_image_file)
            log.info('Update profile image to %s', profile_image_file)

        if banner_image_file:
            self.api.update_profile_banner(banner_image_file)
            log.info('Update profile banner image to %s', banner_image_file)

        return update_status_result

    def search(self, query_text):
        if not self.api:
            log.error('Missing API. Cannot search')
            return None

        @cache('utils.twitter', timex.SECONDS_IN.YEAR)
        def fallback(query_text=query_text):
            log.info('Inner call')
            results_list = self.api.search_users(query_text)
            if not results_list:
                return []
            return list(
                map(
                    lambda user: {
                        'id': user.id,
                        'screen_name': user.screen_name,
                        'name': user.name,
                    },
                    results_list,
                )
            )

        return fallback(query_text)
