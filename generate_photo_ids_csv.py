# Author: ChatGPT
# Date: November 25, 2023
import csv


# def extract_photo_id(line):
#     # 通过分割空格获取数据中的第2列（with_photo_id）
#     return line.split()[0].split('=')[-1]


def main(input_file, output_file):
    photo_ids = set()
    photo_archive_map = {}
    # read file and ectract with_photo_id
    # 读取输入文件并提取 with_photo_id
    with open(input_file, 'r') as file:
        for line in file:
            segs = line.split()
            photo_id = segs[0].split('=')[-1]
            photo_ids.add(photo_id)
            photo_archive_map[str(photo_id)] = segs[1]
    # resort photo_ids
    # 对 photo_ids 进行排序
    sorted_photo_ids = sorted(photo_ids, key=lambda x: int(x))

    # save to csv file
    # 将排序后的 with_photo_id 保存到 CSV 文件
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['index', 'photo_id', 'archive_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for index, photo_id in enumerate(sorted_photo_ids):
            writer.writerow({'index': index, 'photo_id': photo_id, 'archive_id': photo_archive_map[str(photo_id)]})


if __name__ == "__main__":
    # https://web.archive.org/cdx/search/cdx?url=www.panoramio.com/user/2304697?with_photo_id=*&output=txt&limit=999999
    # Replace with your input file path
    input_file = r"d:\code\test\cdx_2304697_with_photo_id.txt" 
    # output filename in this format is required， u2304697 User ID will be used in subsequent scripts
    # 输出文件命必须用这个格式 u2304697 User ID会被之后的程序用到
    output_file = r"D:\code\test\photo_ids_u2304697.csv"  
    main(input_file, output_file)
    print(f"Saved photo_ids to {output_file}")
