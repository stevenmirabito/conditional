from urllib.parse import quote
from flask import g, url_for
from flask import render_template as flask_render_template
from conditional.models.models import EvalSettings

from conditional import db, auth, ldap


def render_template(template_name, **kwargs):
    username = g.userinfo['preferred_username']
    display_name = g.userinfo['name']

    if EvalSettings.query.first() is None:
        db.session.add(EvalSettings())
        db.session.flush()
        db.session.commit()

    logout_url = auth.client.end_session_endpoint + '?redirect_uri=' + quote(url_for('default_route', _external=True))

    lockdown = EvalSettings.query.first().site_lockdown
    is_eboard = ldap.is_eboard(username)
    is_financial = ldap.is_financial_director(username)
    is_eval = ldap.is_eval_director(username)
    is_intromember = ldap.is_intromember(username)

    if is_eval:
        lockdown = False

    return flask_render_template(
        template_name,
        username=username,
        display_name=display_name,
        logout_url=logout_url,
        lockdown=lockdown,
        is_eboard=is_eboard,
        is_eval_director=is_eval,
        is_financial_director=is_financial,
        is_intromember=is_intromember,
        **kwargs)
