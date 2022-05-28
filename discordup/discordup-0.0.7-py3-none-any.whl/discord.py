import shlex
import requests
from subprocess import Popen, PIPE
import os
import tempfile

linkDictionary = {
    "debian": {
        "stable":      "https://discord.com/api/download?platform=linux&format=deb",
        "ptb":         "https://discord.com/api/download/ptb?platform=linux&format=deb",
        "canary":      "https://discord.com/api/download/canary?platform=linux",
        "development": "https://discord.com/api/download/development?platform=linux",
    }
}

class Discord:
    def __init__(self, distroType="debian"):
        self.distroType = distroType
        if self.distroType not in linkDictionary:
            raise SystemExit('Cannot find distro in the dictionary')

    def update(self, type, version):
        if type not in linkDictionary[self.distroType]:
            raise SystemExit('Cannot find type in the link dictionary')
        resp = requests.get(linkDictionary[self.distroType][type])
        latestVersion = resp.url.split("/")[5]
        if latestVersion != version:
            completeName = os.path.join(tempfile.gettempdir(), resp.url.split("/")[-1])

            if os.path.exists(completeName):
                os.remove(completeName)

            with open(completeName, "wb") as f:
                f.write(resp.content)

            if self.distroType == "debian":
                command = shlex.split(f"sudo apt install '{completeName}'")
                process = Popen(command, stdout=PIPE, stderr=PIPE)
                process.communicate()

            os.remove(completeName)
            return "Has just been updated"
        return "Already up to date"

    def findInstallations(self):
        installations = {
            "stable":       {"installed": False, "version": -1, "needs_update": False},
            "ptb":          {"installed": False, "version": -1, "needs_update": False},
            "canary":       {"installed": False, "version": -1, "needs_update": False},
            "development":  {"installed": False, "version": -1, "needs_update": False}
        }

        if self.distroType == "debian":
            command = shlex.split('sudo apt list --installed')
            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            for line in stdout.decode().split("\n"):
                if "discord/now" in line:
                    installations["stable"]["installed"] = True
                    installations["stable"]["version"] = line.split(" ")[1]
                elif "discord-ptb/now" in line:
                    installations["ptb"]["installed"] = True
                    installations["ptb"]["version"] = line.split(" ")[1]
                elif "discord-canary/now" in line:
                    installations["canary"]["installed"] = True
                    installations["canary"]["version"] = line.split(" ")[1]
                elif "discord-development/now" in line:
                    installations["development"]["installed"] = True
                    installations["development"]["version"] = line.split(" ")[1]

        return installations