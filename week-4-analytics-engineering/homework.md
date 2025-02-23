## Module 4 Homework


### Question 1: Understanding dbt model resolution

Provided you've got the following sources.yaml
```yaml
version: 2

sources:
  - name: raw_nyc_tripdata
    database: "{{ env_var('DBT_BIGQUERY_PROJECT', 'dtc_zoomcamp_2025') }}"
    schema:   "{{ env_var('DBT_BIGQUERY_SOURCE_DATASET', 'raw_nyc_tripdata') }}"
    tables:
      - name: ext_green_taxi
      - name: ext_yellow_taxi
```

with the following env variables setup where `dbt` runs:
```shell
export DBT_BIGQUERY_PROJECT=myproject
export DBT_BIGQUERY_DATASET=my_nyc_tripdata
```

What does this .sql model compile to?
```sql
select * 
from {{ source('raw_nyc_tripdata', 'ext_green_taxi' ) }}
```
Answer


- `select * from myproject.my_nyc_tripdata.ext_green_taxi`



### Question 2: dbt Variables & Dynamic Models

Say you have to modify the following dbt_model (`fct_recent_taxi_trips.sql`) to enable Analytics Engineers to dynamically control the date range. 

- In development, you want to process only **the last 7 days of trips**
- In production, you need to process **the last 30 days** for analytics

```sql
select *
from {{ ref('fact_taxi_trips') }}
where pickup_datetime >= CURRENT_DATE - INTERVAL '30' DAY
```

What would you change to accomplish that in a such way that command line arguments takes precedence over ENV_VARs, which takes precedence over DEFAULT value?


- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", env_var("DAYS_BACK", "30")) }}' DAY`



### Question 3: dbt Data Lineage and Execution

Considering the data lineage below **and** that taxi_zone_lookup is the **only** materialization build (from a .csv seed file):



Select the option that does **NOT** apply for materializing `fct_taxi_monthly_zone_revenue`:


- `dbt run --select +models/core/dim_taxi_trips.sql+ --target prod`


### Question 4: dbt Macros and Jinja

Consider you're dealing with sensitive data (e.g.: [PII](https://en.wikipedia.org/wiki/Personal_data)), that is **only available to your team and very selected few individuals**, in the `raw layer` of your DWH (e.g: a specific BigQuery dataset or PostgreSQL schema), 

 - Among other things, you decide to obfuscate/masquerade that data through your staging models, and make it available in a different schema (a `staging layer`) for other Data/Analytics Engineers to explore

- And **optionally**, yet  another layer (`service layer`), where you'll build your dimension (`dim_`) and fact (`fct_`) tables (assuming the [Star Schema dimensional modeling](https://www.databricks.com/glossary/star-schema)) for Dashboarding and for Tech Product Owners/Managers

You decide to make a macro to wrap a logic around it:

```sql
{% macro resolve_schema_for(model_type) -%}

    {%- set target_env_var = 'DBT_BIGQUERY_TARGET_DATASET'  -%}
    {%- set stging_env_var = 'DBT_BIGQUERY_STAGING_DATASET' -%}

    {%- if model_type == 'core' -%} {{- env_var(target_env_var) -}}
    {%- else -%}                    {{- env_var(stging_env_var, env_var(target_env_var)) -}}
    {%- endif -%}

{%- endmacro %}
```

And use on your staging, dim_ and fact_ models as:
```sql
{{ config(
    schema=resolve_schema_for('core'), 
) }}
```

That all being said, regarding macro above, **select all statements that are true to the models using it**:

- When using `core`, it materializes in the dataset defined in `DBT_BIGQUERY_TARGET_DATASET`
- When using `stg`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`
- When using `staging`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`


## Serious SQL

Alright, in module 1, you had a SQL refresher, so now let's build on top of that with some serious SQL.

These are not meant to be easy - but they'll boost your SQL and Analytics skills to the next level.  
So, without any further do, let's get started...

You might want to add some new dimensions `year` (e.g.: 2019, 2020), `quarter` (1, 2, 3, 4), `year_quarter` (e.g.: `2019/Q1`, `2019-Q2`), and `month` (e.g.: 1, 2, ..., 12), **extracted from pickup_datetime**, to your `fct_taxi_trips` OR `dim_taxi_trips.sql` models to facilitate filtering your queries


### Question 5: Taxi Quarterly Revenue Growth

1. Create a new model `fct_taxi_trips_quarterly_revenue.sql`
2. Compute the Quarterly Revenues for each year for based on `total_amount`
3. Compute the Quarterly YoY (Year-over-Year) revenue growth 
  * e.g.: In 2020/Q1, Green Taxi had -12.34% revenue growth compared to 2019/Q1
  * e.g.: In 2020/Q4, Yellow Taxi had +34.56% revenue growth compared to 2019/Q4

Considering the YoY Growth in 2020, which were the yearly quarters with the best (or less worse) and worst results for green, and yellow

  ```
  WITH quarterly_revenue_growth AS (
  SELECT  
    year, 
    quarter, 
    service_type,
    quarterly_revenue, 
    yoy_growth_percentage 
  FROM 
    `taxi-data-447320.nyc_taxi_data.fct_taxi_trips_quarterly_revenue`
  WHERE 
    year = 2020
),
best_worst_quarters AS (
  SELECT 
    service_type, 
    yoy_growth_percentage,
    quarter,
    FIRST_VALUE(quarter) OVER (PARTITION BY service_type ORDER BY yoy_growth_percentage DESC) AS best_quarter,
    FIRST_VALUE(quarter) OVER (PARTITION BY service_type ORDER BY yoy_growth_percentage ASC) AS worst_quarter
  FROM 
    quarterly_revenue_growth
)
SELECT 
  service_type,
  MAX(yoy_growth_percentage) AS best_yoy_growth, 
  MIN(yoy_growth_percentage) AS worst_yoy_growth,
  MAX(best_quarter) AS best_quarter, 
  MAX(worst_quarter) AS worst_quarter
FROM 
  best_worst_quarters
GROUP BY 
  service_type;


  ```

Answer:
- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q1, worst: 2020/Q2}



### Question 6: P97/P95/P90 Taxi Monthly Fare

1. Create a new model `fct_taxi_trips_monthly_fare_p95.sql`
2. Filter out invalid entries (`fare_amount > 0`, `trip_distance > 0`, and `lower(payment_type_description) in ('cash', 'credit card')`)
3. Compute the **continous percentile** of `fare_amount` partitioning by service_type, year and and month

Now, what are the values of `p97`, `p95`, `p90` for Green Taxi and Yellow Taxi, in April 2020?

  ``` 
    SELECT 
    service_type, 
    year,
    fare_amount_p90,
    fare_amount_p95,
    fare_amount_p97
FROM 
    `taxi-data-447320.nyc_taxi_data.fct_taxi_trips_monthly_fare_p95`
WHERE 
    year = 2020
    AND 
    month = 4;

   ```
  ANSWER:

   - green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}



### Question 7: Top #Nth longest P90 travel time Location for FHV



For the Trips that **respectively** started from `Newark Airport`, `SoHo`, and `Yorkville East`, in November 2019, what are **dropoff_zones** with the 2nd longest p90 trip_duration ?

``` 
  

WITH trip_data AS (
  SELECT 
  pickup_zone,
  dropoff_zone,
  trip_duration_seconds
  FROM 
   `taxi-data-447320.nyc_taxi_data.fct_fhv_monthly_zone_traveltime_p90`
  WHERE 
    year = 2019
    AND month = 11
    AND pickup_zone IN ('Newark Airport', 'SoHo', 'Yorkville East')
),
p90_data AS (
  -- Step 2: Calculate the P90 trip duration for each pickup-dropoff pair
  SELECT
    pickup_zone,
    dropoff_zone,
    trip_duration_seconds,
    PERCENTILE_CONT(trip_duration_seconds, 0.9) 
      OVER (PARTITION BY pickup_zone, dropoff_zone) AS p90_trip_duration
  FROM
    trip_data
  ),
  ranked_zones AS (
  select  
    pickup_zone,
    dropoff_zone,
    trip_duration_seconds,
    p90_trip_duration,
    ROW_NUMBER() OVER(PARTITION BY pickup_zone ORDER BY p90_trip_duration DESC) AS Rank
    FROM p90_data

)
select pickup_zone,dropoff_zone,trip_duration_seconds, p90_trip_duration, Rank
from ranked_zones
WHERE Rank = 2
```
- LaGuardia Airport, Park Slope, Clinton East


## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2025/homework/hw4


## Solution 

* To be published after deadline
