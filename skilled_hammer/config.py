try:
    import configparser
except:
    import ConfigParser as configparser  # Python 2

from . import exceptions

parser = configparser.ConfigParser()


def load(file="repositories.conf"):
    """
    Attempts to load repository configuration
    """
    try:
        repositories = {}
        parser.read(file)
        for section in parser.sections():
            data = {
                'directory': parser.get(section, 'directory'),
                'command': parser.get(section, 'command', fallback=None),
                'origin': parser.get(section, 'origin'),
            }
            repositories[data['origin']] = data
        return repositories
    except configparser.NoOptionError as e:
        raise exceptions.MissingOptionError("Missing required option '{0}' in '{1}' repo".format(e.args[0], e.args[1]))
    except configparser.Error as e:
        raise exceptions.ConfigurationSyntaxError(e.message)
