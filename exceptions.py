class HammerException(Exception):
    """Base exception."""


class MissingOptionError(HammerException):
    """Occurs when a particular configuration file section is missing an option."""


class ConfigurationSyntaxError(HammerException):
    """Occurs when configuration file has invalid syntax."""
