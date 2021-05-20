class BaseException(Exception):pass
class BaseWarning(UserWarning): pass
class NotSafeWarning(BaseWarning):
    """NotImplemented"""
class NotInitializedError(BaseException):
    """:raise when models not initialized"""
class ItemNotFound(BaseException):
    """:raise when item not found"""