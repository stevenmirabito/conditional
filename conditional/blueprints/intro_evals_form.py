import uuid
import structlog

from flask import Blueprint, request, jsonify, g

from conditional.models.models import FreshmanEvalData
from conditional.models.models import EvalSettings
from conditional.util.flask import render_template
from conditional.util.auth import restrict_intro_member

from conditional import db, auth

logger = structlog.get_logger()

intro_evals_form_bp = Blueprint('intro_evals_form_bp', __name__)


@intro_evals_form_bp.route('/intro_evals_form/')
@auth.oidc_auth
@restrict_intro_member
def display_intro_evals_form():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display intro evals form')

    eval_data = FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == g.userinfo['preferred_username']).first()

    is_open = EvalSettings.query.first().intro_form_active
    # return names in 'first last (username)' format
    return render_template('intro_evals_form.html',
                           social_events=eval_data.social_events,
                           other_notes=eval_data.other_notes,
                           is_open=is_open)


@intro_evals_form_bp.route('/intro_evals/submit', methods=['POST'])
@auth.oidc_auth
@restrict_intro_member
def submit_intro_evals():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit intro evals form')

    post_data = request.get_json()
    social_events = post_data['socialEvents']
    comments = post_data['comments']

    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == g.userinfo['preferred_username']). \
        update(
        {
            'social_events': social_events,
            'other_notes': comments
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
