class Embed:
    def __init__(self, title="", description="", colour=0xff0000):
        #https://discord.com/developers/docs/resources/channel#embed-object
        self.title = title
        self.description = description
        colour = str(colour)
        self.colour = int(colour, 0)
        self.result = self.create_dict()

    def set_author(self, name="", icon_url=""):
        self.result["author"] = {}
        self.result["author"]["name"] = name
        self.result["author"]["icon_url"] = icon_url

    def set_thumbnail(self, name="", icon_url=""):
        self.result["thumbnail"] = {}
        self.result["thumbnail"]["url"] = name

    def set_footer(self, text=""):
        self.result["footer"] = {}
        self.result["footer"]["text"] = text

    def add_field(self, name="", value="", inline=False):
        field = {
            "name": name,
            "value": value,
            "inline": inline
        }
        if self.result.get("fields") is None:
            self.result["fields"] = []
        self.result["fields"].append(field)

    def create_dict(self):
        result = {
            "title": self.title,
            "description": self.description,
            "color": self.colour,
        }
        return result

    def get_dict(self):
        return self.result
