-- =========================================================
-- Vertex Technologies — Access Control Dashboard
-- Run: mysql -u root -p < schema.sql
-- =========================================================

CREATE DATABASE IF NOT EXISTS vertex_access_control;
USE vertex_access_control;

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(80)  UNIQUE NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    department    VARCHAR(80),
    role          VARCHAR(50) DEFAULT 'ReadOnly',
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(80) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action   VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id       INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS access_requests (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    requester_id   INT NOT NULL,
    resource       VARCHAR(150) NOT NULL,
    justification  TEXT NOT NULL,
    status         ENUM('pending','approved','denied') DEFAULT 'pending',
    reviewer_id    INT,
    reviewer_notes TEXT,
    expires_at     DATETIME,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id)  REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT,
    action        VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id   INT,
    ip_address    VARCHAR(45),
    flagged       BOOLEAN DEFAULT FALSE,
    flag_reason   TEXT,
    timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Roles
INSERT IGNORE INTO roles (name, description) VALUES
    ('Admin',    'Full system access across all modules'),
    ('Manager',  'Can review and approve/deny access requests'),
    ('Analyst',  'Can view and flag audit log entries'),
    ('ReadOnly', 'View-only access to the dashboard');

-- Permissions
INSERT IGNORE INTO permissions (name, resource, action) VALUES
    ('users:read',      'users',    'read'),
    ('users:write',     'users',    'write'),
    ('users:delete',    'users',    'delete'),
    ('roles:read',      'roles',    'read'),
    ('roles:write',     'roles',    'write'),
    ('roles:delete',    'roles',    'delete'),
    ('requests:read',   'requests', 'read'),
    ('requests:review', 'requests', 'write'),
    ('requests:revoke', 'requests', 'delete'),
    ('audit:read',      'audit',    'read'),
    ('audit:flag',      'audit',    'write'),
    ('audit:purge',     'audit',    'delete');

-- Admin gets everything
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name='Admin'), id FROM permissions;

-- Manager
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name='Manager'), id FROM permissions
WHERE name IN ('users:read','roles:read','requests:read','requests:review','audit:read');

-- Analyst
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name='Analyst'), id FROM permissions
WHERE name IN ('users:read','roles:read','requests:read','audit:read','audit:flag');

-- ReadOnly
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT (SELECT id FROM roles WHERE name='ReadOnly'), id FROM permissions
WHERE action='read';

-- Seed users  (password for all: Admin@123)
INSERT IGNORE INTO users (username, email, password_hash, department, role, is_active) VALUES
('admin',    'admin@vertextech.com',    '$2b$12$m0Oc.iOed5XN1JkP/UVO3urQPu1MphQ40G3IWROkJUM5a3KWO9LX.', 'IT Security', 'Admin',    TRUE),
('r.thapa',  'r.thapa@vertextech.com',  '$2b$12$m0Oc.iOed5XN1JkP/UVO3urQPu1MphQ40G3IWROkJUM5a3KWO9LX.', 'Engineering', 'Manager',  TRUE),
('s.gurung', 's.gurung@vertextech.com', '$2b$12$m0Oc.iOed5XN1JkP/UVO3urQPu1MphQ40G3IWROkJUM5a3KWO9LX.', 'DevOps',      'Analyst',  TRUE),
('b.karki',  'b.karki@vertextech.com',  '$2b$12$m0Oc.iOed5XN1JkP/UVO3urQPu1MphQ40G3IWROkJUM5a3KWO9LX.', 'QA',          'ReadOnly', TRUE),
('n.basnet', 'n.basnet@vertextech.com', '$2b$12$m0Oc.iOed5XN1JkP/UVO3urQPu1MphQ40G3IWROkJUM5a3KWO9LX.', 'Product',     'ReadOnly', FALSE);
