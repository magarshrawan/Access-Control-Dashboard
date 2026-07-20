from app.database import get_db


def get_all_requests(status_filter=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT ar.*, req.username AS requester_name, rev.username AS reviewer_name
        FROM access_requests ar
        JOIN users req ON req.id = ar.requester_id
        LEFT JOIN users rev ON rev.id = ar.reviewer_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        query += " AND ar.status = %s"
        params.append(status_filter)
    query += " ORDER BY ar.created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close(); db.close()
    return rows


def get_request_by_id(request_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ar.*, req.username AS requester_name, rev.username AS reviewer_name
        FROM access_requests ar
        JOIN users req ON req.id = ar.requester_id
        LEFT JOIN users rev ON rev.id = ar.reviewer_id
        WHERE ar.id = %s
    """, (request_id,))
    row = cursor.fetchone()
    cursor.close(); db.close()
    return row


def create_request(requester_id, resource, justification, expires_at=None):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO access_requests (requester_id, resource, justification, expires_at) VALUES (%s,%s,%s,%s)",
        (requester_id, resource, justification, expires_at)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close(); db.close()
    return new_id


def review_request(request_id, reviewer_id, status, reviewer_notes):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE access_requests SET status=%s, reviewer_id=%s, reviewer_notes=%s WHERE id=%s",
        (status, reviewer_id, reviewer_notes, request_id)
    )
    db.commit()
    cursor.close(); db.close()


def revoke_request(request_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM access_requests WHERE id = %s", (request_id,))
    db.commit()
    cursor.close(); db.close()
