def get_thread_callback_payload(vthread, post_updates: dict, len_posts_to_download: int):
    len_in_progress = len([k for k, v in post_updates.items() if v["status"] == "in_progress"])
    len_complete = len([k for k, v in post_updates.items() if v["status"] == "complete"])
    len_pending = len_posts_to_download - len(post_updates)

    return {
        "thread_id": vthread.id,
        "thread_title": vthread.title,
        "posts_all": len(vthread.posts),
        "posts_to_download": len_posts_to_download,
        "posts_pending": len_pending,
        "posts_in_progress": len_in_progress,
        "posts_complete": len_complete,
        "status": "complete" if len_posts_to_download == len_complete else "in_progress"
    }


class ThreadProgress:
    def __init__(self, callback, vthread, len_posts_to_download):
        self.callback = callback
        self.vthread = vthread
        self.post_updates = dict()
        self.len_posts_to_download = len_posts_to_download

    def report(self, post_update=None):
        if not self.callback:
            return

        if post_update:
            self.post_updates[post_update["post_id"]] = post_update
        payload = get_thread_callback_payload(self.vthread, self.post_updates, self.len_posts_to_download)
        self.callback(payload)
