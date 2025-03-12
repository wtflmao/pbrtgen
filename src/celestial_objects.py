from skyfield.api import load

def load_ephemeris(filename='de440s.bsp'):
    """加载 JPL DE 星历数据。"""
    return load(filename)

def get_celestial_object(eph, name):
    """从星历数据中获取天体对象。"""
    return eph[name]