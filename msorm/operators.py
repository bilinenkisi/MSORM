from msorm.type_fields import field

class __Operators__:
    def __init__(self):
        self.__value = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return self.value


class GT(__Operators__):
    def __init__(self, field: str, other: [str, int, float, field]):
        super(GT, self).__init__()
        self.value = f"{field}>'{other}'"


class GTE(__Operators__):
    def __init__(self, field: str, other: [str, int, float, field]):
        super(GTE, self).__init__()

        self.value = f"{field}>='{other}'"


class OR(__Operators__):
    def __init__(self, *others, **kwargs):
        self.others = others
        self.kwargs = kwargs
        super(OR, self).__init__()
        self.value = ""
        if others or kwargs:
            for other in others:
                self.value += f"{other.value} OR " if isinstance(other, __Operators__) else ""
            for key, value in kwargs.items():
                self.value += f"{field.find_filter(key, value)} OR "
            self.value = self.value[:-3]

    @classmethod
    def __from_values(cls, value, othervalue):
        new_or = cls()
        new_or.value = value + " OR " + othervalue
        return new_or
    @classmethod
    def __from_value(cls,value):
        new_or = cls()
        new_or.value = value
        return new_or
    def __or__(self, other):
        return self.__from_values(self.value,other.value)
    def __invert__(self):
        raise DeprecationWarning("Depcreated because of filter kwargs")
        values = ""
        if self.others or self.kwargs:
            for other in self.others:
                values += f"{other.value} OR " if isinstance(other, __Operators__) else ""
            for field, value in self.kwargs.items():
                # print(value,field)
                values += f"{field}!='{value}' OR "
            values = values[:-3]
        return self.__from_value(values)

class EQ(__Operators__):
    def __init__(self, field, value):
        super(EQ, self).__init__()
        self.value = f"{field}='{value}'"


class IN(__Operators__):
    def __init__(self, **fields):
        super(IN, self).__init__()
        self.value = ""
        for key, val in fields.items():
            if isinstance(val, (list, set, tuple)):
                self.value += f"""{key} IN ({",".join(['%s' % i for i in val])})"""
            else:
                raise TypeError(f"{key}'s value must be a list, set or tuple for IN operator")


