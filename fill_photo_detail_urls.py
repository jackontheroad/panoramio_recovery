# Author: ChatGPT
# Date: November 25, 2023

import csv
import os
import requests

def fill_photo_detail_urls(input_file, output_file, save_interval):
    # Fills photo_detail_url and saves to CSV, checking for existing data
    # 填充photo_detail_url并保存到CSV，检查已存在的数据
    photo_details = read_existing_data(output_file)
    processed_count = len(photo_details)

    # 获取上次中断的位置
    # Get the last processed position
    last_processed_photo_id = None
    if photo_details:
        last_processed_photo_id = photo_details[-1]['photo_id']
        print(f"Resuming from last processed photo_id: {last_processed_photo_id}")

    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            photo_id = row['photo_id']

            # 如果已处理到上次中断的位置，则开始处理下一个
            # If reached the last processed position, start processing the next one
            if photo_id == last_processed_photo_id:
                last_processed_photo_id = None
                photo_details.clear()
                continue
            if last_processed_photo_id is None:
                # 继续处理
                processed_count += 1
                original_url = f"http://www.panoramio.com/photo/{photo_id}"
                archive_api_url = f"https://archive.org/wayback/available?url={original_url}"

                # Print log information
                print(f"Processing photo_id: {photo_id} (Record {processed_count})")
                print(f"Original URL: {original_url}")
                print(f"Archive API URL: {archive_api_url}")

                # Make a request to retrieve JSON data
                response = requests.get(archive_api_url)
                json_data = response.json()

                # Extract the required information
                if 'archived_snapshots' in json_data and 'closest' in json_data['archived_snapshots']:
                    snapshot_url = json_data['archived_snapshots']['closest']['url']
                else:
                    snapshot_url = None
                    print(f"Failed to retrieve snapshot for photo_id: {photo_id}")

                photo_details.append({'photo_id': photo_id, 'photo_detail_url': snapshot_url})

                # Print snapshot URL
                if snapshot_url:
                    print(f"Snapshot URL: {snapshot_url}")

                # Save every 10 requests
                if processed_count % save_interval == 0:
                    save_to_csv(photo_details, output_file)
                    photo_details.clear()
                    print(f"Saved {processed_count} records to CSV")

    # Process the remaining records
    save_to_csv(photo_details, output_file)
    print(f"Saved {processed_count} records to CSV")

def save_to_csv(photo_details, output_file):
    # Saves a list of photo_details to a CSV file
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['photo_id', 'photo_detail_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if the file is empty
        if csvfile.tell() == 0:
            writer.writeheader()

        for detail in photo_details:
            writer.writerow(detail)
        csvfile.flush()

def read_existing_data(output_file):
    # Reads existing data from the CSV file
    existing_data = []

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_data.append({'photo_id': row['photo_id'], 'photo_detail_url': row['photo_detail_url']})

    return existing_data


if __name__ == "__main__":
    input_file = r"D:\code\test\photo_ids.csv"  # Generated CSV file from the first script
    output_file = r"D:\code\test\photo_details.csv"  # Generated CSV file path and name
    save_interval = 10  # Set request save interval
    fill_photo_detail_urls(input_file, output_file, save_interval)