from __future__ import annotations

import inspect
import sys
import warnings
from functools import lru_cache
from typing import List

import pyodbc

from msorm import mssql_fields, settings
from msorm.exceptions import NotInitializedError, ItemNotFoundException
from msorm.mssql_fields import field

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


# region Operators
class OR:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(OR, self).__init__()
        self.value = ""
        if kwargs:

            for key, value in kwargs.items():
                self.value += f"{field.find_filter(key, value)} OR "
            self.value = self.value[:-3]

    @classmethod
    def __from_values(cls, value, othervalue):
        new_or = cls()
        new_or.value = value + " OR " + othervalue
        return new_or

    @classmethod
    def __from_value(cls, value):
        new_or = cls()
        new_or.value = value
        return new_or

    def __or__(self, other):
        return self.__from_values(self.value, other.value)

    def __invert__(self):
        warnings.warn("Depcreated because of filter kwargs", DeprecationWarning)
        values = ""
        if self.kwargs:

            for field, value in self.kwargs.items():
                values += f"{field}!='{value}' OR "
            values = values[:-3]
        return self.__from_value(values)

    def __str__(self):
        return self.value


# endregion
# region Fields
class Field:
    class bit(field):
        __field__ = "bit"

    class bigint(field):
        __field__ = "bigint"

    class int(field):
        __field__ = "int"

    class smallint(field):
        __field__ = "smallint"

    class tinyint(field):
        __field__ = "tinyint"

    class decimal(field):
        __field__ = "decimal"

        def __init__(self, default=None, precision=18, scale=0, null=True):
            super(Field.decimal, self).__init__(default=default, null=null)
            self.__properties__["precision"] = precision
            self.__properties__["scale"] = scale

    class numeric(field):
        __field__ = "numeric"

        def __init__(self, default=None, precision=18, scale=0, null=True):
            super(Field.numeric, self).__init__(default=default, null=null)
            self.__properties__["precision"] = precision
            self.__properties__["scale"] = scale

    class money(field):
        __field__ = "money"

    class smallmoney(field):
        __field__ = "smallmoney"

    class float(field):
        __field__ = "float"

    class real(field):
        __field__ = "real"

    class char(field):
        __field__ = "char"

        def __init__(self, default=None, length=settings.__MFL__.char_min, null=True):
            min, max = settings.__MFL__.char_min, settings.__MFL__.char_max

            if min > length > max: raise ValueError(
                f"length must be between {min} and {max}")
            super(Field.char, self).__init__(default=default, null=null)
            self.__properties__["length"] = length

    class nchar(field):
        __field__ = "nchar"

        def __init__(self, default=None, length=settings.__MFL__.nchar_min, null=True):
            min, max = settings.__MFL__.nchar_min, settings.__MFL__.nchar_max

            if min > length > max: raise ValueError(
                f"length must be between {min} and {max}")

            super(Field.nchar, self).__init__(default=default, null=null)
            self.__properties__["length"] = length

    class varchar(field):
        __field__ = "varchar"

        def __init__(self, default=None, length=settings.__MFL__.varchar_min, null=True):
            min, max = settings.__MFL__.varchar_min, settings.__MFL__.varchar_max
            if min > length > max: raise ValueError(
                f"length must be between {min} and {max}")

            super(Field.varchar, self).__init__(default=default, null=null)
            self.__properties__["length"] = length

    class nvarchar(field):
        __field__ = "nvarchar"

        def __init__(self, default=None, length=settings.__MFL__.nvarchar_min, null=True):
            min, max = settings.__MFL__.nvarchar_min, settings.__MFL__.nvarchar_max
            if min > length > max: raise ValueError(
                f"length must be between {min} and {max}")

            super(Field.nvarchar, self).__init__(default=default, null=null)
            self.__properties__["length"] = length

    class text(field):
        __field__ = "text"

    class ntext(field):
        __field__ = "ntext"

    class binary(field):
        __field__ = "binary"

        def __init__(self, default=None, length=settings.__MFL__.binary_min, null=True):
            min, max = settings.__MFL__.binary_min, settings.__MFL__.binary_max
            if min > sys.getsizeof(length) > max: raise ValueError(
                f"length must be between {min} and {max}")

            super(Field.binary, self).__init__(default=default, null=null)
            self.__properties__["length"] = length

    class varbinary(field):
        __field__ = "varbinary"

        def __init__(self, default=None, length=settings.__MFL__.varbinary_min, null=True):
            min, max = settings.__MFL__.varbinary_min, settings.__MFL__.varbinary_max
            if min > sys.getsizeof(length) > max: raise ValueError(
                f"length must be between {min} and {max}")

            super(Field.varbinary, self).__init__(default=default, null=null)
            self.__properties__["length"] = length

    class image(field):
        __field__ = "image"

    class date(field):
        __field__ = "date"

    class datetime(field):
        __field__ = "datetime"

    class smalldatetime(field):
        __field__ = "smalldatetime"

    class foreignKey(field):

        def __init__(self, model, value=None, name=None, safe=False):
            # model,value=None, name=None
            self.__model = model
            self.__name = name
            self.__value = value
            super(Field.foreignKey, self).__init__(value, safe=safe)

        def get_model(self):
            return self.__model

        def get_name(self):
            return self.__name

        @property
        def model(self):
            if inspect.isclass(type(self.__model)):
                self.__model = \
                    self.__model.where(
                        **{self.__name if self.__name else self.__model.__class__.__name__: self.__value})[
                        0]
            return self.__model

        @classmethod
        def get_new(cls, *args, **kwargs):
            new_field = cls(*args, **kwargs)
            return new_field


# endregion

class Model:
    __fields__ = None
    __subclass__ = False

    def __safe__init__(self, **kwargs):
        self.__fields__ = kwargs.get("fields") if kwargs.get("fields") else tuple(
            name for name in kwargs.keys() if isinstance(getattr(self, name, None), mssql_fields.field))
        for field in self.__fields__:

            if isinstance(getattr(self, field), Field.foreignKey):
                fk = getattr(self, field)
                setattr(self, field,
                        getattr(self, field).get_new(value=kwargs[field], model=fk.get_model(), name=fk.get_name(),
                                                     safe=False))
            else:
                setattr(self, field, getattr(self, field).produce(kwargs[field]))

    def __unsafe__init(self, **kwargs):
        self.__fields__ = kwargs.get("fields") if kwargs.get("fields") else tuple(
            name for name in kwargs.keys() if isinstance(getattr(self, name, None), mssql_fields.field))
        for field in self.__fields__:

            if isinstance(getattr(self, field), Field.foreignKey):
                fk = getattr(self, field)
                setattr(self, field,
                        getattr(self, field).get_new(value=kwargs[field], model=fk.get_model(), name=fk.get_name(),
                                                     safe=False))
            else:
                setattr(self, field, kwargs.get(field))

    @extras.check_init
    def __init__(self, **kwargs):
        """
        :param __safe: if it is True then call __safe__init__ if not thenn call __unsafe__init__ default value is True
        :param kwargs: gets parameters
        """
        assert self.__subclass__, "Model cannot be initialized directly, it should be subclass of Model to be used and initialized properly."
        # TODO: Check if the variable is suitable for variable
        inits = {
            True: self.__safe__init__,
            False: self.__unsafe__init
        }
        inits.get(kwargs.pop("__safe", True))(**kwargs)

    @extras.check_init
    def __init_subclass__(cls, **kwargs):
        metadata = {}
        for key, val in cls.__dict__.items():
            if isinstance(val, mssql_fields.field):
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
                _dict[field] = getattr(self, field) if isinstance(attr, Field.foreignKey) else attr

            return _dict
        elif depth >= 1:
            for field in fields:
                reference_field = getattr(self, field)
                if isinstance(reference_field, Field.foreignKey):
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

        return tuple(
            getattr(self, field).value if isinstance(getattr(self, field), Field.foreignKey) else getattr(self,
                                                                                                          field)
            for field in fields)

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
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, mssql_fields.field)]
            return (cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields, __safe=False))

    @classmethod
    @extras.check_init
    def get(cls, *args, **kwargs):
        # SELECT TOP 1 column_name FROM table_name
        if not kwargs and not args:
            raise ValueError("you must provide at least one key and one value")
        fields = kwargs.get("fields")

        if fields: del kwargs["fields"]

        cursor = connection.cursor()

        kwargs = " AND ".join([f"{mssql_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
        args = " ".join([str(arg) for arg in args])
        text = 'SELECT TOP 1 {fields} FROM {table} WHERE ({kwargs} {args})'.format(
            fields=str(f'{", ".join(fields)}' if fields else "*"),
            table="dbo." + cls.__name__,
            kwargs=kwargs,
            args=args)
        cursor.execute(text)
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, mssql_fields.field)]
            return (cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields, __safe=False))

        # raise NotImplementedError

    @classmethod
    @extras.check_init
    def where(cls, *args, **kwargs):
        if not kwargs and not args:
            raise ValueError("you must provide at least one key and one value")
        fields = kwargs.get("fields")

        if fields: del kwargs["fields"]

        cursor = connection.cursor()

        kwargs = " AND ".join([f"{mssql_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
        args = " ".join([str(arg) for arg in args])
        text = 'SELECT {fields} FROM {table} WHERE ({kwargs} {args})'.format(
            fields=str(f'{", ".join(fields)}' if fields else "*"),
            table="dbo." + cls.__name__,
            kwargs=kwargs,
            args=args)
        cursor.execute(text)
        objs = []
        for args in cursor:
            __fields__ = [name for name, value in vars(cls).items() if isinstance(value, mssql_fields.field)]
            objs.append(cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields, __safe=False))

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
            objs.append(cls(**{k: v for k, v in zip(__fields__, args)}, fields=fields, __safe=False))
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
class developers_models:
    class INFORMATION_SCHEMA_COLUMNS(Model):
        __name__ = "INFORMATION_SCHEMA.COLUMNS"
        __table_name__ = "INFORMATION_SCHEMA.COLUMNS"
        TABLE_CATALOG = mssql_fields.field(safe=False)
        TABLE_SCHEMA = mssql_fields.field(safe=False)

        TABLE_NAME = mssql_fields.field(safe=False)

        COLUMN_NAME = mssql_fields.field(safe=False)
        ORDINAL_POSITION = mssql_fields.field(safe=False)
        COLUMN_DEFAULT = mssql_fields.field(safe=False)
        IS_NULLABLE = mssql_fields.field(safe=False)
        DATA_TYPE = mssql_fields.field(safe=False)
        CHARACTER_MAXIMUM_LENGTH = mssql_fields.field(safe=False)

        CHARACTER_OCTET_LENGTH = mssql_fields.field(safe=False)
        NUMERIC_PRECISION = mssql_fields.field(safe=False)

        NUMERIC_PRECISION_RADIX = mssql_fields.field(safe=False)
        DATETIME_PRECISION = mssql_fields.field(safe=False)
        CHARACTER_SET_CATALOG = mssql_fields.field(safe=False)
        CHARACTER_SET_SCHEMA = mssql_fields.field(safe=False)
        CHARACTER_SET_NAME = mssql_fields.field(safe=False)
        COLLATION_CATALOG = mssql_fields.field(safe=False)
        COLLATION_SCHEMA = mssql_fields.field(safe=False)
        DOMAIN_CATALOG = mssql_fields.field(safe=False)
        DOMAIN_SCHEMA = mssql_fields.field(safe=False)
        DOMAIN_NAME = mssql_fields.field(safe=False)

        @classmethod
        @extras.check_init
        def get(cls, *args, **kwargs):
            if not kwargs and not args:
                raise ValueError("you must provide at least one key and one value")
            fields = kwargs.get("fields")

            if fields: del kwargs["fields"]

            cursor = connection.cursor()

            kwargs = " AND ".join([f"{mssql_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
            args = " ".join([str(arg) for arg in args])
            text = 'SELECT TOP 1 {fields} FROM {table} WHERE ({kwargs} {args})'.format(
                fields=str(f'{", ".join(fields)}' if fields else "*"),
                table="dbo." + "INFORMATION_SCHEMA.COLUMNS",
                kwargs=kwargs,
                args=args)
            cursor.execute(text)
            for args in cursor:
                __fields__ = [name for name, value in vars(cls).items() if isinstance(value, mssql_fields.field)]
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

            kwargs = " AND ".join([f"{mssql_fields.field.find_filter(key, value)}" for key, value in kwargs.items()])
            args = " ".join([str(arg) for arg in args])
            text = 'SELECT {fields} FROM {table} WHERE ({kwargs} {args})'.format(
                fields=str(f'{", ".join(fields)}' if fields else "*"),
                table="dbo." + "INFORMATION_SCHEMA.COLUMNS",
                kwargs=kwargs,
                args=args)
            cursor.execute(text)
            objs = []
            for args in cursor:
                __fields__ = [name for name, value in vars(cls).items() if isinstance(value, mssql_fields.field)]
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


if __name__ == '__main__':
    print()
    for k, v in Field.__dict__.items():

        try:
            if issubclass(v, field):
                print(f"Field.{k}(\n")
        except:
            pass
