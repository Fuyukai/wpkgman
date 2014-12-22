import sys

import os
# Main pkgman file
from . import FileHelper, YAMLParser, ProgressBar, DatabaseZipHelper
from .WPKGMANINFO import Color as Color
import requests
import textwrap
import platform
import tarfile

arch = platform.uname()[4]


def sync_sources():
    """
    Syncs the repo sources.
    """
    if os.path.exists(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock'):
        print(Color.red + "Error: Lock file exists. Perhaps wpkgman is open elsewhere?" + Color.off, file=sys.stderr)
        return
    FileHelper.OpenFileForWritingText('var/wpkgman/lock').close()
    print("Syncing sources....")
    y = YAMLParser.Config()
    if not hasattr(y, 'mirrors'):
        print(Color.red + "Something went wrong. "
                          "Your config file has probably been just created - try this command again." + Color.off,
              file=sys.stderr)
        os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
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
            sys.stderr.write(Color.red + 'Repo {r} is not working - trying next ({err})\n'.format(r=q,
                                                                                                  err=r.status_code) + Color.off)
    if not success:
        sys.stderr.write(Color.red + 'Could not find any repos.({num} failed)\n'.format(len(y.mirrors)) + Color.off)
    os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')


def check_package_exists(package: str) -> tuple:
    """
    Checks if a package exists in any of the repos.
    @param package: The package to check.
    @return: [0] if it exists, [1] the repo it's located in, [2] the package version
    """
    y = YAMLParser.Config()
    repos_temp = []
    for orepo in y.repos:
        repo = y.repos[orepo]
        repos_temp.append((repo['loc'], repo['priority'], orepo))
    repos_temp.sort(key=lambda tup: tup[1], reverse=True)
    for x in repos_temp:
        repo = YAMLParser.Repo(x[0], x[2])
        if not hasattr(repo, 'packages'):
            print(Color.red + "Something went wrong. Re-run wpkgman with --sync to fix this." + Color.off,
                  file=sys.stderr)
            os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
            return
        for x in repo.packages:
            if x == package:
                return True, repo.name, repo.packages[x]['version']
        else:
            # uh
            continue
    else:
        return False, None, None


def install_packages(packages: list):
    if os.path.exists(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock'):
        print(Color.red + "Error: Lock file exists. Perhaps wpkgman is open elsewhere?" + Color.off)
        return
    FileHelper.OpenFileForWritingText('var/wpkgman/lock').close()
    y = YAMLParser.Config()
    repos_temp = []
    for orepo in y.repos:
        repo = y.repos[orepo]
        repos_temp.append((repo['loc'], repo['priority'], orepo))
    repos_temp.sort(key=lambda tup: tup[1], reverse=True)
    if not hasattr(y, 'repos'):
        print(Color.red + "Something went wrong. Re-run wpkgman with --sync to fix this." + Color.off, file=sys.stderr)
        os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
        return
    to_install = []
    print("Calculating dependencies...")
    for pkg in packages:
        pkg_exists = check_package_exists(pkg)
        if not pkg_exists[0]:
            print(Color.red + "Error: no package called {pkg} exists".format(pkg=pkg) + Color.off, file=sys.stderr)
            os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
            return
        to_install.append((pkg, pkg_exists[2], pkg_exists[1]))
        deps = get_dependencies(pkg, [])
        if deps is False:
            print("Not installing.")
            return
        to_install += deps
    for x in to_install:
        if DatabaseZipHelper.IsPackageVersionInstalled(package=x[0], version=x[1], arch=arch):
            print(Color.yellow + "warning: package {f}-{v} is already installed".format(f=x[0], v=x[1]) + Color.off)
    columns = 0  # to make pycharm shut up
    if not os.environ.get('WPKGMAN_NO_STTY'):
        rows, columns = os.popen('stty size', 'r').read().split()
    # TODO: Add size total to this
    print("Packages to install ({n}):".format(n=len(to_install)))
    str_to_write = ""
    for x in to_install:
        str_to_write += x[0] + "-" + x[1] + " "
    if os.environ.get('WPKGMAN_NO_STTY'):
        print(str_to_write)
    else:
        print(textwrap.fill(str_to_write, int(columns)))
    print(Color.white + "Continue? [Y/n]" + Color.off, end=' ')
    if not input().lower() == 'y':
        os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
        return
    # Download package
    failedcounter = []
    files = []
    for pkg in to_install:
        # Construct a name
        # pkg_name = pkg[0] + '-' + pkg[1] + '-' + arch + '.tar.xz'
        repo = YAMLParser.Repo('var/wpkgman/repos/' + pkg[2] + '.yml', pkg[2])
        pkg_name = repo.packages[pkg[0]]['name'] + '-' + arch + '.tar.xz'

        tempf = b""
        for mirror in y.mirrors:
            tempf = ProgressBar.get_file(mirror + pkg[2] + '/' + pkg[0] + '/' + pkg_name, name=pkg_name)
            if tempf is not None:
                break
        else:
            failedcounter.append(pkg)
            continue
        cache_file = FileHelper.OpenFileForWritingBytes('var/wpkgman/cache/' + pkg_name)
        cache_file.write(tempf)
        cache_file.close()

    # TODO: Add verification
    for num, pkg in enumerate(to_install):
        repo = YAMLParser.Repo('var/wpkgman/repos/' + pkg[2] + '.yml', pkg[2])
        pkg_name = repo.packages[pkg[0]]['name'] + '-' + arch + '.tar.xz'
        try:
            tarball = tarfile.open(FileHelper.GetEffectiveRoot() + 'var/wpkgman/cache/' + pkg_name,
                                   mode='r:xz')
        except FileNotFoundError:
            print("Installing package {pkg} ({n}/{mn})...".format(
                pkg=pkg[0], n=num + 1, mn=len(to_install))
                + Color.red + " failed" + Color.off, file=sys.stderr)
            continue
        print("Installing package {pkg} ({n}/{mn})...".format(pkg=pkg[0], n=num + 1, mn=len(to_install)), end=' ')
        # eh, fuck security!
        for name in tarball.getmembers():
            files.append(name.name)
        try:
            tarball.extractall(path=FileHelper.GetEffectiveRoot())
        except:
            print(Color.red + "Error: cannot extract tarball, file exists in filesystem" + Color.off)
            continue
        # now construct a dict for the installed file
        d = {
            "package": pkg[0],
            "version": pkg[1],
            "repo": pkg[2],
            "arch": arch,
            'files': files
        }

        DatabaseZipHelper.AddPackageToDatabase(pkg[0], d)
        # aaand we're done
        print(Color.green + "done" + Color.off)
    if len(failedcounter) > 0:
        print(Color.red + "{num} packages failed to install.".format(num=len(failedcounter)) + Color.off,
              file=sys.stderr)
    os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')


def get_dependencies(package: str, olddeps: list) -> list:
    y = YAMLParser.Config()
    repos_temp = []
    for orepo in y.repos:
        repo = y.repos[orepo]
        repos_temp.append((repo['loc'], repo['priority'], orepo))
    repos_temp.sort(key=lambda tup: tup[1], reverse=True)
    if not hasattr(y, 'repos'):
        print("Something went wrong. Re-run wpkgman with --sync to fix this.", file=sys.stderr)
        os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
        return
    pkg_exists = check_package_exists(package)
    if not pkg_exists[0]:
        print("Error: no package called {pkg} exists".format(pkg=package), file=sys.stderr)
        os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
        return False
    repo_get_deps = ""
    for repo in repos_temp:
        if repo[2] == pkg_exists[1]:
            repo_get_deps = repo[2]
            break
    else:
        # Huh?
        raise SystemError
    repo = YAMLParser.Repo('var/wpkgman/repos/' + repo_get_deps + '.yml', pkg_exists[1])
    pkg = repo.packages[package]
    dependencies = []
    if not 'dependencies' in pkg:
        return dependencies
    for dep in pkg['dependencies']:
        pkg_exists = check_package_exists(dep)
        if not pkg_exists[0]:
            print("Error: no package called {pkg} exists".format(pkg=dep), file=sys.stderr)
            os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
            return False
        if dep in olddeps:
            continue
        if not DatabaseZipHelper.IsPackageInstalled(dep, arch=arch):
            dependencies.append((dep, pkg_exists[2], pkg_exists[1]))
        dependencies += get_dependencies(dep, olddeps=dependencies)
    return dependencies


def search_package(package: str):
    # If I knew regexps, I would do it here.
    # But I don't.
    # First, get all repos from the config file
    y = YAMLParser.Config()
    repos = []
    for r in y.repos:
        repo = YAMLParser.Repo(y.repos[r]['loc'], r)
        repos.append(repo)
    for repo in repos:
        if not hasattr(repo, 'packages'):
            # Oops!
            continue
        for pkg in repo.packages:
            if package in pkg:
                print(repo.name + "/" + pkg + '-' + repo.packages[pkg]['version'] + ':')
                if 'description' in repo.packages[pkg]:
                    print("\t" + repo.packages[pkg]['description'])
