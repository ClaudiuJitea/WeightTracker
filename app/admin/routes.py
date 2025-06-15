from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.admin.forms import CreateUserForm, EditUserForm, ChangePasswordForm, AdminPasswordChangeForm
from app.models import User
from datetime import datetime
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    total_users = len(users)
    admin_users = len([u for u in users if u.is_admin])
    regular_users = total_users - admin_users
    
    return render_template('admin/dashboard.html', 
                         users=users,
                         total_users=total_users,
                         admin_users=admin_users,
                         regular_users=regular_users)

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@bp.route('/create_user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, 
                   email=form.email.data,
                   is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.username} has been created successfully!', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/create_user.html', form=form)

@bp.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(user.username, user.email)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash(f'User {user.username} has been updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin
    
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/delete_user/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.users'))
    
    # Prevent deleting the last admin
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Cannot delete the last administrator account!', 'error')
            return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User {username} has been deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/change_user_password/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_password(id):
    user = User.query.get_or_404(id)
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(f'Password for {user.username} has been changed successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/change_password.html', form=form, user=user)

@bp.route('/change_admin_password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_admin_password():
    form = AdminPasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid current password!', 'error')
    
    return render_template('admin/change_password.html', form=form)

@bp.route('/toggle_admin/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(id):
    user = User.query.get_or_404(id)
    
    # Prevent removing admin from yourself
    if user.id == current_user.id and user.is_admin:
        flash('You cannot remove admin privileges from your own account!', 'error')
        return redirect(url_for('admin.users'))
    
    # Prevent removing the last admin
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Cannot remove admin privileges from the last administrator!', 'error')
            return redirect(url_for('admin.users'))
        user.remove_admin()
        flash(f'Admin privileges removed from {user.username}!', 'success')
    else:
        user.make_admin()
        flash(f'Admin privileges granted to {user.username}!', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.users'))