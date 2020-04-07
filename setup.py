''' Python install script '''
from setuptools import setup

setup(
    name='liteblue',
    version='0.0.1',
    packages=['liteblue'],
    install_requires=['invoke', 'sqlalchemy', 'pymysql', 'aioredis', 'tornado'],
)
