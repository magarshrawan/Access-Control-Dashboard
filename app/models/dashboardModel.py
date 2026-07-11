from app.database import get_db


def get_dashboard_metrics():
    """
    Returns summary counts for the dashboard home page.
    One query per metric — simple and readable for a coursework project.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total and active users
    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM users WHERE is_active = TRUE")
    active_users = cursor.fetchone()['total']

    # Pending access requests
    cursor.execute("SELECT COUNT(*) AS total FROM access_requests WHERE status = 'pending'")
    pending_requests = cursor.fetchone()['total']

    # Flagged audit log entries
    cursor.execute("SELECT COUNT(*) AS total FROM audit_logs WHERE flagged = TRUE")
    flagged_logs = cursor.fetchone()['total']

    # Total roles
    cursor.execute("SELECT COUNT(*) AS total FROM roles")
    total_roles = cursor.fetchone()['total']

    # Recent audit log (last 7 entries for the activity feed)
    cursor.execute("""
        SELECT al.action, al.timestamp, al.ip_address, u.username
        FROM audit_logs al
        LEFT JOIN users u ON u.id = al.user_id
        ORDER BY al.timestamp DESC
        LIMIT 7
    """)
    recent_activity = cursor.fetchall()

    # Login counts per day for the last 7 days (for the bar chart)
    cursor.execute("""
        SELECT DATE(timestamp) AS day, COUNT(*) AS count
        FROM audit_logs
        WHERE action IN ('LOGIN_SUCCESS', 'LOGIN_FAILED')
          AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(timestamp)
        ORDER BY day ASC
    """)
    login_chart = cursor.fetchall()

    # Request status breakdown (for doughnut chart)
    cursor.execute("""
        SELECT status, COUNT(*) AS count
        FROM access_requests
        GROUP BY status
    """)
    request_chart = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        'total_users':      total_users,
        'active_users':     active_users,
        'pending_requests': pending_requests,
        'flagged_logs':     flagged_logs,
        'total_roles':      total_roles,
        'recent_activity':  recent_activity,
        'login_chart':      login_chart,
        'request_chart':    request_chart,
    }
