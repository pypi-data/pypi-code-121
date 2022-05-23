"""
Generate all urls required for gogo series
"""
import logging
import time

import requests

SERIES_EPISODES_SAVE_FILE = './series_episodes.csv'


def generate_episode_name(name, episode):
    return '-'.join(name + [str(episode)])


class SeriesUrlGenerator:

    def __init__(self, url, delay=500):
        self.url = url
        self.delay = delay

    def find_episode_urls(self, series_name):
        series_name = series_name.replace(':', '')
        name = series_name.lower().split(' ')
        name.append('episode')
        max_episode = self.find_max_episode(name)
        # need to find max episode
        episodes = []
        for ep in range(1, max_episode + 1):
            episodes.append(self.url + '/' + generate_episode_name(name, ep))
        logging.info("total of {0} episodes", str(len(episodes)))
        return episodes

    def find_max_episode(self, name: list[str]) -> int:

        potential_max_episode = 1
        next_potential_max_episode = 12
        while True:
            if self.does_episode_exist(generate_episode_name(name, next_potential_max_episode)):
                # next max is greater than next potential max episode
                potential_max_episode = next_potential_max_episode
                next_potential_max_episode *= 2
            else:
                # in-between potential and next_potential
                left = potential_max_episode
                right = next_potential_max_episode
                while left + 1 < right:
                    mid = (left + right) // 2
                    if self.does_episode_exist(generate_episode_name(name, mid)):
                        left = mid
                    else:
                        right = mid - 1
                    time.sleep(self.delay / 1000)
                return left
            time.sleep(self.delay / 1000)

    def does_episode_exist(self, episode_name: str) -> bool:
        try:
            episode_url = self.url + '/' + episode_name
            resp = requests.get(episode_url)
            status = resp.content
            return status != b'404\n'
        except Exception as e:
            logging.error("error checking episode {0} error {1}".format(episode_name, e))
        return False

