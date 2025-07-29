"""Initial security setup

Revision ID: 001_initial_security
Create Date: 2025-01-29 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = "001_initial_security"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Apply security enhancements"""
    # Create audit log table for HIPAA compliance
    op.create_table('audit_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('timestamp', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('session_id', sa.String(32), nullable=True),
        sa.Column('details', sa.JSON, nullable=True),
    )
    
    # Create indexes for audit table
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_timestamp', 'audit_log', ['timestamp'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_resource', 'audit_log', ['resource_type', 'resource_id'])
    
    # Add security fields to users table (if it doesn't exist, create it)
    try:
        # Check if users table exists
        op.add_column('users', sa.Column('last_login', sa.DateTime, nullable=True))
        op.add_column('users', sa.Column('failed_attempts', sa.Integer, default=0, nullable=False))
        op.add_column('users', sa.Column('locked_until', sa.DateTime, nullable=True))
        op.add_column('users', sa.Column('password_changed_at', sa.DateTime, nullable=True))
        
        # Add indexes for security fields
        op.create_index('ix_users_last_login', 'users', ['last_login'])
        op.create_index('ix_users_locked_until', 'users', ['locked_until'])
        
    except Exception:
        # Users table doesn't exist, create it with security fields
        op.create_table('users',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
            sa.Column('password_hash', sa.String(255), nullable=False),
            sa.Column('first_name', sa.String(100), nullable=False),
            sa.Column('last_name', sa.String(100), nullable=False),
            sa.Column('role', sa.String(50), nullable=False, default='patient'),
            sa.Column('is_active', sa.Boolean, default=True, nullable=False),
            sa.Column('is_verified', sa.Boolean, default=False, nullable=False),
            sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
            # Security enhancements
            sa.Column('last_login', sa.DateTime, nullable=True),
            sa.Column('failed_attempts', sa.Integer, default=0, nullable=False),
            sa.Column('locked_until', sa.DateTime, nullable=True),
            sa.Column('password_changed_at', sa.DateTime, nullable=True),
        )
    
    # Add encryption support fields to patients table
    try:
        op.add_column('patients', sa.Column('name_hash', sa.String(64), nullable=True, index=True))
        op.add_column('patients', sa.Column('cpf_hash', sa.String(64), nullable=True, index=True))
        op.add_column('patients', sa.Column('data_encryption_version', sa.Integer, default=1, nullable=False))
        
        # Add indexes for searchable hashes
        op.create_index('ix_patients_name_hash', 'patients', ['name_hash'])
        op.create_index('ix_patients_cpf_hash', 'patients', ['cpf_hash'])
        
    except Exception:
        # Patients table doesn't exist yet - this is fine for initial setup
        pass

def downgrade():
    """Remove security enhancements"""
    # Remove audit log table
    op.drop_table('audit_log')
    
    # Remove security columns from users (if they exist)
    try:
        op.drop_index('ix_users_last_login', 'users')
        op.drop_index('ix_users_locked_until', 'users')
        op.drop_column('users', 'last_login')
        op.drop_column('users', 'failed_attempts')
        op.drop_column('users', 'locked_until')
        op.drop_column('users', 'password_changed_at')
    except Exception:
        pass
    
    # Remove encryption fields from patients (if they exist)
    try:
        op.drop_index('ix_patients_name_hash', 'patients')
        op.drop_index('ix_patients_cpf_hash', 'patients')
        op.drop_column('patients', 'name_hash')
        op.drop_column('patients', 'cpf_hash')
        op.drop_column('patients', 'data_encryption_version')
    except Exception:
        pass