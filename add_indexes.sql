-- =========================================================
-- Vertex Technologies Access Control Dashboard
-- (Running this in phpMyAdmin SQL tab)
-- =========================================================

-- Users table indexes
ALTER TABLE users ADD INDEX IF NOT EXISTS idx_users_username (username);
ALTER TABLE users ADD INDEX IF NOT EXISTS idx_users_email (email);
ALTER TABLE users ADD INDEX IF NOT EXISTS idx_users_role (role);
ALTER TABLE users ADD INDEX IF NOT EXISTS idx_users_is_active (is_active);
ALTER TABLE users ADD INDEX IF NOT EXISTS idx_users_department (department);

-- Roles table indexes
ALTER TABLE roles ADD INDEX IF NOT EXISTS idx_roles_name (name);

-- Access requests indexes
ALTER TABLE access_requests ADD INDEX IF NOT EXISTS idx_requests_status (status);
ALTER TABLE access_requests ADD INDEX IF NOT EXISTS idx_requests_requester (requester_id);
ALTER TABLE access_requests ADD INDEX IF NOT EXISTS idx_requests_created (created_at);

-- Audit logs indexes
ALTER TABLE audit_logs ADD INDEX IF NOT EXISTS idx_audit_timestamp (timestamp);
ALTER TABLE audit_logs ADD INDEX IF NOT EXISTS idx_audit_user (user_id);
ALTER TABLE audit_logs ADD INDEX IF NOT EXISTS idx_audit_action (action);
ALTER TABLE audit_logs ADD INDEX IF NOT EXISTS idx_audit_flagged (flagged);

-- Role permissions indexes
ALTER TABLE role_permissions ADD INDEX IF NOT EXISTS idx_rp_role (role_id);
ALTER TABLE role_permissions ADD INDEX IF NOT EXISTS idx_rp_permission (permission_id);
