# File helper
import yaml
import sys
import io

def GetEffectiveRoot() -> str:
    """
    Gets the effective root of the system.
    @return: The effective root of the system.
    """
    return "/"


def OpenFileRaw(file: str) -> io.TextIOWrapper:
    """
    Gets the raw file
    @param file: The file object that was requested, or None if the file was not found.
    """
    new_file_name = GetEffectiveRoot() + file
    f = None
    try:
        f = open(new_file_name, 'r')
    except (OSError):
        print("Requested to open {f} but file was not found.".format(f=new_file_name), file=sys.stderr)
    finally:
        return f

def OpenYAMLFile(file: str) -> dict:
    """
    Opens and deserializes a YAML file.
    @param file: The file to open.
    @return: A dictionary containing the values of the YAML file.
    """
    f = OpenFileRaw(file)
    if f is None:
        return None
    dict = yaml.safe_load(f)
    f.close()
    return dict

