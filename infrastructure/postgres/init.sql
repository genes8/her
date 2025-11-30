-- ============================================
-- HEALTHEQUIROUTE DATABASE INITIALIZATION
-- ============================================
-- This script runs automatically when PostgreSQL container starts
-- It enables required extensions for PostGIS and UUID support

-- Enable PostGIS extension for geospatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify extensions are installed
DO $$
BEGIN
    RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
    RAISE NOTICE 'UUID extension enabled';
    RAISE NOTICE 'pg_trgm extension enabled';
END $$;
