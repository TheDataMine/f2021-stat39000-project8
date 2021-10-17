-- name: get_station^
-- Get the station with the given id
SELECT * FROM stations WHERE id = :id;

-- name: get_stations
-- Get the station with the given id
SELECT * FROM stations;

-- name: get_observations
-- Get the weather data
SELECT * FROM observations LIMIT :limit;

-- name: get_observations_starting_after
-- Get the observations starting after the id given
SELECT * FROM observations WHERE id > :id LIMIT :limit;

-- name: get_observations_created_at
-- Get the observations created on the given date
SELECT * FROM observations WHERE strftime("%Y-%m-%d", observation_time) = :created_at LIMIT :limit;

-- name: get_observations_created_at_starting_after
-- Get the observations created on the given date starting after the id given
SELECT * FROM observations WHERE strftime("%Y-%m-%d", observation_time) = :created_at AND id > :id LIMIT :limit;

-- name: get_observations_for_station
-- Get the weather data for the given station
SELECT * FROM observations WHERE station_id = :station_id LIMIT :limit;

-- name: get_observations_for_station_starting_after
-- Get the observations for a given station, starting after the id given
SELECT * FROM observations WHERE station_id = :station_id AND id > :id LIMIT :limit;

-- name: get_observations_for_station_created_at
-- Get the observations created on the given date
SELECT * FROM observations WHERE station_id = :station_id AND strftime("%Y-%m-%d", observation_time) = :created_at LIMIT :limit;

-- name: get_observations_for_station_created_at_starting_after
-- Get the observations created on the given date starting after the id given
SELECT * FROM observations WHERE station_id = :station_id AND strftime("%Y-%m-%d", observation_time) = :created_at AND id > :id LIMIT :limit;