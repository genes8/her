"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-11-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    # Organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('org_type', sa.String(50), nullable=False),
        sa.Column('ods_code', sa.String(10), nullable=True),
        sa.Column('coverage_area', geoalchemy2.types.Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True),
        sa.Column('settings', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ods_code')
    )

    # Teams table
    op.create_table(
        'teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('team_type', sa.String(50), nullable=True),
        sa.Column('base_location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('working_hours', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('nhs_smartcard_id', sa.String(50), nullable=True),
        sa.Column('google_id', sa.String(255), nullable=True),
        sa.Column('preferences', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id')
    )
    op.create_index('idx_users_org', 'users', ['organization_id'])
    op.create_index('idx_users_email', 'users', ['email'])

    # Resources table
    op.create_table(
        'resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('max_visits_per_day', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('skills', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('start_location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('end_location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('working_hours', postgresql.JSONB(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # LSOA table
    op.create_table(
        'lsoa',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lsoa_code', sa.String(20), nullable=False),
        sa.Column('lsoa_name', sa.String(255), nullable=False),
        sa.Column('local_authority_code', sa.String(10), nullable=True),
        sa.Column('local_authority_name', sa.String(255), nullable=True),
        sa.Column('icb_code', sa.String(10), nullable=True),
        sa.Column('icb_name', sa.String(255), nullable=True),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False),
        sa.Column('centroid', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('area_hectares', sa.Numeric(12, 4), nullable=True),
        sa.Column('population_2021', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lsoa_code')
    )
    op.create_index('idx_lsoa_code', 'lsoa', ['lsoa_code'])
    op.create_index('idx_lsoa_icb', 'lsoa', ['icb_code'])
    # Note: GeoAlchemy2 automatically creates GIST index on geometry columns

    # IMD Data table
    op.create_table(
        'imd_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lsoa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data_year', sa.Integer(), nullable=False),
        sa.Column('imd_rank', sa.Integer(), nullable=True),
        sa.Column('imd_decile', sa.Integer(), nullable=True),
        sa.Column('imd_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('income_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('employment_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('education_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('health_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('crime_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('housing_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('environment_score', sa.Numeric(8, 4), nullable=True),
        sa.Column('is_core20', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('imd_decile BETWEEN 1 AND 10', name='check_imd_decile'),
        sa.ForeignKeyConstraint(['lsoa_id'], ['lsoa.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lsoa_id', 'data_year', name='uq_imd_lsoa_year')
    )
    op.create_index('idx_imd_lsoa', 'imd_data', ['lsoa_id'])
    op.create_index('idx_imd_decile', 'imd_data', ['imd_decile'])

    # Demographic Data table
    op.create_table(
        'demographic_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lsoa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data_year', sa.Integer(), nullable=False),
        sa.Column('total_population', sa.Integer(), nullable=True),
        sa.Column('population_0_17', sa.Integer(), nullable=True),
        sa.Column('population_18_64', sa.Integer(), nullable=True),
        sa.Column('population_65_plus', sa.Integer(), nullable=True),
        sa.Column('pct_white', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_asian', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_black', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_mixed', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_other', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_minority', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_english_not_main', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_no_english', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_no_car_household', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_single_parent', sa.Numeric(5, 2), nullable=True),
        sa.Column('pct_lone_pensioner', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lsoa_id'], ['lsoa.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lsoa_id', 'data_year', name='uq_demo_lsoa_year')
    )
    op.create_index('idx_demo_lsoa', 'demographic_data', ['lsoa_id'])

    # Clinical Data table
    op.create_table(
        'clinical_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lsoa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('gp_practice_code', sa.String(10), nullable=True),
        sa.Column('data_period', sa.String(20), nullable=True),
        sa.Column('diabetes_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('hypertension_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('copd_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('asthma_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('chd_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('stroke_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('cancer_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('mental_health_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('dementia_prevalence', sa.Numeric(6, 2), nullable=True),
        sa.Column('emergency_admissions_rate', sa.Numeric(8, 2), nullable=True),
        sa.Column('a_and_e_attendance_rate', sa.Numeric(8, 2), nullable=True),
        sa.Column('clinical_risk_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lsoa_id'], ['lsoa.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_clinical_lsoa', 'clinical_data', ['lsoa_id'])
    op.create_index('idx_clinical_period', 'clinical_data', ['data_period'])

    # Accessibility Data table
    op.create_table(
        'accessibility_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lsoa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('time_to_nearest_gp', sa.Integer(), nullable=True),
        sa.Column('time_to_nearest_hospital', sa.Integer(), nullable=True),
        sa.Column('time_to_nearest_pharmacy', sa.Integer(), nullable=True),
        sa.Column('public_transport_accessibility_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('distance_to_nearest_gp', sa.Numeric(8, 2), nullable=True),
        sa.Column('distance_to_nearest_hospital', sa.Numeric(8, 2), nullable=True),
        sa.Column('access_category', sa.String(20), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lsoa_id'], ['lsoa.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_access_lsoa', 'accessibility_data', ['lsoa_id'])

    # DEX Priority Scores table
    op.create_table(
        'dex_priority_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lsoa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('calculation_date', sa.Date(), nullable=False),
        sa.Column('model_version', sa.String(20), nullable=False),
        sa.Column('clinical_risk_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('social_vulnerability_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('accessibility_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('priority_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('priority_label', sa.String(20), nullable=False),
        sa.Column('explanation_text', sa.Text(), nullable=False),
        sa.Column('contributing_factors', postgresql.JSONB(), nullable=True),
        sa.Column('requires_translator', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_specialist', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('min_visit_time_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['lsoa_id'], ['lsoa.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lsoa_id', 'calculation_date', 'model_version', name='uq_dex_lsoa_date_version')
    )
    op.create_index('idx_dex_lsoa', 'dex_priority_scores', ['lsoa_id'])
    op.create_index('idx_dex_priority', 'dex_priority_scores', [sa.text('priority_score DESC')])
    op.create_index('idx_dex_label', 'dex_priority_scores', ['priority_label'])
    op.create_index('idx_dex_date', 'dex_priority_scores', ['calculation_date'])

    # DEX Model Config table
    op.create_table(
        'dex_model_config',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('model_version', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('clinical_weight', sa.Numeric(4, 2), nullable=False, server_default='0.40'),
        sa.Column('social_weight', sa.Numeric(4, 2), nullable=False, server_default='0.35'),
        sa.Column('accessibility_weight', sa.Numeric(4, 2), nullable=False, server_default='0.25'),
        sa.Column('fuzzy_rules', postgresql.JSONB(), nullable=False),
        sa.Column('aggregation_rules', postgresql.JSONB(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint('clinical_weight + social_weight + accessibility_weight BETWEEN 0.99 AND 1.01', name='weights_sum_to_one'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_version')
    )

    # Visit Locations table
    op.create_table(
        'visit_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lsoa_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('postcode', sa.String(10), nullable=False),
        sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('location_type', sa.String(50), nullable=True),
        sa.Column('required_skills', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('time_windows', postgresql.JSONB(), nullable=True),
        sa.Column('priority_override', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['lsoa_id'], ['lsoa.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    # Note: GeoAlchemy2 automatically creates GIST index on geometry columns
    op.create_index('idx_visit_loc_lsoa', 'visit_locations', ['lsoa_id'])

    # Route Plans table
    op.create_table(
        'route_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('plan_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='DRAFT'),
        sa.Column('optimization_config', postgresql.JSONB(), nullable=True),
        sa.Column('total_resources', sa.Integer(), nullable=True),
        sa.Column('total_visits', sa.Integer(), nullable=True),
        sa.Column('total_distance_km', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('equity_coverage_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('optimized_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_route_plan_date', 'route_plans', ['plan_date'])
    op.create_index('idx_route_plan_org', 'route_plans', ['organization_id'])

    # Route Assignments table
    op.create_table(
        'route_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('route_plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('route_geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326), nullable=True),
        sa.Column('sequence_count', sa.Integer(), nullable=True),
        sa.Column('total_distance_km', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('estimated_start_time', sa.Time(), nullable=True),
        sa.Column('estimated_end_time', sa.Time(), nullable=True),
        sa.Column('total_priority_score', sa.Numeric(10, 2), nullable=True),
        sa.Column('core20_visits_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['route_plan_id'], ['route_plans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Route Stops table
    op.create_table(
        'route_stops',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('route_assignment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('visit_location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stop_sequence', sa.Integer(), nullable=False),
        sa.Column('estimated_arrival', sa.Time(), nullable=True),
        sa.Column('estimated_departure', sa.Time(), nullable=True),
        sa.Column('priority_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('priority_label', sa.String(20), nullable=True),
        sa.Column('actual_arrival', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_departure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['route_assignment_id'], ['route_assignments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['visit_location_id'], ['visit_locations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_route_stops_assignment', 'route_stops', ['route_assignment_id'])
    op.create_index('idx_route_stops_sequence', 'route_stops', ['route_assignment_id', 'stop_sequence'])

    # Audit Log table
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_timestamp', 'audit_log', ['timestamp'])
    op.create_index('idx_audit_user', 'audit_log', ['user_id'])
    op.create_index('idx_audit_entity', 'audit_log', ['entity_type', 'entity_id'])


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('route_stops')
    op.drop_table('route_assignments')
    op.drop_table('route_plans')
    op.drop_table('visit_locations')
    op.drop_table('dex_model_config')
    op.drop_table('dex_priority_scores')
    op.drop_table('accessibility_data')
    op.drop_table('clinical_data')
    op.drop_table('demographic_data')
    op.drop_table('imd_data')
    op.drop_table('lsoa')
    op.drop_table('resources')
    op.drop_table('users')
    op.drop_table('teams')
    op.drop_table('organizations')
