# from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, TableEnvironment

def create_grocery_sink_gcs(t_env):
    table_name = 'grocery_products_sink'
    sink_ddl = f"""
        CREATE TABLE {table_name} (
            `Product ID` STRING,
            `Product` STRING,
            `Quantity` INT
        ) WITH (
            'connector' = 'filesystem',
            'path' = 'gs://fake-ecommerce-taxi-data-447320/grocery_products_output/',
            'format' = 'csv',
            'sink.parallelism' = '1'
        )
    """
    t_env.execute_sql(sink_ddl)
    
    return table_name


def create_grocery_source_local(t_env):
    table_name = "grocery_products_source"
    
    source_ddl = f"""
        CREATE TABLE {table_name} (
            `Product ID` STRING,
            `Product` STRING,
            `Quantity` INT
        ) WITH (
            'connector' = 'filesystem',
            'path' = 'file:///opt/data/grocery_products.csv',  -- Local CSV file path
            'format' = 'csv',
            'csv.ignore-parse-errors' = 'true'
        );
    """
    t_env.execute_sql(source_ddl)
    
    return table_name


def log_processing():
    # Set up the table environment for batch mode using the unified TableEnvironment
    settings = EnvironmentSettings.new_instance().in_batch_mode().build()
    t_env = TableEnvironment.create(settings)
    
    try:
        # Create source and sink tables
        source_table = create_grocery_source_local(t_env)
        gcs_sink_table = create_grocery_sink_gcs(t_env)

        # Insert records into the GCS sink
        t_env.execute_sql(
            f"""
            INSERT INTO {gcs_sink_table}
            SELECT
                `Product ID`,
                `Product`,
                `Quantity`
            FROM {source_table}
            """
        ).wait()

    except Exception as e:
        print("Writing records to GCS failed:", str(e))


if __name__ == '__main__':
    log_processing()