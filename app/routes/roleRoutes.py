from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auth import role_required
from app.controllers.roleController import list_roles_ctrl, get_role_ctrl, get_permissions_matrix_ctrl, create_role_ctrl, update_role_ctrl, delete_role_ctrl

role_bp = Blueprint('roles', __name__, url_prefix='/roles')


@role_bp.route('/')
@login_required
def list_roles():
    roles = list_roles_ctrl()
    return render_template('roles/list.html', roles=roles)


@role_bp.route('/create', methods=['GET', 'POST'])
@role_required('Admin')
def create_role_view():
    if request.method == 'POST':
        success, message = create_role_ctrl(request.form, current_user.id, request.remote_addr)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('roles.list_roles'))
    permissions, assigned_ids = get_permissions_matrix_ctrl()
    return render_template('roles/form.html', role=None, permissions=permissions, assigned_ids=assigned_ids)


@role_bp.route('/<int:role_id>/edit', methods=['GET', 'POST'])
@role_required('Admin')
def edit_role_view(role_id):
    role = get_role_ctrl(role_id)
    if not role:
        flash('Role not found.', 'danger')
        return redirect(url_for('roles.list_roles'))
    if request.method == 'POST':
        success, message = update_role_ctrl(role_id, request.form, current_user.id, request.remote_addr)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('roles.list_roles'))
    permissions, assigned_ids = get_permissions_matrix_ctrl(role_id)
    return render_template('roles/form.html', role=role, permissions=permissions, assigned_ids=assigned_ids)


@role_bp.route('/<int:role_id>/delete', methods=['POST'])
@role_required('Admin')
def delete_role_view(role_id):
    success, message = delete_role_ctrl(role_id, current_user.id, request.remote_addr)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('roles.list_roles'))
