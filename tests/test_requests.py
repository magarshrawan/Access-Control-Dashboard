"""
Tests for Section 3 — Access Requests (CRUD).
"""
from unittest.mock import patch
from tests.conftest import FAKE_REQUEST


class TestRequestList:
    def test_list_renders_all_roles(self, client_as_admin):
        """READ — Any logged-in user can view the request queue."""
        with patch('app.routes.requestRoutes.list_requests_ctrl', return_value=[FAKE_REQUEST]):
            resp = client_as_admin.get('/requests/')
        assert resp.status_code == 200
        assert b'r.thapa' in resp.data

    def test_list_filter_by_status(self, client_as_admin):
        """READ — Status filter param is passed to controller."""
        with patch('app.routes.requestRoutes.list_requests_ctrl', return_value=[]) as mock_ctrl:
            client_as_admin.get('/requests/?status=pending')
            mock_ctrl.assert_called_once_with('pending')

    def test_list_empty_state(self, client_as_admin):
        """READ — Empty queue renders without error."""
        with patch('app.routes.requestRoutes.list_requests_ctrl', return_value=[]):
            resp = client_as_admin.get('/requests/')
        assert resp.status_code == 200
        assert b'No access requests found' in resp.data


class TestRequestSubmit:
    def test_submit_form_accessible_to_all(self, client_as_readonly):
        """CREATE — Even ReadOnly users can submit an access request."""
        resp = client_as_readonly.get('/requests/submit')
        assert resp.status_code == 200
        assert b'Request access' in resp.data

    def test_submit_success_redirects(self, client_as_admin):
        """CREATE — Valid submission redirects to request list."""
        with patch('app.routes.requestRoutes.submit_request_ctrl', return_value=(True, 'Submitted.')):
            resp = client_as_admin.post('/requests/submit', data={
                'resource': 'Prod DB (read)', 'justification': 'Required for Q2 audit work'
            })
        assert resp.status_code == 302

    def test_submit_short_justification_fails(self, client_as_admin):
        """CREATE — Justification under 10 chars shows error."""
        with patch('app.routes.requestRoutes.submit_request_ctrl', return_value=(False, 'Please provide a more detailed justification.')):
            resp = client_as_admin.post('/requests/submit', data={
                'resource': 'Prod DB', 'justification': 'need it'
            })
        assert resp.status_code == 200
        assert b'detailed justification' in resp.data


class TestRequestReview:
    def test_review_form_accessible_to_manager(self, client_as_manager):
        """UPDATE — Manager can view review form."""
        with patch('app.routes.requestRoutes.get_request_ctrl', return_value=FAKE_REQUEST):
            resp = client_as_manager.get('/requests/1/review')
        assert resp.status_code == 200
        assert b'Approve' in resp.data
        assert b'Deny' in resp.data

    def test_review_blocked_for_readonly(self, client_as_readonly):
        """UPDATE — ReadOnly cannot access review form (403)."""
        resp = client_as_readonly.get('/requests/1/review')
        assert resp.status_code == 403

    def test_approve_redirects(self, client_as_manager):
        """UPDATE — Approving redirects to request list."""
        with patch('app.routes.requestRoutes.get_request_ctrl', return_value=FAKE_REQUEST), \
             patch('app.routes.requestRoutes.review_request_ctrl', return_value=(True, 'Request approved.')):
            resp = client_as_manager.post('/requests/1/review', data={'decision': 'approved', 'reviewer_notes': ''})
        assert resp.status_code == 302

    def test_deny_redirects(self, client_as_manager):
        """UPDATE — Denying redirects to request list."""
        with patch('app.routes.requestRoutes.get_request_ctrl', return_value=FAKE_REQUEST), \
             patch('app.routes.requestRoutes.review_request_ctrl', return_value=(True, 'Request denied.')):
            resp = client_as_manager.post('/requests/1/review', data={'decision': 'denied', 'reviewer_notes': 'Not justified.'})
        assert resp.status_code == 302

    def test_review_missing_request_redirects(self, client_as_admin):
        """UPDATE — Reviewing a non-existent request redirects with error."""
        with patch('app.routes.requestRoutes.get_request_ctrl', return_value=None):
            resp = client_as_admin.get('/requests/999/review')
        assert resp.status_code == 302


class TestRequestRevoke:
    def test_revoke_success_by_admin(self, client_as_admin):
        """DELETE — Admin can revoke approved access."""
        with patch('app.routes.requestRoutes.revoke_request_ctrl', return_value=(True, 'Access revoked.')):
            resp = client_as_admin.post('/requests/1/revoke')
        assert resp.status_code == 302

    def test_revoke_blocked_for_manager(self, client_as_manager):
        """DELETE — Manager cannot revoke (Admin-only)."""
        resp = client_as_manager.post('/requests/1/revoke')
        assert resp.status_code == 403

    def test_revoke_blocked_for_readonly(self, client_as_readonly):
        """DELETE — ReadOnly cannot revoke."""
        resp = client_as_readonly.post('/requests/1/revoke')
        assert resp.status_code == 403


class TestRequestControllerValidation:
    def test_empty_resource_rejected(self, app):
        from app.controllers.requestController import submit_request_ctrl
        with app.app_context():
            ok, msg = submit_request_ctrl(
                {'resource': '', 'justification': 'some reason here'},
                requester_id=1, ip_address='127.0.0.1'
            )
        assert ok is False
        assert 'required' in msg.lower()

    def test_short_justification_rejected(self, app):
        from app.controllers.requestController import submit_request_ctrl
        with app.app_context():
            ok, msg = submit_request_ctrl(
                {'resource': 'Prod DB', 'justification': 'short'},
                requester_id=1, ip_address='127.0.0.1'
            )
        assert ok is False
        assert 'detailed' in msg.lower()

    def test_invalid_date_rejected(self, app):
        from app.controllers.requestController import submit_request_ctrl
        with app.app_context():
            ok, msg = submit_request_ctrl(
                {'resource': 'Prod DB', 'justification': 'long enough reason here', 'expires_at': 'not-a-date'},
                requester_id=1, ip_address='127.0.0.1'
            )
        assert ok is False
        assert 'date' in msg.lower()
