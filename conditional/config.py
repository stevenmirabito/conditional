import os
import json

VERSION = "1.5.0"

STATIC_MANIFEST = {
    "/static/app.js": "/static/app.js",
    "/static/css/app.scss": "/static/css/app.css",
    "/static/css/presentations.scss": "/static/css/presentations.css",
}

# Load static asset manifest, if available
manifest_path = os.path.join(os.path.dirname(__file__), 'static', 'manifest.json')
if os.path.isfile(manifest_path):
    with open(manifest_path) as manifest_file:
        STATIC_MANIFEST = json.load(manifest_file)


class Config(object):
    # Flask config
    DEBUG = os.environ.get("CONDITIONAL_DEBUG", "false").lower() == "true"
    APP_NAME = "conditional"
    STATIC_MANIFEST = STATIC_MANIFEST

    # LDAP config
    LDAP_RO = os.environ.get("CONDITIONAL_LDAP_RO", "true").lower() == "true"
    LDAP_BIND_DN = os.environ.get("CONDITIONAL_LDAP_BIND_DN", "")
    LDAP_BIND_PW = os.environ.get("CONDITIONAL_LDAP_BIND_PASSWORD", "")

    # Sentry config
    # Do not set the DSN for local development
    SENTRY_CONFIG = {
        "dsn": os.environ.get("CONDITIONAL_SENTRY_DSN", ""),
        "release": VERSION,
    }

    # Database config
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}/{}".format(
        os.environ.get("CONDITIONAL_DB_DIALECT", "postgresql"),
        os.environ.get("CONDITIONAL_DB_USER", "conditional"),
        os.environ.get("CONDITIONAL_DB_PASSWORD", ""),
        os.environ.get("CONDITIONAL_DB_HOSTNAME", "postgres.csh.rit.edu"),
        os.environ.get("CONDITIONAL_DB_NAME", "conditional"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ZOO_DATABASE_URI = os.environ.get("ZOO_DATABASE_URI", None)
