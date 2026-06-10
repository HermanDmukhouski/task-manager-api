class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class InvalidCursorError(ApplicationError):
    pass
