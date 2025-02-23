{{
    config(
        materialized='table'
    )
}}

WITH quarterly_revenue AS (
    SELECT 
        year, 
        quarter, 
        service_type, 
        SUM(total_amount) AS quarterly_revenue
    FROM {{ ref('fact_trips') }}
    GROUP BY year, quarter, service_type
),
quarterly_revenue_growth AS (
    SELECT 
        qr.year, 
        qr.quarter, 
        qr.service_type, 
        qr.quarterly_revenue,
        LAG(qr.quarterly_revenue) OVER(PARTITION BY qr.service_type, qr.quarter ORDER BY qr.year) AS previous_year_revenue,
        CASE
            WHEN LAG(qr.quarterly_revenue) OVER(PARTITION BY qr.service_type, qr.quarter ORDER BY qr.year) IS NULL THEN NULL
            WHEN LAG(qr.quarterly_revenue) OVER(PARTITION BY qr.service_type, qr.quarter ORDER BY qr.year) = 0  AND quarterly_revenue > 0 THEN 100.00
            WHEN LAG(qr.quarterly_revenue) OVER(PARTITION BY qr.service_type, qr.quarter ORDER BY qr.year) = 0  AND quarterly_revenue = 0 THEN 0.00
            WHEN LAG(qr.quarterly_revenue) OVER(PARTITION BY qr.service_type, qr.quarter ORDER BY qr.year) < 0  THEN NULL
            
            ELSE ROUND(
                ((qr.quarterly_revenue - LAG(qr.quarterly_revenue) OVER(PARTITION BY qr.service_type, qr.quarter ORDER BY qr.year))
                / LAG(qr.quarterly_revenue) OVER(PARTITION BY qr.service_type, qr.quarter ORDER BY qr.year)) * 100,
                2
            )
        END AS yoy_growth_percentage
    FROM quarterly_revenue AS qr
)

SELECT 
    year, 
    service_type, 
    quarter, 
    quarterly_revenue, 
    previous_year_revenue, 
    yoy_growth_percentage
FROM quarterly_revenue_growth
ORDER BY service_type, year, quarter
