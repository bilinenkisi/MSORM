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

__reserved_keys__ = \
[
 'INNER',
 'ROLLBACK',
 'TRIGGER',
 'REPLICATION',
 'SCHEMA',
 'TRANSACTION',
 'DISTINCT',
 'RAISERROR',
 'PLAN',
 'RIGHT',
 'SHUTDOWN',
 'UNION',
 'VIEW',
 'STATISTICS',
 'DELETE',
 'TABLE',
 'FOR',
 'REVERT',
 'CURRENT_TIMESTAMP',
 'BREAK',
 'USE',
 'FREETEXTTABLE',
 'RETURN',
 'DBCC',
 'COLLATE',
 'EXEC',
 'AND',
 'PRINT',
 'IF',
 'READTEXT',
 'READ',
 'TRAN',
 'DOUBLE',
 'PRECISION',
 'WAITFOR',
 'SESSION_USER',
 'LIKE',
 'NOCHECK',
 'NONCLUSTERED',
 'USER',
 'OPENROWSET',
 'CONTAINS',
 'EXTERNAL',
 'ADD',
 'LEFT',
 'SEMANTICSIMILARITYTABLE',
 'DENY',
 'OPTION',
 'IS',
 'OF',
 'PERCENT',
 'CHECKPOINT',
 'KILL',
 'HAVING',
 'BY',
 'DISK',
 'COMPUTE',
 'OR',
 'OVER',
 'THEN',
 'END',
 'FILE',
 'UNIQUE',
 'INTERSECT',
 'INTO',
 'IDENTITY_INSERT',
 'NULLIF',
 'DUMP',
 'SAVE',
 'BROWSE',
 'CURRENT_TIME',
 'WITH',
 'BEGIN',
 'CHECK',
 'CREATE',
 'CLUSTERED',
 'CURSOR',
 'CLOSE',
 'DATABASE',
 'OPENDATASOURCE',
 'PROCEDURE',
 'FETCH',
 'IDENTITYCOL',
 'LOAD',
 'INSERT',
 'TOP',
 'ROWGUIDCOL',
 'NATIONAL',
 'IN',
 'WHILE',
 'ANY',
 'COLUMN',
 'TEXTSIZE',
 'OPENXML',
 'CURRENT',
 'OPEN',
 'WRITETEXT',
 'REVOKE',
 'CONVERT',
 'NOT',
 'FULL',
 'PROC',
 'COMMIT',
 'ON',
 'FROM',
 'CROSS',
 'EXECUTE',
 'AUTHORIZATION',
 'OFF',
 'KEY',
 'SOME',
 'MERGE',
 'DEALLOCATE',
 'DECLARE',
 'FUNCTION',
 'ORDER',
 'ALL',
 'DISTRIBUTED',
 'RESTORE',
 'INDEX',
 'CASE',
 'GRANT',
 'SYSTEM_USER',
 'BETWEEN',
 'RECONFIGURE',
 'UPDATE',
 'ESCAPE',
 'RULE',
 'BACKUP',
 'EXCEPT',
 'AS',
 'TRY_CONVERT',
 'IDENTITY',
 'NULL',
 'VARYING',
 'FILLFACTOR',
 'CONTINUE',
 'EXIT',
 'BULK',
 'CONTAINSTABLE',
 'ROWCOUNT',
 'ALTER',
 'VALUES',
 'RESTRICT',
 'GROUP',
 'PRIMARY',
 'SELECT',
 'JOIN',
 'WITHIN GROUP',
 'SETUSER',
 'TABLESAMPLE',
 'SECURITYAUDIT',
 'TO',
 'GOTO',
 'CONSTRAINT',
 'ELSE',
 'ERRLVL',
 'EXISTS',
 'UNPIVOT',
 'DEFAULT',
 'SET',
 'LINENO',
 'OUTER',
 'SEMANTICKEYPHRASETABLE',
 'REFERENCES',
 'CASCADE',
 'PUBLIC',
 'OPENQUERY',
 'CURRENT_USER',
 'WHERE',
 'ASC',
 'OFFSETS',
 'TSEQUAL',
 'DROP',
 'FREETEXT',
 'HOLDLOCK',
 'DESC',
 'SEMANTICSIMILARITYDETAILSTABLE',
 'UPDATETEXT',
 'PIVOT',
 'WHEN',
 'COALESCE',
 'CURRENT_DATE',
 'TRUNCATE',
 'FOREIGN']
check_if_reserved = lambda key: f"[{key}]" if key.upper() in __reserved_keys__ else key
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
                return check_if_reserved(name) + filter + __filtersf__[item](value)
        return check_if_reserved(name) + "=" + f"'{value}'"
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
                return check_if_reserved(name) + filter + "?"
        return check_if_reserved(name) + "=" + "?"
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
