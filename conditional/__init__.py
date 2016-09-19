import os
from flask import Flask
from flask import g, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from conditional.util.ldap import LDAP
import structlog
import requests

app = Flask(__name__)

if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))

auth_overrides = None
if 'AUTH_OVERRIDES' in app.config:
    auth_overrides = app.config['AUTH_OVERRIDES']

# Disable SSL certificate verification warning
requests.packages.urllib3.disable_warnings()

db = SQLAlchemy(app)
migrate = Migrate(app, db)
logger = structlog.get_logger()
ldap = LDAP(app.config['LDAP_RO'],
            app.config['LDAP_URL'],
            app.config['LDAP_BIND_DN'],
            app.config['LDAP_BIND_PW'],
            app.config['LDAP_USER_OU'],
            app.config['LDAP_GROUP_OU'],
            app.config['LDAP_COMMITTEE_OU'],
            auth_overrides)
auth = OIDCAuthentication(app,
                          issuer=app.config['OIDC_ISSUER'],
                          client_registration_info=app.config['OIDC_CLIENT_CONFIG'])

# Override redirect URI if specified in config. Fixes an issue when running behind the BrowserSync proxy.
if 'OIDC_REDIRECT_URI' in app.config:
    from oic.oic.message import RegistrationRequest

    auth.client_registration_info['redirect_uris'] = app.config['OIDC_REDIRECT_URI']
    auth.client.store_registration_info(RegistrationRequest(**auth.client_registration_info))

# pylint: disable=C0413,ungrouped-imports
from conditional.blueprints.dashboard import dashboard_bp
from conditional.blueprints.attendance import attendance_bp
from conditional.blueprints.major_project_submission import major_project_bp
from conditional.blueprints.intro_evals import intro_evals_bp
from conditional.blueprints.intro_evals_form import intro_evals_form_bp
from conditional.blueprints.housing import housing_bp
from conditional.blueprints.spring_evals import spring_evals_bp
from conditional.blueprints.conditional import conditionals_bp
from conditional.blueprints.member_management import member_management_bp
from conditional.blueprints.slideshow import slideshow_bp
from conditional.blueprints.cache_management import cache_bp

app.register_blueprint(dashboard_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(major_project_bp)
app.register_blueprint(intro_evals_bp)
app.register_blueprint(intro_evals_form_bp)
app.register_blueprint(housing_bp)
app.register_blueprint(spring_evals_bp)
app.register_blueprint(conditionals_bp)
app.register_blueprint(member_management_bp)
app.register_blueprint(slideshow_bp)
app.register_blueprint(cache_bp)

logger.info('conditional started')


@app.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


@app.route('/')
def default_route():
    return redirect('/dashboard/')


@app.cli.command()
def zoo():
    from conditional.models.migrate import free_the_zoo
    free_the_zoo(app.config['ZOO_DATABASE_URI'])
