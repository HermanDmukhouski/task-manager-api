class DomainError(Exception):
    pass


class InvalidEmailError(DomainError):
    pass


class EmptyNameError(DomainError):
    pass


class EmptyTitleError(DomainError):
    pass


class InvalidTaskStatusError(DomainError):
    pass
