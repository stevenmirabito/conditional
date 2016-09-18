import uuid

from datetime import datetime

import structlog

from flask import Blueprint, request, jsonify, g

from conditional.util.flask import render_template
from conditional.util.auth import restrict_evals

from conditional.models.models import Conditional

from conditional import db, auth, ldap

conditionals_bp = Blueprint('conditionals_bp', __name__)

logger = structlog.get_logger()


@conditionals_bp.route('/conditionals/')
@auth.oidc_auth
def display_conditionals():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display conditional listing page')

    conditionals = [
        {
            'name': ldap.get_name(c.uid),
            'date_created': c.date_created,
            'date_due': c.date_due,
            'description': c.description,
            'id': c.id
        } for c in
        Conditional.query.filter(
            Conditional.status == "Pending")]

    return render_template('conditional.html',
                           conditionals=conditionals,
                           conditionals_len=len(conditionals))


@conditionals_bp.route('/conditionals/create', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def create_conditional():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='create new conditional')

    post_data = request.get_json()

    uid = post_data['uid']
    description = post_data['description']
    due_date = datetime.strptime(post_data['dueDate'], "%Y-%m-%d")

    db.session.add(Conditional(uid, description, due_date))
    db.session.flush()
    db.session.commit()

    return jsonify({"success": True}), 200


@conditionals_bp.route('/conditionals/review', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def conditional_review():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='review a conditional')

    post_data = request.get_json()
    cid = post_data['id']
    status = post_data['status']

    logger.info(action="updated conditional-%s to %s" % (cid, status))
    Conditional.query.filter(
        Conditional.id == cid). \
        update(
        {
            'status': status
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@conditionals_bp.route('/conditionals/delete/<cid>', methods=['DELETE'])
@auth.oidc_auth
@restrict_evals
def conditional_delete(cid):
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='delete conditional')

    Conditional.query.filter(
        Conditional.id == cid
    ).delete()
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
