import structlog

from conditional import auth, ldap

from conditional.util.auth import restrict_evals

from flask import Blueprint

logger = structlog.get_logger()
cache_bp = Blueprint('cache_bp', __name__)


@cache_bp.route('/clearcache')
@auth.oidc_auth
@restrict_evals
def clear_cache():
    logger.info('api', action='purge system cache')

    ldap.get_housing_points.cache_clear()
    ldap.get_active_members.cache_clear()
    ldap.get_intro_members.cache_clear()
    ldap.get_non_alumni_members.cache_clear()
    ldap.get_onfloor_members.cache_clear()
    ldap.get_current_students.cache_clear()
    ldap.get_name.cache_clear()
    return "cache cleared", 200


def clear_housing_points_cache():
    ldap.get_housing_points.cache_clear()


def clear_active_members_cache():
    ldap.get_active_members.cache_clear()


def clear_intro_members_cache():
    ldap.get_intro_members.cache_clear()


def clear_non_alumni_cache():
    ldap.get_non_alumni_members.cache_clear()


def clear_onfloor_members_cache():
    ldap.get_onfloor_members.cache_clear()


def clear_current_students_cache():
    ldap.get_current_students.cache_clear()


def clear_user_cache(username):
    ldap.get_name(username).cache_clear()
