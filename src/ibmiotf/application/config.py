import uuid
from ibmiotf import ConfigurationException

# Support Python 2.7 and 3.4 versions of configparser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def ParseConfigFile(configFilePath):
    """
    Parse a standard application configuration file
    """
    parms = configparser.ConfigParser({
        "id": str(uuid.uuid4()),
        "domain": "internetofthings.ibmcloud.com",
        "port": "8883", # Even though this is a string here, the parms.getint method will ensure it's assigned as an int
        "type": "standalone",
        "clean-session": "true"
    })
    sectionHeader = "application"

    try:
        with open(configFilePath) as f:
            try:
                parms.read_file(f)
            except AttributeError:
                # Python 2.7 support
                # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read_file
                parms.readfp(f)

        domain = parms.get(sectionHeader, "domain")
        organization = parms.get(sectionHeader, "org")
        appId = parms.get(sectionHeader, "id")
        appType = parms.get(sectionHeader, "type")

        authKey = parms.get(sectionHeader, "auth-key")
        authToken = parms.get(sectionHeader, "auth-token")
        cleanSession = parms.get(sectionHeader, "clean-session")
        port = parms.getint(sectionHeader, "port")

    except IOError as e:
        reason = "Error reading application configuration file '%s' (%s)" % (configFilePath,e[1])
        raise ConfigurationException(reason)

    return {'domain': domain, 'org': organization, 'id': appId, 'auth-key': authKey, 'auth-token': authToken, 'type': appType, 'clean-session': cleanSession, 'port': int(port)}

