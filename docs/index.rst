.. liteblue documentation master file, created by
   sphinx-quickstart on Mon Apr  6 17:23:12 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to liteblue's documentation!
=====================================

Liteblue is a simple rpc server. It supports sync and async procedures, 
making it easy to support sqlalchemy. Used as the host for a single page
application it will scale via redis to support mutilple hosts. 
It uses Websockets or EventSource to provide real-time updates.

Liteblue cli is written with invoke::

    % liteblue -l
    Subcommands:

        create      creates a new project with a sqlite db
        downgrade   downgrades db to base or revision
        revise      creates an alembic database revision
        run         run a liteblue project
        upgrade     upgrades db to head or revision
        worker      run a liteblue worker



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   start
   context
   application
   authentication
   handlers
   sqlalchemy
   redis
   moo
   utils


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
