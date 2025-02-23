-- generating model for source('staging', 'fhv_tripdata')...
{{ config(materialized='view') }}

WITH fhv_data AS (
    SELECT dispatching_base_num,pickup_datetime,dropoff_datetime,PUlocationID,DOlocationID,
    SR_Flag, Affiliated_base_number FROM {{source('staging','fhv_tripdata')}}
    WHERE dispatching_base_num IS NOT NULL
)
SELECT dispatching_base_num,pickup_datetime,dropoff_datetime,PUlocationID,DOlocationID,
SR_Flag,Affiliated_base_number FROM fhv_data

-- dbt build --select <model.sql> --vars '{'is_test_run: false}'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}