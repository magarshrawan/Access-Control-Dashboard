import mysql.connector
from app.models.auditModel import get_logs, get_log_by_id, flag_log, unflag_log, purge_logs_older_than, log_action


def list_logs_ctrl(search=None, flagged_only=False):
    try:
        return get_logs(search, flagged_only)
    except mysql.connector.Error:
        return []


def flag_log_ctrl(log_id, reason, actor_id, ip_address):
    if not reason or not reason.strip():
        return False, "A reason is required to flag a log entry."
    try:
        if not get_log_by_id(log_id):
            return False, "Log entry not found."
        flag_log(log_id, reason.strip())
        log_action(actor_id, 'AUDIT_LOG_FLAGGED', resource_type='audit_log', resource_id=log_id, ip_address=ip_address)
        return True, "Log entry flagged for review."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def unflag_log_ctrl(log_id, actor_id, ip_address):
    try:
        unflag_log(log_id)
        log_action(actor_id, 'AUDIT_LOG_UNFLAGGED', resource_type='audit_log', resource_id=log_id, ip_address=ip_address)
        return True, "Flag cleared."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def purge_logs_ctrl(days, actor_id, ip_address):
    try:
        days = int(days)
        if days < 30:
            return False, "Retention period must be at least 30 days."
        count = purge_logs_older_than(days)
        log_action(actor_id, 'AUDIT_LOGS_PURGED', resource_type='audit_log', ip_address=ip_address)
        return True, f"Purged {count} log entries older than {days} days."
    except (ValueError, TypeError):
        return False, "Invalid retention period."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."
