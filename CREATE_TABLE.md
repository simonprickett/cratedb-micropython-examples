CREATE TABLE IF NOT EXISTS sensor_readings (
  sensor_id TEXT,
  timestamp TIMESTAMP WITH TIME ZONE GENERATED ALWAYS AS current_timestamp,
  month TIMESTAMP WITH TIME ZONE GENERATED ALWAYS AS date_trunc('month', current_timestamp),
  temp DOUBLE PRECISION
) PARTITIONED BY (month) WITH (column_policy = 'dynamic')

INSERT INTO sensor_readings(sensor_id, temp) VALUES ('0.0.0.0', 12.2)

SELECT * FROM sensor_readings