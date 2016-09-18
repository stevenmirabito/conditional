from functools import wraps
from flask import g, abort
from conditional import ldap


def restrict_intro_member(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not ldap.is_intromember(g.userinfo['uuid']):
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def restrict_eboard(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not ldap.is_eboard(g.userinfo['uuid']):
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def restrict_evals(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not ldap.is_eval_director(g.userinfo['uuid']):
            abort(403)

        return func(*args, **kwargs)

    return decorated_function


def restrict_evals_or_financial(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not ldap.is_eval_director(g.userinfo['uuid']) and not ldap.is_financial_director(g.userinfo['uuid']):
            abort(403)

        return func(*args, **kwargs)

    return decorated_function
