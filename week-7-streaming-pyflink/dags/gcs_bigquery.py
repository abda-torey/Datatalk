from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago

# Default args for the DAG
default_args = {
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define the DAG
with DAG(
    'gcs_to_bigquery',
    default_args=default_args,
    schedule_interval='@daily',  # Schedule to run daily
    catchup=False
) as dag:

    # Create BigQuery table if it doesn't exist
    create_bq_table = BigQueryCreateEmptyTableOperator(
        task_id='create_bq_table',
        dataset_id='fake_ecommerce_data',  # Replace with your dataset name
        table_id='grocery_products',  # Table name in BigQuery
        schema_fields=[
            {'name': 'Product ID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'Product', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'Quantity', 'type': 'INTEGER', 'mode': 'NULLABLE'}
        ],
        project_id='taxi-data-447320'  # Replace with your GCP project ID
    )

    # Load data from GCS to BigQuery
    load_gcs_to_bq = GCSToBigQueryOperator(
        task_id='load_gcs_to_bq',
        bucket='fake-ecommerce-taxi-data-447320',  # Your GCS bucket
        source_objects=['grocery_products_output/part-9000b709-342e-4148-b4bf-6f10ed6fbc7d-task-0-file-0'],  # Path to the product CSV file
        destination_project_dataset_table='taxi-data-447320.fake_ecommerce_data.grocery_products',  # Adjust to match your project and dataset
        schema_fields=[
            {'name': 'Product ID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'Product', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'Quantity', 'type': 'INTEGER', 'mode': 'NULLABLE'}
        ],
        write_disposition='WRITE_TRUNCATE',  # Overwrite the table each time (use WRITE_APPEND to append data)
        source_format='CSV'  # File format in GCS
    )

    # Define task dependencies
    create_bq_table >> load_gcs_to_bq
