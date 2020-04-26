"""
    Common functions used by Click and Invoke
"""
import os
import logging
import logging.config
from importlib import import_module
from contextlib import contextmanager

LOGGER = logging.getLogger(__name__)


class Colored:
    """ sometimes you need to colour console output """

    @staticmethod
    def green(text):
        """ turns text green """
        return f"\033[92m{text}\033[0m"

    @staticmethod
    def red(text):
        """ turns text red """
        return f"\033[91m{text}\033[0m"

    @staticmethod
    def blue(text):
        """ turns text blue """
        return f"\033[94m{text}\033[0m"

    @staticmethod
    def cyan(text):
        """ turns text cyan """
        return f"\033[36m{text}\033[0m"

    @staticmethod
    def gray(text):
        """ turns text gray """
        return f"\033[90m{text}\033[0m"

    @staticmethod
    def pink(text):
        """ turns text pink """
        return f"\033[33m{text}\033[0m"


@contextmanager
def pid_file(path):
    """ creates a file with the process id and removes it """
    pid = os.getpid()
    with open(path, "w") as file:
        file.write(f"{pid}")
    try:
        yield
    finally:
        if os.path.isfile(path):
            os.unlink(path)


def confirm_action(action):
    """ Are you sure? """
    choice = ""
    while choice not in ["y", "n"]:
        choice = input(f"{action} [Y/N] ").lower()
    return choice == "y"


def qname_to_class(qname):
    """ returns a class from module_name:class_name """
    if isinstance(qname, str):
        _modules, _class = qname.split(":")
        return getattr(import_module(_modules), _class)
    return qname
