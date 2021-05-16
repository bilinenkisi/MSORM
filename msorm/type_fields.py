import inspect
from builtins import *
from functools import lru_cache

__filters__ = {
    "gt": ">",
    "gte": ">=",
    "not": "!=",
    "lt": "<",
    "lte": "<=",
    "like": " LIKE ",
    "in": " IN ",
    "not_in": " NOT IN "
}
__filtersf__ = {
    "gt": lambda value: f"'{value}'",
    "gte": lambda value: f"'{value}'",
    "not": lambda value: f"'{value}'",
    "lt": lambda value: f"'{value}'",
    "lte": lambda value: f"'{value}'",
    "like": lambda value: f"'{value}'",
    "in": lambda value: f"""({",".join(tuple(f"'{i}'" for i in value))})""",
    "not_in": lambda value: f"""({",".join(tuple(f"'{i}'" for i in value))})"""
}


class field:
    @staticmethod
    def find_filter(field, value):
        filed_args = field.split("__")
        lenght = len(filed_args)
        if  lenght > 2:
            raise ValueError(f"{field} field cannot be found in the Model")
        name = filed_args.pop(0)
        for item in filed_args:
            filter = __filters__.get(item)
            if filter:
                return name + filter + __filtersf__[item](value)
        return name + "=" + f"'{value}'"

    type = None

    # def __init__(self, value=None):
    #     self.__value = value
    def __init__(self, value=None):
        self.value = value
        # print(self.__value,self.__class__,"ok")

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        if val:
            self.__value = self.type(val)
        else:
            self.__value = val

    @classmethod
    def get_new(cls, *args, **kwargs):
        # print(cls,"yepp",args,kwargs)
        # print("salık")
        new_field = cls(*args, **kwargs)
        return new_field

    def __str__(self):
        return str(self.__value)
    # def __new__(cls,*args,**kwargs):
    #     return super(cls.__class__, cls).__new__(cls, *args, **kwargs)
    #
    #     return cls(*args,**kwargs)


class foreignKey(field):
    type = int

    def __init__(self, model, value=None, name=None):
        # model,value=None, name=None
        self.__model = model
        self.__name = name
        self.__value = value
        super(foreignKey, self).__init__(value)

    def get_model(self):
        #         # print(self.__model,"salam")
        return self.__model

    def get_name(self):
        return self.__name

    @property
    @lru_cache()
    def model(self):
        if inspect.isclass(type(self.__model)):
            # print(self.__model,"sekis")
            self.__model = \
                self.__model.where(**{self.__name if self.__name else self.__model.__class__.__name__: self.__value})[
                    0]
        return self.__model


class nvarchar(field):
    type = str


class number(field):
    type = int

    def __mul__(self, other):
        other = int(str(other))

        return self.__dict__.get("_field__value") * other


class bit(field):
    type = bool


class double(field):
    type = float

class Fields:
    # TODO: Add all data types from MSSQL
    @staticmethod
    def str(*args, **kwargs):
        return nvarchar(*args, **kwargs)

    @staticmethod
    def int(*args, **kwargs):
        return number(*args, **kwargs)

    @staticmethod
    def float(*args, **kwargs):
        return double(*args, **kwargs)

    @staticmethod
    def bool(*args, **kwargs):
        return bit(*args, **kwargs)

    @staticmethod
    def foreignKey(*args, **kwargs):
        return foreignKey(*args, **kwargs)

