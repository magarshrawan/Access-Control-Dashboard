"""
Tests for Section 4 — Audit Log (CRUD).
"""
from unittest.mock import patch
from tests.conftest import FAKE_LOG


class TestAuditList:
    def test_list_renders_for_admin(self, client_as_admin):
        """READ — Admin can view audit log."""
        with patch('app.routes.auditRoutes.list_logs_ctrl', return_value=[FAKE_LOG]):
            resp = client_as_admin.get('/audit/')
        assert resp.status_code == 200
        assert b'LOGIN_SUCCESS' in resp.data

    def test_list_renders_for_analyst(self, client_as_manager):
        """READ — Manager can also view audit log."""
        with patch('app.routes.auditRoutes.list_logs_ctrl', return_value=[FAKE_LOG]):
            resp = client_as_manager.get('/audit/')
        assert resp.status_code == 200

    def test_list_blocked_for_readonly(self, client_as_readonly):
        """READ — ReadOnly cannot access audit log (403)."""
        resp = client_as_readonly.get('/audit/')
        assert resp.status_code == 403

    def test_list_search_filter(self, client_as_admin):
        """READ — Search param is passed to controller."""
        with patch('app.routes.auditRoutes.list_logs_ctrl', return_value=[]) as mock_ctrl:
            client_as_admin.get('/audit/?search=admin')
            mock_ctrl.assert_called_once_with(search='admin', flagged_only=False)

    def test_list_flagged_only_filter(self, client_as_admin):
        """READ — Flagged-only checkbox is passed correctly."""
        with patch('app.routes.auditRoutes.list_logs_ctrl', return_value=[]) as mock_ctrl:
            client_as_admin.get('/audit/?flagged=1')
            mock_ctrl.assert_called_once_with(search=None, flagged_only=True)

    def test_list_empty_state(self, client_as_admin):
        """READ — Empty audit log renders without error."""
        with patch('app.routes.auditRoutes.list_logs_ctrl', return_value=[]):
            resp = client_as_admin.get('/audit/')
        assert resp.status_code == 200
        assert b'No log entries found' in resp.data


class TestAuditFlag:
    def test_flag_success(self, client_as_admin):
        """UPDATE — Admin can flag a suspicious log entry."""
        with patch('app.routes.auditRoutes.flag_log_ctrl', return_value=(True, 'Flagged.')):
            resp = client_as_admin.post('/audit/1/flag', data={'reason': 'Suspicious activity'})
        assert resp.status_code == 302

    def test_unflag_success(self, client_as_admin):
        """UPDATE — Admin can clear a flag after review."""
        with patch('app.routes.auditRoutes.unflag_log_ctrl', return_value=(True, 'Flag cleared.')):
            resp = client_as_admin.post('/audit/1/unflag')
        assert resp.status_code == 302

    def test_flag_blocked_for_manager(self, client_as_manager):
        """UPDATE — Manager cannot flag (Analyst/Admin only)."""
        resp = client_as_manager.post('/audit/1/flag', data={'reason': 'test'})
        assert resp.status_code == 403

    def test_flag_blocked_for_readonly(self, client_as_readonly):
        """UPDATE — ReadOnly cannot flag."""
        resp = client_as_readonly.post('/audit/1/flag', data={'reason': 'test'})
        assert resp.status_code == 403


class TestAuditPurge:
    def test_purge_success_by_admin(self, client_as_admin):
        """DELETE — Admin can purge old logs."""
        with patch('app.routes.auditRoutes.purge_logs_ctrl', return_value=(True, 'Purged 12 entries.')):
            resp = client_as_admin.post('/audit/purge', data={'days': '90'})
        assert resp.status_code == 302

    def test_purge_blocked_for_manager(self, client_as_manager):
        """DELETE — Manager cannot purge logs (Admin-only)."""
        resp = client_as_manager.post('/audit/purge', data={'days': '90'})
        assert resp.status_code == 403

    def test_purge_blocked_for_readonly(self, client_as_readonly):
        """DELETE — ReadOnly cannot purge logs."""
        resp = client_as_readonly.post('/audit/purge', data={'days': '90'})
        assert resp.status_code == 403


class TestAuditControllerValidation:
    def test_flag_requires_reason(self, app):
        from app.controllers.auditController import flag_log_ctrl
        with app.app_context():
            with patch('app.controllers.auditController.get_log_by_id', return_value=FAKE_LOG):
                ok, msg = flag_log_ctrl(1, reason='', actor_id=1, ip_address='127.0.0.1')
        assert ok is False
        assert 'reason' in msg.lower()

    def test_purge_minimum_30_days(self, app):
        from app.controllers.auditController import purge_logs_ctrl
        with app.app_context():
            ok, msg = purge_logs_ctrl(days=10, actor_id=1, ip_address='127.0.0.1')
        assert ok is False
        assert '30' in msg

    def test_purge_invalid_days(self, app):
        from app.controllers.auditController import purge_logs_ctrl
        with app.app_context():
            ok, msg = purge_logs_ctrl(days='abc', actor_id=1, ip_address='127.0.0.1')
        assert ok is False
        assert 'Invalid' in msg
