-- ============================================================
-- SQL SCRIPT: Users Table Creation
-- Purpose: Authentication and authorization system
-- Author: Exam Scheduling System
-- ============================================================

-- Create users table for authentication
-- This table stores login credentials and role information
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'professeur', 'etudiant')),
    linked_id INTEGER,  -- References professeur.id or etudiant.id based on role
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Ensure linked_id is provided for non-admin users
    CONSTRAINT chk_linked_id CHECK (
        (role = 'admin' AND linked_id IS NULL) OR
        (role IN ('professeur', 'etudiant') AND linked_id IS NOT NULL)
    )
);

-- Create index on username for faster login lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Create index on role for role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Add foreign key constraints if needed (optional, depends on your schema)
-- Note: These are commented out as they may not be needed if tables don't exist yet
-- ALTER TABLE users ADD CONSTRAINT fk_professeur 
--     FOREIGN KEY (linked_id) REFERENCES professeur(id) 
--     ON DELETE CASCADE;
-- 
-- ALTER TABLE users ADD CONSTRAINT fk_etudiant 
--     FOREIGN KEY (linked_id) REFERENCES etudiant(id) 
--     ON DELETE CASCADE;

-- ============================================================
-- SAMPLE DATA (for testing - remove in production)
-- ============================================================
-- Note: These are example hashes. In production, use bcrypt to generate proper hashes
-- Default password for all test accounts: "password123"
-- 
-- To create a proper hash, use Python:
-- import bcrypt
-- bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
-- ============================================================

-- Example admin user (password: password123)
-- INSERT INTO users (username, password_hash, role, linked_id) VALUES
-- ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5x5K5Xe', 'admin', NULL);

-- Example professeur user (password: password123)
-- Replace 1 with actual professeur.id
-- INSERT INTO users (username, password_hash, role, linked_id) VALUES
-- ('prof1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5x5K5Xe', 'professeur', 1);

-- Example etudiant user (password: password123)
-- Replace 1 with actual etudiant.id
-- INSERT INTO users (username, password_hash, role, linked_id) VALUES
-- ('etud1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5x5K5Xe', 'etudiant', 1);
