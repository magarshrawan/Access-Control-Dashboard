import mysql.connector
from datetime import datetime
from app.models.requestModel import get_all_requests, get_request_by_id, create_request, review_request, revoke_request
from app.models.auditModel import log_action


def list_requests_ctrl(status_filter=None):
    try:
        return get_all_requests(status_filter)
    except mysql.connector.Error:
        return []


def get_request_ctrl(request_id):
    try:
        return get_request_by_id(request_id)
    except mysql.connector.Error:
        return None


def submit_request_ctrl(form, requester_id, ip_address):
    resource      = form.get('resource', '').strip()
    justification = form.get('justification', '').strip()
    expires_raw   = form.get('expires_at', '').strip()

    if not resource or not justification:
        return False, "Resource and justification are required."
    if len(justification) < 10:
        return False, "Please provide a more detailed justification (at least 10 characters)."

    expires_at = None
    if expires_raw:
        try:
            expires_at = datetime.strptime(expires_raw, '%Y-%m-%d')
        except ValueError:
            return False, "Invalid expiry date format."
    try:
        new_id = create_request(requester_id, resource, justification, expires_at)
        log_action(requester_id, 'ACCESS_REQUESTED', resource_type='request', resource_id=new_id, ip_address=ip_address)
        return True, "Access request submitted for review."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def review_request_ctrl(request_id, form, reviewer_id, ip_address):
    decision = form.get('decision', '')
    notes    = form.get('reviewer_notes', '').strip()
    if decision not in ('approved', 'denied'):
        return False, "Invalid decision."
    try:
        review_request(request_id, reviewer_id, decision, notes)
        action = 'ACCESS_APPROVED' if decision == 'approved' else 'ACCESS_DENIED'
        log_action(reviewer_id, action, resource_type='request', resource_id=request_id, ip_address=ip_address)
        return True, f"Request {decision}."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def revoke_request_ctrl(request_id, actor_id, ip_address):
    try:
        req = get_request_by_id(request_id)
        if not req:
            return False, "Request not found."
        revoke_request(request_id)
        log_action(actor_id, 'ACCESS_REVOKED', resource_type='request', resource_id=request_id, ip_address=ip_address)
        return True, "Access has been revoked."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."
