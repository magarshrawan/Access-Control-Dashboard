"""
Tests for authentication — login, logout, and audit trail.
"""
from unittest.mock import patch
from tests.conftest import FAKE_USER


class TestLoginPage:
    def test_login_page_loads(self, client_no_auth):
        """GET /auth/login renders 200 for unauthenticated users."""
        resp = client_no_auth.get('/auth/login')
        assert resp.status_code == 200
        assert b'Sign in' in resp.data

    def test_login_redirects_if_already_authenticated(self, client_as_admin):
        """Authenticated users visiting /auth/login get redirected to dashboard."""
        resp = client_as_admin.get('/auth/login')
        assert resp.status_code == 302
        assert '/users/' in resp.headers['Location']

    def test_login_invalid_credentials(self, client_no_auth):
        """POST with wrong credentials shows danger alert, not a crash."""
        with patch('app.routes.authRoutes.authenticate', return_value=(None, 'Invalid username or password.')):
            resp = client_no_auth.post('/auth/login', data={'username': 'bad', 'password': 'wrong'})
        assert resp.status_code == 200
        assert b'Invalid username or password' in resp.data

    def test_login_valid_credentials_redirects(self, app, client_no_auth):
        """POST with correct credentials logs the user in and redirects."""
        from app.auth import AuthUser
        fake_user = AuthUser(1, 'admin', 'admin@vertextech.com', 'Admin', True)
        with patch('app.routes.authRoutes.authenticate', return_value=(fake_user, 'Logged in successfully.')):
            resp = client_no_auth.post('/auth/login', data={'username': 'admin', 'password': 'Admin@123'})
        assert resp.status_code == 302

    def test_logout_redirects_to_login(self, client_as_admin):
        """GET /auth/logout ends session and redirects to login page."""
        resp = client_as_admin.get('/auth/logout')
        assert resp.status_code == 302
        assert '/auth/login' in resp.headers['Location']

    def test_unauthenticated_redirected_from_protected_page(self, client_no_auth):
        """Unauthenticated access to /users/ redirects to login."""
        resp = client_no_auth.get('/users/')
        assert resp.status_code == 302
        assert 'login' in resp.headers['Location']
