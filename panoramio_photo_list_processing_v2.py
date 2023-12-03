import requests
import csv
from bs4 import BeautifulSoup
import os
import re
import sys
import os.path
import pandas as pd
import traceback
import time

# csv文件名中必须带有user_id的格式像这样 u2304697, 不要添加其他的任何数字
# csv filename containing user_id like this 'u2304697' is required, do not add other numbers in the filename.
csv_file = r"d:\code\test\photo_ids_u2304697.csv"

user_id = re.findall(r'\d+', os.path.basename(csv_file))[0]

output_file = os.path.join(os.path.dirname(csv_file), f"""photo_list_u{user_id}_v2.csv""")

csv_header = ["photo_id", "user_id", "archive_id", "with_photo_id", "with_photo_index", "page", "idx_in_page",
              "last_in_page", "thumbnail_url", "page_url", "photo_page_url", "title",]

web_archive_host = "https://web.archive.org"


request_headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}
# proxies_1 = {"https": "http://127.0.0.1:10809"}
proxies_1 = {}
proxies_2 = {}
request_interval = 2  # 2 seconds
one_or_zero = 0

processed_photo_ids = set()
start_index = 0
if os.path.isfile(output_file):
    try:
        df = pd.read_csv(output_file)
        last_line = df.iloc[-1]
        last_in_page = last_line["last_in_page"]
        if int(last_in_page) == 0:
            print("------------error------------")
            print(
                "Please remove all rows of last page in csv. They are not intact and need to be repopulated."
            )
            print("请删除csv中最后一页的数据，这页的数据不完整，需要重新下载.")
            sys.exit()
        start_index = int(last_line["with_photo_index"]) + 1
        last_page = last_line["page"]
        processed_photo_ids = set(map(str, df["photo_id"]))
    except SystemExit:
        sys.exit()
    except:
        df = None
print("-----------start_index-----------"+str(start_index)+"----------------")
print("-----------start_page-----------"+str(last_page)+"----------------")
time.sleep(10)
# 创建 CSV 文件
with open(output_file, "a", newline="", encoding="utf-8") as output_file:
    writer = csv.DictWriter(output_file, fieldnames=csv_header)
    if output_file.tell() == 0:
        writer.writeheader()
    count = 0
    df = pd.read_csv(csv_file)

    for index, row in df.iloc[start_index:].iterrows():
        print("--------------------------------index---last_page----" + str(index) + "-----"+str(last_page)+"--------------")
        photo_id = str(row['photo_id'])
        if photo_id in processed_photo_ids:
            print("------skip--photo_id---" + str(photo_id) + "-------------------")
            continue
        archive_id = row['archive_id']
        page_url = f"""https://web.archive.org/web/{archive_id}/http://www.panoramio.com/user/{user_id}?with_photo_id={photo_id}"""

        start_time = time.time()
        proxies = proxies_1 if count // 20 % 2 == one_or_zero else proxies_2
        print("-------" + str(count) + "------------------"+str(proxies)+"------------------")
        try:
            response = requests.get(page_url, proxies=proxies, headers=request_headers, timeout=55)
        except:
            traceback.print_exc()
            one_or_zero = 0 if one_or_zero == 1 else 1
            proxies = proxies_1 if count // 20 % 2 == one_or_zero else proxies_2
            print("-------" + str(count) + "------------------"+str(proxies)+"------------------")
            try:
                response = requests.get(page_url, proxies=proxies, headers=request_headers, timeout=55)
            except:
                time.sleep(60)
                response = requests.get(page_url, proxies=proxies, headers=request_headers, timeout=55)

        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time < request_interval:
            time.sleep(request_interval-elapsed_time)

        print("------responsed--count----------------------------------" + str(count) + "-------------------")
        photos_soup = BeautifulSoup(response.content, "html.parser")
        page = photos_soup.find("span", class_="selected").text
        print("-------page-------" + str(page) + "-------------------")
        photos = photos_soup.find_all("img", class_="photo")

        last_page = page
        idx_in_page = 0
        photo_num = len(photos)
        for photo in photos:
            current_photo_id = photo["id"].split("_")[-1]
            processed_photo_ids.add(str(current_photo_id))
            photo_thumbnail = photo["src"]
            photo_page_url = web_archive_host + photo.parent["href"]
            try:
                title = photo.parent.parent.find_all("a")[1].text
            except:
                traceback.print_exc()
                title = "error"
            last_in_page = 0
            if idx_in_page == photo_num - 1:
                last_in_page = 1
            # write to csv file
            writer.writerow({"photo_id": current_photo_id, "user_id": user_id, "archive_id": archive_id,
                             "with_photo_id": photo_id, "with_photo_index": row['index'],
                             "page": page, "last_in_page": last_in_page, "idx_in_page": idx_in_page,
                             "thumbnail_url": photo_thumbnail, "page_url": page_url, "photo_page_url": photo_page_url,
                             "title": title})
            idx_in_page += 1

        count += 1
        output_file.flush()
        print("-------page--end-----" + str(page) + "-------------------")
