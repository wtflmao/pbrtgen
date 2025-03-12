from skyfield.api import load

def get_timescale():
    """获取 Skyfield 的 timescale。"""
    return load.timescale()

def get_utc_time(ts, year, month, day, hour, minute, second):
    """使用 Skyfield 的 timescale 创建 Time 对象。"""
    return ts.utc(year, month, day, hour, minute, second)