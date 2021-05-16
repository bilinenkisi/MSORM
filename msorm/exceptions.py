class BaseException(Exception):pass
class BaseWarning(UserWarning): pass
class NotSafeWarning(UserWarning):
    """NotImplemented"""
class NotInitializedError(BaseException):
    """:raise when models not initialized"""