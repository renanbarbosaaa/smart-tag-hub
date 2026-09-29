class DomainError(Exception):
    pass


class InvalidUrlError(DomainError):
    pass


class InvalidSlugError(DomainError):
    pass


class SlugAlreadyExistsError(DomainError):
    pass


class SlugGenerationError(DomainError):
    pass