#!/usr/bin/env python3.4
# wpkgman launcher
# Does the option parsing then passes the options to pkgman.py
from pkgman import pkgman as pkgman
from pkgman import FileHelper as FileHelper
import argparse
import os

# Are we running on a test system?
test_sys = os.environ.get('WPKGMAN_TEST')
# Inject a function into the open/close helper lib to redirect packages to a test dir.
if test_sys:
    def GetEffectiveRoot():
        """
        Gets the effective root of the system.
        @return: The effective root of the system. /home/<user>/dev/wpkgman/fakeroot
        """
        if os.environ.get('WPKGMAN_ROOT'):
            return os.environ['WPKGMAN_ROOT']
        else:
            return os.environ['HOME'] + '/dev/wpkgman/fakeroot/'
    FileHelper.GetEffectiveRoot = GetEffectiveRoot

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

parser = argparse.ArgumentParser(description='Wise Package Manager')

pkgman.install_package(['dummypackage'])

#pkgman.sync_sources()