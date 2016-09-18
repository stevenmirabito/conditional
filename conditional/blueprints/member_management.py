import csv
import io
import uuid

from datetime import datetime

import structlog

from flask import Blueprint, request, jsonify, g

from conditional.models.models import FreshmanAccount
from conditional.models.models import FreshmanEvalData
from conditional.models.models import FreshmanCommitteeAttendance
from conditional.models.models import MemberCommitteeAttendance
from conditional.models.models import FreshmanSeminarAttendance
from conditional.models.models import MemberSeminarAttendance
from conditional.models.models import FreshmanHouseMeetingAttendance
from conditional.models.models import MemberHouseMeetingAttendance
from conditional.models.models import HouseMeeting
from conditional.models.models import EvalSettings
from conditional.models.models import OnFloorStatusAssigned
from conditional.models.models import SpringEval

from conditional.blueprints.cache_management import clear_active_members_cache
from conditional.blueprints.cache_management import clear_onfloor_members_cache

from conditional.util.flask import render_template
from conditional.util.auth import restrict_evals, restrict_evals_or_financial
from conditional.models.models import attendance_enum

from conditional import db, auth, ldap

logger = structlog.get_logger()

member_management_bp = Blueprint('member_management_bp', __name__)


def get_member_info():
    member_list = []
    number_onfloor = 0

    for member in ldap.get_current_students():
        uid = member['uid'][0].decode('utf-8')
        member_uuid = member['entryUUID'][0].decode('utf-8')

        name = ldap.get_name(member_uuid)
        active = ldap.is_active(member_uuid)
        onfloor = ldap.is_onfloor(member_uuid)
        room_number = ldap.get_room_number(member_uuid)
        room = room_number if room_number != "N/A" else ""
        hp = ldap.get_housing_points(member_uuid)
        member_list.append({
            "uid": uid,
            "name": name,
            "active": active,
            "onfloor": onfloor,
            "room": room,
            "hp": hp
        })

        if onfloor:
            number_onfloor += 1

    return member_list, number_onfloor


@member_management_bp.route('/manage')
@auth.oidc_auth
@restrict_evals_or_financial
def display_member_management():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display member management')

    member_list, onfloor_number = get_member_info()

    freshmen = FreshmanAccount.query
    freshmen_list = []

    for freshman_user in freshmen:
        freshmen_list.append({
            "id": freshman_user.id,
            "name": freshman_user.name,
            "onfloor": freshman_user.onfloor_status,
            "room": "" if freshman_user.room_number is None else freshman_user.room_number,
            "eval_date": freshman_user.eval_date
        })

    settings = EvalSettings.query.first()
    if settings:
        lockdown = settings.site_lockdown
        intro_form = settings.intro_form_active
    else:
        lockdown = False
        intro_form = False

    return render_template('member_management.html',
                           active=member_list,
                           num_current=len(member_list),
                           num_active=len(ldap.get_active_members()),
                           num_fresh=len(freshmen_list),
                           num_onfloor=onfloor_number,
                           freshmen=freshmen_list,
                           site_lockdown=lockdown,
                           intro_form=intro_form)


@member_management_bp.route('/manage/settings', methods=['PUT'])
@auth.oidc_auth
@restrict_evals
def member_management_eval():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='submit site settings')

    post_data = request.get_json()

    if 'siteLockdown' in post_data:
        logger.info('backend', action="changed site lockdown setting to %s" % post_data['siteLockdown'])
        EvalSettings.query.update(
            {
                'site_lockdown': post_data['siteLockdown']
            })

    if 'introForm' in post_data:
        logger.info('backend', action="changed intro form setting to %s" % post_data['introForm'])
        EvalSettings.query.update(
            {
                'intro_form_active': post_data['introForm']
            })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def member_management_adduser():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='add fid user')

    post_data = request.get_json()

    name = post_data['name']
    onfloor_status = post_data['onfloor']
    room_number = post_data['roomNumber']

    # empty room numbers should be NULL
    if room_number == "":
        room_number = None

    logger.info('backend', action="add f_%s as onfloor: %s with room_number: %s" % (name, onfloor_status, room_number))
    db.session.add(FreshmanAccount(name, onfloor_status, room_number))
    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user/upload', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def member_management_uploaduser():
    f = request.files['file']

    if not f:
        return "No file", 400

    try:
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)

        for new_user in csv_input:
            name = new_user[0]
            onfloor_status = new_user[1]

            if new_user[2]:
                room_number = new_user[2]
            else:
                room_number = None

            db.session.add(FreshmanAccount(name, onfloor_status, room_number))

        db.session.flush()
        db.session.commit()
        return jsonify({"success": True}), 200
    except csv.Error:
        return "file could not be processed", 400


@member_management_bp.route('/manage/user/<uid>', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def member_management_edituser(uid):
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='edit uid user')

    post_data = request.get_json()

    if not uid.isdigit():
        active_member = post_data['activeMember']

        if ldap.is_eval_director(g.userinfo['uuid']):
            logger.info('backend', action="edit %s room: %s onfloor: %s housepts %s" %
                                          (uid, post_data['roomNumber'], post_data['onfloorStatus'],
                                           post_data['housingPoints']))
            room_number = post_data['roomNumber']
            onfloor_status = post_data['onfloorStatus']
            housing_points = post_data['housingPoints']

            ldap.set_roomnumber(uid, room_number)
            if onfloor_status:
                ldap.add_member_to_group(uid, "onfloor")
            else:
                ldap.remove_member_from_group(uid, "onfloor")
            ldap.set_housingpoints(uid, housing_points)

        # Only update if there's a diff
        logger.info('backend', action="edit %s active: %s" % (uid, active_member))
        if ldap.is_active(uid) != active_member:
            if active_member:
                ldap.set_active(uid)
            else:
                ldap.set_inactive(uid)

            if active_member:
                db.session.add(SpringEval(uid))
            else:
                SpringEval.query.filter(
                    SpringEval.uid == uid and
                    SpringEval.active).update(
                    {
                        'active': False
                    })
            clear_active_members_cache()
    else:
        logger.info('backend', action="edit freshman account %s room: %s onfloor: %s eval_date: %s sig_missed %s" %
                                      (uid, post_data['roomNumber'], post_data['onfloorStatus'],
                                       post_data['evalDate'], post_data['sigMissed']))

        name = post_data['name']

        if post_data['roomNumber'] == "":
            room_number = None
        else:
            room_number = post_data['roomNumber']

        onfloor_status = post_data['onfloorStatus']
        eval_date = post_data['evalDate']

        if post_data['sigMissed'] == "":
            sig_missed = None
        else:
            sig_missed = post_data['sigMissed']

        FreshmanAccount.query.filter(FreshmanAccount.id == uid).update({
            'name': name,
            'eval_date': datetime.strptime(eval_date, "%Y-%m-%d"),
            'onfloor_status': onfloor_status,
            'room_number': room_number,
            'signatures_missed': sig_missed
        })

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/user/<uid>', methods=['GET'])
@auth.oidc_auth
@restrict_evals_or_financial
def member_management_getuserinfo(uid):
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='retrieve user info')

    acct = None
    if uid.isnumeric():
        acct = FreshmanAccount.query.filter(
            FreshmanAccount.id == uid).first()

    # missed hm
    def get_hm_date(hm_id):
        return HouseMeeting.query.filter(
            HouseMeeting.id == hm_id). \
            first().date.strftime("%Y-%m-%d")

    # if fid
    if acct:
        missed_hm = [
            {
                'date': get_hm_date(hma.meeting_id),
                'id': hma.meeting_id,
                'excuse': hma.excuse,
                'status': hma.attendance_status
            } for hma in FreshmanHouseMeetingAttendance.query.filter(
                FreshmanHouseMeetingAttendance.fid == acct.id and
                (FreshmanHouseMeetingAttendance.attendance_status != attendance_enum.Attended))]

        hms_missed = []
        for hm in missed_hm:
            if hm['status'] != "Attended":
                hms_missed.append(hm)

        return jsonify(
            {
                'id': acct.id,
                'name': acct.name,
                'eval_date': acct.eval_date.strftime("%Y-%m-%d"),
                'missed_hm': hms_missed,
                'onfloor_status': acct.onfloor_status,
                'room_number': acct.room_number,
                'sig_missed': acct.signatures_missed
            }), 200

    if ldap.is_eval_director(g.userinfo['uuid']):
        missed_hm = [
            {
                'date': get_hm_date(hma.meeting_id),
                'id': hma.meeting_id,
                'excuse': hma.excuse,
                'status': hma.attendance_status
            } for hma in MemberHouseMeetingAttendance.query.filter(
                MemberHouseMeetingAttendance.uid == uid and
                (MemberHouseMeetingAttendance.attendance_status != attendance_enum.Attended))]

        hms_missed = []
        for hm in missed_hm:
            if hm['status'] != "Attended":
                hms_missed.append(hm)
        return jsonify(
            {
                'name': ldap.get_name(uid),
                'room_number': ldap.get_room_number(uid),
                'onfloor_status': ldap.is_onfloor(uid),
                'housing_points': ldap.get_housing_points(uid),
                'active_member': ldap.is_active(uid),
                'missed_hm': hms_missed,
                'user': 'eval'
            }), 200
    else:
        return jsonify(
            {
                'name': ldap.get_name(uid),
                'active_member': ldap.is_active(uid),
                'user': 'financial'
            }), 200


@member_management_bp.route('/manage/user/<fid>', methods=['DELETE'])
@auth.oidc_auth
@restrict_evals
def member_management_deleteuser(fid):
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='edit fid user')

    if not fid.isdigit():
        return "can only delete freshman accounts", 400

    logger.info('backend', action="delete freshman account %s" % fid)

    for fca in FreshmanCommitteeAttendance.query.filter(FreshmanCommitteeAttendance.fid == fid):
        db.session.delete(fca)

    for fts in FreshmanSeminarAttendance.query.filter(FreshmanSeminarAttendance.fid == fid):
        db.session.delete(fts)

    for fhm in FreshmanHouseMeetingAttendance.query.filter(FreshmanHouseMeetingAttendance.fid == fid):
        db.session.delete(fhm)

    FreshmanAccount.query.filter(FreshmanAccount.id == fid).delete()

    db.session.flush()
    db.session.commit()
    return jsonify({"success": True}), 200


@member_management_bp.route('/manage/upgrade_user', methods=['POST'])
@auth.oidc_auth
@restrict_evals
def member_management_upgrade_user():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('api', action='convert fid to uid entry')

    post_data = request.get_json()

    fid = post_data['fid']
    uid = post_data['uid']
    signatures_missed = post_data['sigsMissed']

    logger.info('backend', action="upgrade freshman-%s to %s sigsMissed: %s" %
                                  (fid, uid, signatures_missed))
    acct = FreshmanAccount.query.filter(
        FreshmanAccount.id == fid).first()

    new_acct = FreshmanEvalData(uid, signatures_missed)
    new_acct.eval_date = acct.eval_date

    db.session.add(new_acct)
    for fca in FreshmanCommitteeAttendance.query.filter(FreshmanCommitteeAttendance.fid == fid):
        db.session.add(MemberCommitteeAttendance(uid, fca.meeting_id))
        # XXX this might fail horribly #yoloswag
        db.session.delete(fca)

    for fts in FreshmanSeminarAttendance.query.filter(FreshmanSeminarAttendance.fid == fid):
        db.session.add(MemberSeminarAttendance(uid, fts.seminar_id))
        # XXX this might fail horribly #yoloswag
        db.session.delete(fts)

    for fhm in FreshmanHouseMeetingAttendance.query.filter(FreshmanHouseMeetingAttendance.fid == fid):
        db.session.add(MemberHouseMeetingAttendance(
            uid, fhm.meeting_id, fhm.excuse, fhm.attendance_status))
        # XXX this might fail horribly #yoloswag
        db.session.delete(fhm)

    if acct.onfloor_status:
        db.session.add(OnFloorStatusAssigned(uid, datetime.now()))

    if acct.room_number:
        ldap.set_roomnumber(uid, acct.room_number)

    # XXX this might fail horribly #yoloswag
    db.session.delete(acct)

    db.session.flush()
    db.session.commit()

    clear_onfloor_members_cache()

    return jsonify({"success": True}), 200
