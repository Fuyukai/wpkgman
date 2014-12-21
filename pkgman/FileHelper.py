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


def OpenFileRaw(file: str, mode: str='r') -> io.FileIO:
    """
    Gets the raw file
    @param file: The file to open.
    @param mode: The opening mode of the file. Defaults to r (text read).
    @return: The file object that was requested, or None if the file was not found.
    """
    new_file_name = GetEffectiveRoot() + file
    f = None
    try:
        f = open(new_file_name, mode)
    except OSError:
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
    content = yaml.safe_load(f)
    f.close()
    return content

def OpenFileForWritingText(file: str) -> io.FileIO:
    """
    Opens a file for writing in text mode.
    @param file: The file to open
    @return: The file object that was requested, or None if cannot be opened.
    """
    new_file_name = GetEffectiveRoot() + file
    f = None
    try:
        f = open(new_file_name, 'w')
    except OSError:
        print("Requested to open {f} but file could not be opened.".format(f=new_file_name), file=sys.stderr)
    finally:
        return f

def OpenFileForWritingBytes(file: str) -> io.FileIO:
    """
    Opens a file for writing in bytes mode.
    @param file: The file to open
    @return: The file object that was requested, or None if cannot be opened.
    """
    new_file_name = GetEffectiveRoot() + file
    f = None
    try:
        f = open(new_file_name, 'wb')
    except OSError:
        print("Requested to open {f} but file could not be opened.".format(f=new_file_name), file=sys.stderr)
    finally:
        return f

def WriteYAMLFile(file: str, content: dict) -> None:
    """
    Writes data to a YAML file.
    @param file: The file to open.
    @param content: The content to write to the file.
    @return If the write operation succeeded.
    """
    f = OpenFileForWritingText(file)
    if f is None:
        return False
    yaml.safe_dump(content, f)
    f.close()
    return True