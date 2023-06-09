#!/usr/bin/env python3.4
# wpkgman launcher
# Does the option parsing then passes the options to pkgman.py
import argparse
import sys

from pkgman import pkgman as pkgman
from pkgman import FileHelper as FileHelper
from pkgman.WPKGMANINFO import Color as Color
import os


# Are we running on a test system?
test_sys = os.environ.get('WPKGMAN_TEST')

# Create starter directories
if not os.path.exists(FileHelper.GetEffectiveRoot() + 'var'):
    os.makedirs(FileHelper.GetEffectiveRoot() + 'var')

if not os.path.exists(FileHelper.GetEffectiveRoot() + 'etc'):
    os.makedirs(FileHelper.GetEffectiveRoot() + 'etc')

if not os.path.exists(FileHelper.GetEffectiveRoot() + 'var/wpkgman'):
    os.makedirs(FileHelper.GetEffectiveRoot() + 'var/wpkgman')

if not os.path.exists(FileHelper.GetEffectiveRoot() + 'var/wpkgman/repos'):
    os.makedirs(FileHelper.GetEffectiveRoot() + 'var/wpkgman/repos')

if not os.path.exists(FileHelper.GetEffectiveRoot() + 'var/wpkgman/cache'):
    os.makedirs(FileHelper.GetEffectiveRoot() + 'var/wpkgman/cache')

parser = argparse.ArgumentParser(description='Wise Package Manager', prog="wpkgman")
parser.add_argument("-I", "--install", nargs="+", help="Install package(s)", metavar="PKG")
parser.add_argument("-S", "--sync", action="store_true", default=False,
                    help="Sync repository databases")
parser.add_argument("-s", "--search", nargs=1, help="Search for packages", metavar="PKG")
parser.add_argument("-R", "--remove", nargs="+", help="Remove package(s)", metavar="PKG")
parser.add_argument("--force", action="store_true", default=False, help="Force action (NOT RECOMMENDED)")
args = parser.parse_args()
hasarg = False


def check_uid():
    if os.getuid() != 0 and not os.environ.get('WPKGMAN_TEST'):
        print(Color.red + "Error: wpkgman must be run as root" + Color.off, file=sys.stderr)
        sys.exit(1)

if args.sync:
    check_uid()
    pkgman.sync_sources()
    hasarg = True
if args.search:
    pkgman.search_package(args.search[0])
    hasarg = True
elif args.install:
    check_uid()
    pkgman.install_packages(args.install)
    hasarg = True
elif args.remove:
    check_uid()
    pkgman.remove_packages(args.remove, args.force)
    hasarg = True

if not hasarg:
    print(Color.red + "Error: no argument specified" + Color.off, file=sys.stderr)


#pkgman.sync_sources()