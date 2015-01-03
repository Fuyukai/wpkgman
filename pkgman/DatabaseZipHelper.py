import sys

import io
from . import FileHelper
from .WPKGMANINFO import Color as Color
import yaml
import warnings
import shutil
import os
warnings.filterwarnings("ignore")

def GetDatabaseFile(mode: str='rt') -> io.TextIOWrapper:
    """
    Gets the file object of the database file.
    @return: The file object representing the database file.
    """
    file = FileHelper.OpenFileRaw("var/wpkgman/installed.db", 'rb')
    if file is None:
        # Silently create a new dbfile
        file = open(FileHelper.GetEffectiveRoot() + "var/wpkgman/installed.db", mode='w')
        file.write("""# Sample install database""")
        file.close()
    file = FileHelper.OpenFileRaw("var/wpkgman/installed.db", mode=mode)
    return file

def GetDatabaseContent() -> dict:
    fobj = GetDatabaseFile('rt')
    yaml_content = {}
    try:
        yaml_content = yaml.safe_load(fobj)
    except:
        print(Color.yellow + "WARNING: INSTALLED PACKAGE IS CORRUPTED. RESTORE FROM INSTALLED.DB.BAK." + Color.off)
        os.remove(FileHelper.GetEffectiveRoot() + 'var/wpkgman/lock')
        sys.exit(1)
    finally:
        fobj.close()
    if yaml_content is None:
        return {'packages': {}}
    return yaml_content

def WriteToDatabaseFile(content: dict):
    # Safety first!
    shutil.copy2(FileHelper.GetFullFilePath('var/wpkgman/installed.db'),
                 FileHelper.GetFullFilePath('var/wpkgman/installed.db.bak'))
    content_old = GetDatabaseContent()
    # get an empty database file
    fobj = GetDatabaseFile(mode='wt')
    new_content = dict(list(content_old.items()) + list(content.items()))
    yaml.safe_dump(new_content, fobj)
    fobj.close()

def IsPackageInstalled(package: str, arch: str="") -> bool:
    """
    Checks if a package is installed in the database.
    @param package: The package to check.
    @param arch: Deprecated. Not used any more.
    @return: If the package is installed or not.
    """
    content = GetDatabaseContent()
    if 'packages' not in content:
        WriteToDatabaseFile({'packages': {}})
        return False
    pkgs = content['packages']
    if package not in pkgs:
        return False
    else:
        return True

def CanReinstallPackage(package: str) -> bool:
    """
    Check if the package can be reinstalled.
    @param package: The package to check.
    @return: If it can be reinstalled or not.
    """
    content = GetDatabaseContent()
    pkgs = content['packages']
    if package not in pkgs:
        return True
    else:
        return not pkgs[package]['noreinstall']

def IsPackageVersionInstalled(package: str, version: str, arch: str="") -> bool:
    """
    Checks if a package with the specified version is installed.
    @param package: The package.
    @param version: The version of package to check.
    @param arch: Deprecated, not used any more.
    @return: If the package with the specified version is installed.
    """
    # First, cut out a bit of extra processing
    if not IsPackageInstalled(package=package):
        return False

    content = GetDatabaseContent()
    pkgs = content['packages']
    pkg = pkgs[package]
    if not 'version' in pkg:
        return False
    else:
        if pkg['version'] == version:
            return True
        else:
            return False

def DoesPackageOwnFile(package: str, file: str, arch: str='x86_64') -> bool:
    """
    Checks if a package owns the specified file.
    @param package: The package.
    @param file: The FULL path to the file, without the root (/)
    @param arch: The architecture.
    @return: If the package owns the file.
    """
    pass

def AddPackageToDatabase(pkg: str, content: dict) -> None:
    """
    Adds package to database.
    @param pkg:
    @param content:
    @return:
    """
    dbc = GetDatabaseContent()
    dbc['packages'][pkg] = content
    WriteToDatabaseFile(dbc)


def RemovePackageFromDatabase(pkg: str) -> bool:
    dbc = GetDatabaseContent()
    try:
        dbc['packages'].pop(pkg)
    except KeyError:
        return False
    else:
        WriteToDatabaseFile(dbc)
        return True


def GetPackageFiles(pkg: str) -> list:
    """
    Gets the files that the package owns.
    @param pkg: The package to check.
    @return: Returns a list of files, or an empty list if the package is not installed/owns no files.
    """
    if not IsPackageInstalled(pkg):
        return []
    content = GetDatabaseContent()
    pkg_files = content['packages'][pkg]['files']
    return pkg_files


def IsFileUniqueToPackage(package: str, file: str) -> bool:
    """

    @param package: The package to check.
    @param file: The file to check.
    @return: If the file is unique to the pkg.
    """

    content = GetDatabaseContent()
    for pkg in content['packages']:
        if pkg == package:
            continue
        f = content['packages'][pkg]
        if file in f['files']:
            return False
    return True