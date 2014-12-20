import os, sys
# Main pkgman file
from . import FileHelper, YAMLParser, ProgressBar
import requests
import yaml

def sync_sources():
    print("Syncing sources....")
    y = YAMLParser.Config()
    if not hasattr(y, 'mirrors'):
        print("Something went wrong. Your config file has probably been just created - try this command again.")
        return
    success = False
    for q in y.mirrors:
        r = requests.get(q)
        if r.status_code == requests.codes.ok:
            for x in y.repos:
                full_url = q
                full_url += x + '/' + 'repo.yml'

                dl_file = ProgressBar.get_file(full_url, x)
                if dl_file:
                    file_to_write = FileHelper.OpenFileForWritingText(y.repos[x]['loc'])
                    file_to_write.write(dl_file.decode())
                    file_to_write.close()
            success = True
            break
        else:
            sys.stderr.write('Repo {r} is not working - trying next ({err})\n'.format(r=q, err=r.status_code))
    if not success:
        sys.stderr.write('Could not find any repos.({num} failed)\n'.format(len(y.mirrors)))