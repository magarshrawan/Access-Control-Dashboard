"""
Tests for Section 1 — User Management (CRUD).
Covers: list, create, edit, deactivate, RBAC enforcement, and validation.
"""
from unittest.mock import patch
from tests.conftest import FAKE_USER


class TestUserList:
    def test_list_renders_for_admin(self, client_as_admin):
        """READ — Admin can view user list."""
        with patch('app.routes.userRoutes.list_users_ctrl', return_value=[FAKE_USER]):
            resp = client_as_admin.get('/users/')
        assert resp.status_code == 200
        assert b'admin' in resp.data

    def test_list_renders_for_readonly(self, client_as_readonly):
        """READ — ReadOnly can also view the user list (read-only mode)."""
        with patch('app.routes.userRoutes.list_users_ctrl', return_value=[FAKE_USER]):
            resp = client_as_readonly.get('/users/')
        assert resp.status_code == 200

    def test_list_empty_state(self, client_as_admin):
        """READ — Empty user list shows a helpful message, not a crash."""
        with patch('app.routes.userRoutes.list_users_ctrl', return_value=[]):
            resp = client_as_admin.get('/users/')
        assert resp.status_code == 200
        assert b'No users found' in resp.data

    def test_list_search_filter_passed_to_controller(self, client_as_admin):
        """READ — Search query param is passed through to the controller."""
        with patch('app.routes.userRoutes.list_users_ctrl', return_value=[]) as mock_ctrl:
            client_as_admin.get('/users/?search=admin&role=Admin&status=active')
            mock_ctrl.assert_called_once_with('admin', 'Admin', 'active')


class TestUserCreate:
    def test_create_form_accessible_to_admin(self, client_as_admin):
        """CREATE — Admin can access the create form."""
        resp = client_as_admin.get('/users/create')
        assert resp.status_code == 200
        assert b'Add new user' in resp.data

    def test_create_form_blocked_for_readonly(self, client_as_readonly):
        """CREATE — ReadOnly is blocked with 403."""
        resp = client_as_readonly.get('/users/create')
        assert resp.status_code == 403

    def test_create_form_blocked_for_manager(self, client_as_manager):
        """CREATE — Manager is also blocked (Admin-only operation)."""
        resp = client_as_manager.get('/users/create')
        assert resp.status_code == 403

    def test_create_success_redirects(self, client_as_admin):
        """CREATE — Valid form submission creates user and redirects."""
        with patch('app.routes.userRoutes.create_user_ctrl', return_value=(True, 'User created.')):
            resp = client_as_admin.post('/users/create', data={
                'username': 'newuser', 'email': 'new@vertextech.com',
                'password': 'Secure@123', 'department': 'QA', 'role': 'ReadOnly'
            })
        assert resp.status_code == 302
        assert '/users/' in resp.headers['Location']

    def test_create_failure_stays_on_form(self, client_as_admin):
        """CREATE — Validation failure re-renders the form with error message."""
        with patch('app.routes.userRoutes.create_user_ctrl', return_value=(False, 'Username already taken.')):
            resp = client_as_admin.post('/users/create', data={
                'username': 'admin', 'email': 'admin@vertextech.com',
                'password': 'Secure@123', 'department': 'IT', 'role': 'Admin'
            })
        assert resp.status_code == 200
        assert b'Username already taken' in resp.data


class TestUserEdit:
    def test_edit_form_preloaded_for_admin(self, client_as_admin):
        """UPDATE — Edit form renders pre-filled with existing user data."""
        with patch('app.routes.userRoutes.get_user_ctrl', return_value=FAKE_USER):
            resp = client_as_admin.get('/users/1/edit')
        assert resp.status_code == 200
        assert b'admin' in resp.data

    def test_edit_404_for_missing_user(self, client_as_admin):
        """UPDATE — Editing a non-existent user redirects with error flash."""
        with patch('app.routes.userRoutes.get_user_ctrl', return_value=None):
            resp = client_as_admin.get('/users/999/edit')
        assert resp.status_code == 302

    def test_edit_success_redirects(self, client_as_admin):
        """UPDATE — Valid edit form redirects to user list."""
        with patch('app.routes.userRoutes.get_user_ctrl', return_value=FAKE_USER), \
             patch('app.routes.userRoutes.update_user_ctrl', return_value=(True, 'Updated.')):
            resp = client_as_admin.post('/users/1/edit', data={
                'username': 'admin', 'email': 'admin@vertextech.com',
                'department': 'IT Security', 'role': 'Admin', 'is_active': 'on'
            })
        assert resp.status_code == 302

    def test_edit_blocked_for_readonly(self, client_as_readonly):
        """UPDATE — ReadOnly cannot access edit form (403)."""
        resp = client_as_readonly.get('/users/1/edit')
        assert resp.status_code == 403


class TestUserDeactivate:
    def test_deactivate_success(self, client_as_admin):
        """DELETE (soft) — Admin can deactivate a user."""
        with patch('app.routes.userRoutes.deactivate_user_ctrl', return_value=(True, 'User deactivated.')):
            resp = client_as_admin.post('/users/1/deactivate')
        assert resp.status_code == 302

    def test_deactivate_blocked_for_readonly(self, client_as_readonly):
        """DELETE (soft) — ReadOnly cannot deactivate users."""
        resp = client_as_readonly.post('/users/1/deactivate')
        assert resp.status_code == 403


class TestUserControllerValidation:
    """Unit tests for controller-level validation — no DB or HTTP involved."""

    def test_empty_username_rejected(self):
        from app.controllers.userController import create_user_ctrl
        ok, msg = create_user_ctrl(
            {'username': '', 'email': 'a@b.com', 'password': 'Secure@123', 'role': 'ReadOnly'},
            actor_id=1, ip_address='127.0.0.1'
        )
        assert ok is False
        assert 'required' in msg.lower()

    def test_short_password_rejected(self):
        from app.controllers.userController import create_user_ctrl
        ok, msg = create_user_ctrl(
            {'username': 'user1', 'email': 'a@b.com', 'password': 'short', 'role': 'ReadOnly'},
            actor_id=1, ip_address='127.0.0.1'
        )
        assert ok is False
        assert '8 characters' in msg

    def test_invalid_role_rejected(self):
        from app.controllers.userController import create_user_ctrl
        ok, msg = create_user_ctrl(
            {'username': 'user1', 'email': 'a@b.com', 'password': 'Secure@123', 'role': 'SuperAdmin'},
            actor_id=1, ip_address='127.0.0.1'
        )
        assert ok is False
        assert 'Invalid role' in msg
