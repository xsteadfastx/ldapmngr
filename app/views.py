from flask.ext.login import login_user, login_required, logout_user, current_user
from flask import render_template, redirect, session, flash, request, url_for
from app import app
from operator import itemgetter
from .config import *
from .forms import *
from .ldaptools import *
from .login import *
from .password_suggestion import password_suggestion


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(uid=form.username.data, passwd=form.password.data)
        if user.active is not False:
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('login'))
    return render_template('index.html', form=form)


@app.route('/login')
@login_required
def login():
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    form = NewUserForm(password=password_suggestion(5))
    users = user_ls()
    users = sorted(users, key=itemgetter(2))
    if request.method == 'POST' and form.validate():
        try:
            user_add(form.admin_password.data,
                     form.username.data,
                     form.first_name.data,
                     form.last_name.data,
                     form.email.data,
                     form.password.data)
            flash('Added user', 'success')
            return redirect(url_for('users'))
        except Exception:
            flash('Failed to add user', 'danger')
            return redirect(url_for('users'))
    return render_template('users.html', form=form, users=users)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_edit(username):
    attributes = user_attributes(username)
    form = EditUserForm(email=attributes[3], password=password_suggestion(5))
    if request.method == 'POST' and form.validate():
        try:
            user_modify(
                form.admin_password.data,
                username,
                form.email.data,
                form.password.data)
            flash('Modified user', 'success')
            return redirect('/user/' + username)
        except Exception:
            flash('Failed to modify user', 'danger')
            return redirect('/user/' + username)
    return render_template(
        'user_edit.html',
        username=username,
        form=form,
        attributes=attributes)


@app.route('/user/<username>/delete', methods=['GET', 'POST'])
@login_required
def user_delete(username):
    form = DelUserForm()
    if request.method == 'POST' and form.validate():
        try:
            user_rm(form.admin_password.data, username)
            flash('Deleted user', 'success')
            return redirect(url_for('users'))
        except Exception:
            flash('Failed to delete user', 'danger')
            return redirect('/user/' + username + '/delete')
    return render_template('item_delete.html', itemname=username, form=form)


@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    new_group_form = NewGroupForm(prefix='new_group_form')
    new_group_member_form = NewGroupMemberForm(prefix='new_group_member_form')
    groups = group_ls()
    if request.method == 'POST' and new_group_form.validate():
        try:
            group_add(new_group_form.admin_password.data,
                      new_group_form.groupname.data,
                      new_group_form.username.data)
            flash('Added group', 'success')
            return redirect(url_for('groups'))
        except Exception:
            flash('Failed to add group', 'danger')
            return redirect(url_for('groups'))
    return render_template(
        'groups.html',
        new_group_form=new_group_form,
        new_group_member_form=new_group_member_form,
        groups=groups)


@app.route('/group/<groupname>/del-group', methods=['GET', 'POST'])
@login_required
def group_del(groupname):
    form = DelGroupForm()
    if request.method == 'POST' and form.validate():
        try:
            group_rm(form.admin_password.data,
                     groupname)
            flash('Removed group', 'success')
            return redirect(url_for('groups'))
        except Exception:
            flash('Failed to remove group', 'danger')
            return redirect(url_for('groups'))
    return render_template('item_delete.html', form=form, itemname=groupname)


@app.route('/group/<groupname>/add-member', methods=['GET', 'POST'])
@login_required
def group_add_member(groupname):
    # print request.form
    if request.form.get('new_group_member_form-username') and request.form.get('new_group_member_form-admin_password'):
        username = request.form.get('new_group_member_form-username')
        admin_password = request.form.get(
            'new_group_member_form-admin_password')
        try:
            user_addto(admin_password, groupname, username)
            flash('Added user to group', 'success')
            return redirect(url_for('groups'))
        except Exception:
            flash('Failed to add user', 'danger')
            return redirect(url_for('groups'))


@app.route('/group/<groupname>/del-user/<username>', methods=['GET', 'POST'])
@login_required
def group_del_member(groupname, username):
    form = DelUserForm()
    if request.method == 'POST' and form.validate():
        try:
            user_rmfrom(form.admin_password.data,
                        groupname,
                        username)
            flash('Removed user from group', 'success')
            return redirect(url_for('groups'))
        except Exception:
            flash('Failed to remove user', 'success')
            return redirect(url_for('groups'))
    return render_template('item_delete.html', form=form, itemname=username)
