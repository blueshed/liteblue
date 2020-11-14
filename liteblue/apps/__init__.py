"""
    This is a our invoke program
"""
import os
import sys
import tornado.log
from invoke import Program, Collection
from . import run
from . import db
from . import cfg

sys.path.insert(0, os.getcwd())

VERSION = "0.0.11"

_NAMESPACE_ = Collection()

_NAMESPACE_.add_task(run.run)
_NAMESPACE_.add_task(run.worker)
_NAMESPACE_.add_task(run.create)
_NAMESPACE_.add_task(db.upgrade)
_NAMESPACE_.add_task(db.downgrade)
_NAMESPACE_.add_task(db.revise)
_NAMESPACE_.add_task(cfg.cfg)

tornado.log.enable_pretty_logging()

program = Program(version=VERSION, namespace=_NAMESPACE_)  # pylint: disable=C0103
