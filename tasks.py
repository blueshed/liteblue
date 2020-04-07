''' cli task '''
import asyncio
import json
import alembic.config
import tornado.log
from alembic import command
from invoke import task
from liteblue.moo import Moo
from tests.app.main import Config


@task
def run(_):
    ''' run the web server '''
    from tests.app.main import main

    tornado.log.enable_pretty_logging()
    main()


@task
def test(ctx):
    ''' run pytest coverage '''
    ctx.run(
        'source venv/bin/activate && py.test --cov liteblue --cov-report term-missing tests'
    )


@task
def lint(ctx):
    ''' run lint on project and tests '''
    ctx.run('source venv/bin/activate && black liteblue tests')
    ctx.run('source venv/bin/activate && pylint liteblue')


@task
def reflect(_):
    ''' describe the procedures '''
    from liteblue.describe import describe

    print(json.dumps(describe(procedures, procedures.__all__), indent=4))


def alembic_cfg():
    ''' get the alembic config from web config data '''
    cfg = alembic.config.Config()
    cfg.set_main_option('script_location', Config.alembic_script_location)
    cfg.set_main_option('sqlalchemy.url', Config.db_url)
    return cfg


@task
def upgrade(_, revision='head'):
    ''' upgrades db to head or revision '''
    command.upgrade(alembic_cfg(), revision)


@task
def downgrade(_, revision='base'):
    ''' downgrades db to base or revision '''
    command.downgrade(alembic_cfg(), revision)


@task
def revise(_, comment):
    ''' creates an alembic database revision '''
    command.revision(alembic_cfg(), comment, autogenerate=True)


@task
def docs(ctx):
    ''' build docs '''
    ctx.run('cd docs && make html')


async def go():
    async with Moo(Config) as cow:
        print(await cow.add(2, 2))


@task
def moo(_):
    ''' run a moo task '''
    asyncio.run(go())


@task(pre=[docs])
def release(ctx, message, part='patch'):
    ''' release the build to git hub '''
    ctx.run(f"git add . && git commit -m '{message}'")
    ctx.run(f'bumpversion {part}')
