import sys
import requests
from progressbar import Bar, FileTransferSpeed, Percentage, ProgressBar
# Taken from http://stackoverflow.com/questions/10525635/python-3-and-requests-with-a-progressbar
def get_file(file_url, name):
    r = requests.get(file_url)
    if not r.status_code == requests.codes.ok:
        print("Getting URL " + file_url + " failed ({code})".format(code=r.status_code), file=sys.stderr)
        return None
    size = int(r.headers['Content-Length'].strip())
    bytes = 0
    widgets = [name, ": ", Bar(marker="=", left="[", right=""),
        "] ", Percentage(), " ",  FileTransferSpeed(), " ",
        "- {0}B".format(str(round(size, 4))[:4])]
    pbar = ProgressBar(widgets=widgets, maxval=size, fd=sys.stdout).start()
    file = []
    for buf in r.iter_content(1024):
        if buf:
            file.append(buf)
            bytes += len(buf)
            pbar.update(bytes)
    pbar.finish()
    return b"".join(file)
