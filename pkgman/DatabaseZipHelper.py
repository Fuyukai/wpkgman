import zipfile
import io
from . import FileHelper, YAMLParser

import warnings
warnings.filterwarnings("ignore")

def GetDatabaseFile(mode: str='r') -> zipfile.ZipFile:
    """
    Gets the file object of the database tarball.
    @return: The file object representing the database file.
    """
    zip = FileHelper.OpenFileRaw("var/wpkgman/installed.db", 'rb')
    if zip is None:
        # Silently create a new zipfile
        z = zipfile.ZipFile(file=FileHelper.GetEffectiveRoot() + 'var/wpkgman/installed.db', mode='a')
        return z
    else:
        zip.close()
        return zipfile.ZipFile(file=FileHelper.GetEffectiveRoot() + 'var/wpkgman/installed.db', mode=mode)

def GetFileFromZipfile(file: str) -> io.BufferedReader:
    zip = GetDatabaseFile()
    try:
        return zip.read(file)
    except KeyError:
        return None

def IsPackageInstalled(package: str, arch) -> bool:
    """
    Checks if a package is installed in the database.
    @param package: The package to check.
    @return: If the package is installed or not.
    """
    return True if GetFileFromZipfile(package + '/' + package + '-' + arch + '.yml') else False

def IsPackageVersionInstalled(package: str, version: str, arch) -> bool:
    """
    Checks if a package with the specified version is installed.
    @param package: The package.
    @param version: The version of package to check.
    @param arch: The architecture.
    @return: If the package with the specified version is installed.
    """
    # First, cut out a bit of extra processing
    if not IsPackageInstalled(package=package, arch=arch):
        return False

    # Okay
    f = GetFileFromZipfile(package + '/' + package + '-' + arch + '.yml')
    # Make something else do the parsing for me
    pkg = YAMLParser.InstalledPackage(f)
    if version != pkg.version:
        return False
    else:
        return True

def DoesPackageOwnFile(package: str, file: str, arch: str='x86_64') -> bool:
    """
    Checks if a package owns the specified file.
    @param package: The package.
    @param file: The FULL path to the file.
    @param arch: The architecture.
    @return: If the package owns the file.
    """
    pass

def AddFileToZipfile(file: str, content: str) -> None:
    """

    @param file:
    @param file_on_disk:
    @return:
    """
    # it's easier just to add it from disk
    zip = GetDatabaseFile(mode='a')
    try:
        zip.writestr(file, data=content)
    except UserWarning:
        # go away
        pass