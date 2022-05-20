
import re
import os
import requests
import subprocess

def readActions(format_inhalt_list, messanger="Telegram", asset_url=""):
    actions = []
    for format, inhalt in format_inhalt_list:
        
        format_split = format.split(" - ")
        if len(format_split) == 2 and format_split[1] != messanger:
            continue
        elif len(format_split) == 2:
            format = format_split[0]

        action = {}

        if format == "Textnachricht":
            if messanger =="Telegram":
                inhalt = inhalt.replace(".", "\.")
                inhalt = inhalt.replace("(", "\(")
                inhalt = inhalt.replace(")", "\)")
                inhalt = inhalt.replace("!", "\!")
                inhalt = inhalt.replace("?", "\?")
                inhalt = inhalt.replace("-", "\-")
                inhalt = inhalt.replace("+", "\+")
                inhalt = inhalt.replace("#", "\#")

                action["parse_mode"] = "MarkdownV2"

            action["type"] = "message"
            action["text"] = inhalt

        elif format == "Audionachricht":
            action["type"] = "audio"
            regex = r"Datei: (?P<file>.*)\nAnzeigename: (?P<name>.*)\nPerformer: (?P<performer>.*)"

            match = re.search(regex, inhalt)
            if match:
                action["url"] = os.path.join(asset_url, match.group('file'))
                if requests.get(action["url"]).status_code != 200:
                    print("Die angegebenen Datei ({}) konnte nicht unter der Asset URL ({}) gefunden werden.".format(
                    match.group('file'), asset_url))
                action["title"] = match.group('name')
                action["performer"] = match.group('performer')
            else:
                action["url"] = os.path.join(asset_url, "platzhalter.mp3")
                action["title"] = inhalt
                action["performer"] = "🤖"

        elif format == "Sprachnachricht":
            action["type"] = "voice"
            regex = r"Datei: (?P<file>.*)"

            match = re.search(regex, inhalt)
            if match:
                mp3_filepath = os.path.join("assets/", match.group('file'))
                ogg_filename = match.group('file').replace(".mp3", ".ogg")
                ogg_filepath =  os.path.join("assets/", ogg_filename)
                subprocess.run(["ffmpeg", "-loglevel", "error", '-i', mp3_filepath, "-b:a", " 64k", "-ac", "1", '-acodec', 'libopus', '-y', "-hide_banner", ogg_filepath])

                if messanger=="Telegram":
                    action["file"] = ogg_filepath
                else:
                    action["url"] = os.path.join(asset_url, match.group('file'))
            else:
                action["url"] = os.path.join(asset_url, "platzhalter.mp3")
                action["caption"] = inhalt

        elif format == "Foto":
            action["type"] = "photo"            
            file_match = re.search(r"Datei: (?P<file>.*)", inhalt)

            if file_match:
                if messanger=="Telegram":
                    action["file"] = os.path.join("assets", file_match.group('file'))
                else:
                    action["url"] = os.path.join(asset_url, file_match.group('file'))
                    if requests.get(action["url"]).status_code != 200:
                        print("Die angegebene Datei ({}) konnte nicht unter der Asset URL ({}) gefunden werden.".format(
                        file_match.group('file'), asset_url))
            else:
                action["url"] = os.path.join(asset_url, "platzhalter.png")

            caption_match = re.search(r"Anzeigename: (?P<name>.*)", inhalt)
            if caption_match:
                action["caption"] = caption_match.group('name')

        elif format == "GIF":
            action["type"] = "document"
            regex = r"Datei: (?P<file>.*)\nAnzeigename: (?P<name>.*)"

            match = re.search(regex, inhalt)
            if match:
                action["url"] = os.path.join(asset_url, match.group('file'))
                if requests.get(action["url"]).status_code != 200:
                    print("Die angegebene Datei ({}) konnte nicht unter der Asset URL ({}) gefunden werden.".format(
                    match.group('file'), asset_url))
                action["caption"] = match.group('name')
            else:
                action["url"] = os.path.join(asset_url, "platzhalter.png")
                action["caption"] = inhalt

        elif format == "GPS":
            action["type"] = "venue"

            action["longitude"] = re.search(
                r"L: (?P<long>.*)", inhalt).group('long')
            action["latitude"] = re.search(r"B: (?P<lat>.*)", inhalt).group('lat')
            action["title"] = re.search(
                r"Anzeigename: (?P<name>.*)", inhalt).group('name')
            action["address"] = re.search(
                r"Adresse: (?P<address>.*)", inhalt).group('address')

        elif format == "Video":
            action["type"] = "video"
            regex = r"Datei: (?P<file>.*)\nAnzeigename: (?P<caption>.*)"

            match = re.search(regex, inhalt)
            if match:
                action["url"] = os.path.join(asset_url, match.group('file'))
                if requests.get(action["url"]).status_code != 200:
                    print("Die angegebene Datei ({}) konnte nicht unter der Asset URL ({}) gefunden werden.".format(
                    match.group('file'), asset_url))
                action["caption"] = match.group('caption')

        elif format == "Sticker":
            regex = r"ID: (?P<id>.*)$"

            match = re.search(regex, inhalt)
            action["type"] = "sticker"
            if match:
                action["id"] = match.group('id')
            else:
                print("Die angegebenen Informationen im Feld ({}) stimmen nicht mit dem angegebenen Format ({}) überein.".format(
                    inhalt, format))
        elif format == "Kontextspeicherung":
            action["type"] = "function"
            action["func"] = "save_text_to_context"
            action["key"] = "name"
        elif format == "Return":
            action["type"] = "return"
            action["state"] = inhalt
        elif format == "Formel":
            action["type"] = "function"
            action["func"] = re.search(
                r"function: (?P<function>.*)", inhalt).group('function')
            for line in inhalt.split("\n")[1:]:
                if len(line.split(": "))==2:
                    argument, value = line.split(": ")
                    action[argument] = value

        else:
            print("Das angegebene Format ({}) ist nicht bekannt".format(format))

        if action:
            actions.append(action)

    return actions
