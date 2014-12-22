import os, sys
# Main pkgman file
from . import FileHelper, YAMLParser, ProgressBar, DatabaseZipHelper
from .WPKGMANINFO import Color as Color
import requests
import textwrap
import platform
import tarfile
import yaml
import shutil
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
            sys.stderr.write(Color.red + 'Repo {r} is not working - trying next ({err})\n'.format(r=q, err=r.status_code) + Color.off)
    if not success:
        sys.stderr.write(Color.red + 'Could not find any repos.({num} failed)\n'.format(len(y.mirrors)) + Color.off)
    os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')

def check_package_exists(package: str) -> tuple:
    """
    Checks if a package exists in any of the repos.
    @param package: The package to check.
    @return: [0] if it exists, [1] the repo it's located in.
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
            print(Color.red + "Something went wrong. Re-run wpkgman with --sync to fix this." + Color.off, file=sys.stderr)
            return
        for x in repo.packages:
            if x == package:
                return True, repo.name, repo.packages[x]['version']
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
        return
    to_install = []
    print("Calculating dependencies...")
    for pkg in packages:
        pkg_exists = check_package_exists(pkg)
        if not pkg_exists[0]:
            print(Color.red + "Error: no package called {pkg} exists".format(pkg=pkg) + Color.off, file=sys.stderr)
            return
        to_install.append((pkg, pkg_exists[2], pkg_exists[1]))
        deps = get_dependencies(pkg, [])
        if deps is False:
            print("Not installing.")
            return
        to_install += deps
    for x in to_install:
        if DatabaseZipHelper.IsPackageVersionInstalled(package=x[0], version=x[1]):
            print(Color.yellow + "warning: package {f}-{v} is already installed".format(f=x[0], v=x[1]) + Color.off)
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
    print("Continue? [Y/n]", end=' ')
    if not input().lower() == 'y':
        return
    # Download package
    failedcounter = []
    files = []
    for pkg in to_install:
        # Construct a name
        continue_loop = False
        pkg_name = pkg[0] + '-' + pkg[1] + '-' + arch + '.tar.xz'

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

        tarball = tarfile.open(FileHelper.GetEffectiveRoot() + 'var/wpkgman/cache/' + pkg_name,
                                  mode='r:xz')

        # eh, fuck security!
        for name in tarball.getmembers():
            files.append(name.name)
        tarball.extractall(path=FileHelper.GetEffectiveRoot())

        # now construct a YAML file for the installed package
        d = {
            "package": pkg[0],
            "version": pkg[1],
            "repo": pkg[2],
            'files': files
        }
        # Write directly to /tmp instead of using filehelper

        DatabaseZipHelper.AddFileToZipfile(pkg[0] + '/' + pkg[0] +
                                           '-' + arch + '.yml', yaml.dump(d))
        # aaand we're done
    if len(failedcounter) > 0:
        print("{num} packages failed to install.".format(num=len(failedcounter)), file=sys.stderr)
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
        return
    pkg_exists = check_package_exists(package)
    if not pkg_exists[0]:
        print("Error: no package called {pkg} exists".format(pkg=package), file=sys.stderr)
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
            return False
        if dep in olddeps:
            continue
        dependencies.append((dep, pkg_exists[2], pkg_exists[1]))
        dependencies += get_dependencies(dep, olddeps=dependencies)
    return dependencies

def search_package(package: str):
    pass