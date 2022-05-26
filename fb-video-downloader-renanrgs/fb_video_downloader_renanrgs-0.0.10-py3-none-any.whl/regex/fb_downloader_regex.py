import re


def get_video_links(video_data: str) -> dict[str, str]:
    pattern = re.compile(f'(FBQualityLabel=\\\\"\d+p){__get_url_pattern()}')
    video_links = pattern.findall(video_data)
    videos = {__quality_str(quality): __final_url(link) for quality, link in video_links}
    return videos


def get_audio_link(video_data: str) -> str:
    pattern = re.compile(f'audio_channel_configuration{__get_url_pattern()}')
    audio_link = pattern.search(video_data).groups()
    return __final_url(audio_link[0])


def get_video_data(source: str, fb_video_id) -> str:
    pattern = re.compile(f'"id":"{fb_video_id}".+?{fb_video_id}')
    video_data = pattern.search(source).group()
    return video_data


def get_video_id(url: str) -> str:
    pattern = re.compile('\d+')
    video_id = pattern.search(url).group()
    return video_id


def __get_url_pattern() -> str:
    return '.+?(https:\\\\/\\\\/video.+?oe=[A-Za-z0-9]+)'


def __final_url(url: str) -> str:
    return url.replace('amp;', '').replace('\\', '')


def __quality_str(video_quality: str) -> str:
    pattern = re.compile('\d+')
    return pattern.search(video_quality).group()
