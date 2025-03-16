from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, DataTypes, TableEnvironment, StreamTableEnvironment


def create_taxi_events_sink_gcs(t_env):
    table_name = 'taxi_events_sink'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            VendorID INTEGER,
            lpep_pickup_datetime VARCHAR,
            lpep_dropoff_datetime VARCHAR,
            store_and_fwd_flag VARCHAR,
            RatecodeID INTEGER,
            PULocationID INTEGER,
            DOLocationID INTEGER,
            passenger_count INTEGER,
            trip_distance DOUBLE,
            fare_amount DOUBLE,
            extra DOUBLE,
            mta_tax DOUBLE,
            tip_amount DOUBLE,
            tolls_amount DOUBLE,
            ehail_fee DOUBLE,
            improvement_surcharge DOUBLE,
            total_amount DOUBLE,
            payment_type INTEGER,
            trip_type INTEGER,
            congestion_surcharge DOUBLE,
            pickup_timestamp TIMESTAMP
        ) WITH (
            'connector' = 'filesystem',
            'path' = 'gs://fake-ecommerce-taxi-data-447320/',
            'format' = 'csv',
            'sink.parallelism' = '4'  -- Control the number of output files based on parallelism
        )
    """
    t_env.execute_sql(sink_ddl)
    
    return table_name


def create_events_source_kafka(t_env):
    table_name = "taxi_events_source"

    
    pattern = "yyyy-MM-dd HH:mm:ss"
    
    source_ddl = f"""
            CREATE TABLE {table_name} (
                VendorID INTEGER,
                lpep_pickup_datetime VARCHAR,
                lpep_dropoff_datetime VARCHAR,
                store_and_fwd_flag VARCHAR,
                RatecodeID INTEGER,
                PULocationID INTEGER,
                DOLocationID INTEGER,
                passenger_count INTEGER,
                trip_distance DOUBLE,
                fare_amount DOUBLE,
                extra DOUBLE,
                mta_tax DOUBLE,
                tip_amount DOUBLE,
                tolls_amount DOUBLE,
                ehail_fee STRING,
                improvement_surcharge DOUBLE,
                total_amount DOUBLE,
                payment_type INTEGER,
                trip_type INTEGER,
                congestion_surcharge STRING,
                pickup_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
                WATERMARK FOR pickup_timestamp AS pickup_timestamp - INTERVAL '15' SECOND
            ) WITH (
                'connector' = 'kafka',
                'properties.bootstrap.servers' = 'redpanda-1:29092',
                'topic' = 'green-data',
                'scan.startup.mode' = 'latest-offset',
                'properties.auto.offset.reset' = 'latest',
                'format' = 'json'
            );
            """
    t_env.execute_sql(source_ddl)
        
    return table_name

def log_processing():
    # Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)
    # env.set_parallelism(1)

    # Set up the table environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)
    try:
        # Create Kafka table
        source_table = create_events_source_kafka(t_env)
        gcs_sink = create_taxi_events_sink_gcs(t_env)
        # write records to postgres too!
        t_env.execute_sql(
            f"""
            INSERT INTO {gcs_sink}
                    SELECT
                    VendorID,
                    lpep_pickup_datetime,
                    lpep_dropoff_datetime,
                    store_and_fwd_flag,
                    RatecodeID,
                    PULocationID,
                    DOLocationID,
                    passenger_count,
                    trip_distance,
                    fare_amount,
                    extra,
                    mta_tax,
                    tip_amount,
                    tolls_amount,
                    CAST(NULLIF(ehail_fee, '') AS DOUBLE) AS ehail_fee,
                    improvement_surcharge,
                    total_amount,
                    payment_type,
                    trip_type,
                    CAST(NULLIF(congestion_surcharge, '') AS DOUBLE) AS congestion_surcharge,
                    pickup_timestamp
            FROM {source_table}
                    """
        ).wait()

    except Exception as e:
        print("Writing records from Kafka to GCP failed:", str(e))


if __name__ == '__main__':
    log_processing()
