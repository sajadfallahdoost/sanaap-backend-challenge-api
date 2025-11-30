-- Document Management System Database Schema
-- PostgreSQL Database Schema Definition

-- Users Table (extends Django's auth_user)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254) UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    role VARCHAR(10) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT users_role_check CHECK (role IN ('admin', 'editor', 'viewer'))
);

-- Indexes for users table
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    file_path VARCHAR(500) UNIQUE NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    size BIGINT NOT NULL,
    uploaded_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT documents_processing_status_check CHECK (
        processing_status IN ('pending', 'processing', 'completed', 'failed')
    ),
    CONSTRAINT documents_size_check CHECK (size > 0)
);

-- Indexes for documents table
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by_id);
CREATE INDEX idx_documents_file_type ON documents(file_type);
CREATE INDEX idx_documents_file_extension ON documents(file_extension);
CREATE INDEX idx_documents_processing_status ON documents(processing_status);
CREATE INDEX idx_documents_created_at ON documents(created_at);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(20) NOT NULL,
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT DEFAULT '',
    details JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT audit_logs_action_check CHECK (
        action IN (
            'login', 'logout', 'login_failed',
            'document_upload', 'document_view', 'document_download',
            'document_update', 'document_delete',
            'user_create', 'user_update', 'user_role_change',
            'user_delete', 'password_change', 'system_error'
        )
    ),
    CONSTRAINT audit_logs_resource_type_check CHECK (
        resource_type IN ('user', 'document', 'system')
    )
);

-- Indexes for audit_logs table
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_ip_address ON audit_logs(ip_address);

-- Full-text search index for documents
CREATE INDEX idx_documents_title_search ON documents USING gin(to_tsvector('english', title));
CREATE INDEX idx_documents_description_search ON documents USING gin(to_tsvector('english', description));

-- Composite indexes for common queries
CREATE INDEX idx_documents_user_created ON documents(uploaded_by_id, created_at DESC);
CREATE INDEX idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp DESC);

-- Sample Data Insertion
-- Insert admin user (password: admin123)
INSERT INTO users (username, email, password, role, is_staff, is_superuser)
VALUES (
    'admin',
    'admin@example.com',
    'pbkdf2_sha256$600000$...',  -- Use Django's password hasher
    'admin',
    TRUE,
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Insert sample editor user
INSERT INTO users (username, email, password, role)
VALUES (
    'editor',
    'editor@example.com',
    'pbkdf2_sha256$600000$...',
    'editor'
) ON CONFLICT (username) DO NOTHING;

-- Insert sample viewer user
INSERT INTO users (username, email, password, role)
VALUES (
    'viewer',
    'viewer@example.com',
    'pbkdf2_sha256$600000$...',
    'viewer'
) ON CONFLICT (username) DO NOTHING;

-- Database Statistics Views
CREATE OR REPLACE VIEW document_statistics AS
SELECT
    COUNT(*) as total_documents,
    SUM(size) as total_size,
    AVG(size) as average_size,
    COUNT(DISTINCT uploaded_by_id) as unique_uploaders,
    COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed_documents,
    COUNT(CASE WHEN processing_status = 'pending' THEN 1 END) as pending_documents,
    COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed_documents
FROM documents;

-- User Activity View
CREATE OR REPLACE VIEW user_activity AS
SELECT
    u.id,
    u.username,
    u.role,
    COUNT(d.id) as document_count,
    SUM(d.size) as total_upload_size,
    MAX(d.created_at) as last_upload
FROM users u
LEFT JOIN documents d ON u.id = d.uploaded_by_id
GROUP BY u.id, u.username, u.role;

-- Database Maintenance Functions
-- Function to clean old audit logs (older than 1 year)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audit_logs
    WHERE timestamp < NOW() - INTERVAL '1 year';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update document statistics
CREATE OR REPLACE FUNCTION update_document_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on document changes
CREATE TRIGGER trigger_update_document_timestamp
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_document_updated_at();

-- Performance Tuning Recommendations
-- 1. Enable query planner statistics
-- ANALYZE users;
-- ANALYZE documents;
-- ANALYZE audit_logs;

-- 2. Set appropriate autovacuum settings
-- ALTER TABLE documents SET (autovacuum_vacuum_scale_factor = 0.1);
-- ALTER TABLE audit_logs SET (autovacuum_vacuum_scale_factor = 0.05);

-- 3. Connection pooling configuration (via PgBouncer or Django settings)
-- Set in Django: CONN_MAX_AGE = 600

-- Backup and Recovery Notes
-- Regular backups: pg_dump -Fc dms_db > backup.dump
-- Point-in-time recovery: Enable WAL archiving
-- Replication: Set up streaming replication for high availability

