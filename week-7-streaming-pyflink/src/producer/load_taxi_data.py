import csv
import json
from kafka import KafkaProducer
from time import time

def main():
    # Initialize Kafka producer with larger batch settings
    producer = KafkaProducer(
        bootstrap_servers='redpanda-1:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        batch_size=32768,  # Increased batch size to 32KB
        linger_ms=5,       # Reduced linger time to 5ms
        acks='all',        # Ensure data reliability
        compression_type='gzip'  # Compress messages to reduce size
    )

    csv_file = '/opt/data/green_tripdata_2019-01.csv'

    # Open the CSV file and read its contents
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        start_time = time()

        # Send data in batches asynchronously
        for row in reader:
           
            producer.send('green-data', value=row)
            print(f"sent row: {json.dumps(row)}")

        # Flush to ensure all messages are sent
        producer.flush()
        producer.close()

        end_time = time()
        print(f"Data processing completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
