import io
from . import FileHelper
import yaml
import warnings
warnings.filterwarnings("ignore")


def GetDatabaseFile(mode: str='rt') -> io.TextIOWrapper:
    """
    Gets the file object of the database file.
    @return: The file object representing the database file.
    """
    file = FileHelper.OpenFileRaw("var/wpkgman/installed.db", 'rb')
    if file is None:
        # Silently create a new lzmafile
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
        yaml_content = {'packages': {}}
        fobj.close()
        fobj = FileHelper.OpenFileRaw("var/wpkgman/installed.db", mode='w')
        yaml.safe_dump(yaml_content, fobj)
        fobj.close()
    finally:
        fobj.close()
    if yaml_content is None:
        return {'packages': {}}
    return yaml_content


def WriteToDatabaseFile(content: dict):
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