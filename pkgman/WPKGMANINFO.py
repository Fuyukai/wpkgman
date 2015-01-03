__WPKGMAN_VERSION = "0.2.0"
__WPKGMAN_AUTHOR = "Eyes"

class Color:
    off = "\033[0m"
    black = "\033[0;30m"
    red = "\033[0;31m"
    green = "\033[0;32m"
    cyan = "\033[0;36m"
    yellow = "\033[1;33m"
    white = "\033[1;37m"

    # Dirty hacks
    # def remove(*args, **kwargs):
    # print("os.remove(" + str(args) + str(kwargs) + ")")
    # os.oldremove(*args, **kwargs)
    # os.oldremove = os.remove
    # os.remove = remove