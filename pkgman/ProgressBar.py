import sys

import requests
from progressbar import Bar, FileTransferSpeed, Percentage, ProgressBar
from .WPKGMANINFO import Color as Color

# Taken from http://stackoverflow.com/questions/10525635/python-3-and-requests-with-a-progressbar
def get_file(file_url, name):
    r = requests.get(file_url, stream=True)
    if not r.status_code == requests.codes.ok:
        print(Color.red + "Getting URL " + file_url + " failed ({code})".format(code=r.status_code) + Color.off, file=sys.stderr)
        return None
    size = int(r.headers['Content-Length'].strip())
    bytes = 0
    widgets = [name, ": ", Bar(marker="=", left="[", right="] "),
        Percentage(), " ",  FileTransferSpeed(), " ",
        str(round(bytes / 1024, 2)), "KB",
        " of {0}{1}".format(get_appropriate_rounded_size(size), get_appropriate_rounded_unit(size))]
    pbar = ProgressBar(widgets=widgets, maxval=size, fd=sys.stdout).start()
    file = []
    for buf in r.iter_content(1024):
        if buf:
            file.append(buf)
            bytes += len(buf)
            pbar.widgets[7] = get_appropriate_rounded_size(bytes)
            pbar.widgets[8] = get_appropriate_rounded_unit(bytes)
            pbar.update(bytes)
    pbar.finish()
    return b"".join(file)


def get_appropriate_rounded_size(bytes):
    if 1024 < bytes < 1048576:
        return str(round(bytes / 1024))
    elif 1048576 < bytes < 1073741824:
        return str(round(bytes / 1024 / 1024))
    elif bytes > 1073741824:
        return str(round(bytes / 1024 / 1024 / 1024))
    else:
        return str(round(bytes, 2))


def get_appropriate_rounded_unit(bytes):
    if 1024 < bytes < 1048576:
        return 'KB'
    elif 1048576 < bytes < 1073741824:
        return 'MB'
    elif bytes > 1073741824:
        return 'GB'
    else:
        return 'B'