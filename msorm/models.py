from __future__ import annotations

from functools import lru_cache
from typing import List

import pyodbc

import msorm.type_fields as type_fields
from msorm.exceptions import NotInitializedError, ItemNotFoundException

connection = None
__connected__ = False


def init(server, database, username, password):
    """
    :param server: Server Ip or Server Name
    :param database: Database Name
    :param username: required for remote server. for local set as ""
    :param password: required for remote server. for local set as ""
    :return:
    """
    global connection
    connection = pyodbc.connect('Driver={SQL Server};'
                                f'Server={server}4;'
                                f'Database={database};'
                                f'UID={username};'
                                f'PWD={password};')
    global __connected__
    __connected__ = True
    # if not connection:
    #     raise NotInitializedError("models must be initialized before model creation")


__safe__ = None
__models__ = None
__columns__ = None


class extras:
    @staticmethod
    def check_init(func):
        def core(*args, **kwargs):
            __table_name__ = getattr(args[0], "__name__", "")

            if __table_name__.startswith("INFORMATION_SCHEMA"): return func(*args, **kwargs)
            if not __connected__: raise NotInitializedError("MSORM must be initialized before model creation")
            return func(*args, **kwargs)

        return core


# class ModelMeta(type):
#     def __new__(cls, *args, **kwargs):
#         print(args,"selam",kwargs,"sed")
#         metadata = {}
#         for key, val in args[2].items():
#
#             if isinstance(val, type_fields.field):
#                 metadata[key] = val
#         args[2]["metadata"] = metadata
#
#         return type(args[0],args[1],args[2])


class Model():
    __fields__ = None
    __subclass__ = False

    @extras.check_init
    def __init__(self, **kwargs):
        assert self.__subclass__, "Model cannot be initialized directly, it should be subclass of Model to be used and initialized properly."
        # TODO: Check if the variable is suitable for variable
        self.__fields__ = kwargs.get("fields") if kwargs.get("fields") else tuple(
            name for name in kwargs.keys() if isinstance(getattr(self, name, None), type_fields.field))
        for field in self.__fields__:

            if isinstance(getattr(self, field), type_fields.foreignKey):
                fk = getattr(self, field)
                setattr(self, field,
                        getattr(self, field).get_new(value=kwargs[field], model=fk.get_model(), name=fk.get_name()))
            else:
                setattr(self, field, getattr(self, field).get_new(value=kwargs[field]).value)

    @extras.check_init
    def __init_subclass__(cls, **kwargs):
        metadata = {}
        for key, val in cls.__dict__.items():
            if isinstance(val,type_fields.field):
                metadata[key] = val

        cls.__metadata__ = metadata
        cls.__subclass__ = True

    @extras.check_init
    def __setattr__(self, key, value):
        super(Model, self).__setattr__(key, value)

    @lru_cache()
    def dict(self, *fields: str, depth=0):
        """

        :param fields: Fields wants to be appended in return. if it is null, then return values of every field
        :param depth: if depth > 0 then loop through fields and if field is a foreignKey then add a parameter, which have same name with model_name of foreignKey,
        to dicts and call dict function for that model with depth-1

        :return: A tuple of dictionary collections of fields and their values
        """

        fields = fields if fields else getattr(self, "__fields__", None)
        _dict = {
        }
        if depth == 0:
            for field in fields:
                attr = getattr(self, field)
                _dict[field] = getattr(self, field) if isinstance(attr,type_fields.foreignKey) else attr

            return _dict
        elif depth >= 1:
            for field in fields:
                reference_field = getattr(self, field)
                if isinstance(reference_field, type_fields.foreignKey):
                    _dict[type(reference_field.model).__name__] = reference_field.model.dict(depth=depth - 1)
                    _dict[field] = reference_field.value

                else:

                    _dict[field] = reference_field
            return _dict
        else:
            raise ValueError("depth cannot be less than 0")

    @lru_cache()
    def values(self, *fields: str):
        """

        :param fields: Fields wants to be appended in return. if it is null, then return values of every field
        :return: A tuple of fields values
        """

        fields = fields if fields else getattr(self, "__fields__", None)

        return tuple(getattr(self, field).value if isinstance(getattr(self, field),type_fields.foreignKey) else getattr(self, field) for field in fields)

    @classmethod
    @extras.check_init
    def __class__(cls):
        return cls

    @classmethod
    @extras.check_init
    def first(cls, fields=None):

        fields = fields

        cursor = connection.cursor()

        text = 'SELECT TOP 1 {fields} FROM {table}'.format(
            fields=str(f'{", ".join(fields)}' if fields else "*"),
            table="dbo." + cls.__name__)
        cursor.execute(text)
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, type_fields.field)]
            return (cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields))

    @classmethod
    @extras.check_init
    def get(cls, *args, **kwargs):
        # SELECT TOP 1 column_name FROM table_name
        if not kwargs and not args:
            raise ValueError("you must provide at least one key and one value")
        fields = kwargs.get("fields")

        if fields: del kwargs["fields"]

        cursor = connection.cursor()

        kwargs = " AND ".join([f"{type_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
        args = " ".join([str(arg) for arg in args])
        text = 'SELECT TOP 1 {fields} FROM {table} WHERE ({kwargs} {args})'.format(
            fields=str(f'{", ".join(fields)}' if fields else "*"),
            table="dbo." + cls.__name__,
            kwargs=kwargs,
            args=args)
        cursor.execute(text)
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, type_fields.field)]
            return (cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields))

        # raise NotImplementedError

    @classmethod
    @extras.check_init
    def where(cls, *args, **kwargs):
        if not kwargs and not args:
            raise ValueError("you must provide at least one key and one value")
        fields = kwargs.get("fields")

        if fields: del kwargs["fields"]

        cursor = connection.cursor()

        kwargs = " AND ".join([f"{type_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
        args = " ".join([str(arg) for arg in args])
        text = 'SELECT {fields} FROM {table} WHERE ({kwargs} {args})'.format(
            fields=str(f'{", ".join(fields)}' if fields else "*"),
            table="dbo." + cls.__name__,
            kwargs=kwargs,
            args=args)
        cursor.execute(text)
        objs = []
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, type_fields.field)]
            objs.append(cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields))

        return QueryDict(objs)

    @classmethod
    @extras.check_init
    def all(cls, *fields):
        cursor = connection.cursor()

        text = 'SELECT {fields} FROM {table}'.format(fields=str(f'{", ".join(fields)}' if fields else "*"),
                                                     table="dbo." + cls.__name__)
        cursor.execute(text)
        objs = []
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if not name.startswith('_')]
            __fields__ = fields if fields else __fields__
            objs.append(cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields))
        return QueryDict(objs)

    @classmethod
    @extras.check_init
    def count(cls):

        cursor = connection.cursor()

        text = 'SELECT COUNT(*) FROM {table}'.format(
            table="dbo." + cls.__name__
        )
        cursor.execute(text)
        for i in cursor:
            return i[0]

    def __iter__(self):
        for field in self.__fields__:
            yield getattr(self, field, None)

class QueryDict:
    __model__ = Model

    def __init__(self, models: List[Model]):
        self.__objects__ = models
        self.__model__ = self.__objects__[0].__class__ if self.__objects__ else self.__model__

    def add(self, model: __model__):
        if isinstance(model, self.__model__):
            self.__objects__.append(model)
        else:
            raise TypeError(f"model must be instance of {self.__model__.__class__.__name__}")

    def __find(self, first, second):
        return first == second

    @lru_cache()
    def find(self, func):
        founds = []
        for obj in self.__objects__:
            found = obj if func(obj) else None
            if found: founds.append(found)
        return QueryDict(founds)

    def get(self, func):
        for obj in self.__objects__:
            found = obj if func(obj) else None
            if found:
                return found
        raise ItemNotFoundException("Cannot found item")

    def remove(self, func):
        for obj in self.__objects__:
            found = obj if func(obj) else None
            if found:
                self.__objects__.remove(found)
                return
        raise ItemNotFoundException("Cannot found item")

    def pop(self, func):
        for obj in self.__objects__:
            found = obj if func(obj) else None
            if found:
                self.__objects__.remove(found)
                return found
        raise ItemNotFoundException("Cannot found item")

    @lru_cache()
    def values(self, *fields: str):
        """

        :param fields: Fields wants to be appended in return. if it is null, then return values of every field
        :return: A tuple of fields values
        """

        fields = fields if fields else getattr(self.__objects__[0], "__fields__", None)
        _list = []
        for obj in self.__objects__:
            _list.append(obj.values(*fields))

        return tuple(_list)

    @lru_cache()
    def dicts(self, *fields: str, depth=0):
        """

        :param fields: Fields wants to be appended in return. if it is null, then return values of every field
        :param depth: if depth > 0 then loop through fields and if field is a foreignKey then add a parameter, which have same name with model_name of foreignKey,
        to dicts and call dict function for that model with depth-1

        :return: A tuple of dictionary collections of fields and their values
        """

        if len(self.__objects__) == 0:
            return [{}]
        # fields = fields if fields else getattr(self.__objects__[0], "__fields__", None)
        _list = []

        for obj in self.__objects__:
            _list.append(obj.dict(*fields, depth=depth))
        return tuple(_list)

    @lru_cache()
    def __iter__(self):
        for obj in self.__objects__:
            yield obj

    def __getitem__(self, item):
        return self.__objects__[item]

    def __len__(self):
        return len(self.__objects__)


# if __name__ == '__main__':
class INFORMATION_SCHEMA_COLUMNS(Model):
    __name__ = "INFORMATION_SCHEMA.COLUMNS"
    __table_name__ = "INFORMATION_SCHEMA.COLUMNS"
    TABLE_CATALOG = type_fields.nvarchar()
    TABLE_SCHEMA = type_fields.nvarchar()

    TABLE_NAME = type_fields.nvarchar()

    COLUMN_NAME = type_fields.nvarchar()
    ORDINAL_POSITION = type_fields.nvarchar()
    COLUMN_DEFAULT = type_fields.nvarchar()
    IS_NULLABLE = type_fields.nvarchar()
    DATA_TYPE = type_fields.nvarchar()
    CHARACTER_MAXIMUM_LENGTH = type_fields.nvarchar()

    CHARACTER_OCTET_LENGTH = type_fields.nvarchar()
    NUMERIC_PRECISION = type_fields.nvarchar()

    NUMERIC_PRECISION_RADIX = type_fields.nvarchar()
    DATETIME_PRECISION = type_fields.nvarchar()
    CHARACTER_SET_CATALOG = type_fields.nvarchar()
    CHARACTER_SET_SCHEMA = type_fields.nvarchar()
    CHARACTER_SET_NAME = type_fields.nvarchar()
    COLLATION_CATALOG = type_fields.nvarchar()
    COLLATION_SCHEMA = type_fields.nvarchar()
    DOMAIN_CATALOG = type_fields.nvarchar()
    DOMAIN_SCHEMA = type_fields.nvarchar()
    DOMAIN_NAME = type_fields.nvarchar()

    @classmethod
    @extras.check_init
    def get(cls, *args, **kwargs):
        # SELECT TOP 1 column_name FROM table_name
        if not kwargs and not args:
            raise ValueError("you must provide at least one key and one value")
        fields = kwargs.get("fields")

        if fields: del kwargs["fields"]

        cursor = connection.cursor()

        kwargs = " AND ".join([f"{type_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
        args = " ".join([str(arg) for arg in args])
        text = 'SELECT TOP 1 {fields} FROM {table} WHERE ({kwargs} {args})'.format(
            fields=str(f'{", ".join(fields)}' if fields else "*"),
            table="dbo." + "INFORMATION_SCHEMA.COLUMNS",
            kwargs=kwargs,
            args=args)
        cursor.execute(text)
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, type_fields.field)]
            return (cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields))

        # raise NotImplementedError

    @classmethod
    @extras.check_init
    def where(cls, *args, **kwargs):
        if not kwargs and not args:
            raise ValueError("you must provide at least one key and one value")
        fields = kwargs.get("fields")

        if fields: del kwargs["fields"]

        cursor = connection.cursor()

        kwargs = " AND ".join([f"{type_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
        args = " ".join([str(arg) for arg in args])
        text = 'SELECT {fields} FROM {table} WHERE ({kwargs} {args})'.format(
            fields=str(f'{", ".join(fields)}' if fields else "*"),
            table="dbo." + "INFORMATION_SCHEMA.COLUMNS",
            kwargs=kwargs,
            args=args)
        cursor.execute(text)
        objs = []
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, type_fields.field)]
            objs.append(cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields))

        return QueryDict(objs)

    @classmethod
    @extras.check_init
    def all(cls, *fields):
        cursor = connection.cursor()

        text = 'SELECT {fields} FROM {table}'.format(fields=str(f'{", ".join(fields)}' if fields else "*"),
                                                     table="INFORMATION_SCHEMA.COLUMNS")
        cursor.execute(text)
        objs = []
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if not name.startswith('_')]
            __fields__ = fields if fields else __fields__
            objs.append(cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields))
        return QueryDict(objs)
