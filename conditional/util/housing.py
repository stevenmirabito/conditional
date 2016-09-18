from functools import lru_cache
from conditional import ldap
from conditional.models import models


@lru_cache(maxsize=1024)
def get_housing_queue():
    ofm = [
        {
            'uid': m.uid,
            'time': m.onfloor_granted,
            'points': ldap.get_housing_points(m.uid)
        } for m in models.OnFloorStatusAssigned.query.all()
        if ldap.is_active(ldap.get_uuid_for_uid(m.uid))]

    # sort by housing points then by time in queue
    ofm.sort(key=lambda m: m['time'])
    ofm.sort(key=lambda m: m['points'], reverse=True)

    queue = [m['uid'] for m in ofm if ldap.get_room_number(ldap.get_uuid_for_uid(m['uid'])) == "N/A" and
             ldap.is_current_student(ldap.get_uuid_for_uid(m['uid']))]

    return queue


def get_queue_with_points():
    ofm = [
        {
            'uid': m.uid,
            'time': m.onfloor_granted,
            'points': ldap.get_housing_points(m.uid)
        } for m in models.OnFloorStatusAssigned.query.all()
        if ldap.is_active(ldap.get_uuid_for_uid(m.uid))]

    # sort by housing points then by time in queue
    ofm.sort(key=lambda m: m['time'])
    ofm.sort(key=lambda m: m['points'], reverse=True)

    queue = [
        {
            'name': ldap.get_name(ldap.get_uuid_for_uid(m['uid'])),
            'points': m['points']
        } for m in ofm if ldap.get_room_number(ldap.get_uuid_for_uid(m['uid'])) == "N/A" and
        ldap.is_current_student(ldap.get_uuid_for_uid(m['uid']))]

    return queue


def get_queue_length():
    return len(get_housing_queue())


def get_queue_position(username):
    try:
        return get_housing_queue().index(username)
    except (IndexError, ValueError):
        return "0"
