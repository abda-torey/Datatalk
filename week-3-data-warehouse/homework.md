## Module 3 Homework

<b><u>Important Note:</b></u> <p> For this homework we will be using the Yellow Taxi Trip Records for **January 2024 - June 2024 NOT the entire year of data** 
Parquet Files from the New York
City Taxi Data found here: </br> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page </br>






<b>BIG QUERY SETUP:</b></br>
Create an external table using the Yellow Taxi Trip Records. </br>
Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table). </br>
</p>

## Question 1:
Question 1: What is count of records for the 2024 Yellow Taxi Data?
```
SELECT COUNT(*) FROM `taxi-data-447320.nyc_taxi_data.nyc_regular_table`;
```
- 20,332,093



## Question 2:
Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.</br> 
What is the **estimated amount** of data that will be read when this query is executed on the External Table and the Table?

```
SELECT COUNT(DISTINCT PULocationID) AS Unique_PUlocations FROM `taxi-data-447320.nyc_taxi_data.nyc_regular_table` 

SELECT COUNT(DISTINCT PULocationID) AS Unique_PUlocations FROM `taxi-data-447320.nyc_taxi_data.nyc_external_table`

```

- 0 MB for the External Table and 155.12 MB for the Materialized Table


## Question 3:
Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?

- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires 
reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.

## Question 4:
How many records have a fare_amount of 0?

``` 
SELECT COUNT(*) FROM `taxi-data-447320.nyc_taxi_data.nyc_regular_table` 
WHERE fare_amount = 0; 
```
- 8,333

## Question 5:
What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)
``` 
CREATE OR REPLACE TABLE `taxi-data-447320.nyc_taxi_data.nyc_taxi_partitioned`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT * FROM `taxi-data-447320.nyc_taxi_data.nyc_regular_table`;
  ```
- Partition by tpep_dropoff_datetime and Cluster on VendorID

## Question 6:
Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime
2024-03-01 and 2024-03-15 (inclusive)</br>
```  
SELECT COUNT(DISTINCT VendorID) AS Unique_IDs FROM `taxi-data-447320.nyc_taxi_data.nyc_regular_table`
WHERE DATE(tpep_dropoff_datetime)BETWEEN '2024-03-01' AND '2024-03-15'
;

SELECT COUNT(DISTINCT VendorID) AS Unique_IDs FROM `taxi-data-447320.nyc_taxi_data.nyc_taxi_partitioned`
WHERE DATE(tpep_dropoff_datetime)BETWEEN '2024-03-01' AND '2024-03-15'
;

 ```

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values? </br>

Choose the answer which most closely matches.</br> 

- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table


## Question 7: 
Where is the data stored in the External Table you created?

- GCP Bucket


## Question 8:
It is best practice in Big Query to always cluster your data:
- True


## (Bonus: Not worth points) Question 9:
No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?

 -0B, bigquerry can scan the metadata of the table for queries such as count, it won't need to scan the whole table

