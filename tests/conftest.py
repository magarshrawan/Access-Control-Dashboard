import pytest
from datetime import datetime
from unittest.mock import patch
from app import create_app
from app.auth import AuthUser


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def admin_user():
    return AuthUser(1, 'admin', 'admin@vertextech.com', 'Admin', True)


@pytest.fixture
def manager_user():
    return AuthUser(2, 'r.thapa', 'r.thapa@vertextech.com', 'Manager', True)


@pytest.fixture
def readonly_user():
    return AuthUser(4, 'b.karki', 'b.karki@vertextech.com', 'ReadOnly', True)


@pytest.fixture
def client_as_admin(app, admin_user):
    from app import login_manager
    login_manager._user_callback = lambda uid: admin_user
    with app.test_client() as c:
        with c.session_transaction() as s:
            s['_user_id'] = '1'
            s['_fresh'] = True
        yield c


@pytest.fixture
def client_as_manager(app, manager_user):
    from app import login_manager
    login_manager._user_callback = lambda uid: manager_user
    with app.test_client() as c:
        with c.session_transaction() as s:
            s['_user_id'] = '2'
            s['_fresh'] = True
        yield c


@pytest.fixture
def client_as_readonly(app, readonly_user):
    from app import login_manager
    login_manager._user_callback = lambda uid: readonly_user
    with app.test_client() as c:
        with c.session_transaction() as s:
            s['_user_id'] = '4'
            s['_fresh'] = True
        yield c


@pytest.fixture
def client_no_auth(app):
    with app.test_client() as c:
        yield c


# ── Shared fake data ──────────────────────────────────────────
FAKE_USER = {
    'id': 1, 'username': 'admin', 'email': 'admin@vertextech.com',
    'department': 'IT Security', 'role': 'Admin', 'is_active': True,
    'created_at': datetime(2026, 6, 1)
}

FAKE_ROLE = {
    'id': 1, 'name': 'Admin', 'description': 'Full access',
    'created_at': datetime(2026, 1, 1), 'permission_count': 12, 'user_count': 1
}

FAKE_PERMS = [
    {'id': 1, 'name': 'users:read',  'resource': 'users', 'action': 'read'},
    {'id': 2, 'name': 'users:write', 'resource': 'users', 'action': 'write'},
]

FAKE_REQUEST = {
    'id': 1, 'requester_id': 2, 'resource': 'Prod DB (read)',
    'justification': 'Q2 audit preparation work', 'status': 'pending',
    'reviewer_id': None, 'reviewer_notes': None, 'expires_at': None,
    'created_at': datetime(2026, 6, 1),
    'requester_name': 'r.thapa', 'reviewer_name': None
}

FAKE_LOG = {
    'id': 1, 'user_id': 1, 'action': 'LOGIN_SUCCESS', 'resource_type': 'user',
    'resource_id': 1, 'ip_address': '10.0.0.5', 'flagged': False,
    'flag_reason': None, 'timestamp': datetime(2026, 6, 1, 9, 0, 0),
    'username': 'admin'
}
