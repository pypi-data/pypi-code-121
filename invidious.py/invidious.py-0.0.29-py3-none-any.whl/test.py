from invidious import *

searched = search("distrotube")

channels = []

for item in searched:
    if type(item) == ChannelItem:
        channel = get_channel(item.authorId)
        channels.append(channel)

for channel in channels:
    print(channel.author)