from facebook_video_downloader.model.video import Video
from facebook_video_downloader.video_downloader.video_downloader import \
    VideoDownloader


def main():
    
    print('===================================')
    video_url = input('Cole a URL do video: ')
    print('===================================')
    video = Video(video_url)

    print('===================================')
    print('Avaialble Resolutions')
    print('===================================')
    print(*video.resolutions_links.keys(), sep='p - ', end='p\n')

    resolution = input('Choose one resolution: ')
    file = VideoDownloader(video, resolution).download()

    with open('my_video.mp4', 'bw') as video_file:
        video_file.write(file)

if __name__ == '__main__':
    main()
