'''
    This is a our invoke program
'''
import tornado.log
from invoke import Program, Collection
from . import run
from . import db

VERSION = '0.0.3'

_NAMESPACE_ = Collection()

_NAMESPACE_.add_task(run.run)
_NAMESPACE_.add_task(run.create)
_NAMESPACE_.add_task(db.upgrade)
_NAMESPACE_.add_task(db.downgrade)
_NAMESPACE_.add_task(db.revise)

tornado.log.enable_pretty_logging()

program = Program(
    version=VERSION, namespace=_NAMESPACE_
)  # pylint: disable=C0103
