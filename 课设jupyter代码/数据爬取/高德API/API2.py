import os
import pandas as pd

# ================= 1. 配置路径 (保持与你原脚本一致) =================
BASE_PATH = r"D:\大学作业\毕业设计\确认项目\数据爬取\高德API\API获取的数据"
OUTPUT_DIR = os.path.join(BASE_PATH, "beijing")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def generate_t1_data():
    # 2. 亦庄T1线 核心数据 (根据最新运营数据整理)
    # 字段顺序: 站名, 累计里程(m), 经度, 纬度
    raw_data = [
        ("屈庄", 0, 116.486221, 39.721245),
        ("融兴街", 801, 116.489112, 39.727567),
        ("瑞合庄", 1603, 116.491456, 39.734231),
        ("太和桥北", 2978, 116.495827, 39.739901),
        ("四海庄", 3616, 116.502112, 39.741234),
        ("九号村", 4609, 116.510345, 39.745678),
        ("泰河路", 5215, 116.514567, 39.750123),
        ("鹿圈东", 5954, 116.520123, 39.755678),
        ("亦庄同仁", 7182, 116.528901, 39.762345),
        ("荣昌东街", 7786, 116.536789, 39.764567), # 可换乘亦庄线
        ("亦创会展中心", 8394, 116.541234, 39.768901),
        ("经海一路", 9762, 116.548901, 39.778901),
        ("定海园西", 11019, 116.547449, 39.795703),
        ("定海园", 11899, 116.556789, 39.800123)
    ]

    # 3. 生成 Station 数据
    stations = []
    prev_meter = 0
    for name, meter, lon, lat in raw_data:
        dist_km = round((meter - prev_meter) / 1000.0, 3)
        stations.append({
            "系统": "北京地铁",
            "线路": "亦庄有轨电车T1线",
            "站名": name,
            "站间距(km)": dist_km if meter > 0 else 0.0,
            "累计里程(km)": round(meter / 1000.0, 3),
            "经度": lon,
            "纬度": lat,
            "station ID": f"T1_{name}",
            "pinyin": "",
            "year of opening": "2020"
        })
        prev_meter = meter

    # 4. 生成 Edge 数据
    edges = []
    for i in range(len(stations) - 1):
        s1 = stations[i]
        s2 = stations[i+1]
        edges.append({
            "系统": "北京地铁",
            "线路": "亦庄有轨电车T1线",
            "from_station": s1["站名"],
            "to_station": s2["站名"],
            "from_id": s1["station ID"],
            "to_id": s2["station ID"],
            "distance(km)": s2["站间距(km)"],
            "year of segment opening": "2020"
        })

    # 5. 保存文件
    pd.DataFrame(stations).to_csv(os.path.join(OUTPUT_DIR, "亦庄有轨电车T1线_stations.csv"), index=False, encoding='utf_8_sig')
    pd.DataFrame(edges).to_csv(os.path.join(OUTPUT_DIR, "亦庄有轨电车T1线_edges.csv"), index=False, encoding='utf_8_sig')
    
    print(f"✅ 亦庄T1线数据已成功注入到: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_t1_data()