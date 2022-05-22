from uuid import uuid4

from vripper.model.vpost import VPost


class VThread:
    def __init__(self, id=None, title=None, url=None, with_empty_post=False):
        self.id = id or str(uuid4())
        self.title = title
        self.url = url
        self.posts = []

        if with_empty_post:
            self.posts.append(VPost())
