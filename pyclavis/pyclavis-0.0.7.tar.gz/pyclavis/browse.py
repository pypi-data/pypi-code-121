import webbrowser

_browsers_types = [
    "mozilla",
    "firefox",
    "galeon",
    "epiphany",
    "skipstone",
    "kfmclient",
    "konqueror",
    "kfm",
    "mosaic",
    "opera",
    "grail",
    "links",
    "elinks",
    "lynx",
    "w3m",
    "windows-default",
    "macosx",
    "safari",
    "google-chrome",
    "chrome",
    "chromium",
    "chromium-browser",
]


def get_supported_browsers():
    _browsers = []
    for bt in _browsers_types:
        try:
            _ = webbrowser.get(bt)
            _browsers.append(bt)
        except:
            pass
    return _browsers
