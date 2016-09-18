import os

# Flask config
DEBUG = True
HOST_NAME = 'localhost'
SERVER_NAME = 'localhost:6969'
APP_NAME = 'conditional'
IP = '0.0.0.0'
PORT = 6969
SECRET_KEY = 'vdZzY5zua9jZu92Et7q4uNJB' # Change this!

# OpenID Connect SSO config
OIDC_ISSUER = 'https://sso.csh.rit.edu/auth/realms/csh'
OIDC_CLIENT_CONFIG = {
    'client_id': '',
    'client_secret': ''
}

# Local Development config (THESE OPTIONS SHOULD NEVER BE SET IN PRODUCTION!)
OIDC_REDIRECT_URI = 'http://localhost:3000/redirect_uri'
AUTH_OVERRIDES = {
    # This setting allows you to elevate permissions for certain users, useful for testing
    # functions only accessible to the evaluations director or other eboard members.
    # Format: '<entryUUID>': '<evals|financial|eboard>'
    ""
}

# LDAP config
LDAP_RO = True
LDAP_URL = 'ldaps://ldap.csh.rit.edu:636/'
LDAP_BIND_DN = 'cn=conditional,ou=Apps,dc=csh,dc=rit,dc=edu'
LDAP_BIND_PW = ''
LDAP_USER_OU = 'ou=Users,dc=csh,dc=rit,dc=edu'
LDAP_GROUP_OU = 'ou=Groups,dc=csh,dc=rit,dc=edu'
LDAP_COMMITTEE_OU = 'ou=Committees,dc=csh,dc=rit,dc=edu'

# Database config
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(os.getcwd(), "data.db"))
SQLALCHEMY_TRACK_MODIFICATIONS = False
ZOO_DATABASE_URI = 'mysql+pymysql://user:pass@host/database'
