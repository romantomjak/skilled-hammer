class HammerException(Exception):
    """Base exception."""


class MissingOptionError(HammerException):
    """A particular configuration file section is missing an option."""


class ConfigurationSyntaxError(HammerException):
    """Configuration file has invalid syntax."""


class SuspiciousOperation(HammerException):
    """Suspicious HTTP request is detected."""


class UnknownRepository(HammerException):
    """Requested repository has not been added to repositories.conf."""
