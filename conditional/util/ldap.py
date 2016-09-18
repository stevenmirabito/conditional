import copy
from functools import lru_cache
from flask import g

import ldap
import ldap.modlist
from ldap.ldapobject import ReconnectLDAPObject


class LDAPError(Exception):
    pass


class LDAP:
    def __init__(self, ro, ldap_url, bind_dn, bind_pw, user_ou, group_ou, committee_ou, auth_overrides=None):
        self.read_only = ro
        self.user_search_ou = user_ou
        self.group_search_ou = group_ou
        self.committee_search_ou = committee_ou
        self.ldap_conn = ReconnectLDAPObject(ldap_url)
        self.ldap_conn.simple_bind_s(bind_dn, bind_pw)
        self.auth_overrides = auth_overrides

    def _get_field(self, uuid, field):
        ldap_results = self.ldap_conn.search_s(self.user_search_ou, ldap.SCOPE_SUBTREE, "(entryUUID=%s)" % uuid,
                                               ['entryUUID', field])
        if len(ldap_results) != 1:
            raise LDAPError("Wrong number of results found for uuid %s." % uuid)
        if field not in ldap_results[0][1]:
            return None
        return ldap_results[0][1][field][0]

    def _set_field(self, uuid, field, new_val):
        if self.read_only:
            print('LDAP modification: setting %s on %s to %s' % (field, uuid, new_val))
            return
        ldap_results = self.ldap_conn.search_s(self.user_search_ou, ldap.SCOPE_SUBTREE, "(entryUUID=%s)" % uuid,
                                               ['entryUUID', field])

        if len(ldap_results) != 1:
            raise LDAPError("Wrong number of results found for uuid %s." % uuid)

        old_result = ldap_results[0][1]
        new_result = copy.deepcopy(ldap_results[0][1])
        new_result[field] = [str(new_val).encode('ascii')]
        ldap_mod_list = ldap.modlist.modifyModlist(old_result, new_result)
        userdn = "entryUUID=%s,%s" % (uuid, self.user_search_ou)
        self.ldap_conn.modify_s(userdn, ldap_mod_list)

    def _get_members(self):
        return self.ldap_conn.search_s(self.user_search_ou, ldap.SCOPE_SUBTREE, "objectClass=houseMember",
                                       ['*', 'entryUUID'])

    def _is_member_of_group(self, uuid, group):
        ldap_results = self.ldap_conn.search_s(self.user_search_ou, ldap.SCOPE_SUBTREE, "(entryUUID=%s)" % uuid,
                                               ['memberOf'])

        if not ldap_results:
            return False
        else:
            try:
                return "cn=" + group + "," + self.group_search_ou in \
                       [x.decode('utf-8') for x in ldap_results[0][1]['memberOf']]
            except KeyError:
                return False

    def _add_member_to_group(self, uuid, group):
        if self.read_only:
            print("LDAP: Adding user %s to group %s" % (uuid, group))
            return
        if self._is_member_of_group(uuid, group):
            return
        ldap_results = self.ldap_conn.search_s(self.group_search_ou, ldap.SCOPE_SUBTREE, "(cn=%s)" % group,
                                               ['entryUUID', 'member'])
        if len(ldap_results) != 1:
            raise LDAPError("Wrong number of results found for group %s." % group)
        old_results = ldap_results[0][1]
        new_results = copy.deepcopy(ldap_results[0][1])
        new_entry = "entryUUID=%s,%s" % (uuid, self.user_search_ou)
        new_entry = new_entry.encode('utf-8')
        new_results['member'].append(new_entry)
        ldap_modlist = ldap.modlist.modifyModlist(old_results, new_results)
        groupdn = "cn=%s,%s" % (group, self.group_search_ou)
        self.ldap_conn.modify_s(groupdn, ldap_modlist)

    def _remove_member_from_group(self, uuid, group):
        if self.read_only:
            print("LDAP: Removing user %s from group %s" % (uuid, group))
            return
        if not self._is_member_of_group(uuid, group):
            return
        ldap_results = self.ldap_conn.search_s(self.group_search_ou, ldap.SCOPE_SUBTREE, "(cn=%s)" % group,
                                               ['entryUUID', 'member'])
        if len(ldap_results) != 1:
            raise LDAPError("Wrong number of results found for group %s." % group)
        old_results = ldap_results[0][1]
        new_results = copy.deepcopy(ldap_results[0][1])
        new_results['member'] = [i for i in old_results['member'] if
                                 i.decode('utf-8') != "entryUUID=%s,%s" % (uuid, self.user_search_ou)]
        ldap_modlist = ldap.modlist.modifyModlist(old_results, new_results)
        groupdn = "cn=%s,%s" % (group, self.group_search_ou)
        self.ldap_conn.modify_s(groupdn, ldap_modlist)

    def _is_member_of_committee(self, uuid, committee):
        ldap_results = self.ldap_conn.search_s(self.committee_search_ou, ldap.SCOPE_SUBTREE, "(cn=%s)" % committee,
                                               ['entryUUID', 'head'])
        if len(ldap_results) != 1:
            raise LDAPError("Wrong number of results found for committee %s." % committee)
        return "entryUUID=" + uuid + "," + self.user_search_ou in \
               [x.decode('utf-8') for x in ldap_results[0][1]['head']]

    @lru_cache(maxsize=1024)
    def get_uuid_for_uid(self, uid):
        # Temporary method to ease transition to UUIDs
        ldap_results = self.ldap_conn.search_s(self.user_search_ou, ldap.SCOPE_SUBTREE, "(uid=%s)" % uid,
                                               ['*', 'entryUUID'])
        if len(ldap_results) != 1:
            raise LDAPError("Wrong number of results found for uid %s." % uid)
        if 'entryUUID' not in ldap_results[0][1]:
            return None
        return ldap_results[0][1]['entryUUID'][0].decode('utf-8')

    @lru_cache(maxsize=1024)
    def get_housing_points(self, uuid):
        return int(self._get_field(uuid, 'housingPoints'))

    def get_room_number(self, uuid):
        roomno = self._get_field(uuid, 'roomNumber')
        if roomno is None:
            return "N/A"
        return roomno.decode('utf-8')

    @lru_cache(maxsize=1024)
    def get_active_members(self):
        return [x for x in self.get_current_students()
                if self.is_active(x['entryUUID'][0].decode('utf-8'))]

    @lru_cache(maxsize=1024)
    def get_intro_members(self):
        return [x for x in self.get_current_students()
                if self.is_intromember(x['entryUUID'][0].decode('utf-8'))]

    @lru_cache(maxsize=1024)
    def get_non_alumni_members(self):
        return [x for x in self.get_current_students()
                if self.is_alumni(x['entryUUID'][0].decode('utf-8'))]

    @lru_cache(maxsize=1024)
    def get_onfloor_members(self):
        return [x for x in self.get_current_students()
                if self.is_onfloor(x['entryUUID'][0].decode('utf-8'))]

    @lru_cache(maxsize=1024)
    def get_current_students(self):
        return [x[1] for x in self._get_members()
                if self.is_current_student(x[1]['entryUUID'][0].decode('utf-8'))]

    def is_active(self, uuid):
        return self._is_member_of_group(uuid, 'active')

    def is_alumni(self, uuid):
        # When alumni status becomes a group rather than an attribute this will
        # change to use _is_member_of_group.
        alum_status = self._get_field(uuid, 'alumni')
        return alum_status is not None and alum_status.decode('utf-8') == '1'

    def is_eboard(self, uuid):
        if self.auth_overrides and \
                g.userinfo['uuid'] in self.auth_overrides and \
                self.auth_overrides[g.userinfo['uuid']] == 'eboard':
            return True

        return self._is_member_of_group(uuid, 'eboard')

    def is_intromember(self, uuid):
        if self.auth_overrides and \
                g.userinfo['uuid'] in self.auth_overrides and \
                self.auth_overrides[g.userinfo['uuid']] == 'intro':
            return True

        return self._is_member_of_group(uuid, 'intromembers')

    def is_onfloor(self, uuid):
        return self._is_member_of_group(uuid, 'onfloor')

    def is_financial_director(self, uuid):
        if self.auth_overrides and \
                g.userinfo['uuid'] in self.auth_overrides and \
                self.auth_overrides[g.userinfo['uuid']] == 'financial':
            return True

        return self._is_member_of_committee(uuid, 'Financial')

    def is_eval_director(self, uuid):
        if self.auth_overrides and \
                g.userinfo['uuid'] in self.auth_overrides and \
                self.auth_overrides[g.userinfo['uuid']] == 'evals':
            return True

        # TODO FIXME Evaulations -> Evaluations
        return self._is_member_of_committee(uuid, 'Evaulations')

    def is_current_student(self, uuid):
        return self._is_member_of_group(uuid, 'current_student')

    def set_housingpoints(self, uuid, housing_points):
        self._set_field(uuid, 'housingPoints', housing_points)

    def set_roomnumber(self, uuid, room_number):
        self._set_field(uuid, 'roomNumber', room_number)

    def set_active(self, uuid):
        self._add_member_to_group(uuid, 'active')

    def set_inactive(self, uuid):
        self._remove_member_from_group(uuid, 'active')

    @lru_cache(maxsize=1024)
    def get_name(self, uuid):
        return self._get_field(uuid, 'cn').decode('utf-8')
