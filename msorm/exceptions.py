class BaseException(Exception):pass
class NotInitializedError(BaseException):
    """:raise when models not initialized"""