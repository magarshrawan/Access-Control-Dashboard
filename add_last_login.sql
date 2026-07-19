-- Running this in phpMyAdmin SQL tab to add last_login column
-- Only needed if  users table doesn't already have it

ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login DATETIME DEFAULT NULL;
