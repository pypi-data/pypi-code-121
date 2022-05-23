import clipboard

def pasteboard_read():
    return clipboard.paste()


def pasteboard_write(output):
    clipboard.copy(output)
