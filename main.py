from skyfield.api import load, Topos, EarthSatellite, wgs84
from astropy.coordinates import ICRS, EarthLocation, GCRS
from astropy.time import Time
import astropy.units as u

# 1. 加载 JPL DE 星历数据
eph = load('de440s.bsp') # from Year 1849 to Year 2150
earth = eph['earth']
sun = eph['sun']
moon = eph['moon']

# 2. 定义时间 (2025年3月10日 UTC+8 08:00)
ts = load.timescale() # 获取 skyfield 的 timescale
time_utc = ts.utc(2025, 3, 10, 8, 0, 0) # 使用 skyfield 的 timescale 创建 Time 对象

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
earth_icrs = ICRS(
    x=earth_position.au[0] * u.au,
    y=earth_position.au[1] * u.au,
    z=earth_position.au[2] * u.au,
    representation_type='cartesian'
)

sun_icrs = ICRS(
    x=sun_position.au[0] * u.au,
    y=sun_position.au[1] * u.au,
    z=sun_position.au[2] * u.au,
    representation_type='cartesian'
)

moon_icrs = ICRS(
    x=moon_position.au[0] * u.au,
    y=moon_position.au[1] * u.au,
    z=moon_position.au[2] * u.au,
    representation_type='cartesian'
)

satellite_1008_icrs = ICRS(
    x=satellite_1008_position.au[0] * u.au,
    y=satellite_1008_position.au[1] * u.au,
    z=satellite_1008_position.au[2] * u.au,
    representation_type='cartesian'
)

satellite_32899_icrs = ICRS(
    x=satellite_32899_position.au[0] * u.au,
    y=satellite_32899_position.au[1] * u.au,
    z=satellite_32899_position.au[2] * u.au,
    representation_type='cartesian'
)

# 6. 将 skyfield 的位置转换为 astropy 的 ICRS 坐标 (单位 km)
# 正确提取三维坐标分量并添加单位
au_to_km = 149597870.7  # 1 au in km

earth_icrs_km = ICRS(
    x=earth_icrs.x.value * au_to_km * u.km,
    y=earth_icrs.y.value * au_to_km * u.km,
    z=earth_icrs.z.value * au_to_km * u.km,
    representation_type='cartesian'
)

sun_icrs_km = ICRS(
    x=sun_icrs.x.value * au_to_km * u.km,
    y=sun_icrs.y.value * au_to_km * u.km,
    z=sun_icrs.z.value * au_to_km * u.km,
    representation_type='cartesian'
)

moon_icrs_km = ICRS(
    x=moon_icrs.x.value * au_to_km * u.km,
    y=moon_icrs.y.value * au_to_km * u.km,
    z=moon_icrs.z.value * au_to_km * u.km,
    representation_type='cartesian'
)

satellite_1008_icrs_km = ICRS(
    x=satellite_1008_icrs.x.value * au_to_km * u.km,
    y=satellite_1008_icrs.y.value * au_to_km * u.km,
    z=satellite_1008_icrs.z.value * au_to_km * u.km,
    representation_type='cartesian'
)

satellite_32899_icrs_km = ICRS(
    x=satellite_32899_icrs.x.value * au_to_km * u.km,
    y=satellite_32899_icrs.y.value * au_to_km * u.km,
    z=satellite_32899_icrs.z.value * au_to_km * u.km,
    representation_type='cartesian'
)


# 7.1. 转换为 GCRS 坐标 (单位: 千米 km)
earth_gcrs_km = earth_icrs_km.transform_to(GCRS(obstime=Time(time_utc.utc_iso()))).cartesian
sun_gcrs_km = sun_icrs_km.transform_to(GCRS(obstime=Time(time_utc.utc_iso()))).cartesian
moon_gcrs_km = moon_icrs_km.transform_to(GCRS(obstime=Time(time_utc.utc_iso()))).cartesian
satellite_1008_gcrs_km = satellite_1008_icrs_km.transform_to(GCRS(obstime=Time(time_utc.utc_iso()))).cartesian
satellite_32899_gcrs_km = satellite_32899_icrs_km.transform_to(GCRS(obstime=Time(time_utc.utc_iso()))).cartesian

# 7. 输出结果
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