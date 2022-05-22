class PostProgress:
    def __init__(self, vpost, len_images_to_download, is_postprocessing_enabled, callback):
        self.image_updates = dict()
        self.vpost = vpost
        self.len_images_to_download = len_images_to_download
        self.callback = callback
        self.is_postprocessing_enabled = is_postprocessing_enabled

    def report(self, image_update=None):
        if not self.callback:
            return

        if image_update:
            self.image_updates[image_update["filename"]] = image_update

        self.callback(self._get_payload())

    def _get_payload(self):
        complete_status = "complete" if self.is_postprocessing_enabled else "downloaded"
        len_images = len(self.vpost.images)
        len_complete = len([v for v in self.image_updates.values() if v["status"] == complete_status])
        len_failed = len([v for v in self.image_updates.values() if v["status"] == "failed"])
        len_pending = self.len_images_to_download - len(self.image_updates)

        return {
            "post_id": self.vpost.id,
            "post_title": self.vpost.title,
            "images_all": len_images,
            "images_to_download": self.len_images_to_download,
            "images_pending": len_pending,
            "images_complete": len_complete,
            "images_failed": len_failed,
            "status": "complete" if self.len_images_to_download == len_complete else "in_progress"
        }
