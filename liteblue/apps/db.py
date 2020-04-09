""" database tasks """
from importlib import import_module
from invoke import task
import alembic.config
from alembic import command
from .utils import confirm_action, Colored


def alembic_cfg(name, settings):
    """ get the alembic config from web config data """
    db_url_name = f"{name}_db_url" if name != "default" else "db_url"
    script_location = (
        f"{name}_alembic_script_location"
        if name != "default"
        else "alembic_script_location"
    )
    cfg = alembic.config.Config()
    cfg.set_main_option("script_location", getattr(settings, script_location))
    cfg.set_main_option("sqlalchemy.url", getattr(settings, db_url_name))
    return cfg


def confirm_db_action(action, db_url):
    """db are you sure? """
    return confirm_action(f"{action} {db_url}")


@task
def upgrade(_, project, revision="head", name="default", force=False):
    """ upgrades db to head or revision """
    if force is True or confirm_db_action(Colored.green("UPGRADE"), name):
        app = import_module(project)
        command.upgrade(alembic_cfg(name, app.config.Config), revision)


@task
def downgrade(_, project, revision="base", name="default"):
    """ downgrades db to base or revision """
    if confirm_db_action(Colored.red("DOWNGRADE"), name):
        app = import_module(project)
        command.downgrade(alembic_cfg(name, app.config.Config), revision)


@task
def revise(_, project, comment, name="default"):
    """ creates an alembic database revision """
    app = import_module(project)
    command.revision(alembic_cfg(name, app.config.Config), comment, autogenerate=True)
