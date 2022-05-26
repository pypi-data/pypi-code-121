from src.fb_downloader.fb_downloader import Video720Downloader
from src.model.video import Video


def main():
    video = Video('https://www.facebook.com/watch?v=211833304017649')
    video_downloader = Video720Downloader(video)
    video_downloader.download()


if __name__ == '__main__':
    main()
