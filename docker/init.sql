-- PostgreSQL initialization script for Docker
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE quizbot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'quizbot')\gexec

-- Create user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'quizbot') THEN

      CREATE ROLE quizbot LOGIN PASSWORD 'your_password_here';
   END IF;
END
$do$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE quizbot TO quizbot;

-- Create extensions
\c quizbot;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Log initialization
\echo 'PostgreSQL initialization completed'
