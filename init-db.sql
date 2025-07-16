-- Initialize AgriSphere Risk Database

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create additional extensions for geospatial operations
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_farms_location ON farms USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_weather_stations_location ON weather_stations USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_climate_events_affected_area ON climate_events USING GIST (affected_area);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_farms_owner_name ON farms (owner_name);
CREATE INDEX IF NOT EXISTS idx_farms_risk_score ON farms (risk_score);
CREATE INDEX IF NOT EXISTS idx_farm_assessments_farm_id ON farm_assessments (farm_id);
CREATE INDEX IF NOT EXISTS idx_farm_assessments_date ON farm_assessments (assessment_date);
CREATE INDEX IF NOT EXISTS idx_weather_data_station_id ON weather_data (station_id);
CREATE INDEX IF NOT EXISTS idx_weather_data_timestamp ON weather_data (timestamp);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE agrisphere_risk TO agrisphere_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agrisphere_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agrisphere_user; 