import json
import uuid

from datetime import datetime

import structlog

from flask import Blueprint, jsonify, request, g

from conditional.util.flask import render_template
from conditional.util.auth import restrict_evals
from conditional.blueprints.intro_evals import display_intro_evals
from conditional.blueprints.spring_evals import display_spring_evals

from conditional.models.models import FreshmanEvalData
from conditional.models.models import SpringEval

from conditional import db, auth


logger = structlog.get_logger()

slideshow_bp = Blueprint('slideshow_bp', __name__)


@slideshow_bp.route('/slideshow/intro')
@auth.oidc_auth
@restrict_evals
def slideshow_intro_display():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display intro slideshow')

    return render_template('intro_eval_slideshow.html',
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=display_intro_evals(internal=True))


@slideshow_bp.route('/slideshow/intro/members')
@auth.oidc_auth
@restrict_evals
def slideshow_intro_members():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve intro members slideshow data')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_intro_evals(internal=True))


@slideshow_bp.route('/slideshow/intro/review', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def slideshow_intro_review():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit intro member evaluation')

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']

    logger.info("backend", action="submit intro eval for %s status: %s" % (uid, status))
    FreshmanEvalData.query.filter(
        FreshmanEvalData.uid == uid and
        FreshmanEvalData.active). \
        update(
        {
            'freshman_eval_result': status
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@slideshow_bp.route('/slideshow/spring')
@auth.oidc_auth
@restrict_evals
def slideshow_spring_display():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display membership evaluations slideshow')

    return render_template('spring_eval_slideshow.html',
                           date=datetime.now().strftime("%Y-%m-%d"),
                           members=display_spring_evals(internal=True))


@slideshow_bp.route('/slideshow/spring/members')
@auth.oidc_auth
@restrict_evals
def slideshow_spring_members():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retreive membership evaluations slideshow daat')

    # can't be jsonify because
    #   ValueError: dictionary update sequence element #0 has length 7; 2 is
    #   required
    return json.dumps(display_spring_evals(internal=True))


@slideshow_bp.route('/slideshow/spring/review', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def slideshow_spring_review():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit membership evaulation')

    post_data = request.get_json()
    uid = post_data['uid']
    status = post_data['status']
    # points = post_data['points']
    logger.info("backend", action="submit spring eval for %s status: %s" % (uid, status))

    SpringEval.query.filter(
        SpringEval.uid == uid and
        SpringEval.active). \
        update(
        {
            'status': status
        })

    # points are handeled automagically through constitutional override
    # HousingEvalsSubmission.query.filter(
    #    HousingEvalsSubmission.uid == uid and
    #    HousingEvalsSubmission.active).\
    #    update(
    #        {
    #            'points': points
    #        })

    # current_points = ldap_get_housing_points(uid)
    # ldap_set_housingpoints(uid, current_points + points)

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200
