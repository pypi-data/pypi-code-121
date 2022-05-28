import discord
from _distro import findDistroType

def main(install=False):
    distroType = findDistroType()
    if distroType == "unknown":
        print("\033[1m" + "ERROR" + ":\033[0m", "Distro not supported yet")
        exit()

    client = discord.Discord(distroType=distroType)

    installations = client.findInstallations()
    for installation, details in installations.items():
        if details["installed"]:
            updateStatus = client.update(installation, details["version"])
            print("\033[1m"+installation.upper()+":\033[0m", updateStatus)
        elif install:
            updateStatus = client.update(installation, -1)
            print("\033[1m"+installation.upper()+":\033[0m", updateStatus)
        else:
            print("\033[1m"+installation.upper()+":\033[0m", "Not installed")

if __name__ == "__main__":
    main()