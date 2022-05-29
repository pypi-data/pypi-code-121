"""Get Firefox Profile."""

from selenium import webdriver

MIME_TYPES_NEVER_ASK = [
    'application/octet-stream',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
]


def _get():
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('browser.download.folderList', 2)
    firefox_profile.set_preference(
        'browser.download.manager.showWhenStarting',
        False,
    )
    firefox_profile.set_preference(
        'browser.download.manager.showAlertOnComplete',
        False,
    )

    firefox_profile.set_preference(
        'browser.download.panel.shown',
        False,
    )
    firefox_profile.set_preference('browser.download.dir', '/tmp/')

    mime_types = ','.join(MIME_TYPES_NEVER_ASK)
    firefox_profile.set_preference(
        'browser.helperApps.neverAsk.saveToDisk',
        mime_types,
    )
    firefox_profile.set_preference(
        'browser.helperApps.neverAsk.openFile',
        mime_types,
    )
    firefox_profile.set_preference(
        'browser.download.manager.closeWhenDone',
        True,
    )
    firefox_profile.set_preference(
        'browser.helperApps.alwaysAsk.force',
        False,
    )
    return firefox_profile
