from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auth import role_required
from app.controllers.userController import (
    list_users_ctrl, get_user_ctrl, create_user_ctrl,
    update_user_ctrl, deactivate_user_ctrl,
    change_password_ctrl, get_profile_ctrl,
    get_departments_ctrl, VALID_ROLES
)

user_bp = Blueprint('users', __name__, url_prefix='/users')


@user_bp.route('/')
@login_required
def list_users():
    search        = request.args.get('search', '').strip() or None
    role_filter   = request.args.get('role', '').strip() or None
    status_filter = request.args.get('status', '').strip() or None
    dept_filter   = request.args.get('dept', '').strip() or None

    users = list_users_ctrl(search, role_filter, status_filter, dept_filter)
    departments = get_departments_ctrl()

    return render_template(
        'users/list.html',
        users=users, roles=VALID_ROLES, departments=departments,
        search=search or '', role_filter=role_filter or '',
        status_filter=status_filter or '', dept_filter=dept_filter or ''
    )


@user_bp.route('/create', methods=['GET', 'POST'])
@role_required('Admin')
def create_user_view():
    if request.method == 'POST':
        success, message = create_user_ctrl(
            request.form, current_user.id, request.remote_addr
        )
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('users.list_users'))
    return render_template('users/form.html', roles=VALID_ROLES, user=None)


@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required('Admin')
def edit_user_view(user_id):
    user = get_user_ctrl(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users.list_users'))
    if request.method == 'POST':
        success, message = update_user_ctrl(
            user_id, request.form, current_user.id, request.remote_addr
        )
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('users.list_users'))
    return render_template('users/form.html', roles=VALID_ROLES, user=user)


@user_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@role_required('Admin')
def deactivate_user_view(user_id):
    success, message = deactivate_user_ctrl(
        user_id, current_user.id, request.remote_addr
    )
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('users.list_users'))


@user_bp.route('/profile')
@login_required
def profile():
    user = get_profile_ctrl(current_user.id)
    if not user:
        flash('Profile not found.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    return render_template('users/profile.html', user=user)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password_view():
    if request.method == 'POST':
        success, message = change_password_ctrl(
            current_user.id, request.form, request.remote_addr
        )
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('users.profile'))
    return render_template('users/change_password.html')
