import mysql.connector
from app.models.dashboardModel import get_dashboard_metrics


def get_dashboard_ctrl():
    try:
        return get_dashboard_metrics()
    except mysql.connector.Error:
        return {
            'total_users': 0, 'active_users': 0,
            'pending_requests': 0, 'flagged_logs': 0,
            'total_roles': 0, 'recent_activity': [],
            'login_chart': [], 'request_chart': [],
        }
