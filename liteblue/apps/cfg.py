"""
    I thought we might use configparser or yaml
    but then thought better of it. ConfigParser is
    too constricted in the values you can get back.
    Yaml just creates dictionaries and does do
    much else. So sticking with classes for present.
"""
import configparser
from importlib import import_module
from pkg_resources import resource_filename
from invoke import task


@task(help={"project": "name of project"})
def cfg(_, project):
    """ print out the values of the config class of a project """
    cfg_ = import_module(project + ".config")
    for key in dir(cfg_.Config):
        if key[0] != "_":
            print(f"{key}:", getattr(cfg_.Config, key))


@task(help={"project": "name of project"})
def read(_, project):
    """ print config """
    config = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation()
    )
    config.read(f"{project}.ini")
    for section in config.sections():
        print(section)
        for key in config[section]:
            print("\t", key, config[section][key])
    print(dict(**config["tornado"]))


@task(help={"project": "name of project"})
def write(_, project):
    """ write config ini file for project """
    default_ini = resource_filename("liteblue.apps", "default.ini")
    config = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation()
    )
    config.read(default_ini)
    config.set("default", "name", project)
    config.set("default", "static_path", resource_filename("liteblue.apps", "static"))
    with open(f"{project}.ini", "w") as configfile:
        config.write(configfile)
