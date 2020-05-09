""" tasks to create and run projects """
import os
import logging
from importlib import import_module
from pkg_resources import resource_filename
import tornado.template
from invoke import task
from .db import revise, upgrade
from .docker import docker
from .utils import qname_to_class, confirm_action, Colored

LOGGER = logging.getLogger(__name__)


@task(help={"project": "name of project"})
def create(ctx, project):
    """ creates a new project with a sqlite db """
    if os.path.isdir(project):
        if confirm_action(Colored.red("DELETE ") + project + "?"):
            ctx.run(f"rm -rf {project}")
        else:
            return
    if os.path.isfile(f"{project}.db"):
        os.unlink(f"{project}.db")
    LOGGER.info(Colored.cyan("creating: ") + project)
    template_dir = resource_filename("liteblue.apps", "simple")
    loader = tornado.template.Loader(template_dir)
    for path, folders, files in os.walk(template_dir):
        target_path = os.path.join(project, path[len(template_dir) + 1 :])
        for folder in folders:
            folder_path = os.path.join(target_path, folder)
            os.makedirs(folder_path)
        for filename in files:
            template = os.path.join(path, filename)
            target = os.path.join(target_path, os.path.splitext(filename)[0])
            tmpl = loader.load(template)
            with open(target, "wb") as file:
                file.write(tmpl.generate(project_name=project))
    os.makedirs(f"{project}/scripts/versions")
    revise(ctx, project, "first pass")
    upgrade(ctx, project, force=True)
    docker(ctx, project, force=True)


@task(help={"package": "the liteblue module to run"})
def run(_, package):
    """ run a liteblue project """
    app = import_module(package)
    app.main()


@task(help={"config": "config.Config module path"})
def worker(_, config):
    """ run a liteblue worker """
    from liteblue.worker import main  # pylint: disable=C0415

    cfg_ = qname_to_class(config)
    main(cfg_)
