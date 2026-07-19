from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.auth import role_required
from app.controllers.auditController import (
    list_logs_ctrl, flag_log_ctrl, unflag_log_ctrl, purge_logs_ctrl
)

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')


@audit_bp.route('/')
@role_required('Admin', 'Manager', 'Analyst')
def list_logs():
    search       = request.args.get('search', '').strip() or None
    flagged_only = request.args.get('flagged') == '1'
    date_from    = request.args.get('date_from', '').strip() or None
    date_to      = request.args.get('date_to', '').strip() or None

    logs = list_logs_ctrl(
        search=search,
        flagged_only=flagged_only,
        date_from=date_from,
        date_to=date_to
    )
    return render_template(
        'audit/list.html',
        logs=logs,
        search=search or '',
        flagged_only=flagged_only,
        date_from=date_from or '',
        date_to=date_to or ''
    )


@audit_bp.route('/<int:log_id>/flag', methods=['POST'])
@role_required('Admin', 'Analyst')
def flag_log_view(log_id):
    reason = request.form.get('reason', '')
    success, message = flag_log_ctrl(log_id, reason, current_user.id, request.remote_addr)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('audit.list_logs'))


@audit_bp.route('/<int:log_id>/unflag', methods=['POST'])
@role_required('Admin', 'Analyst')
def unflag_log_view(log_id):
    success, message = unflag_log_ctrl(log_id, current_user.id, request.remote_addr)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('audit.list_logs'))


@audit_bp.route('/purge', methods=['POST'])
@role_required('Admin')
def purge_logs_view():
    days = request.form.get('days', '90')
    success, message = purge_logs_ctrl(days, current_user.id, request.remote_addr)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('audit.list_logs'))
