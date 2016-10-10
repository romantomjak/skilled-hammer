class HammerException(Exception):
    """Base exception."""


class SuspiciousOperation(HammerException):
    """Suspicious HTTP request is detected."""


class UnknownRepository(HammerException):
    """Requested repository has not been added to repositories.conf."""


class MissingSecret(HammerException):
    """Environment variable HAMMER_SECRET has not been defined."""
