class HammerException(Exception):
    """Base exception."""


class MissingOptionError(HammerException):
    """Occurs when a particular configuration file section is missing an option."""


class ConfigurationSyntaxError(HammerException):
    """Occurs when configuration file has invalid syntax."""


class SuspiciousOperation(HammerException):
    """Occurs when a suspicious HTTP request is detected."""


class UnknownRepository(HammerException):
    """Occurs when a repository has not been added to hammer.conf."""
