import tarfile
import io
from . import FileHelper, YAMLParser

def GetDatabaseFile() -> tarfile.TarFile:
    """
    Gets the file object of the database tarball.
    @return: The file object representing the database file.
    """
    tarball = FileHelper.OpenFileRaw("var/wpkgman/installed.db", 'rb')
    if tarball is None:
        # Silently create a new tarfile.
        tar = tarfile.open(name=FileHelper.GetEffectiveRoot() + "var/wpkgman/installed.db",
                           mode='w:xz')
        tarinfo = tarfile.TarInfo(name="database.yml")
        samplefile = io.StringIO(initial_value=b"""# WPKGMAN Database File
# Thank you for using wpkgman!
# This file is left blank by default.""")
        tarinfo.size = len(samplefile.read())
        samplefile.seek(0)
        tar.addfile(tarinfo, samplefile)
        # overly complex - check!
        tarball = FileHelper.OpenFileRaw("var/wpkgman/installed.db", 'rb')
    else:
        tarball.close()
    return tarfile.open(name=FileHelper.GetEffectiveRoot() + "var/wpkgman/installed.db",
                           mode='r:xz')

def GetFileFromTarball(file: str) -> io.BufferedReader:
    tarball = GetDatabaseFile()
    try:
        return tarball.extractfile(file)
    except KeyError:
        return None

def IsPackageInstalled(package: str, arch: str='x86_64') -> bool:
    """
    Checks if a package is installed in the database.
    @param package: The package to check.
    @return: If the package is installed or not.
    """
    return True if GetFileFromTarball(package + '/' + package + arch + '.yml') else False

def IsPackageVersionInstalled(package: str, version: str, arch: str='x86_64') -> bool:
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
    f = GetFileFromTarball(package + '/' + package + arch + '.yml')
    # Make something else do the parsing for me
    pkg = YAMLParser.InstalledPackage(fileobj=f)
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
