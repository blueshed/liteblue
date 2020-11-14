"""
    We want a description of functions and classes made remotely callable
"""
import inspect
import typing
from collections import OrderedDict


def annotation_to_str(annotation):
    """ converts annotation to string """
    if annotation is None:
        return None
    if isinstance(annotation, str):
        return annotation
    if inspect.isclass(annotation):
        return annotation.__name__
    if isinstance(annotation, typing._GenericAlias):  # pylint: disable=W0212
        return str(annotation)
    if inspect.isfunction(annotation):
        return annotation.__name__
    return annotation


def describe_sql(metadata):
    """
    returns a jsonable sql metadata
    """
    result = {}
    for table_name in metadata.tables:
        table = metadata.tables[table_name]
        pks = [col.name for col in table.primary_key]
        fkeys = {
            col.column_keys[0]: str(col.elements[0].column)
            for col in table.foreign_key_constraints
        }
        result[table.name] = {
            col.name: {
                "pk": col.name in pks,
                "type": col.type.python_type.__name__,
                "sql": repr(col.type),
                "fkey": fkeys.get(col.name),
            }
            for col in table.c
        }
    return result


def describe(target, limit):
    """
    Will dir target and inspect each function

    functions starting with '_' are ignored,
    as are functions whose name is not in limit
    """
    result = OrderedDict()
    for key in filter(lambda x: x[0] != "_", dir(target)):
        if limit and key not in limit:
            continue
        func = getattr(target, key)
        if inspect.isfunction(func):
            name = key
            desc = inspect.signature(func)
            docs = inspect.getdoc(func)
            result[name] = OrderedDict(
                [
                    ("params", [str(p) for p in desc.parameters.values()]),
                    (
                        "returns",
                        annotation_to_str(desc.return_annotation)
                        if desc.return_annotation is not desc.empty
                        else "",
                    ),
                    ("docs", docs),
                ]
            )
    return result
