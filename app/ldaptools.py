from .config import *
from base64 import encodestring
import ldap
import ldap.modlist as modlist
import re
import sha
import string


def encode_password(password):
    '''encode password to sha'''
    sha_digest = sha.new(password).digest()
    return '{SHA}' + string.strip(encodestring(sha_digest))


def get_full_user_dn(username):
    '''get full dn for username'''
    # define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn']
    search_filter = 'uid=' + username

    # connection and bind
    l = ldap.open(LDAP_SERVER)

    # search for full dn
    ldap_result_id = l.search(LDAP_USER_BASE, search_scope, search_filter,
                              retrieve_attributes)

    return l.result(ldap_result_id)[1][0][0]


def get_full_group_dn(group):
    # define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn']
    search_filter = 'cn=' + group

    # connect
    l = ldap.open(LDAP_SERVER)

    # search for full dn
    ldap_result_id = l.search(LDAP_GROUP_BASE, search_scope, search_filter,
                              retrieve_attributes)

    return l.result(ldap_result_id)[1][0][0]


def get_username(dn):
    '''get full dn for username'''
    # define variables
    search_scope = ldap.SCOPE_BASE

    # connection and bind
    l = ldap.open(LDAP_SERVER)

    # search for full dn
    ldap_result_id = l.search(dn, search_scope, '(objectClass=*)')

    return l.result(ldap_result_id)[1][0][1]['uid'][0]


def user_attributes(username):
    # define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['uid', 'givenName', 'sn', 'mail']
    search_filter = 'uid=' + username

    # connect
    l = ldap.open(LDAP_SERVER)

    # search
    ldap_result_id = l.search(LDAP_USER_BASE, search_scope, search_filter,
                              retrieve_attributes)

    # create result list
    result = []
    for i in l.result(ldap_result_id)[1]:
        attributes = [i[1]['uid'][0],
                      i[1]['givenName'][0],
                      i[1]['sn'][0],
                      i[1]['mail'][0]]
        result.append(attributes)

    return result[0]


def user_ls():
    ''' returns a list of users '''
    # define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['uid', 'givenName', 'sn', 'mail']
    search_filter = 'uid=*'

    # connect
    l = ldap.open(LDAP_SERVER)

    # search
    ldap_result_id = l.search(LDAP_USER_BASE, search_scope, search_filter,
                              retrieve_attributes)

    # create result list
    result = []
    for i in l.result(ldap_result_id)[1]:
        attributes = [i[1]['uid'][0],
                      i[1]['givenName'][0],
                      i[1]['sn'][0],
                      i[1]['mail'][0]]
        result.append(attributes)

    return result


def user_add(admin_password, username, first_name, last_name, email, password):
    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # dn of the new user
    new_user_dn = 'cn=%s %s,%s' % (first_name,
                                   last_name, LDAP_USER_BASE)

    # getting ldap attributes together
    attrs = {}
    attrs['objectclass'] = ['top', 'inetOrgPerson']
    attrs['cn'] = '%s %s' % (str(first_name), str(last_name))
    attrs['mail'] = str(email)
    attrs['givenName'] = str(first_name)
    attrs['sn'] = str(last_name)
    attrs['uid'] = str(username)
    attrs['userPassword'] = str(encode_password(password))

    # create ldif
    ldif = modlist.addModlist(attrs)

    # add ldif to server
    l.add_s(new_user_dn, ldif)

    # disconnect
    l.unbind_s()


def user_modify(admin_password, username, email, password):
    # define variables
    full_dn = get_full_user_dn(username)

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # encode password
    password = encode_password(password)

    # create mod list and modify ldap entry
    mod_list = (
        (ldap.MOD_REPLACE,
         'userPassword',
         str(password)),
        (ldap.MOD_REPLACE,
         'mail',
         str(email)),
    )
    l.modify(full_dn, mod_list)

    # disconnect
    l.unbind_s()


def user_rm(admin_password, username):
    # define variables
    full_dn = get_full_user_dn(username)

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, admin_password)

    # delete
    l.delete_s(full_dn)

    # disconnect
    l.unbind_s()


def user_addto(admin_password, groupname, username):
    ''' add user to group '''
    # get full dn's
    full_group_dn = get_full_group_dn(str(groupname))
    full_user_dn = get_full_user_dn(str(username))

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, str(admin_password))

    # getting attrs together
    mod_attrs = [(ldap.MOD_ADD, 'member', full_user_dn)]

    l.modify_s(full_group_dn, mod_attrs)

    # disconnect
    l.unbind_s()


def user_rmfrom(admin_password, groupname, username):
    ''' removes user from group'''
    # get full dn's
    full_group_dn = get_full_group_dn(str(groupname))
    full_user_dn = get_full_user_dn(str(username))

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, str(admin_password))

    # getting attrs together
    mod_attrs = [(ldap.MOD_DELETE, 'member', full_user_dn)]

    l.modify_s(full_group_dn, mod_attrs)

    # disconnect
    l.unbind_s()


def group_add(admin_password, groupname, username):
    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, str(admin_password))

    # dn of the new group
    new_group_dn = 'cn=%s,%s' % (str(groupname), LDAP_GROUP_BASE)

    # getting ldap attributes together
    attrs = {}
    attrs['objectClass'] = ['top', 'groupOfNames']
    attrs['cn'] = str(groupname)
    attrs['member'] = get_full_user_dn(str(username))

    # create ldif
    ldif = modlist.addModlist(attrs)

    # add ldif to server
    l.add_s(new_group_dn, ldif)

    # disconnect
    l.unbind_s()


def group_ls():
    ''' creating an array with group and users '''
    # define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['cn', 'member']
    search_filter = 'objectClass=groupOfNames'

    # connect
    l = ldap.open(LDAP_SERVER)

    # search
    ldap_result_id = l.search(LDAP_GROUP_BASE, search_scope, search_filter,
                              retrieve_attributes)

    # print result
    groups = {}
    for group in l.result(ldap_result_id)[1]:
        group_members = []
        for member in group[1]['member']:
            group_members.append(user_attributes(get_username(member)))
        groups[group[1]['cn'][0]] = group_members

    return groups


def group_rm(admin_password, groupname):
    # definde variables
    full_dn = get_full_group_dn(str(groupname))

    # connection and bind
    l = ldap.open(LDAP_SERVER)
    l.simple_bind_s(LDAP_ADMIN, str(admin_password))

    # delete
    l.delete_s(full_dn)

    # disconnect
    l.unbind_s()


def is_in_group(group, user):
    # define variables
    search_scope = ldap.SCOPE_SUBTREE
    retrieve_attributes = ['member']
    search_filter = 'cn=%s' % group

    # connect
    l = ldap.open(LDAP_SERVER)

    # search
    ldap_result_id = l.search(LDAP_GROUP_BASE, search_scope, search_filter,
                              retrieve_attributes)

    member_list = l.result(ldap_result_id)[1][0][1]['member']
    try:
        if get_full_user_dn(user) in member_list:
            return True
        else:
            return False
    except Exception:
        return False


def ldap_fetch(uid, password):
    # search_filter = "uid=" + uid
    l = ldap.open(LDAP_SERVER)
    try:
        l.bind_s(get_full_user_dn(uid), password)
        return unicode(uid)
    except Exception:
        return None

    l.unbind_s()
