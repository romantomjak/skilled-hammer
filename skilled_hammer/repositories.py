from skilled_hammer import exceptions

try:
    import configparser
except:
    import ConfigParser as configparser  # Python 2

parser = configparser.ConfigParser()


def load():
    """
    Attempts to load repository configuration
    """
    try:
        repositories = {}
        parser.read("conf/repositories.conf")
        for section in parser.sections():
            data = {
                'name': section,
                'directory': parser.get(section, 'directory'),
                'command': parser.get(section, 'command', fallback=None),
                'origin': parser.get(section, 'origin'),
            }
            repositories[data['origin']] = data
        return repositories
    except configparser.NoOptionError as e:
        print("Missing required option '{0}' in '{1}' repo".format(e.args[0], e.args[1]))
    except configparser.Error as e:
        print(e.message)
    exit(1)


def repo_url_from_payload(payload):
    """
    Validates payload and returns repo url depending on where it's hosted
    """
    if not payload:
        raise exceptions.SuspiciousOperation("Invalid payload")

    if 'repository' in payload:
        # github
        if 'url' in payload['repository']:
            return payload['repository']['url']
        # bitbucket
        if 'links' in payload['repository']\
                and 'html' in payload['repository']['links']\
                and 'href' in payload['repository']['links']['html']:
            return payload['repository']['links']['html']['href']

    raise exceptions.SuspiciousOperation("Invalid payload")
