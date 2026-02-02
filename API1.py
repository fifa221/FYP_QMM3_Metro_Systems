import os
import requests
import pandas as pd
import re
from math import radians, cos, sin, asin, sqrt
import time

# ================= 1. 配置路径 =================
BASE_PATH = r"D:\大学作业\毕业设计\确认项目\数据爬取\高德API\API获取的数据"
if not os.path.exists(BASE_PATH): os.makedirs(BASE_PATH)

# ================= 2. 系统清单 (嘉兴已改为 hanghai) =================
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
    # 处理线路名称中的非法字符
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', filename)
    pd.DataFrame(data).to_csv(os.path.join(folder, f"{safe_name}.csv"), index=False, encoding='utf_8_sig')

# ================= 4. 核心处理逻辑 =================
def process_city_data(json_data, system_name, pinyin_target):
    """提取线路、站点及边数据"""
    lines = json_data.get('l', [])
    for l in lines:
        line_name = l['kn']
        
        # 杭海城际铁路的特定筛选逻辑
        if pinyin_target == "hanghai":
            if "杭海" not in line_name: continue
        else:
            if not any(k in line_name for k in ["地铁", "线", "轨道", "城际", "市域"]): continue

        stations, edges = [], []
        prev_st = None
        total_km = 0.0

        for st in l.get('st', []):
            curr_p = st['sl'].split(',')
            dist = get_distance(prev_st['coords'], curr_p) if prev_st else 0.0
            total_km += dist
            
            # 站点数据 (完全对齐你的模板字段)
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

            # 边数据 (满足 Station 和 Edge 分离的要求)
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

        save_csv(stations, pinyin_target, f"{line_name}_stations")
        save_csv(edges, pinyin_target, f"{line_name}_edges")
        print(f"   ✨ 已保存: {line_name}")

def run():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for code, pinyin, name in CITIES:
        print(f"🚀 正在处理系统: {name}")
        
        # 杭海线的重定向逻辑：从杭州数据源提取
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
    print("\n✅ 数据抓取与分离保存任务（含 hanghai 更新）已完成！")