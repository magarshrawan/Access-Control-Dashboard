from app.database import get_db


def get_all_roles():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, r.name, r.description, r.created_at,
               COUNT(DISTINCT rp.permission_id) AS permission_count,
               (SELECT COUNT(*) FROM users u WHERE u.role = r.name) AS user_count
        FROM roles r
        LEFT JOIN role_permissions rp ON rp.role_id = r.id
        GROUP BY r.id, r.name, r.description, r.created_at
        ORDER BY r.id
    """)
    roles = cursor.fetchall()
    cursor.close(); db.close()
    return roles


def get_role_by_id(role_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
    role = cursor.fetchone()
    cursor.close(); db.close()
    return role


def get_all_permissions():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM permissions ORDER BY resource, action")
    perms = cursor.fetchall()
    cursor.close(); db.close()
    return perms


def get_permission_ids_for_role(role_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT permission_id FROM role_permissions WHERE role_id = %s", (role_id,))
    ids = {row[0] for row in cursor.fetchall()}
    cursor.close(); db.close()
    return ids


def create_role(name, description, permission_ids):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO roles (name, description) VALUES (%s, %s)", (name, description))
    role_id = cursor.lastrowid
    for pid in permission_ids:
        cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)", (role_id, pid))
    db.commit()
    cursor.close(); db.close()
    return role_id


def update_role(role_id, name, description, permission_ids):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE roles SET name=%s, description=%s WHERE id=%s", (name, description, role_id))
    cursor.execute("DELETE FROM role_permissions WHERE role_id = %s", (role_id,))
    for pid in permission_ids:
        cursor.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)", (role_id, pid))
    db.commit()
    cursor.close(); db.close()


def delete_role(role_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
    db.commit()
    cursor.close(); db.close()
