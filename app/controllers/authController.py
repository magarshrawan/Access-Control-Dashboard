from flask import request
from app import bcrypt
from app.auth import AuthUser
from app.models.userModel import get_user_by_username
from app.models.auditModel import log_action


def authenticate(username, password):
    ip = request.remote_addr
    user_row = get_user_by_username(username)
    if not user_row:
        log_action(None, 'LOGIN_FAILED', resource_type='user', ip_address=ip)
        return None, "Invalid username or password."
    if not user_row['is_active']:
        log_action(user_row['id'], 'LOGIN_BLOCKED_INACTIVE', resource_type='user', ip_address=ip)
        return None, "This account has been deactivated. Contact an administrator."
    if not bcrypt.check_password_hash(user_row['password_hash'], password):
        log_action(user_row['id'], 'LOGIN_FAILED', resource_type='user', ip_address=ip)
        return None, "Invalid username or password."
    log_action(user_row['id'], 'LOGIN_SUCCESS', resource_type='user', ip_address=ip)
    return AuthUser(user_row['id'], user_row['username'], user_row['email'], user_row['role'], user_row['is_active']), "Logged in successfully."
