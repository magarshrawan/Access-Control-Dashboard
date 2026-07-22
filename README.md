# Vertex Technologies — Access Control Dashboard

A full-stack web-based Identity and Access Management (IAM) system built with Python, Flask, Jinja2, HTML/CSS/JavaScript, and MySQL. Developed as a coursework project for the Web Technology module at Softwarica College of IT & E-Commerce.

---

## Features

### 4 CRUD Sections (16 features total)

| Section | Create | Read | Update | Delete |
|---|---|---|---|---|
| **User Management** | Register user | List + search users | Edit profile + role | Deactivate (soft delete) |
| **Roles & Permissions** | Create role | View roles matrix | Edit permissions | Delete role |
| **Access Requests** | Submit request | View request queue | Approve / Deny | Revoke access |
| **Audit Log** | Auto-log events | Search + filter logs | Flag suspicious entry | Purge old logs |

### Security Features
- **bcrypt password hashing** via Flask-Bcrypt
- **Role-Based Access Control (RBAC)** via custom `@role_required()` decorator
- **Flask-Login session management** with inactive user blocking
- **Environment variables** via `.env` — secrets never hardcoded
- **Parameterised SQL queries** — SQL injection prevention
- **Audit logging** on every significant action with IP address and timestamp
- **Soft delete** — users deactivated, never hard-deleted

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x + Flask 3.0 |
| Templating | Jinja2 |
| Frontend | HTML5, CSS3, JavaScript |
| Database | MySQL 8.0 |
| Auth | Flask-Login + Flask-Bcrypt |
| Testing | pytest |
| Icons | Tabler Icons |
| Charts | Chart.js |

---

## Project Structure

```
vertex_access_control/
├── run.py                        # Entry point
├── schema.sql                    # MySQL schema + seed data
├── requirements.txt
├── .env                          # Secrets (not committed)
├── .env.example                  # Template for .env
├── add_indexes.sql               # Performance indexes
├── add_last_login.sql            # Schema migration
├── app/
│   ├── __init__.py               # App factory
│   ├── auth.py                   # Flask-Login + RBAC decorator
│   ├── database.py               # MySQL connection helper
│   ├── controllers/              # Business logic + validation
│   ├── models/                   # SQL queries (data access layer)
│   ├── routes/                   # Flask Blueprints (URL definitions)
│   ├── static/
│   │   ├── css/main.css
│   │   ├── css/responsive.css
│   │   ├── css/profile.css
│   │   ├── css/errors.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── partials/sidebar.html
│       ├── auth/
│       ├── users/
│       ├── roles/
│       ├── requests/
│       ├── audit/
│       └── errors/
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_users.py
    ├── test_roles.py
    ├── test_requests.py
    └── test_audit.py
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL 8.0 (via XAMPP or standalone)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/vertex_access_control.git
cd vertex_access_control
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` with your MySQL credentials:
```
SECRET_KEY=your-random-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=vertex_access_control
```

### 5. Set up the database
Open phpMyAdmin or MySQL shell and run:
```sql
source schema.sql
source add_last_login.sql
source add_indexes.sql
```

### 6. Run the application
```bash
python run.py
```

Visit: **http://127.0.0.1:5000**

---

## Default Login Credentials

| Username | Password | Role |
|---|---|---|
| admin | Admin@123 | Admin |
| r.thapa | Admin@123 | Manager |
| s.gurung | Admin@123 | Analyst |
| b.karki | Admin@123 | ReadOnly |

---

## Role Permissions

| Permission | Admin | Manager | Analyst | ReadOnly |
|---|---|---|---|---|
| View users | ✅ | ✅ | ✅ | ✅ |
| Create/edit users | ✅ | ❌ | ❌ | ❌ |
| Manage roles | ✅ | ❌ | ❌ | ❌ |
| Submit access requests | ✅ | ✅ | ✅ | ✅ |
| Review requests | ✅ | ✅ | ❌ | ❌ |
| Revoke access | ✅ | ❌ | ❌ | ❌ |
| View audit log | ✅ | ✅ | ✅ | ❌ |
| Flag audit entries | ✅ | ❌ | ✅ | ❌ |
| Purge audit logs | ✅ | ❌ | ❌ | ❌ |

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Expected output: **70 tests passing**

---

## Database Schema

6 tables in MySQL:

- `users` — core identity table
- `roles` — role definitions
- `permissions` — granular resource:action permissions
- `role_permissions` — many-to-many junction table
- `access_requests` — request workflow with approval tracking
- `audit_logs` — immutable event log with flag support

---

## Git Commit Convention

This project uses conventional commits:

- `feat:` — new feature
- `fix:` — bug fix
- `style:` — UI/CSS changes
- `refactor:` — code restructure
- `test:` — test additions
- `docs:` — documentation
- `chore:` — config/dependency changes
- `db:` — database schema changes

---

## Limitations

- No multi-factor authentication (MFA) — schema supports it but not implemented
- No email notifications for access request decisions
- Per-request MySQL connections (no connection pooling)
- No server-side pagination for large datasets
- Single-server Flask deployment (no Gunicorn/Nginx)

---

## References

- Grinberg, M. (2018) *Flask Web Development*. 2nd edn. O'Reilly Media.
- OWASP Foundation (2021) *OWASP Top Ten 2021*. https://owasp.org/Top10/
- Pallets Projects (2024) *Flask Documentation*. https://flask.palletsprojects.com/
- Oracle Corporation (2024) *MySQL 8.0 Reference Manual*. https://dev.mysql.com/doc/
- NIST (2020) *SP 800-207: Zero Trust Architecture*. https://doi.org/10.6028/NIST.SP.800-207
- Sandhu, R. S. et al. (1996) 'Role-Based Access Control Models', *IEEE Computer*, 29(2), pp. 38–47.

---

*Vertex Technologies Access Control Dashboard — ST5036CMD Coursework*
