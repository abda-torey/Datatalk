{{
    config(
        materialized = 'table'
    )
}}

WITH fhv_data AS (
    SELECT * FROM {{ ref('stg_fhv_tripdata') }}
),
dim_zones AS (
    SELECT * FROM {{ ref('dim_zones') }}
    WHERE borough != 'Unknown'
)
SELECT 
    fhv_data.dispatching_base_num,
    CAST(fhv_data.pickup_datetime AS TIMESTAMP) AS pickup_datetime,
    CAST(fhv_data.dropOff_datetime AS TIMESTAMP) AS dropOff_datetime,
    fhv_data.PUlocationID,
    pickup_zone.borough AS pickup_borough, 
    pickup_zone.zone AS pickup_zone, 
    fhv_data.DOlocationID,
    dropoff_zone.borough AS dropoff_borough, 
    dropoff_zone.zone AS dropoff_zone,
    EXTRACT(YEAR FROM CAST(fhv_data.pickup_datetime AS TIMESTAMP)) AS year,
    EXTRACT(MONTH FROM CAST(fhv_data.pickup_datetime AS TIMESTAMP)) AS month,
    fhv_data.SR_Flag,
    fhv_data.Affiliated_base_number
FROM fhv_data
INNER JOIN dim_zones AS pickup_zone
    ON fhv_data.PUlocationID = pickup_zone.locationid
INNER JOIN dim_zones AS dropoff_zone
    ON fhv_data.DOlocationID = dropoff_zone.locationid
