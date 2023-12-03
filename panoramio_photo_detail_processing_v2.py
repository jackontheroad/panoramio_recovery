import requests
import csv
from bs4 import BeautifulSoup
import re
import sys
import os.path
import pandas as pd
import traceback
import time

csv_file = r"d:\code\test\photo_list_u2304697_v2.csv"

output_file = csv_file[:-4] + "_complete.csv"
start_index = 0
field_names = [
    "index", "photo_id", "user_id", "archive_id", "with_photo_id", "with_photo_index", "page", "idx_in_page",
    "last_in_page", "thumbnail_url", "page_url", "photo_page_url",
    "title", "photo_url",  "latlon", "tags", "uploaded_on", "taken_on", "location",
]
# proxies_1 = {"https": "http://127.0.0.1:10809"}
proxies_1 = {}
proxies_2 = {}
headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}
save_interval = 10  # every 10 lopps flush to csvfile
request_interval = 2  # seconds
if os.path.isfile(output_file):
    try:
        df = pd.read_csv(output_file)
    except pd.errors.EmptyDataError:
        df = None
    if df is not None and len(df.index) > 0:
        last_line = df.iloc[-1]
        start_index = int(last_line["index"]) + 1

df = pd.read_csv(csv_file)
one_or_zero = 1
with open(output_file, "a", newline="", encoding="utf-8") as output_file:
    # writer = csv.writer(output_file)
    writer = csv.DictWriter(output_file, fieldnames=field_names)
    if output_file.tell() == 0:
        # writer.writerow(field_names)
        writer.writeheader()
    for index, row in df.iloc[start_index:].iterrows():
        photo_page_url = row["photo_page_url"]
        # get html content
        start_time = time.time()
        proxies = proxies_1 if index // 20 % 2 == one_or_zero else proxies_2
        print("--------------"+str(proxies)+"------------------")
        try:
            response = requests.get(photo_page_url, proxies=proxies, headers=headers, timeout=55)
        except:
            traceback.print_exc()
            one_or_zero = 0 if one_or_zero == 1 else 1
            proxies = proxies_1 if index // 20 % 2 == one_or_zero else proxies_2
            print("--------------"+str(proxies)+"------------------")
            try:
                response = requests.get(photo_page_url, proxies=proxies, headers=headers, timeout=55)
            except:
                time.sleep(60)
                response = requests.get(photo_page_url, proxies=proxies, headers=headers, timeout=55)

        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time < request_interval:
            time.sleep(request_interval-elapsed_time)
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            photo_url = soup.find("img", id="main-photo_photo").get("src")
        except:
            photo_url = None

        # try:
        #     title = soup.find("img", id="main-photo_photo").get("alt")
        # except:
        #     title = None
        try:
            latlon = (soup.find("abbr", class_="latitude").attrs["title"]
                      + ","
                      + soup.find("abbr", class_="longitude").attrs["title"])
        except:
            latlon = ""
        try:
            uploaded = soup.find("ul", id="details").find("li").text.replace("Uploaded on ", "").strip()
            uploaded = uploaded if uploaded and len(uploaded.split(
                " ")) == 3 else uploaded + ", " + re.findall(r"\d+", photo_page_url)[0][:4]
        except:
            uploaded = ""
        # uploaded = soup.find("li", text="Uploaded on").next_sibling.text
        try:
            tags_text = ", ".join([a.text.strip() for a in soup.find("ul", id="interim-tags").find_all("a")[:-1]])
        except:
            tags_text = ""
        try:
            location = soup.find("p", id="place").text.replace("Photo taken in ", "").strip()
            location = " ".join(location.split())
        except:
            location = ""
        try:
            taken_on = soup.find("li", id="tech-details").find_all('li')[1].text.replace("Taken on ", "").strip()
        except:
            taken_on = ""
        row_dict = row.to_dict()
        row_dict["index"] = index
        row_dict["photo_url"] = photo_url
        # row_dict["title"] = title
        row_dict["latlon"] = latlon
        row_dict["tags"] = tags_text
        row_dict["uploaded_on"] = uploaded
        row_dict["taken_on"] = taken_on
        row_dict["location"] = location

        # writer.writerow(row.values)
        writer.writerow(row_dict)
        print("---------" + str(index) + "---------" + tags_text + "--------" + location + "---------")
        if index and index % save_interval == 0:
            print("---------" + str(index) + "---------saved------------")
            output_file.flush()
