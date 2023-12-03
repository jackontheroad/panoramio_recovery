import pandas as pd
import simplekml

csv_file = r"d:\code\test\photo_list_u2304697_v2_complete.csv"
kml_file = csv_file[:-4] + ".kml"

# custom_icon_url = "D:/code/resource/shaded_dot.png"
# custom_icon_url = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
custom_icon_url = 'http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png'
icon_color = "ff0000ff"
df = pd.read_csv(csv_file)

# 创建 KML 对象
# Create KML Object
kml = simplekml.Kml()

# 创建样式对象，并设置图标
# Create style object, and set the icon
style = simplekml.Style()
style.iconstyle.icon.href = custom_icon_url
style.iconstyle.color = icon_color
style.iconstyle.scale = 0.7

# 遍历 DataFrame 中的每一行，将经纬度添加为 KML 点
# Iterate over every row in dataframe, and convert lat,lon to the points in KML.
count = 0
for index, row in df.iterrows():
    latlon_str = str(row["latlon"])  # 替换为你的纬度列的列名
    # if not pd.isna(row['latlon']) and "error" not in latlon_str:
    if not pd.isna(row['latlon']):
        count += 1
        coords = latlon_str.strip().split(",")
        point = kml.newpoint(coords=[(coords[1], coords[0])])
        # point.name = "{:05d}".format(row["index"]) + row["title"]
        # point.extendeddata.schemadata.newsimpledata("photo_url", row['photo_url'])
        # point.extendeddata.schemadata.newsimpledata("thumbnail_url", row['thumbnail_url'])
        tags_str = "" if pd.isna(row["tags"]) else row["tags"]
        time_str = "uploaded on " + row['uploaded_on']
        location = "" if pd.isna(row["location"]) else row["location"]
        if not pd.isna(row['taken_on']):
            time_str = row['taken_on']
        # 在描述中添加 HTML 代码，包括图片标签
        description_html = f"""
            <![CDATA[
                <div style="font-size: 20px;">
                    <p style="margin-bottom: 2px;margin-top: 0px;">Title: <a href="{row['photo_page_url']}">{row['title']}</a></p>
                    <p style="margin-bottom: 2px;margin-top: 0px;">Tags: {tags_str}</p>
                    <p style="margin-bottom: 2px;margin-top: 0px;">Date: {time_str}</p>
                    <p style="margin-bottom: 2px;margin-top: 0px;">Location: {location}</p>
                    <p style="margin-bottom: 2px;margin-top: 0px;"><a href="{row['photo_url']}">Big picture</a></p>
                    <img src="{row['thumbnail_url']}" alt="Image" style="margin-top: 5px;">
                </div>
            ]]>
        """
        point.description = description_html
        point.style = style
    # point.description = f"Additional information: {row['AdditionalInfo']}"  # 可选，添加其他信息
print("--------------" + str(count) + "----------------")
# 保存 KML 文件
kml.save(kml_file)
