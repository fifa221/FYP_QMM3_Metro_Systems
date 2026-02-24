import pandas as pd
import glob
import os

# ================= 配置区域 =================

# 1. 源数据文件夹 (你存放原始csv的位置)
# 使用 r"..." 表示原始字符串，防止反斜杠转义问题
source_dir = r"D:\大学作业\毕业设计\确认项目\FYP_QMM3_Metro_Systems\数据爬取\高德API\API获取的数据\zhengzhou"

# 2. 整合后输出文件夹
output_dir = r"D:\大学作业\毕业设计\确认项目\FYP_QMM3_Metro_Systems\数据爬取\高德API\整合数据"

# ===========================================

def merge_and_save(file_pattern, output_filename):
    # 构建完整的搜索路径
    search_path = os.path.join(source_dir, file_pattern)
    all_files = glob.glob(search_path)
    
    print(f"\n正在搜索: {search_path}")
    
    if not all_files:
        print(f"❌ 警告: 在源目录未找到匹配 '{file_pattern}' 的文件。请检查路径是否正确。")
        return

    print(f"找到 {len(all_files)} 个文件，准备合并...")
    
    df_list = []
    for filename in all_files:
        try:
            # encoding='utf-8-sig' 用于处理带有BOM的中文CSV，防止乱码
            df = pd.read_csv(filename, encoding='utf-8-sig')
            df_list.append(df)
        except Exception as e:
            print(f"⚠️ 读取文件 {os.path.basename(filename)} 出错: {e}")

    if df_list:
        # 合并所有数据
        combined_df = pd.concat(df_list, ignore_index=True)
        
        # 确保输出目录存在，不存在则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"已创建输出目录: {output_dir}")

        # 构建完整的输出路径
        full_output_path = os.path.join(output_dir, output_filename)
        
        # 保存文件
        combined_df.to_csv(full_output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 成功！文件已保存至: {full_output_path}")
        print(f"   总行数: {len(combined_df)}")
    else:
        print("没有可合并的数据。")

# --- 主程序执行 ---

if __name__ == "__main__":
    print("--- 开始处理地铁数据 ---")
    
    # 1. 合并 Stations (站点)
    # 文件名保存为：北京_All_Stations.csv
    merge_and_save('*_stations.csv', 'zhengzhou_All_Stations.csv')

    # 2. 合并 Edges (路段)
    # 文件名保存为：北京_All_Edges.csv
    merge_and_save('*_edges.csv', 'zhengzhou_All_Edges.csv')
    
    print("\n--- 处理结束 ---")