def findDistroType():
    systemType = "unknown"
    try:
        open("/etc/debian_version").read()
        systemType = "debian"
    except Exception:
        pass

    return systemType