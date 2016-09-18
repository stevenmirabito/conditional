import uuid
import structlog

from flask import Blueprint, g

from conditional import auth, ldap

from conditional.models.models import FreshmanEvalData
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import TechnicalSeminar
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import MajorProject
from conditional.models.models import Conditional
from conditional.models.models import HouseMeeting
from conditional.models.models import CommitteeMeeting

from conditional.util.housing import get_queue_length, get_queue_position
from conditional.util.flask import render_template

logger = structlog.get_logger()

dashboard_bp = Blueprint('dashboard_bp', __name__)


def get_freshman_data(user_id):
    freshman = {}
    freshman_data = FreshmanEvalData.query.filter(FreshmanEvalData.uid == user_id).first()

    freshman['status'] = freshman_data.freshman_eval_result
    # number of committee meetings attended
    c_meetings = [m.meeting_id for m in
                  MemberCommitteeAttendance.query.filter(
                      MemberCommitteeAttendance.uid == user_id
                  )]
    freshman['committee_meetings'] = len(c_meetings)
    # technical seminar total
    t_seminars = [s.seminar_id for s in
                  MemberSeminarAttendance.query.filter(
                      MemberSeminarAttendance.uid == user_id
                  )]
    freshman['ts_total'] = len(t_seminars)
    attendance = [m.name for m in TechnicalSeminar.query.filter(
        TechnicalSeminar.id.in_(t_seminars)
    )]

    freshman['ts_list'] = attendance

    h_meetings = [(m.meeting_id, m.attendance_status) for m in
                  MemberHouseMeetingAttendance.query.filter(
                      MemberHouseMeetingAttendance.uid == user_id)]
    freshman['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])
    freshman['social_events'] = freshman_data.social_events
    freshman['general_comments'] = freshman_data.other_notes
    freshman['fresh_proj'] = freshman_data.freshman_project
    freshman['sig_missed'] = freshman_data.signatures_missed
    freshman['eval_date'] = freshman_data.eval_date
    return freshman


def is_voting_member(uid, active, intro_member):
    if intro_member:
        # Check to see if they've passed their intro evaluation
        eval_data = FreshmanEvalData.query.filter(
                FreshmanEvalData.uid == uid
        ).first()

        if eval_data.freshman_eval_result:
            return True
    else:
        # Upperclassmen, check to see if they're active
        return active


@dashboard_bp.route('/dashboard/')
@auth.oidc_auth
def display_dashboard():
    member_uuid = g.userinfo['uuid']
    user_id = g.userinfo['preferred_username']

    log = logger.new(user_id=member_uuid,
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display dashboard')

    data = dict()

    # freshman shit
    if ldap.is_intromember(user_id):
        data['freshman'] = get_freshman_data(user_id)
    else:
        data['freshman'] = False

    # Member Status
    data['active'] = ldap.is_active(member_uuid)
    # On-Floor Status
    data['onfloor'] = ldap.is_onfloor(member_uuid)
    # Voting Status
    data['voting'] = is_voting_member(user_id, data['active'], data['freshman'])

    # freshman shit
    if ldap.is_intromember(user_id):
        data['freshman'] = get_freshman_data(user_id)
    else:
        data['freshman'] = False

    spring = {}
    c_meetings = [m.meeting_id for m in
                  MemberCommitteeAttendance.query.filter(
                      MemberCommitteeAttendance.uid == user_id
                  )]
    spring['committee_meetings'] = len(c_meetings)
    h_meetings = [(m.meeting_id, m.attendance_status) for m in
                  MemberHouseMeetingAttendance.query.filter(
                      MemberHouseMeetingAttendance.uid == user_id)]
    spring['hm_missed'] = len([h for h in h_meetings if h[1] == "Absent"])

    data['spring'] = spring

    # only show housing if member has onfloor status
    if ldap.is_onfloor(user_id):
        housing = dict()
        housing['points'] = ldap.get_housing_points(user_id)
        housing['room'] = ldap.get_room_number(user_id)
        if housing['room'] == "N/A":
            housing['queue_pos'] = "%s / %s" % (get_queue_position(user_id), get_queue_length())
        else:
            housing['queue_pos'] = "N/A"
    else:
        housing = None

    data['housing'] = housing

    data['major_projects'] = [
        {
            'id': p.id,
            'name': p.name,
            'status': p.status,
            'description': p.description
        } for p in
        MajorProject.query.filter(MajorProject.uid == user_id)]

    data['major_projects_count'] = len(data['major_projects'])

    spring['mp_status'] = "Failed"
    for mp in data['major_projects']:
        if mp['status'] == "Pending":
            spring['mp_status'] = 'Pending'
            continue
        if mp['status'] == "Passed":
            spring['mp_status'] = 'Passed'
            break

    conditionals = [
        {
            'date_created': c.date_created,
            'date_due': c.date_due,
            'description': c.description,
            'status': c.status
        } for c in
        Conditional.query.filter(Conditional.uid == user_id)]
    data['conditionals'] = conditionals
    data['conditionals_len'] = len(conditionals)

    cm_attendance = [
        {
            'type': m.committee,
            'datetime': m.timestamp.date()
        } for m in CommitteeMeeting.query.filter(
            CommitteeMeeting.id.in_(c_meetings)
        )]

    hm_attendance = [
        {
            'reason': m.excuse,
            'datetime': HouseMeeting.query.filter(
                HouseMeeting.id == m.meeting_id).first().date
        } for m in
        MemberHouseMeetingAttendance.query.filter(
            MemberHouseMeetingAttendance.uid == user_id
        ).filter(MemberHouseMeetingAttendance.attendance_status == "Absent")]

    data['cm_attendance'] = cm_attendance
    data['cm_attendance_len'] = len(cm_attendance)
    data['hm_attendance'] = hm_attendance
    data['hm_attendance_len'] = len(hm_attendance)

    return render_template('dashboard.html', **data)
