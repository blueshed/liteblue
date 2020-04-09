""" Test the json functionality """
import enum
from dataclasses import dataclass
from datetime import datetime, date, time
from decimal import Decimal
from types import SimpleNamespace
from liteblue.handlers import json_utils
from .helpers.enum_helpers import EnumHelper


@dataclass
class dcRole:
    _type_: str
    name: str
    act: EnumHelper


class Foo:
    """ simple test class """

    def to_json(self):
        """ with to_json method """
        return {"_type_": "Foo", "name": "Harry"}


class Bert:
    pass


def test_datetime():
    dt = datetime(2018, 11, 11, 10, 30, 42)
    dtf = dt.isoformat().replace("T", " ")
    assert f'"{dtf}"' == json_utils.dumps(dt)


def test_date():
    dt = date(2018, 11, 11)
    dtf = dt.isoformat().replace("T", " ")
    assert f'"{dtf}"' == json_utils.dumps(dt)


def test_decimal():
    value = Decimal("42.1")
    assert f"{value}" == json_utils.dumps(value)


def test_obj():
    value = Bert()
    try:
        assert '{"hello": "world"}' == json_utils.dumps(value)
    except TypeError:
        pass


def test_to_json():
    data = json_utils.dumps(Foo())
    data_str = '{"_type_": "Foo", "name": "Harry"}'
    assert data_str == data


def test_doc_dict():
    data = json_utils.dumps(Foo())
    data_str = '{"_type_": "Foo", "name": "Harry"}'
    assert data_str == data
    obj = json_utils.loads(data_str, object_hook=lambda x: SimpleNamespace(**x))
    assert obj._type_ == "Foo"
    assert obj.__class__.__name__ == "SimpleNamespace"
    assert obj.name == "Harry"


def test_doc_dataclass():
    data = json_utils.dumps(dcRole(_type_="Foo", name="Harry", act=EnumHelper(1)))
    data_str = '{"_type_": "Foo", "name": "Harry", "act": "LOGIN"}'
    assert data_str == data
    obj = json_utils.loads(data_str, object_hook=lambda x: dcRole(**x))
    assert obj._type_ == "Foo"
    assert obj.__class__.__name__ == "dcRole"
    assert obj.name == "Harry"


def test_type_from_json():
    assert json_utils.type_from_json(str, None) == None
    assert json_utils.type_from_json(str, "foo") == "foo"
    assert json_utils.type_from_json(int, "4") == 4
    assert json_utils.type_from_json(float, "4.1") == 4.1
    assert json_utils.type_from_json(bool, "true") is True
    assert json_utils.type_from_json(bool, "FALSE") is False
    assert json_utils.type_from_json(Decimal, "10.1234") == Decimal("10.1234")
    assert json_utils.type_from_json(datetime, "2020-10-14 23:11:56") == datetime(
        2020, 10, 14, 23, 11, 56
    )
    assert json_utils.type_from_json(date, "2020-10-14") == date(2020, 10, 14)
    assert json_utils.type_from_json(time, "23:11:56") == time(23, 11, 56)
