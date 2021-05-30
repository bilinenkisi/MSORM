# region Exceptions
class BaseException(Exception): pass


class NotInitializedError(BaseException):
    """:raise when models not initialized"""


class ItemNotFoundException(BaseException):
    """:raise when item not found"""


# endregion

# region Warnings
class BaseWarning(UserWarning): pass


class NotSafeWarning(BaseWarning):
    """NotImplemented"""
class DeveloperToolsWarning(BaseWarning):
    """:warn when user attempts to use developer tools or variables"""
# endregion
