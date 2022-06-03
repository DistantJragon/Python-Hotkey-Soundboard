from colorama import Fore, Style, init


def enable_formatting():
    init()


def grey_out(text: str):
    return Fore.BLACK + Style.BRIGHT + text + Style.RESET_ALL


def brighten(text: str):
    return Style.BRIGHT + text + Style.RESET_ALL


# def strike(text: str):
#     return termcolor.colored(text, attrs=["blink"])
