import uuid
import structlog

from flask import Blueprint, request, jsonify, g

from conditional.models.models import MajorProject

from conditional.util.flask import render_template
from conditional.util.auth import restrict_evals

from conditional import db, auth, ldap


logger = structlog.get_logger()

major_project_bp = Blueprint('major_project_bp', __name__)


@major_project_bp.route('/major_project/')
@auth.oidc_auth
def display_major_project():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display major project form')

    major_projects = [
        {
            'username': p.uid,
            'name': ldap.get_name(ldap.get_uuid_for_uid(p.uid)),
            'proj_name': p.name,
            'status': p.status,
            'description': p.description,
            'id': p.id,
            'is_owner': bool(g.userinfo['preferred_username'] == p.uid)
        } for p in
        MajorProject.query]

    major_projects.reverse()
    major_projects_len = len(major_projects)
    # return names in 'first last (username)' format
    return render_template('major_project_submission.html',
                           major_projects=major_projects,
                           major_projects_len=major_projects_len)


@major_project_bp.route('/major_project/submit', methods=['POST'])
@auth.oidc_auth
def submit_major_project():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit major project')

    post_data = request.get_json()
    name = post_data['projectName']
    description = post_data['projectDescription']

    if name == "" or description == "":
        return jsonify({"success": False}), 400
    project = MajorProject(g.userinfo['preferred_username'], name, description)

    db.session.add(project)
    db.session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route('/major_project/review', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def major_project_review():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='review major project')

    post_data = request.get_json()
    pid = post_data['id']
    status = post_data['status']

    print(post_data)
    MajorProject.query.filter(
        MajorProject.id == pid). \
        update(
        {
            'status': status
        })
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route('/major_project/delete/<pid>', methods=['DELETE'])
@auth.oidc_auth
def major_project_delete(pid):
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='review major project')

    # get user data
    user_name = g.userinfo['preferred_username']
    major_project = MajorProject.query.filter(
        MajorProject.id == pid
    ).first()
    creator = major_project.uid

    if creator == user_name or ldap.is_eval_director(user_name):
        MajorProject.query.filter(
            MajorProject.id == pid
        ).delete()
        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200
    else:
        return "Must be project owner to delete!", 401
