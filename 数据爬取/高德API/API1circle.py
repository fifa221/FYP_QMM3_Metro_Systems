import os
import requests
import pandas as pd
import re
from math import radians, cos, sin, asin, sqrt
import time

# ================= 1. 配置路径 (已改为相对路径) =================
# 使用相对路径，这样无论代码文件夹放在哪里，只要结构不变就能运行
BASE_PATH = os.path.join("API获取的数据（含环）")
if not os.path.exists(BASE_PATH): 
    os.makedirs(BASE_PATH)

# ================= 2. 系统清单 =================
CITIES = [
    ("1100", "beijing", "北京地铁"), ("1200", "tianjin", "天津地铁"), ("8100", "xianggang", "港铁"),
    ("3100", "shanghai", "上海地铁"), ("4401", "guangzhou", "广州地铁"), ("2201", "changchun", "长春轨道交通"),
    ("2102", "dalian", "大连地铁"), ("4201", "wuhan", "武汉地铁"), ("4403", "shenzhen", "深圳地铁"),
    ("5000", "chongqing", "重庆轨道交通"), ("3201", "nanjing", "南京地铁"), ("2101", "shenyang", "沈阳地铁"),
    ("5101", "chengdu", "成都地铁"), ("4406", "foshan", "佛山地铁"), ("6101", "xian", "西安地铁"),
    ("3205", "suzhou", "苏州轨道交通"), ("5301", "kunming", "昆明地铁"), ("3301", "hangzhou", "杭州地铁"),
    ("2301", "haerbin", "哈尔滨地铁"), ("4101", "zhengzhou", "郑州地铁"), ("4301", "changsha", "长沙地铁"),
    ("3302", "ningbo", "宁波轨道交通"), ("3202", "wuxi", "无锡地铁"), ("3702", "qingdao", "青岛地铁"),
    ("3601", "nanchang", "南昌地铁"), ("3501", "fuzhou", "福州地铁"), ("4419", "dongguan", "东莞轨道交通"),
    ("4501", "nanning", "南宁地铁"), ("3401", "hefei", "合肥轨道交通"), ("1301", "shijiazhuang", "石家庄地铁"),
    ("5201", "guiyang", "贵阳地铁"), ("3502", "xiamen", "厦门轨道交通"), ("6501", "wulumuqi", "乌鲁木齐地铁"),
    ("3303", "wenzhou", "温州轨道交通"), ("3701", "jinan", "济南地铁"), ("6201", "lanzhou", "兰州轨道交通"),
    ("3204", "changzhou", "常州地铁"), ("3203", "xuzhou", "徐州地铁"), ("8200", "aomen", "澳门轻轨"),
    ("1501", "huhehaote", "呼和浩特地铁"), ("1401", "taiyuan", "太原轨道交通"), ("4103", "luoyang", "洛阳轨道交通"),
    ("3306", "shaoxing", "绍兴轨道交通"), ("3304", "hanghai", "杭海城际铁路"), ("3402", "wuhu", "芜湖轨道交通"),
    ("3307", "jinhua", "金华轨道交通"), ("3206", "nantong", "南通地铁"), ("3310", "taizhou", "台州市域铁路")
]

# ================= 3. 工具函数 =================
def get_distance(p1, p2):
    """计算经纬度距离(km)"""
    try:
        lon1, lat1 = map(radians, map(float, p1))
        lon2, lat2 = map(radians, map(float, p2))
        return round(2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2)) * 6371, 3)
    except: return 0.0

def save_csv(data, pinyin, filename):
    folder = os.path.join(BASE_PATH, pinyin)
    if not os.path.exists(folder): os.makedirs(folder)
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', filename)
    pd.DataFrame(data).to_csv(os.path.join(folder, f"{safe_name}.csv"), index=False, encoding='utf_8_sig')

# ================= 4. 核心处理逻辑 =================
def process_city_data(json_data, system_name, pinyin_target):
    """提取线路、站点及边数据，并处理环线闭合"""
    lines = json_data.get('l', [])
    for l in lines:
        line_name = l['kn']
        
        # 杭海城际铁路筛选
        if pinyin_target == "hanghai":
            if "杭海" not in line_name: continue
        else:
            if not any(k in line_name for k in ["地铁", "线", "轨道", "城际", "市域"]): continue

        stations, edges = [], []
        prev_st = None
        total_km = 0.0
        
        # 环线标记检测 (高德数据中 lo: "1" 代表环线)
        is_circle = str(l.get('lo')) == "1"

        station_list = l.get('st', [])
        for st in station_list:
            curr_p = st['sl'].split(',')
            dist = get_distance(prev_st['coords'], curr_p) if prev_st else 0.0
            total_km += dist
            
            # 站点记录
            stations.append({
                "系统": system_name,
                "线路": line_name,
                "站名": st['n'],
                "站间距(km)": dist,
                "累计里程(km)": round(total_km, 3),
                "经度": curr_p[0],
                "纬度": curr_p[1],
                "station ID": st['si'],
                "pinyin": st.get('py', ''),
                "year of opening": ""
            })

            # 边记录
            if prev_st:
                edges.append({
                    "系统": system_name,
                    "线路": line_name,
                    "from_station": prev_st['name'],
                    "to_station": st['n'],
                    "from_id": prev_st['id'],
                    "to_id": st['si'],
                    "distance(km)": dist,
                    "year of segment opening": ""
                })
            prev_st = {'coords': curr_p, 'name': st['n'], 'id': st['si']}

        # --- 关键修改：处理环线闭合逻辑 ---
        if is_circle and len(stations) > 1:
            first_st = stations[0]
            last_st = stations[-1]
            
            # 计算终点站回到起点站的距离
            p_last = (last_st['经度'], last_st['纬度'])
            p_first = (first_st['经度'], first_st['纬度'])
            closing_dist = get_distance(p_last, p_first)
            
            # 1. 在边数据中增加闭合边 (例如：积水潭 -> 西直门)
            edges.append({
                "系统": system_name,
                "线路": line_name,
                "from_station": last_st['站名'],
                "to_station": first_st['站名'],
                "from_id": last_st['station ID'],
                "to_id": first_st['station ID'],
                "distance(km)": closing_dist,
                "year of segment opening": ""
            })
            
            # 2. 在站点数据末尾增加一个“回到起点”的虚拟行，以体现完整里程（可选）
            # 如果不需要增加行，只需体现边即可。老师提到的环线核心是边要连起来。
            stations.append({
                "系统": system_name,
                "线路": line_name,
                "站名": first_st['站名'] + "(闭环回起点)",
                "站间距(km)": closing_dist,
                "累计里程(km)": round(total_km + closing_dist, 3),
                "经度": first_st['经度'],
                "纬度": first_st['纬度'],
                "station ID": first_st['station ID'],
                "pinyin": first_st['pinyin'],
                "year of opening": ""
            })

        save_csv(stations, pinyin_target, f"{line_name}_stations")
        save_csv(edges, pinyin_target, f"{line_name}_edges")
        print(f"   ✨ 已保存: {line_name} {'(环线已闭合)' if is_circle else ''}")

def run():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for code, pinyin, name in CITIES:
        print(f"🚀 正在处理系统: {name}")
        
        if pinyin == "hanghai":
            url = f"https://map.amap.com/service/subway?srhdata=3301_drw_hangzhou.json"
        else:
            url = f"https://map.amap.com/service/subway?srhdata={code}_drw_{pinyin}.json"
            
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200 and len(res.text) > 10:
                process_city_data(res.json(), name, pinyin)
            else:
                print(f"   ⚠️ {name} 数据接口无效，跳过")
        except Exception as e:
            print(f"   ❌ {name} 抓取异常: {e}")
        time.sleep(0.3)

if __name__ == "__main__":
    run()
    print("\n✅ 数据抓取与分离保存任务已完成！(环线已通过相对路径处理)")