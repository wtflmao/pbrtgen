from skyfield.api import EarthSatellite, load
import os
import requests
from datetime import datetime, timedelta

# 项目根目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# TLE缓存目录
TLE_CACHE_DIR = os.path.join(PROJECT_ROOT, 'tle')

# 确保TLE缓存目录存在
os.makedirs(TLE_CACHE_DIR, exist_ok=True)

def download_tle_file(url, filename):
    """下载TLE文件
    
    Args:
        url (str): TLE文件下载地址
        filename (str): 保存的文件名
        
    Returns:
        str: 下载的文件路径
    """
    filepath = os.path.join(TLE_CACHE_DIR, filename)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查下载是否成功
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"成功下载TLE文件: {filepath}")
        return filepath
    except Exception as e:
        print(f"下载TLE文件失败: {e}")
        return None

def is_tle_cache_valid(filepath, max_age_days=1):
    """检查TLE缓存文件是否有效
    
    Args:
        filepath (str): 文件路径
        max_age_days (int): 最大缓存有效期（天）
        
    Returns:
        bool: 缓存是否有效
    """
    if not os.path.exists(filepath):
        return False
    
    # 获取文件最后修改时间
    file_mtime = os.path.getmtime(filepath)
    file_age = datetime.now() - datetime.fromtimestamp(file_mtime)
    
    return file_age <= timedelta(days=max_age_days)

def get_tle_data(url, filename='active_satellites.tle'):
    """获取TLE数据，优先使用缓存
    
    Args:
        url (str): TLE文件下载地址
        filename (str): 缓存文件名
        
    Returns:
        dict: TLE数据字典
    """
    filepath = os.path.join(TLE_CACHE_DIR, filename)
    
    # 检查缓存是否有效
    if is_tle_cache_valid(filepath):
        print(f"使用缓存的TLE文件: {filepath}")
    else:
        # 下载新的TLE文件
        filepath = download_tle_file(url, filename)
        if not filepath:
            raise RuntimeError("无法获取TLE数据")
    
    # 解析TLE文件
    return parse_tle_file(filepath)

def parse_tle_file(filepath):
    """解析TLE文件
    
    Args:
        filepath (str): TLE文件路径
        
    Returns:
        dict: 解析后的TLE数据字典
    """
    tle_data = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 每3行为一组TLE数据
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                sat_name = lines[i].strip()
                tle_line1 = lines[i+1].strip()
                tle_line2 = lines[i+2].strip()
                
                tle_data[sat_name] = [tle_line1, tle_line2]
        
        print(f"成功解析 {len(tle_data)} 个卫星的TLE数据")
        return tle_data
    except Exception as e:
        print(f"解析TLE文件失败: {e}")
        return {}

def load_tle_data(tle_data):
    """加载 TLE 数据。
    
    Args:
        tle_data (dict): TLE数据字典，格式为 {卫星名: [tle1_line, tle2_line]}
        
    Returns:
        dict: 处理后的TLE数据字典
    """
    tle = {}
    for key, value in tle_data.items():
        tle[key] = value
    return tle

def get_satellite(tle, name, ts):
    """从 TLE 数据创建 EarthSatellite 对象。
    
    Args:
        tle (dict): TLE数据字典，格式为 {卫星名: [tle1_line, tle2_line]}
        name (str): 卫星名称
        ts: 时间刻度对象
        
    Returns:
        EarthSatellite: 创建的卫星对象
    """
    return EarthSatellite(tle[name][0], tle[name][1], name, ts)