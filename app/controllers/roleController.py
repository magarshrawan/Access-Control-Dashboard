import mysql.connector
from app.models.roleModel import get_all_roles, get_role_by_id, get_all_permissions, get_permission_ids_for_role, create_role, update_role, delete_role
from app.models.auditModel import log_action


def list_roles_ctrl():
    try:
        return get_all_roles()
    except mysql.connector.Error:
        return []


def get_role_ctrl(role_id):
    try:
        return get_role_by_id(role_id)
    except mysql.connector.Error:
        return None


def get_permissions_matrix_ctrl(role_id=None):
    try:
        perms = get_all_permissions()
        assigned = get_permission_ids_for_role(role_id) if role_id else set()
        return perms, assigned
    except mysql.connector.Error:
        return [], set()


def _get_permission_ids(form):
    if hasattr(form, 'getlist'):
        return [int(p) for p in form.getlist('permissions')]
    v = form.get('permissions', [])
    return [int(x) for x in (v if isinstance(v, list) else [v] if v else [])]


def create_role_ctrl(form, actor_id, ip_address):
    name = form.get('name', '').strip()
    description = form.get('description', '').strip()
    permission_ids = _get_permission_ids(form)
    if not name:
        return False, "Role name is required."
    try:
        new_id = create_role(name, description, permission_ids)
        log_action(actor_id, 'ROLE_CREATED', resource_type='role', resource_id=new_id, ip_address=ip_address)
        return True, f"Role '{name}' created successfully."
    except mysql.connector.IntegrityError:
        return False, f"A role named '{name}' already exists."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def update_role_ctrl(role_id, form, actor_id, ip_address):
    name = form.get('name', '').strip()
    description = form.get('description', '').strip()
    permission_ids = _get_permission_ids(form)
    if not name:
        return False, "Role name is required."
    try:
        update_role(role_id, name, description, permission_ids)
        log_action(actor_id, 'ROLE_UPDATED', resource_type='role', resource_id=role_id, ip_address=ip_address)
        return True, f"Role '{name}' updated successfully."
    except mysql.connector.IntegrityError:
        return False, f"A role named '{name}' already exists."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."


def delete_role_ctrl(role_id, actor_id, ip_address):
    try:
        role = get_role_by_id(role_id)
        if not role:
            return False, "Role not found."
        delete_role(role_id)
        log_action(actor_id, 'ROLE_DELETED', resource_type='role', resource_id=role_id, ip_address=ip_address)
        return True, f"Role '{role['name']}' deleted successfully."
    except mysql.connector.Error:
        return False, "A database error occurred. Please try again."
