# exceptions.py
class APIError(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message):
        super().__init__(message)
