-- Install the dblink extension
CREATE EXTENSION IF NOT EXISTS dblink;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'taxi_trip_data') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE taxi_trip_data');
    END IF;
END $$;
