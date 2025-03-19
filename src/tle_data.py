from skyfield.api import EarthSatellite, load

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