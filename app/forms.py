from wtforms import TextField, PasswordField
from wtforms.validators import Required
from flask_wtf import Form


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])


class NewUserForm(Form):
    username = TextField('Username', validators=[Required()])
    first_name = TextField('First name', validators=[Required()])
    last_name = TextField('Last name', validators=[Required()])
    email = TextField('Email', validators=[Required()])
    password = TextField('Password', validators=[Required()])
    admin_password = PasswordField('Password', validators=[Required()])


class EditUserForm(Form):
    email = TextField('Email', validators=[Required()])
    password = TextField('Password', validators=[Required()])
    admin_password = PasswordField('Password', validators=[Required()])


class DelUserForm(Form):
    admin_password = PasswordField('Password', validators=[Required()])


class NewGroupForm(Form):
    groupname = TextField('Groupname', validators=[Required()])
    username = TextField('First user', validators=[Required()])
    admin_password = PasswordField('Password', validators=[Required()])


class DelGroupForm(Form):
    admin_password = PasswordField('Password', validators=[Required()])


class NewGroupMemberForm(Form):
    username = TextField('', validators=[Required()])
    admin_password = PasswordField('', validators=[Required()])
