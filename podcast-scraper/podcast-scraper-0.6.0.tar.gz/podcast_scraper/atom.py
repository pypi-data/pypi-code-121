import logging

from feedgen.feed import FeedGenerator


class Atom:
    def __init__(self) -> None:
        self.atom = self.to_atom()
        super().__init__()

    def to_atom(self):
        fg = FeedGenerator()
        fg.id("id")
        fg.title("Monde Diplo")
        fg.subtitle("subtitle")
        fg.author({"name": "nicolas", "email": "nicolas@foo.fr"})
        fg.language("fr")

        return fg

    def get_size(self):
        return len(self.atom._FeedGenerator__feed_entries)

    def add_items(self, item):
        try:
            fe = self.atom.add_entry()
            fe.id(item.url)
            fe.link(href=item.url, rel="alternate")
            fe.title(item.title)
            fe.content(item.description, type="html")
            # fe.updated(get_date(item.date_start))
        except Exception as e:
            logging.error("Item %s failed", item.id)
            raise e

    def to_string(self):
        return self.atom.atom_str(pretty=True).decode()
