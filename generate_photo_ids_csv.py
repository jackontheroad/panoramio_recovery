# Author: ChatGPT
# Date: November 25, 2023
import csv


# def extract_photo_id(line):
#     # 通过分割空格获取数据中的第2列（with_photo_id）
#     return line.split()[0].split('=')[-1]


def main(input_file, output_file):
    photo_ids = set()
    photo_archive_map = {}
    # 读取输入文件并提取 with_photo_id
    with open(input_file, 'r') as file:
        for line in file:
            segs = line.split()
            photo_id = segs[0].split('=')[-1]
            photo_ids.add(photo_id)
            photo_archive_map[str(photo_id)] = segs[1]

    # 对 photo_ids 进行排序
    sorted_photo_ids = sorted(photo_ids, key=lambda x: int(x))

    # 将排序后的 with_photo_id 保存到 CSV 文件
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['index', 'photo_id', 'archive_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for index, photo_id in enumerate(sorted_photo_ids):
            writer.writerow({'index': index, 'photo_id': photo_id, 'archive_id': photo_archive_map[str(photo_id)]})


if __name__ == "__main__":
    # http://web.archive.org/cdx/search/cdx?url=www.panoramio.com%2Fuser%2F263050%3Fcomment_page%3D1%26photo_page%3D*&output=txt&limit=999999
    # input_file = r"c:\Users\jack\Desktop\webarchive5.txt"  # Replace with your input file path
    input_file = r"d:\code\test\cdx_2304697_with_photo_id.txt"
    output_file = r"D:\code\test\photo_ids_u2304697.csv"  # Generated CSV file path and name
    main(input_file, output_file)
    print(f"Saved photo_ids to {output_file}")
