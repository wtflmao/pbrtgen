from skyfield.api import load, Topos, EarthSatellite, wgs84
from astropy.coordinates import ICRS, EarthLocation, GCRS
from astropy.time import Time
import astropy.units as u

from .celestial_objects import load_ephemeris, get_celestial_object
from .coordinates import skyfield_to_icrs, icrs_to_gcrs, convert_au_to_km
from .time_utils import get_timescale, get_utc_time
from .tle_data import load_tle_data, get_satellite

# 1. 加载 JPL DE 星历数据
eph = load_ephemeris() # from Year 1849 to Year 2150
earth = get_celestial_object(eph, 'earth')
sun = get_celestial_object(eph, 'sun')
moon = get_celestial_object(eph, 'moon')

# 2. 定义时间 (2025年3月10日 UTC+8 08:00)
ts = get_timescale() # 获取 skyfield 的 timescale
time_utc = get_utc_time(ts, 2025, 3, 10, 8, 0, 0) # 使用 skyfield 的 timescale 创建 Time 对象

# 3. 定义 Starlink 卫星的 TLE 数据 
TLE1 = {'STARLINK-1008': '1 44714C 19074B   25068.82340278  .00023551  00000+0  15777-2 0   687',
        'STARLINK-32899': '1 62994C 25031P   25068.72965278 -.00277140  00000+0 -65975-2 0   681'}
TLE2 = {'STARLINK-1008': '2 44714  53.0541  24.5636 0001323  91.3133  52.2749 15.06379808    12',
        'STARLINK-32899': '2 62994  43.0001  46.1320 0001076 273.3956 308.7151 15.41042779    11'}

satellite_1008 = EarthSatellite(TLE1['STARLINK-1008'], TLE2['STARLINK-1008'], 'Starlink-1008', load.timescale())
satellite_32899 = EarthSatellite(TLE1['STARLINK-32899'], TLE2['STARLINK-32899'], 'Starlink-32899', load.timescale())

# 4. 定义地面观测站的位置 (例如， Greenwich Observatory)
# 使用 Topos 定义地面位置，需要经纬度。这里使用格林威治天文台的经纬度作为示例
observer_location = Topos(latitude_degrees=51.4769, longitude_degrees=0.0) # 格林威治天文台


# 5. 计算天体在地心系中的位置 (地心坐标，因为我们使用 earth.at(time_utc))
earth_position = earth.at(time_utc).position  # 地球自身的地心坐标，应该是 [0, 0, 0] (实际上是地球-月球质心)
sun_position = sun.at(time_utc).position
moon_position = moon.at(time_utc).position
satellite_1008_position = (earth + satellite_1008).at(time_utc).position
satellite_32899_position = (earth + satellite_32899).at(time_utc).position


# 6. 将 skyfield 的位置转换为 astropy 的 ICRS 坐标
# 正确提取三维坐标分量并添加单位
earth_icrs = skyfield_to_icrs(earth_position)
sun_icrs = skyfield_to_icrs(sun_position)
moon_icrs = skyfield_to_icrs(moon_position)
satellite_1008_icrs = skyfield_to_icrs(satellite_1008_position)
satellite_32899_icrs = skyfield_to_icrs(satellite_32899_position)

# 7. 将 skyfield 的位置转换为 astropy 的 ICRS 坐标 (单位 km)
# 正确提取三维坐标分量并添加单位
au_to_km = 149597870.7  # 1 au in km

earth_icrs_km = convert_au_to_km(earth_icrs)
sun_icrs_km = convert_au_to_km(sun_icrs)
moon_icrs_km = convert_au_to_km(moon_icrs)
satellite_1008_icrs_km = convert_au_to_km(satellite_1008_icrs)
satellite_32899_icrs_km = convert_au_to_km(satellite_32899_icrs)


# 8. 转换为 GCRS 坐标 (单位: 千米 km)
earth_gcrs_km = icrs_to_gcrs(earth_icrs_km, time_utc.utc_iso())
sun_gcrs_km = icrs_to_gcrs(sun_icrs_km, time_utc.utc_iso())
moon_gcrs_km = icrs_to_gcrs(moon_icrs_km, time_utc.utc_iso())
satellite_1008_gcrs_km = icrs_to_gcrs(satellite_1008_icrs_km, time_utc.utc_iso())
satellite_32899_gcrs_km = icrs_to_gcrs(satellite_32899_icrs_km, time_utc.utc_iso())

# 9. 输出结果
print(f"Time: {time_utc.utc_iso()}")
print("--------------------")
print(f"Earth (ICRS, AU): X={earth_icrs.x:.6f}, Y={earth_icrs.y:.6f}, Z={earth_icrs.z:.6f}")
print(f"Sun (ICRS, AU): X={sun_icrs.x:.6f}, Y={sun_icrs.y:.6f}, Z={sun_icrs.z:.6f}")
print(f"Moon (ICRS, AU): X={moon_icrs.x:.6f}, Y={moon_icrs.y:.6f}, Z={moon_icrs.z:.6f}")
print(f"Starlink-1008 (ICRS, AU): X={satellite_1008_icrs.x:.6f}, Y={satellite_1008_icrs.y:.6f}, Z={satellite_1008_icrs.z:.6f}")
print(f"Starlink-32899 (ICRS, AU): X={satellite_32899_icrs.x:.6f}, Y={satellite_32899_icrs.y:.6f}, Z={satellite_32899_icrs.z:.6f}")

print("--------------------")
print(f"Earth (ICRS, km): X={earth_icrs_km.x:.6f}, Y={earth_icrs_km.y:.6f}, Z={earth_icrs_km.z:.6f}")
print(f"Sun (ICRS, km): X={sun_icrs_km.x:.6f}, Y={sun_icrs_km.y:.6f}, Z={sun_icrs_km.z:.6f}")
print(f"Moon (ICRS, km): X={moon_icrs_km.x:.6f}, Y={moon_icrs_km.y:.6f}, Z={moon_icrs_km.z:.6f}")
print(f"Starlink-1008 (ICRS, km): X={satellite_1008_icrs_km.x:.6f}, Y={satellite_1008_icrs_km.y:.6f}, Z={satellite_1008_icrs_km.z:.6f}")
print(f"Starlink-32899 (ICRS, km): X={satellite_32899_icrs_km.x:.6f}, Y={satellite_32899_icrs_km.y:.6f}, Z={satellite_32899_icrs_km.z:.6f}")

print("--------------------")
print(f"Earth (GCRS, km): X={earth_gcrs_km.x:.6f}, Y={earth_gcrs_km.y:.6f}, Z={earth_gcrs_km.z:.6f}")
print(f"Sun (GCRS, km): X={sun_gcrs_km.x:.6f}, Y={sun_gcrs_km.y:.6f}, Z={sun_gcrs_km.z:.6f}") # 应该接近地球坐标
print(f"Moon (GCRS, km): X={moon_gcrs_km.x:.6f}, Y={moon_gcrs_km.y:.6f}, Z={moon_gcrs_km.z:.6f}")
print(f"Starlink-1008 (GCRS, km): X={satellite_1008_gcrs_km.x:.6f}, Y={satellite_1008_gcrs_km.y:.6f}, Z={satellite_1008_gcrs_km.z:.6f}")
print(f"Starlink-32899 (GCRS, km): X={satellite_32899_gcrs_km.x:.6f}, Y={satellite_32899_gcrs_km.y:.6f}, Z={satellite_32899_gcrs_km.z:.6f}")