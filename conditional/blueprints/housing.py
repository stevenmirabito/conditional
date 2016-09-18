import uuid
import structlog

from flask import Blueprint, g

from conditional import auth, ldap

from conditional.models.models import FreshmanAccount
from conditional.util.housing import get_queue_with_points
from conditional.util.flask import render_template

logger = structlog.get_logger()

housing_bp = Blueprint('housing_bp', __name__)


@housing_bp.route('/housing')
@auth.oidc_auth
def display_housing():
    log = logger.new(user_id=g.userinfo['uuid'],
                     request_id=str(uuid.uuid4()))
    log.info('frontend', action='display housing')

    housing = {}
    onfloors = [member['entryUUID'][0].decode('utf-8') for member in ldap.get_onfloor_members()]
    onfloor_freshmen = FreshmanAccount.query.filter(
        FreshmanAccount.room_number is not None
    )

    room_list = set()

    for m in onfloors:
        room = ldap.get_room_number(m)
        if room is not None and room != "None":
            if room in housing:
                housing[room].append(ldap.get_name(m))
            else:
                housing[room] = [ldap.get_name(m)]
            room_list.add(room)

    for f in onfloor_freshmen:
        name = f.name
        room = str(f.room_number)
        if room != "None":
            if room in housing:
                housing[room].append(name)
                room_list.add(room)
            else:
                housing[room] = [name]
                room_list.add(room)

    # return names in 'first last (username)' format
    return render_template('housing.html',
                           queue=get_queue_with_points(),
                           housing=housing,
                           room_list=sorted(list(room_list)))
