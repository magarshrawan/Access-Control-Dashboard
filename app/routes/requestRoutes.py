from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auth import role_required
from app.controllers.requestController import list_requests_ctrl, get_request_ctrl, submit_request_ctrl, review_request_ctrl, revoke_request_ctrl

request_bp = Blueprint('requests', __name__, url_prefix='/requests')


@request_bp.route('/')
@login_required
def list_requests():
    status_filter = request.args.get('status', '').strip() or None
    requests_list = list_requests_ctrl(status_filter)
    return render_template('requests/list.html', requests=requests_list, status_filter=status_filter or '')


@request_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_request_view():
    if request.method == 'POST':
        success, message = submit_request_ctrl(request.form, current_user.id, request.remote_addr)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('requests.list_requests'))
    return render_template('requests/form.html')


@request_bp.route('/<int:request_id>/review', methods=['GET', 'POST'])
@role_required('Admin', 'Manager')
def review_request_view(request_id):
    req = get_request_ctrl(request_id)
    if not req:
        flash('Request not found.', 'danger')
        return redirect(url_for('requests.list_requests'))
    if request.method == 'POST':
        success, message = review_request_ctrl(request_id, request.form, current_user.id, request.remote_addr)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('requests.list_requests'))
    return render_template('requests/review.html', req=req)


@request_bp.route('/<int:request_id>/revoke', methods=['POST'])
@role_required('Admin')
def revoke_request_view(request_id):
    success, message = revoke_request_ctrl(request_id, current_user.id, request.remote_addr)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('requests.list_requests'))
