import warnings

from msorm import settings
from msorm.exceptions import DeveloperToolsWarning

warnings.filterwarnings("once", category=DeveloperToolsWarning)

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
    __sub_instance__ = False
    __field__ = "field"  # name of field
    __properties__ = {"default": None,
                      "null": True}

    @staticmethod
    def find_filter(field, value):
        filed_args = field.split("__")
        lenght = len(filed_args)
        if lenght > 2:
            raise ValueError(f"{field} field cannot be found in the Model")
        name = filed_args.pop(0)
        for item in filed_args:
            filter = __filters__.get(item)
            if filter:
                return name + filter + __filtersf__[item](value)
        return name + "=" + f"'{value}'"
    @staticmethod
    def n_find_filter(field, value):
        filed_args = field.split("__")
        lenght = len(filed_args)
        if lenght > 2:
            raise ValueError(f"{field} field cannot be found in the Model")
        name = filed_args.pop(0)
        for item in filed_args:
            filter = __filters__.get(item)
            if filter:
                return name + filter + "?"
        return name + "=" + "?"
    def __init__(self, default=None, safe=True, null=True):
        if not self.__sub_instance__ and safe:
            warnings.warn("DO NOT FORGET, USING DIRECT field CLASS IS NOT SUITABLE FOR NORMAL USAGE",
                          DeveloperToolsWarning)

        self.value = default
        self.null = null
        self.__properties__["null"] = null
        if default and safe:
            self.__properties__["default"] = self.value = settings.MDC.get(self.__field__, self.__developer_field_produce)(default)

    def __init_subclass__(cls, **kwargs):
        cls.__sub_instance__ = True

    @property
    def value(self):

        return self.__value

    @value.setter
    def value(self, val):

        self.__value = val

    @classmethod
    def get_new(cls, *args, **kwargs):
        new_field = cls(*args, **kwargs)
        return new_field

    def __developer_field_produce(self, val):
        warnings.warn("DO NOT FORGET, USING DIRECT field CLASS IS NOT SUITABLE FOR NORMAL USAGE",
                      DeveloperToolsWarning)
        return val

    def produce(self, val, field="field"):
        if val is None and self.null:
            return val

        return settings.MDC.get(self.__field__, self.__developer_field_produce)(val, field)

    def __str__(self):
        return str(self.__value)
