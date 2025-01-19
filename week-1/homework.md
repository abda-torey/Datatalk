# Module 1 Homework: Docker & SQL

In this homework we'll prepare the environment and practice
Docker and SQL




## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?



### Answer 
  `pip --version`
    24.3.1 

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

### Answer
  - db:5432



##  Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the green taxi trips from October 2019:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

Download this data and put it into Postgres.

You can use the code from the course. It's up to you whether
you want to use Jupyter or a python script.

## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 
### Answer 
  1. `SELECT COUNT(*) AS trips_1_mile FROM green_tripdata
WHERE trip_distance <= 1
AND
lpep_pickup_datetime >= '2019-10-01'
AND
lpep_dropoff_datetime < '2019-11-01'`
  - 104,802
  
  2. `SELECT COUNT(*) AS trips_1_mile FROM green_tripdata
WHERE trip_distance > 1 AND trip_distance <= 3
AND
lpep_pickup_datetime >= '2019-10-01'
AND
lpep_dropoff_datetime < '2019-11-01'`
         
         - 198,924
     
  1. `SELECT COUNT(*) AS trips_1_mile FROM green_tripdata
WHERE trip_distance > 3 AND trip_distance <= 7
AND
lpep_pickup_datetime >= '2019-10-01'
AND
lpep_dropoff_datetime < '2019-11-01'`
          
          - 109,603
  
  1. `SELECT COUNT(*) AS trips_1_mile FROM green_tripdata
WHERE trip_distance > 7 AND trip_distance <= 10
AND
lpep_pickup_datetime >= '2019-10-01'
AND
lpep_dropoff_datetime < '2019-11-01'`
    
          - 27,678
  
  1. `SELECT COUNT(*) AS trips_1_mile FROM green_tripdata
WHERE trip_distance >  10
AND
lpep_pickup_datetime >= '2019-10-01'
AND
lpep_dropoff_datetime < '2019-11-01'`
          
          - 35,189



## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

### Answer
    `SELECT DATE(lpep_pickup_datetime) AS pickup_date,MAX(trip_distance) AS longest_trip_distance FROM green_tripdata GROUP BY pickup_date ORDER BY longest_trip_distance DESC LIMIT 1;`

        - 2019-10-31




## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.

### Answer
  `SELECT  s."Zone" AS PickUp_Zone, g."PULocationID", ROUND(SUM(g."total_amount")::numeric,2) AS sum_location_total 
FROM "green_tripdata" AS g
JOIN
"taxi_zone_lookup" AS s
ON g."PULocationID" = s."LocationID"
WHERE DATE(lpep_pickup_datetime) = '2019-10-18'
GROUP BY g."PULocationID",s."Zone"
ORDER BY sum_location_total DESC
LIMIT 3;
` 
   - East Harlem North, East Harlem South, Morningside Heights



## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone
name "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

### Answer
  `SELECT drop_zn."Zone" AS dropff_zone, MAX(g."tip_amount") AS max_tip
FROM "green_tripdata" AS g
JOIN 
"taxi_zone_lookup" AS drop_zn
ON
drop_zn."LocationID" = g."DOLocationID"
JOIN
"taxi_zone_lookup" AS pickup_zn
ON
pickup_zn."LocationID" = g."PULocationID"
WHERE DATE(g."lpep_pickup_datetime") BETWEEN '2019-10-01' AND '2019-10-31'
AND
pickup_zn."Zone" = 'East Harlem North'
GROUP BY drop_zn."Zone"
ORDER BY max_tip DESC
LIMIT 1;`

   - JFK Airport



## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. 
Copy the files from the course repo
[here](../../../01-docker-terraform/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

### Answer:
- 
    - terraform init, terraform apply -auto-approve, terraform destroy



## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2025/homework/hw1
