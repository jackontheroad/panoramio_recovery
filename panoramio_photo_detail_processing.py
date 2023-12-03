import requests
import csv
from bs4 import BeautifulSoup
import re
import sys
import os.path
import pandas as pd
import traceback
import time

csv_file = r"d:\code\test\panoramio_photos_u263050.csv"

output_file = csv_file[:-4] + "_complete.csv"
start_index = 0
field_names = [
    "index", "photo_id", "is_last_in_page", "page", "idx_in_page", "title", "photo_page_url",
    "thumbnail_url", "page_url_next_or_current",
    "photo_url", "latlon", "tags", "uploaded_on", "taken_on", "location",
]
proxies_xray = {"https": "http://127.0.0.1:10809"}
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
    if start_index == 0:
        # writer.writerow(field_names)
        writer.writeheader()
    for index, row in df.iloc[start_index:].iterrows():
        photo_page_url = row["photo_page_url"]
        # 获取 HTML 内容
        start_time = time.time()
        proxies = proxies_xray if index // 20 % 2 == one_or_zero else {}
        print("--------------"+str(proxies)+"------------------")
        try:
            response = requests.get(photo_page_url, proxies=proxies, headers=headers, timeout=30)
        except:
            traceback.print_exc()
            one_or_zero = 0 if one_or_zero == 1 else 1
            proxies = proxies_xray if index // 20 % 2 == one_or_zero else {}
            print("--------------"+str(proxies)+"------------------")
            response = requests.get(photo_page_url, proxies=proxies, headers=headers, timeout=30)
                

        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time < request_interval:
            time.sleep(request_interval-elapsed_time)
        soup = BeautifulSoup(response.content, "html.parser")

        # 查找要获取的数据
        try:
            photo_url = soup.find("img", id="main-photo_photo").get("src")
        except:
            photo_url = None
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
        except:
            location = ""
        try:
            taken_on = soup.find("li", id="tech-details").find_all('li')[1].text.replace("Taken on ", "").strip()
        except:
            taken_on = ""

        row["photo_id"] = row["photo_id"] if "photo" not in row["photo_id"] else row["photo_id"].split("_")[-1]
        row["photo_url"] = photo_url
        row["latlon"] = latlon
        row["tags"] = tags_text
        row["uploaded_on"] = uploaded
        row["taken_on"] = taken_on
        row["location"] = location

        # writer.writerow(row.values)
        writer.writerow(row.to_dict())
        print("---------" + str(index) + "---------" + tags_text + "--------" + location + "---------")
        if index and index % save_interval == 0:
            print("---------" + str(index) + "---------saved------------")
            output_file.flush()
