{{
    config(
        materialized='table'
    )
}}

WITH valid_trips AS (
    SELECT service_type,year,month,fare_amount, trip_distance, payment_type_description
    FROM {{ref('fact_trips')}}
    WHERE fare_amount > 0
    AND
    trip_distance > 0
    AND
    LOWER(payment_type_description) IN ('cash', 'credit card')
),
percentile_calculations AS (
    SELECT service_type, year,month,fare_amount,
    ROUND(PERCENTILE_CONT(fare_amount,0.95) OVER(PARTITION BY service_type,year, month 
    
    ),1) AS fare_amount_p95,
    ROUND(PERCENTILE_CONT(fare_amount,0.9) OVER(PARTITION BY service_type,year, month 
    
    ),1) AS fare_amount_p90,
    ROUND(PERCENTILE_CONT(fare_amount,0.97) OVER(PARTITION BY service_type,year, month 
    
    ),1) AS fare_amount_p97
    FROM valid_trips
)

SELECT DISTINCT service_type,year,month,fare_amount_p90,fare_amount_p95,fare_amount_p97 FROM percentile_calculations
ORDER BY service_type, year, month