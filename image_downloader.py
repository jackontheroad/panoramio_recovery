# Author: ChatGPT
# Date: November 25, 2023
import os
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
import time
import traceback

# Read image URLs from the CSV file using pandas
csv_file_path = r"d:\code\panoramio\photo_list_u2304697_v2_complete.csv"
# Define the folder path for saving images
save_folder = r"d:\code\panoramio\photo_thumbnails"
# proxies_1 = {"https": "http://127.0.0.1:10809"}
proxies_1 = {}
proxies_2 = {}
request_interval = 2  # 2 seconds
one_or_zero = 0


def download_image(index, url, save_folder):
    global one_or_zero
    try:
        # Extract filename from the URL
        filename = os.path.basename(url)
        # Check if the file already exists
        save_path = os.path.join(save_folder, filename)
        if os.path.exists(save_path):
            print(f"Image {filename} already exists. Skipping...")
            return
        # Check if the URL is not empty or NaN
        if pd.notna(url) and url.strip() != "":
            start_time = time.time()
            proxies = proxies_1 if index // 20 % 2 == one_or_zero else proxies_2
            print("--------------"+str(proxies)+"------------------")
            # Send HTTP request to get the image
            try:
                response = requests.get(url, proxies=proxies, timeout=55)
            except:
                traceback.print_exc()
                one_or_zero = 0 if one_or_zero == 1 else 1
                proxies = proxies_1 if index // 20 % 2 == one_or_zero else proxies_2
                print("--------------"+str(proxies)+"------------------")
                try:
                    response = requests.get(url, proxies=proxies, timeout=55)
                except:
                    time.sleep(60)
                    response = requests.get(url, proxies=proxies, timeout=55)

            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time < request_interval:
                time.sleep(request_interval-elapsed_time)

            if response.status_code == 200:
                # Convert binary data to an image
                image = Image.open(BytesIO(response.content))

                # Save the image
                image.save(save_path)
                print(f"Image downloaded and saved: {save_path}")

            else:
                print(f"Failed to download image from {url}. Status code: {response.status_code}")

        else:
            print(f"Skipping row {index + 1}. URL is empty or NaN.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    df = pd.read_csv(csv_file_path)
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Get the image URL
        image_url = row['photo_url']
        # image_url = row['thumbnail_url']

        # Download and save the image if the URL is not empty or NaN
        download_image(index, image_url, save_folder)
