from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
from time import sleep
import psycopg2
import psycopg2.extras
import json
import argparse
import csv

def login(sb):
    sb.open("https://photos.google.com/login")
    input("Press Enter after completing authentication...")

def write_records_to_csv(records, filename='records_without_timezone.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'url'])
        for record in records:
            writer.writerow([record['id'], record['url']])
    print(f"Records written to {filename}")

def update_timezone_for_records():
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

    cursor.execute("SELECT id, url FROM hashes WHERE timezone IS NULL")
    records = cursor.fetchall()

    if not records:
        print("No records found without timezone.")
        cursor.close()
        conn.close()
        return

    # Write records to CSV before lookup
    write_records_to_csv(records)

    with SB(uc=True) as sb:
        login(sb)
        for record in records:
            record_id = record['id']
            url = record['url']
            sb.open(url)
            sleep(5)  # Wait for the page to load

            timezone_elements = sb.find_elements("span[aria-label^='GMT']")
            displayed_timezone_elements = [x for x in timezone_elements if x.is_displayed()]
            if displayed_timezone_elements:
                timezone_element = displayed_timezone_elements[0]
                timezone = timezone_element.text
            else:
                timezone = None
                print(f"No timezone found for record ID {record_id}.")

            if timezone:
                label_elements = sb.find_elements("div[aria-label^='Photo']")
                displayed_label_elements = [x for x in label_elements if x.is_displayed()]
                if displayed_label_elements:
                    label_element = displayed_label_elements[0]
                    label = label_element.get_attribute('aria-label')
                    date_str = label.split(' – ')[-1]
                    timestamp = date_str + timezone[3:]

                    cursor.execute(
                        "UPDATE hashes SET timezone = %s, timestamp = %s WHERE id = %s",
                        (timezone, timestamp, record_id)
                    )
                    conn.commit()
                    print(f"Updated record ID {record_id} with timezone {timezone} and timestamp {timestamp}.")

    cursor.close()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Update timezone for records without timezone.')
    args = parser.parse_args()

    update_timezone_for_records()

if __name__ == "__main__":
    main()