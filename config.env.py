import os

# Flask config
DEBUG = False
HOST_NAME = os.environ.get('CONDITIONAL_HOST_NAME', 'conditional.csh.rit.edu')
SERVER_NAME = os.environ.get('CONDITIONAL_SERVER_NAME', 'conditional.csh.rit.edu:443')
APP_NAME = os.environ.get('CONDITIONAL_APP_NAME', 'conditional')
IP = os.environ.get('CONDITIONAL_SERVER_IP', '0.0.0.0')
PORT = int(os.environ.get('CONDITIONAL_SERVER_PORT', 8080))
SECRET_KEY = os.environ.get('CONDITIONAL_SECRET_KEY', 'thisisntverysecure')

# OpenID Connect SSO config
OIDC_ISSUER = os.environ.get('CONDITIONAL_OIDC_ISSUER', 'https://sso.csh.rit.edu/auth/realms/csh')
OIDC_CLIENT_CONFIG = {
    'client_id': os.environ.get('CONDITIONAL_OIDC_CLIENT_ID', 'conditional'),
    'client_secret': os.environ.get('CONDITIONAL_OIDC_CLIENT_SECRET', '')
}

# LDAP config
LDAP_RO = False if os.environ.get('CONDITIONAL_LDAP_RO', 'true').lower() == 'false' else True
LDAP_URL = os.environ.get('CONDITIONAL_LDAP_URL', 'ldaps://ldap.csh.rit.edu:636/')
LDAP_BIND_DN = os.environ.get('CONDITIONAL_LDAP_BIND_DN', '')
LDAP_BIND_PW = os.environ.get('CONDITIONAL_LDAP_BIND_PW', '')
LDAP_USER_OU = os.environ.get('CONDITIONAL_LDAP_USER_OU', 'ou=Users,dc=csh,dc=rit,dc=edu')
LDAP_GROUP_OU = os.environ.get('CONDITIONAL_LDAP_GROUP_OU', 'ou=Groups,dc=csh,dc=rit,dc=edu')
LDAP_COMMITTEE_OU = os.environ.get('CONDITIONAL_LDAP_COMMITTEE_OU', 'ou=Committees,dc=csh,dc=rit,dc=edu')

# Database config
SQLALCHEMY_DATABASE_URI = os.environ.get('CONDITIONAL_DATABASE_URI', 'sqlite:///{}'.format(os.path.join(os.getcwd(), "data.db")))
SQLALCHEMY_TRACK_MODIFICATIONS = False

