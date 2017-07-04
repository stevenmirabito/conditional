import os
from pbr.version import VersionInfo

VERSION = VersionInfo("conditional").semantic_version().release_string()


class Config(object):
    # Flask config
    DEBUG = os.environ.get("CONDITIONAL_DEBUG", "false").lower() == "true"
    APP_NAME = "conditional"

    # LDAP config
    LDAP_RO = os.environ.get("CONDITIONAL_LDAP_RO", "true").lower() == "true"
    LDAP_BIND_DN = os.environ.get("CONDITIONAL_LDAP_BIND_DN", "")
    LDAP_BIND_PW = os.environ.get("CONDITIONAL_LDAP_BIND_PW", "")

    # Sentry config
    # Do not set the DSN for local development
    SENTRY_CONFIG = {
        "dsn": os.environ.get("CONDITIONAL_SENTRY_DSN", ""),
        "release": VERSION,
    }

    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get("CONDITIONAL_DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ZOO_DATABASE_URI = os.environ.get("ZOO_DATABASE_URI", None)
