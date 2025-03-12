from skyfield.api import EarthSatellite, load

def load_tle_data(tle1_data, tle2_data):
  """加载 TLE 数据。"""
  tle1 = {}
  tle2 = {}
  for key, value in tle1_data.items():
    tle1[key] = value
  for key, value in tle2_data.items():
    tle2[key] = value
  return tle1, tle2

def get_satellite(tle1, tle2, name, ts):
    """从 TLE 数据创建 EarthSatellite 对象。"""
    return EarthSatellite(tle1[name], tle2[name], name, ts)