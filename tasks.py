""" cli task """
import asyncio
import json
import alembic.config
import tornado.log
from alembic import command
from invoke import task
from tests.app.main import Config


@task
def run(_):
    """ run the web server """
    from tests.app.main import main

    tornado.log.enable_pretty_logging()
    main()


@task
def test(ctx):
    """ run pytest coverage """
    ctx.run(
        "source venv/bin/activate && py.test --cov liteblue --cov-report term-missing tests"
    )


@task
def lint(ctx):
    """ run lint on project and tests """
    ctx.run("source venv/bin/activate && black liteblue tests")
    ctx.run("source venv/bin/activate && pylint liteblue")


@task
def docs(ctx):
    """ build docs """
    ctx.run("cd docs && make html")


@task
def clean(ctx):
    """ tidy up """
    ctx.run("rm -rf dist")


@task(pre=[clean, docs])
def release(ctx, message, part="patch"):
    """ release the build to git hub """
    ctx.run(f"git add . && git commit -m '{message}'")
    ctx.run(f"bumpversion {part}")
    ctx.run("pip install -r requirements.txt")
    ctx.run("python setup.py sdist bdist_wheel")
    ctx.run("twine upload dist/*")
