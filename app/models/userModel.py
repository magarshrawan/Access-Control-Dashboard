from app.database import get_db


def get_all_users(search=None, role_filter=None, status_filter=None, dept_filter=None):
    """READ — list users with optional filters including department."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if search:
        query += " AND (username LIKE %s OR email LIKE %s OR department LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if role_filter:
        query += " AND role = %s"
        params.append(role_filter)
    if status_filter == 'active':
        query += " AND is_active = TRUE"
    elif status_filter == 'inactive':
        query += " AND is_active = FALSE"
    if dept_filter:
        query += " AND department = %s"
        params.append(dept_filter)

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users


def get_all_departments():
    """READ — get distinct departments for the filter dropdown."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT DISTINCT department FROM users "
        "WHERE department IS NOT NULL AND department != '' "
        "ORDER BY department"
    )
    depts = [row['department'] for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return depts


def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user


def get_user_by_username(username):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user


def create_user(username, email, password_hash, department, role):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, department, role) VALUES (%s,%s,%s,%s,%s)",
        (username, email, password_hash, department, role)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return new_id


def update_user(user_id, username, email, department, role, is_active):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET username=%s, email=%s, department=%s, role=%s, is_active=%s WHERE id=%s",
        (username, email, department, role, is_active, user_id)
    )
    db.commit()
    cursor.close()
    db.close()


def deactivate_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET is_active = FALSE WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()


def change_password(user_id, new_password_hash):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (new_password_hash, user_id)
    )
    db.commit()
    cursor.close()
    db.close()


def update_last_login(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,)
    )
    db.commit()
    cursor.close()
    db.close()
