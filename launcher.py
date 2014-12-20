# wpkgman launcher
# Does the option parsing then passes the options to pkgman.py
from pkgman import pkgman as pkgman
from pkgman import FileHelper as FileHelper
import argparse
import yaml
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
        return os.environ['HOME'] + '/dev/wpkgman/fakeroot/'
    FileHelper.GetEffectiveRoot = GetEffectiveRoot

parser = argparse.ArgumentParser(description='Wise Package Manager')


args = parser.parse_args()