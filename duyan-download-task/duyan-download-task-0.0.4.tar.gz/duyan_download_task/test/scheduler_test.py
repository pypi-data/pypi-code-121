from duyan_download_task import DownloadTaskScheduler


def test_scheduler():
    scheduler = DownloadTaskScheduler('config.ini', 'download_task_scheduler')
    scheduler.start()


if __name__ == '__main__':
    test_scheduler()
