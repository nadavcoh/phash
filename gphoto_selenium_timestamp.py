import psycopg2
import psycopg2.extras
import json
import argparse
import csv

def write_records_to_csv(records, filename='records_without_timestamp.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'timezone', 'label'])
        for record in records:
            writer.writerow([record['id'], record['timezone'], record['label']])
    print(f"Records written to {filename}")

def write_updated_records_to_csv(records, filename='updated_records.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'timezone', 'label', 'timestamp'])
        for record in records:
            writer.writerow([record['id'], record['timezone'], record['label'], record['timestamp']])
    print(f"Updated records written to {filename}")

def update_timestamp_for_records():
    with open('config.json') as config_file:
        config = json.load(config_file)

    conn = psycopg2.connect(
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"]
    )
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Connection Successful to PostgreSQL")

    cursor.execute("SELECT id, timezone, label FROM hashes WHERE timestamp IS NULL and timezone is not null")
    records = cursor.fetchall()

    if not records:
        print("No records found without timestamp.")
        cursor.close()
        conn.close()
        return

    # Write records to CSV before lookup
    write_records_to_csv(records)

    i = 0
    n = len(records)
    print(f"Found {n} records without timestamp.")
    updated_records = []
    for record in records:
        print(f"Processing record {i+1}/{n}...")
        i += 1
        record_id = record['id']
        timezone = record['timezone']
        label = record['label']
        
        if not timezone or not label:
            print(f"Missing timezone or label for record ID {record_id}.")
            continue

        date_str = label.split(' – ')[-1]
        timestamp = date_str + timezone[3:]

        cursor.execute(
            "UPDATE hashes SET timestamp = %s WHERE id = %s",
            (timestamp, record_id)
        )
        conn.commit()
        print(f"Updated record ID {record_id} with timezone {timezone}, label {label}, and timestamp {timestamp}.")

        updated_records.append({
            'id': record_id,
            'timezone': timezone,
            'label': label,
            'timestamp': timestamp
        })

    cursor.close()
    conn.close()

    # Write updated records to CSV
    write_updated_records_to_csv(updated_records)

def main():
    update_timestamp_for_records()

if __name__ == "__main__":
    main()