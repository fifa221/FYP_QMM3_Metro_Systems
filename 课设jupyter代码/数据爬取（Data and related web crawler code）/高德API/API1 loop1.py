import os
import requests
import pandas as pd
import re
from math import radians, cos, sin, asin, sqrt
import time

# ================= 1. 配置路径 (相对路径) =================
BASE_PATH = os.path.join("API获取的数据（含环和分叉）")
if not os.path.exists(BASE_PATH): 
    os.makedirs(BASE_PATH)

# ================= 2. 系统清单 =================
CITIES = [
    ("1100", "Beijing", "北京地铁", "beijing"), ("1200", "Tianjin", "天津地铁", "tianjin"), 
    ("8100", "Hong Kong", "港铁", "xianggang"), ("3100", "Shanghai", "上海地铁", "shanghai"), 
    ("4401", "Guangzhou", "广州地铁", "guangzhou"), ("2201", "Changchun", "长春轨道交通", "changchun"),
    ("2102", "Dalian", "大连地铁", "dalian"), ("4201", "Wuhan", "武汉地铁", "wuhan"), 
    ("4403", "Shenzhen", "深圳地铁", "shenzhen"), ("5000", "Chongqing", "重庆轨道交通", "chongqing"), 
    ("3201", "Nanjing", "南京地铁", "nanjing"), ("2101", "Shenyang", "沈阳地铁", "shenyang"),
    ("5101", "Chengdu", "成都地铁", "chengdu"), ("4406", "Foshan", "佛山地铁", "foshan"), 
    ("6101", "Xi'an", "西安地铁", "xian"), ("3205", "Suzhou", "苏州轨道交通", "suzhou"), 
    ("5301", "Kunming", "昆明地铁", "kunming"), ("3301", "Hangzhou", "杭州地铁", "hangzhou"),
    ("2301", "Harbin", "哈尔滨地铁", "haerbin"), ("4101", "Zhengzhou", "郑州地铁", "zhengzhou"), 
    ("4301", "Changsha", "长沙地铁", "changsha"), ("3302", "Ningbo", "宁波轨道交通", "ningbo"), 
    ("3202", "Wuxi", "无锡地铁", "wuxi"), ("3702", "Qingdao", "青岛地铁", "qingdao"),
    ("3601", "Nanchang", "南昌地铁", "nanchang"), ("3501", "Fuzhou", "福州地铁", "fuzhou"), 
    ("4419", "Dongguan", "东莞轨道交通", "dongguan"), ("4501", "Nanning", "南宁地铁", "nanning"), 
    ("3401", "Hefei", "合肥轨道交通", "hefei"), ("1301", "Shijiazhuang", "石家庄地铁", "shijiazhuang"),
    ("5201", "Guiyang", "贵阳地铁", "guiyang"), ("3502", "Xiamen", "厦门轨道交通", "xiamen"), 
    ("6501", "Urumqi", "乌鲁木齐地铁", "wulumuqi"), ("3303", "Wenzhou", "温州轨道交通", "wenzhou"), 
    ("3701", "Jinan", "济南地铁", "jinan"), ("6201", "Lanzhou", "兰州轨道交通", "lanzhou"),
    ("3204", "Changzhou", "常州地铁", "changzhou"), ("3203", "Xuzhou", "徐州地铁", "xuzhou"), 
    ("8200", "Macau", "澳门轻轨", "aomen"), ("1501", "Hohhot", "呼和浩特地铁", "huhehaote"), 
    ("1401", "Taiyuan", "太原轨道交通", "taiyuan"), ("4103", "Luoyang", "洛阳轨道交通", "luoyang"),
    ("3306", "Shaoxing", "绍兴轨道交通", "shaoxing"), ("3304", "Hanghai Intercity", "杭海城际铁路", "hangzhou"), 
    ("3402", "Wuhu", "芜湖轨道交通", "wuhu"), ("3307", "Jinhua", "金华轨道交通", "jinhua"), 
    ("3206", "Nantong", "南通地铁", "nantong"), ("3310", "Taizhou", "台州市域铁路", "taizhou")
]

# ================= 3. 工具函数 =================
def get_distance(p1, p2):
    """计算经纬度距离(km)"""
    try:
        lon1, lat1 = map(radians, map(float, p1))
        lon2, lat2 = map(radians, map(float, p2))
        return round(2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2)) * 6371, 3)
    except: return 0.0

def save_csv(data, folder_name, filename):
    folder = os.path.join(BASE_PATH, folder_name)
    if not os.path.exists(folder): os.makedirs(folder)
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', filename)
    pd.DataFrame(data).to_csv(os.path.join(folder, f"{safe_name}.csv"), index=False, encoding='utf_8_sig')

# ================= 4. 核心处理逻辑 =================
def process_city_data(json_data, system_name, folder_name):
    """提取线路数据，自动识别重名线路并按需加 ID"""
    lines = json_data.get('l', [])
    
    # --- 新增逻辑：预扫描线路名称统计 ---
    line_name_counts = {}
    valid_lines = []
    
    # 先初步筛选出符合条件的线路，并统计名称出现次数
    for l in lines:
        line_name = l['kn']
        if folder_name == "Hanghai Intercity":
            if "杭海" not in line_name: continue
        else:
            if not any(k in line_name for k in ["地铁", "线", "轨道", "城际", "市域"]): continue
        
        valid_lines.append(l)
        line_name_counts[line_name] = line_name_counts.get(line_name, 0) + 1

    # --- 开始处理经过筛选的线路 ---
    for l in valid_lines:
        line_name = l['kn']
        line_id = l.get('ls', 'unknown')
        
        # 核心逻辑：如果名称出现次数 > 1，则文件名带 ID，否则不带
        if line_name_counts[line_name] > 1:
            file_base_name = f"{line_name}_{line_id}"
        else:
            file_base_name = line_name

        stations, edges = [], []
        prev_st = None
        total_km = 0.0
        is_circle = str(l.get('lo')) == "1"

        station_list = l.get('st', [])
        for st in station_list:
            curr_p = st['sl'].split(',')
            dist = get_distance(prev_st['coords'], curr_p) if prev_st else 0.0
            total_km += dist
            
            stations.append({
                "系统": system_name, "线路": line_name, "线路ID": line_id,
                "站名": st['n'], "站间距(km)": dist, "累计里程(km)": round(total_km, 3),
                "经度": curr_p[0], "纬度": curr_p[1], "station ID": st['si'],
                "pinyin": st.get('py', ''), "year of opening": ""
            })

            if prev_st:
                edges.append({
                    "系统": system_name, "线路": line_name, "线路ID": line_id,
                    "from_station": prev_st['name'], "to_station": st['n'],
                    "from_id": prev_st['id'], "to_id": st['si'],
                    "distance(km)": dist, "year of segment opening": ""
                })
            prev_st = {'coords': curr_p, 'name': st['n'], 'id': st['si']}

        # 环线闭合逻辑
        if is_circle and len(stations) > 1:
            first_st, last_st = stations[0], stations[-1]
            p_last, p_first = (last_st['经度'], last_st['纬度']), (first_st['经度'], first_st['纬度'])
            closing_dist = get_distance(p_last, p_first)
            
            edges.append({
                "系统": system_name, "线路": line_name, "线路ID": line_id,
                "from_station": last_st['站名'], "to_station": first_st['站名'],
                "from_id": last_st['station ID'], "to_id": first_st['station ID'],
                "distance(km)": closing_dist, "year of segment opening": ""
            })
            stations.append({
                "系统": system_name, "线路": line_name, "线路ID": line_id,
                "站名": first_st['站名'] + "(闭环回起点)", "站间距(km)": closing_dist,
                "累计里程(km)": round(total_km + closing_dist, 3),
                "经度": first_st['经度'], "纬度": first_st['纬度'],
                "station ID": first_st['station ID'], "pinyin": first_st['pinyin'], "year of opening": ""
            })

        save_csv(stations, folder_name, f"{file_base_name}_stations")
        save_csv(edges, folder_name, f"{file_base_name}_edges")
        
        info = f"   ✨ 已保存: {file_base_name}"
        if is_circle: info += " [环线]"
        print(info)

def run():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for code, folder_name, sys_name, api_slug in CITIES:
        print(f"🚀 正在处理系统: {sys_name} ({folder_name})")
        url = f"https://map.amap.com/service/subway?srhdata={code}_drw_{api_slug}.json"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200 and len(res.text) > 10:
                process_city_data(res.json(), sys_name, folder_name)
            else:
                print(f"   ⚠️ {sys_name} 接口无效")
        except Exception as e:
            print(f"   ❌ {sys_name} 异常: {e}")
        time.sleep(0.3)

if __name__ == "__main__":
    run()
    print("\n✅ 处理完成！仅重名分叉线路带有编号。")