{{ config(materialized='table') }}
WITH fhv_travel_time AS (
    SELECT * FROM {{ref('dim_fhv_trips')}}
)
SELECT dispatching_base_num,
pickup_datetime,
dropOff_datetime,
TIMESTAMP_DIFF(dropOff_datetime,pickup_datetime, SECOND) AS trip_duration_seconds,
PUlocationID,
pickup_borough, 
pickup_zone, 
DOlocationID,
dropoff_borough, 
dropoff_zone,
year,
month,
SR_Flag,
Affiliated_base_number
FROM fhv_travel_time