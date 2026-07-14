from datetime import datetime, timedelta
from app.database import get_db


def log_action(user_id, action, resource_type=None, resource_id=None, ip_address=None):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (user_id, action, resource_type, resource_id, ip_address) VALUES (%s,%s,%s,%s,%s)",
        (user_id, action, resource_type, resource_id, ip_address)
    )
    db.commit()
    cursor.close(); db.close()


def get_logs(search=None, flagged_only=False, date_from=None, date_to=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT al.*, u.username FROM audit_logs al LEFT JOIN users u ON u.id = al.user_id WHERE 1=1"
    params = []
    if search:
        query += " AND (u.username LIKE %s OR al.action LIKE %s OR al.ip_address LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if flagged_only:
        query += " AND al.flagged = TRUE"
    if date_from:
        query += " AND al.timestamp >= %s"
        params.append(date_from)
    if date_to:
        query += " AND al.timestamp <= %s"
        params.append(date_to)
    query += " ORDER BY al.timestamp DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close(); db.close()
    return rows


def get_log_by_id(log_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT al.*, u.username FROM audit_logs al LEFT JOIN users u ON u.id=al.user_id WHERE al.id=%s", (log_id,))
    row = cursor.fetchone()
    cursor.close(); db.close()
    return row


def flag_log(log_id, flag_reason):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE audit_logs SET flagged=TRUE, flag_reason=%s WHERE id=%s", (flag_reason, log_id))
    db.commit()
    cursor.close(); db.close()


def unflag_log(log_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE audit_logs SET flagged=FALSE, flag_reason=NULL WHERE id=%s", (log_id,))
    db.commit()
    cursor.close(); db.close()


def purge_logs_older_than(days=90):
    cutoff = datetime.now() - timedelta(days=days)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM audit_logs WHERE timestamp < %s", (cutoff,))
    count = cursor.rowcount
    db.commit()
    cursor.close(); db.close()
    return count
