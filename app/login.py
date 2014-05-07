from flask.ext.login import UserMixin
from .ldaptools import ldap_fetch, is_in_group
from .config import *


class User(UserMixin):

    def __init__(self, uid=None, passwd=None):
        self.active = False
        ldapres = ldap_fetch(uid=uid, password=passwd)

        if ldapres is not None:
            self.id = ldapres
            if is_in_group(LDAP_LOGIN_GROUP, self.id):
                self.active = True

    def is_active(self):
        return self.active

    def get_id(self):
        return self.id
