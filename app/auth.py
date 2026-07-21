from functools import wraps
from flask import abort
from flask_login import UserMixin, current_user
from app import login_manager
from app.database import get_db


class AuthUser(UserMixin):
    def __init__(self, id, username, email, role, is_active):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self._is_active = is_active

    @property
    def is_active(self):
        return self._is_active


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if row:
        return AuthUser(row['id'], row['username'], row['email'], row['role'], row['is_active'])
    return None


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role not in allowed_roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
