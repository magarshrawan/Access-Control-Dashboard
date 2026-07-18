import mysql.connector
from app import bcrypt
from app.models.userModel import (
    get_all_users, get_user_by_id, get_user_by_username,
    create_user, update_user, deactivate_user,
    change_password, update_last_login
)
from app.models.auditModel import log_action

VALID_ROLES = ['Admin', 'Manager', 'Analyst', 'ReadOnly']


def list_users_ctrl(search=None, role_filter=None, status_filter=None):
    try:
        return get_all_users(search, role_filter, status_filter)
    except mysql.connector.Error:
        return []


def get_user_ctrl(user_id):
    try:
        return get_user_by_id(user_id)
    except mysql.connector.Error:
        return None


def create_user_ctrl(form, actor_id, ip_address):
    username   = form.get('username', '').strip()
    email      = form.get('email', '').strip()
    password   = form.get('password', '')
    department = form.get('department', '').strip()
    role       = form.get('role', 'ReadOnly')

    if not username or not email or not password:
        return False, "Username, email, and password are required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if role not in VALID_ROLES:
        return False, "Invalid role selected."
    try:
        if get_user_by_username(username):
            return False, f"Username '{username}' is already taken."
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_id = create_user(username, email, password_hash, department, role)
        log_action(actor_id, 'USER_CREATED', resource_type='user',
                   resource_id=new_id, ip_address=ip_address)
        return True, f"User '{username}' created successfully."
    except mysql.connector.IntegrityError:
        return False, "A user with that username or email already exists."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def update_user_ctrl(user_id, form, actor_id, ip_address):
    username   = form.get('username', '').strip()
    email      = form.get('email', '').strip()
    department = form.get('department', '').strip()
    role       = form.get('role', 'ReadOnly')
    is_active  = form.get('is_active') == 'on'

    if not username or not email:
        return False, "Username and email are required."
    if role not in VALID_ROLES:
        return False, "Invalid role selected."
    try:
        update_user(user_id, username, email, department, role, is_active)
        log_action(actor_id, 'USER_UPDATED', resource_type='user',
                   resource_id=user_id, ip_address=ip_address)
        return True, f"User '{username}' updated successfully."
    except mysql.connector.IntegrityError:
        return False, "That username or email is already in use by another account."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def deactivate_user_ctrl(user_id, actor_id, ip_address):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        deactivate_user(user_id)
        log_action(actor_id, 'USER_DEACTIVATED', resource_type='user',
                   resource_id=user_id, ip_address=ip_address)
        return True, f"User '{user['username']}' has been deactivated."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def change_password_ctrl(user_id, form, ip_address):
    """
    Validates and processes a password change request.
    Checks current password, confirms new password matches,
    enforces minimum length, then updates the hash.
    """
    current_password = form.get('current_password', '')
    new_password     = form.get('new_password', '')
    confirm_password = form.get('confirm_password', '')

    if not current_password or not new_password or not confirm_password:
        return False, "All fields are required."

    if len(new_password) < 8:
        return False, "New password must be at least 8 characters long."

    if new_password != confirm_password:
        return False, "New passwords do not match."

    if current_password == new_password:
        return False, "New password must be different from your current password."

    try:
        user = get_user_by_id(user_id)
        if not user:
            return False, "User not found."

        if not bcrypt.check_password_hash(user['password_hash'], current_password):
            return False, "Current password is incorrect."

        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        change_password(user_id, new_hash)
        log_action(user_id, 'PASSWORD_CHANGED', resource_type='user',
                   resource_id=user_id, ip_address=ip_address)
        return True, "Password changed successfully."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def get_profile_ctrl(user_id):
    """Returns the full user profile for the profile page."""
    try:
        return get_user_by_id(user_id)
    except mysql.connector.Error:
        return None
