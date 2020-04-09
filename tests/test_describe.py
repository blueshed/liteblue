from liteblue.describe import describe, describe_sql
from .app import procedures
from .app import tables


async def test_describe():
    ''' we need more tests that this. '''
    result = await procedures.reflect()
    print(result)

    assert result['procedures']['add']['docs'] == 'returns a plus b '

    result = describe(
        procedures, [name for name in procedures.__all__ if name != 'add']
    )
    print(result)

    assert result.get('add') is None


def test_get_user():
    assert procedures.get_user() is None


def test_describe_sql():

    result = describe_sql(tables.metadata)
    print(result)
    assert result['user']['id']['pk'] is True
