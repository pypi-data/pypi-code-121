from facebook_video_downloader.model.video import Video
from facebook_video_downloader.video_downloader.video_downloader import \
    VideoDownloader


def main():
    # Private video https://www.facebook.com/watch?v=707123573841390
    video = Video('https://www.facebook.com/watch?v=1016513142327343')
    print(video.video_links.keys())
    video_downloader = VideoDownloader(video)
    file = video_downloader.download()
    print(file)


if __name__ == '__main__':
    main()
