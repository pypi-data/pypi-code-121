import argparse
from ._discord import Discord
from ._distro import findDistroType

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--install", required=False, help="Use this parameter to install all Discord clients.")
    args = vars(ap.parse_args())
    if args["install"] not in ["stable", "ptb", "canary", "development", "all", None]:
        print(
            f"{args['install']} is not a valid version, please use one of the following: \"stable\", \"ptb\", \"canary\", \"development\" or \"all\"")
        exit()
   #################### GØR SÅ MAN KAN BRUGE ARG PARSE TIL AT INSTALLERE
    distroType = findDistroType()
    if distroType == "unknown":
        print("\033[1m" + "ERROR" + ":\033[0m", "Distro not supported yet")
        exit()

    client = Discord(distroType=distroType)

    installations = client.findInstallations()
    if args["install"] == "all":
        for installation in installations:
            installations[installation]["installed"] = True
            installations[installation]["version"] = "-1"
    elif args["install"] != None:
        installations[args["install"]]["installed"] = True
        installations[args["install"]]["version"] = "-1"

    print(installations)
    for installation, details in installations.items():
        if details["installed"]:
            updateStatus = client.update(installation, details["version"])
            print("\033[1m"+installation.upper()+":\033[0m", updateStatus)
        else:
            print("\033[1m"+installation.upper()+":\033[0m", "Not installed")

if __name__ == "__main__":
    main()