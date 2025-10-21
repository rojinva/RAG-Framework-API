class AlreadyExistsError(Exception):
    """Custom exception raised when a resource already exists."""
    pass

class NotFoundError(Exception):
    """Custom exception raised when a resource is not found."""
    pass

class NoAccessError(Exception):
    """Custom exception raised when a user does not have access to a resource."""
    pass
