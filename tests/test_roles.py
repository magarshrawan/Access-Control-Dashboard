"""
Tests for Section 2 — Roles & Permissions (CRUD).
"""
from unittest.mock import patch
from tests.conftest import FAKE_ROLE, FAKE_PERMS


class TestRoleList:
    def test_list_renders_for_admin(self, client_as_admin):
        """READ — Admin can see the roles matrix."""
        with patch('app.routes.roleRoutes.list_roles_ctrl', return_value=[FAKE_ROLE]):
            resp = client_as_admin.get('/roles/')
        assert resp.status_code == 200
        assert b'Admin' in resp.data

    def test_list_renders_for_readonly(self, client_as_readonly):
        """READ — All logged-in users can view roles (read-only)."""
        with patch('app.routes.roleRoutes.list_roles_ctrl', return_value=[FAKE_ROLE]):
            resp = client_as_readonly.get('/roles/')
        assert resp.status_code == 200

    def test_list_empty_state(self, client_as_admin):
        """READ — Empty roles list renders without error."""
        with patch('app.routes.roleRoutes.list_roles_ctrl', return_value=[]):
            resp = client_as_admin.get('/roles/')
        assert resp.status_code == 200
        assert b'No roles defined' in resp.data


class TestRoleCreate:
    def test_create_form_accessible_to_admin(self, client_as_admin):
        """CREATE — Admin can access create form with permission checkboxes."""
        with patch('app.routes.roleRoutes.get_permissions_matrix_ctrl', return_value=(FAKE_PERMS, set())):
            resp = client_as_admin.get('/roles/create')
        assert resp.status_code == 200
        assert b'Add new role' in resp.data

    def test_create_blocked_for_readonly(self, client_as_readonly):
        """CREATE — ReadOnly gets 403."""
        resp = client_as_readonly.get('/roles/create')
        assert resp.status_code == 403

    def test_create_blocked_for_manager(self, client_as_manager):
        """CREATE — Manager gets 403 (Admin-only)."""
        resp = client_as_manager.get('/roles/create')
        assert resp.status_code == 403

    def test_create_success_redirects(self, client_as_admin):
        """CREATE — Valid submission redirects to roles list."""
        with patch('app.routes.roleRoutes.create_role_ctrl', return_value=(True, 'Role created.')), \
             patch('app.routes.roleRoutes.get_permissions_matrix_ctrl', return_value=(FAKE_PERMS, set())):
            resp = client_as_admin.post('/roles/create', data={'name': 'Viewer', 'description': 'View only'})
        assert resp.status_code == 302

    def test_create_duplicate_name_stays_on_form(self, client_as_admin):
        """CREATE — Duplicate role name shows error, stays on form."""
        with patch('app.routes.roleRoutes.create_role_ctrl', return_value=(False, "A role named 'Admin' already exists.")), \
             patch('app.routes.roleRoutes.get_permissions_matrix_ctrl', return_value=(FAKE_PERMS, set())):
            resp = client_as_admin.post('/roles/create', data={'name': 'Admin'})
        assert resp.status_code == 200
        assert b'already exists' in resp.data


class TestRoleEdit:
    def test_edit_form_loads_with_checked_permissions(self, client_as_admin):
        """UPDATE — Edit form shows existing role with its permissions pre-checked."""
        with patch('app.routes.roleRoutes.get_role_ctrl', return_value=FAKE_ROLE), \
             patch('app.routes.roleRoutes.get_permissions_matrix_ctrl', return_value=(FAKE_PERMS, {1})):
            resp = client_as_admin.get('/roles/1/edit')
        assert resp.status_code == 200

    def test_edit_missing_role_redirects(self, client_as_admin):
        """UPDATE — Editing non-existent role redirects with error."""
        with patch('app.routes.roleRoutes.get_role_ctrl', return_value=None):
            resp = client_as_admin.get('/roles/999/edit')
        assert resp.status_code == 302


class TestRoleDelete:
    def test_delete_success(self, client_as_admin):
        """DELETE — Admin can delete a role."""
        with patch('app.routes.roleRoutes.delete_role_ctrl', return_value=(True, 'Role deleted.')):
            resp = client_as_admin.post('/roles/1/delete')
        assert resp.status_code == 302

    def test_delete_blocked_for_manager(self, client_as_manager):
        """DELETE — Manager cannot delete roles."""
        resp = client_as_manager.post('/roles/1/delete')
        assert resp.status_code == 403


class TestRoleControllerValidation:
    def test_empty_role_name_rejected(self, app):
        from app.controllers.roleController import create_role_ctrl
        with app.app_context():
            ok, msg = create_role_ctrl(
                {'name': '', 'description': 'test'},
                actor_id=1, ip_address='127.0.0.1'
            )
        assert ok is False
        assert 'required' in msg.lower()
