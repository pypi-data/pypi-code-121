from .io.file import read_lines

def gethostname():
    return read_lines('/etc/hostname', strip=True)[0]

