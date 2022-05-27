from collections import defaultdict
from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
import yaml

import time

def read_action_yaml(filename, action_functions={}):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    actions_dict = {}

    for key, value in yaml_dict.items():
        actions_dict[key] = Action(value, action_functions=action_functions)

    return actions_dict


unsend_messages = defaultdict(set)

class Action():
    def __init__(self, actions, action_functions={}):
        self.actions = actions
        self.action_functions = action_functions

    def __call__(self, client, update: WhatsAppUpdate, context):
        for item in self.actions:
            if item["type"] == "return":
                return item["state"]

            wait_itteration = 0
            max_wait_itteration = 30
            while unsend_messages[update.From] and wait_itteration <= max_wait_itteration:
                print(unsend_messages, wait_itteration)
                time.sleep(.1)
                wait_itteration+=1

            if item["type"] == "message":
                message = client.messages.create(
                    body=item["text"].format(
                        **{"profileName": update.ProfileName, "echo": update.Body, **context}),
                    from_=update.To,
                    to=update.From
                )
                print("before add",unsend_messages)
                unsend_messages[update.From].add(message.sid)
                print("after add",unsend_messages)
                print(message.sid)
            elif item["type"] == "venue":
                message = client.messages.create(
                    body=item["title"],
                    persistent_action=['geo:{},{}|{}'.format(
                        item["latitude"], item["longitude"], item["address"])],
                    from_=update.To,
                    to=update.From
                )
                unsend_messages[update.From].add(message.sid)
            elif item["type"] == "photo":
                message = client.messages.create(
                    media_url=item["url"],
                    from_=update.To,
                    to=update.From
                )
                unsend_messages[update.From].add(message.sid)
            elif item["type"] == "video":
                message = client.messages.create(
                    media_url=item["url"],
                    from_=update.To,
                    to=update.From
                )
                unsend_messages[update.From].add(message.sid)
            elif item["type"] == "media_group":
                message = client.messages.create(
                    media_url=item["urls"],
                    from_=update.To,
                    to=update.From
                )
                unsend_messages[update.From].add(message.sid)
            elif item["type"] == "audio" or item["type"] == "voice":
                message = client.messages.create(
                    media_url=[item["url"]],
                    from_=update.To,
                    to=update.From
                )
                unsend_messages[update.From].add(message.sid)
            elif item["type"] == "poll":
                message = item["question"] + "\n"
                for option in item["options"]:
                    message += option + "\n"
                message = client.messages.create(
                    body=message,
                    from_=update.To,
                    to=update.From
                )
                unsend_messages[update.From].add(message.sid)

            elif item["type"] == "function":
                arguments = {i: item[i]
                             for i in item if i != 'type' and i != 'func'}
                self.action_functions[item["func"]](
                    client, update, context, **arguments)