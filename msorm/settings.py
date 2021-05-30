import datetime
import sys

import pyodbc


class __MFL__:
    """mssql_field_limits"""
    # region exact numeric fields
    bit_max = 1
    bit_min = 0
    bigint_max = 9_223_372_036_854_775_807
    bigint_min = -bigint_max
    int_max = 2_147_483_647
    int_min = -int_max
    smallint_max = 32_767
    smallint_min = -smallint_max
    tinyint_max = 255
    tinyint_min = 0
    decimal_max = float("inf")
    decimal_min = -float("inf")
    numeric_max = float("inf")
    numeric_min = -float("inf")
    # TODO: Add support for money symbols and convertion
    money_max = 922_337_203_685_477.58
    money_min = -money_max
    smallmoney_max = 214_748.3647
    smallmoney_min = -smallmoney_max
    # endregion
    # region float and real

    float_max = real_max = float("inf")
    float_min = real_min = float("-inf")

    # endregion
    # region String types mostly
    char_max = 8000
    char_min = 1
    nchar_max = 4000
    nchar_min = 1
    varchar_max = 8000
    varchar_min = 1
    nvarchar_max = 4000
    nvarchar_min = 1
    text_max = 2_147_483_647
    text_min = 1
    ntext_max = 2_147_483_647
    ntext_min = 1

    # endregion
    # region binary
    # min and max depends on byte size
    binary_min = varbinary_min = 1
    binary_max = varbinary_max = 8000
    image_max = 2_147_483_647
    image_min = 1
    # endregion
    # region NotImplemented Types For Limits
    # date
    # datetime
    # smalldatetime

    # endregion


__type_based_equality = {
    "int": lambda min, max, value: min <= value <= max,
    "float": lambda min, max, value: min <= value <= max,
    "bool": lambda min, max, value: min <= value <= max,
    "str": lambda min, max, value: min <= len(value) <= max,
    "bytes": lambda min, max, value: min <= sys.getsizeof(value) <= max,
    "datetime": lambda min, max, value: True  # Not added yet

}


def _limit_check(value, data_type: str):
    min, max = getattr(__MFL__, data_type + "_min"), getattr(__MFL__, data_type + "_max")

    if __type_based_equality.get(type(value).__name__)(min, max, value):
        return value
    else:
        raise ValueError(f"value exceeds {data_type}_max value or least than {data_type}_min")


def _type_check(value, python_types: tuple):
    if isinstance(value, python_types):
        return value

    else:
        raise TypeError(f"Value must be {', '.join([i.__name__ for i in python_types])}")


class __MFA__:

    @staticmethod
    def bigint(value):
        return _limit_check(_type_check(value, (int,)), "bigint")

    @staticmethod
    def int(value):
        return _limit_check(_type_check(value, (int,)), "int")

    @staticmethod
    def smallint(value):
        return _limit_check(_type_check(value, (int,)), "smallint")

    @staticmethod
    def bit(value):
        return _limit_check(_type_check(value, (bool, int, float)), "bit")

    @staticmethod
    def tinyint(value):
        return _limit_check(_type_check(value, (int,)), "tinyint")

    @staticmethod
    def decimal(value):
        return _limit_check(_type_check(value, (float,)), "decimal")

    @staticmethod
    def numeric(value):
        return _limit_check(_type_check(value, (float,)), "numeric")

    @staticmethod
    def money(value):
        return _limit_check(_type_check(value, (float,)), "money")

    @staticmethod
    def smallmoney(value):
        return _limit_check(_type_check(value, (float,)), "smallmoney")

    @staticmethod
    def float(value):
        return _limit_check(_type_check(value, (float,)), "float")

    @staticmethod
    def real(value):
        return _limit_check(_type_check(value, (float,)), "real")

    @staticmethod
    def char(value):
        return _limit_check(_type_check(value, (str,)), "char")

    @staticmethod
    def nchar(value):
        return _limit_check(_type_check(value, (str,)), "nchar")

    @staticmethod
    def varchar(value):
        return _limit_check(_type_check(value, (str,)), "varchar")

    @staticmethod
    def nvarchar(value):
        return _limit_check(_type_check(value, (str,)), "nvarchar")

    @staticmethod
    def text(value):
        return _limit_check(_type_check(value, (str,)), "text")

    @staticmethod
    def ntext(value):
        return _limit_check(_type_check(value, (str,)), "ntext")

    @staticmethod
    def binary(value):
        return pyodbc.Binary(_limit_check(_type_check(value, (bytes,)), "binary"))

    @staticmethod
    def nbinary(value):
        return pyodbc.Binary(_limit_check(_type_check(value, (bytes,)), "nbinary"))

    @staticmethod
    def image(value):
        return pyodbc.Binary(_limit_check(_type_check(value, (bytes,)), "image"))

    @staticmethod
    def date(value):
        return _type_check(value, (datetime.date,))

    @staticmethod
    def datetime(value):
        return _type_check(value, (datetime.datetime,))

    @staticmethod
    def smalldatetime(value):
        return _type_check(value, (datetime.time,))


MDC = {
    "bit": __MFA__.bit,
    "bigint": __MFA__.bigint,
    "int": __MFA__.int,
    "smallint": __MFA__.smallint,
    "tinyint": __MFA__.tinyint,
    "decimal": __MFA__.decimal,
    "numeric": __MFA__.numeric,
    "money": __MFA__.money,
    "smallmoney": __MFA__.smallmoney,
    "float": __MFA__.float,
    "real": __MFA__.real,
    "char": __MFA__.char,
    "nchar": __MFA__.nchar,
    "varchar": __MFA__.varchar,
    "nvarchar": __MFA__.nvarchar,
    "text": __MFA__.text,
    "ntext": __MFA__.ntext,
    "binary": __MFA__.binary,
    "nbinary": __MFA__.nbinary,
    "image": __MFA__.image,
    "date": __MFA__.date,
    "datetime": __MFA__.datetime,
    "smalldatetime": __MFA__.smalldatetime,

}

