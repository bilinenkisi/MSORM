from __future__ import annotations

from functools import lru_cache
from typing import List

import pyodbc

import msorm.type_fields as type_fields
from msorm.exceptions import NotInitializedError

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
            if not __connected__: raise NotInitializedError("MSORM must be initialized before model creation")
            return func(*args, **kwargs)

        return core


class Model(object):
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
                setattr(self, field, getattr(self, field).get_new(value=kwargs[field]))
    @extras.check_init
    def __init_subclass__(cls, **kwargs):
        cls.__subclass__ = True

    @extras.check_init
    def __setattr__(self, key, value):
        super(Model, self).__setattr__(key, value)

    @classmethod
    @extras.check_init
    def __class__(cls):
        return cls

    @classmethod
    @extras.check_init
    def get(cls, *args, **kwargs) -> NotImplementedError:
        raise NotImplementedError

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
    def find(self, field, value):
        founds = []
        for obj in self.__objects__:
            found = obj if getattr(obj, field, None).value == value else None
            if found: founds.append(found)
        return QueryDict(founds)

    def get(self, field, value):
        for obj in self.__objects__:
            found = obj if getattr(obj, field, None).value == value else None
            if found:
                return found
        return found

    def remove(self, field, value):
        for obj in self.__objects__:
            found = obj if getattr(obj, field, None).value == value else None
            if found:
                self.__objects__.remove(found)
                return

    def pop(self, field, value):
        for obj in self.__objects__:
            found = obj if getattr(obj, field, None).value == value else None
            if found:
                self.__objects__.remove(found)
                return found

    @lru_cache()
    def values(self, *fields: str):
        """

        :param fields: Fields wants to be appended in return. if it is null, then return values of every field
        :return: A tuple of fields values
        """

        fields = fields if fields else getattr(self.__objects__[0], "__fields__", None)
        _list = []
        for obj in self.__objects__:
            _list.append(tuple(getattr(obj, field).value for field in fields))

        return tuple(_list)

    @lru_cache()
    def dicts(self, *fields: str):
        """

        :param fields: Fields wants to be appended in return. if it is null, then return values of every field
        :return: A tuple of dictionary collections of fields and their values
        """
        # print( self.__model__.__dict__["__fields__"])
        if len(self.__objects__) == 0:
            return [{}]
        fields = fields if fields else getattr(self.__objects__[0], "__fields__", None)
        _list = []

        for obj in self.__objects__:
            _dict = {
            }
            for field in fields:
                _dict[field] = getattr(obj, field).value
            _list.append(_dict)
        return tuple(_list)

    @lru_cache()
    def __iter__(self):
        for obj in self.__objects__:
            yield obj

    def __getitem__(self, item):
        return self.__objects__[item]

    def __len__(self):
        return len(self.__objects__)
