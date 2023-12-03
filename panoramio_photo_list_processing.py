import requests
import csv
from bs4 import BeautifulSoup
import re
import sys
import os.path
import pandas as pd

# page_url = r"https://web.archive.org/web/20161105193651/http://www.panoramio.com/user/5347106?comment_page=1&photo_page=1"
page_url = r"http://web.archive.org/web/20161105123656/http://www.panoramio.com/user/263050?comment_page=1&photo_page=1"
csv_file = r"D:\code\test\panoramio_photos.csv"

numbers = re.findall(r"\d+", page_url)
archive_id = numbers[0]
user_id = numbers[1]
page = int(numbers[-1])

csv_file = csv_file[:-4] + "_u" + str(user_id) + ".csv"

web_archive_host = "https://web.archive.org"
proxies_1 = {"https": "http://127.0.0.1:10809"}
proxies_2 = {}

index = 0
if os.path.isfile(csv_file):
    try:
        df = pd.read_csv(csv_file)
    except pd.errors.EmptyDataError:
        df = None
    if df is not None and len(df.index) > 0:
        last_line = df.iloc[-1]
        is_last_in_page = last_line["is_last_in_page"]
        if int(is_last_in_page) == 0:
            print("------------error------------")
            print(
                "Please remove all last page rows in csv. They are not intact and need to be repopulate."
            )
            print("请删除csv中最后一页的数据，这页的数据不完整，需要重新下载.")
            sys.exit()
        next_page_url = last_line["page_url_next_or_current"]
        index = int(last_line["index"]) + 1

        if next_page_url and next_page_url.strip():
            page_url = next_page_url

if not page_url or not page_url.strip():
    print("------------error------------")
    print("Please check page_url. It's empty.")
    print("请检查page_url. 不能为空.")
    sys.exit()

with open(csv_file, "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    if page == 1:
        writer.writerow(
            ["index", "photo_id", "is_last_in_page", "page", "idx_in_page", "title", "photo_page_url", "thumbnail_url",
             "page_url_next_or_current", "photo_url", "latlon", "tags", "location", "uploaded_on", "taken_on",])
    count = 0
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    
    while True:
        print("-------page-------" + str(page) + "-------------------")
        photos_url = page_url
        proxies = proxies_1 if count / 38 % 2 == 1 else proxies_2
        count += 1
        photos_response = requests.get(photos_url,
                                       headers=headers,
                                       proxies=proxies,
                                       timeout=30)
        print("------responsed---" + str(page) + "-------------------")
        photos_soup = BeautifulSoup(photos_response.content, "html.parser")
        photos = photos_soup.find_all("img", class_="photo")

        a_next = photos_soup.find("a", string="Next »")
        next_page_url = web_archive_host + a_next["href"] if a_next else None
        # print(photos)
        # break
    
        idx_in_page = 0
        photo_num = len(photos)
        for photo in photos:
            
            photo_id = photo["id"].split("_")[-1]
            photo_title = photo["title"]
            photo_thumbnail = photo["src"]
            photo_url = web_archive_host + photo.parent["href"]
            is_last_in_page = 0
            page_url_next_or_current = None
            if idx_in_page == photo_num - 1:
                is_last_in_page = 1
                page_url_next_or_current = next_page_url
                page_url = next_page_url
            elif idx_in_page == 0:
                page_url_next_or_current = page_url
            # latitude = photo["latitude"]
            # longitude = photo["longitude"]
            # tags = photo["tags"]
            print(str(idx_in_page) + "----" + photo_title)
            # 写入 CSV 文件
            writer.writerow([index, photo_id, is_last_in_page, page, idx_in_page, photo_title, photo_url,
                             photo_thumbnail, page_url_next_or_current, "photo_url", "latlon", "tags", "location",
                             "uploaded_on", "taken_on",])
            idx_in_page += 1
            index += 1

        csvfile.flush()
        print("-------page-------" + str(page) + "-------------------")
        page += 1

        if page_url is None:
            break
