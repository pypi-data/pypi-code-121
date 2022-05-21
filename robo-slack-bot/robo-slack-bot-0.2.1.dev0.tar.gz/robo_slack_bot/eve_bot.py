#!/bin/env python

import slack
import json
import logging
import argparse
import requests
from cmath import log
from crypt import methods
from flask import Flask, request, Response
from pathlib import Path
from lxml.html import open_http_urllib
from slackeventsapi import SlackEventAdapter


BOT_USER_OAUTH_TOKEN = "xoxb-964897116659-2042766866597-sU50iievgJmk1ymHAv2ZuCfj"
SIGNING_SECRET = "a788e3ee35ad3c3db7718b8e7a33e318"


app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, "/slack/events", app)


@slack_event_adapter.on("message")
def message(payload):
    client = slack.WebClient(token=BOT_USER_OAUTH_TOKEN)
    slack_message_icons = ":parrot: :mega:"

    event = payload.get("event", {})
    logging.debug("Event: " + str(event))
    channel_id = event.get("channel")
    logging.debug("Channel ID: " + str(channel_id))
    user_id = event.get("user")
    logging.debug("User ID: " + str(user_id))
    text = event.get("text")
    logging.debug("Text: " + str(text))
    BOT_ID = event.get("bot_id")
    logging.debug("Bot ID: " + str(BOT_ID))

    if BOT_ID == None:
        # if BOT_ID != user_id:
        slack_message = slack_message_icons + ": " + text

        client.chat_postMessage(
            channel=channel_id,
            blocks=json.loads(
                """
            [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text":" """
                + slack_message
                + """ ",
                        "emoji": true
                    }
                }
            ]
        """
            ),
        )
    else:
        logging.debug("Ignoring message from self")


@app.route("/test", methods=["POST"])
def test():
    try:
        data = request.form
        logging.debug("Data: " + str(data))
        user_id = data.get("user_name")
        logging.debug("User ID: " + str(user_id))
        channel_id = data.get("channel_name")
        logging.debug("Channel ID: " + str(channel_id))
        text = data.get("text")
        # if text contain an _ as a first character, or last character, then remove it
        if text[0] == "_" or text[-1] == "_":
            text = text[1:-1]
        logging.debug("Text: " + str(text))

        url = arg_parser().recipe_scaper_api
        logging.debug("URL: " + url)

        payload = json.dumps({"url": text})
        logging.debug("data: " + payload)
        headers = {"Content-Type": "application/json"}
        logging.debug("headers: " + str(headers))
        response = requests.request("POST", url, headers=headers, data=payload)
        logging.debug("Response: " + str(response.text))
        message = json.loads(response.text)
        logging.debug(message.keys())
        # Validate the http response and return the recipe or a message
        if "code" in message.keys():
            if message["code"] == "200":
                if "recipe" in message.keys():
                    if message["recipe"] !=  None:
                        client = slack.WebClient(token=BOT_USER_OAUTH_TOKEN)
                        client.chat_postMessage(
                            channel=channel_id,
                            text="Hi "
                            + user_id
                            + ", Adding recipe:\n `"
                            + message["recipe"]["recipe_title"]
                            + "` \n The given ingredients are:\n ```"
                            + message["recipe"]["recipe_ingredients"]
                            + "```",
                        )
                    elif message["recipe"] == None:
                        client = slack.WebClient(token=BOT_USER_OAUTH_TOKEN)
                        client.chat_postMessage(
                            channel=channel_id,
                            text="Hi "
                            + user_id
                            + ", I could not find a recipe for the given url: `"
                            + text
                            + "`",
                        )
                return Response(status=200)
            if message["code"] == "400":
                client = slack.WebClient(token=BOT_USER_OAUTH_TOKEN)
                client.chat_postMessage(
                    channel=channel_id,
                    text="Hi "
                    + user_id
                    + ",\n I couldn't find any recipe for the given url: *"
                    + text
                    + "*",
                )
                return Response(status=200)
    except Exception as e:
        logging.error("Error: " + str(e))
        return Response(status=500)


def check_debug(args):
    """Check if debuging is set from the command line

    Args:
        args (dict): arguments from the command line

    Returns:
        object: Looging type object
    """

    if args.debug:
        return logging.DEBUG
    else:
        return logging.INFO


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    parser.add_argument("--ip", default="0.0.0.0", help="ip address to bind to")
    parser.add_argument("--port", default=5000, help="port to listen on")
    parser.add_argument(
        "--recipe-scaper-api",
        default="http://localhost:5000/",
        help="url to the recipe scraper api",
    )
    return parser.parse_args()


def main():
    args = arg_parser()
    log_format = "%(asctime)s - %(levelname)5s - %(filename)20s:%(lineno)5s - %(funcName)20s()  - %(message)s"
    logging.basicConfig(level=check_debug(args), format=log_format)
    logging.debug("Arguments: " + str(args))
    app.run(debug=args.debug, host=args.ip, port=args.port)


if __name__ == "__main__":
    main()


# /test https://www.bbcgoodfood.com/recipes/tuna-sundried-tomato-pasta-bake
