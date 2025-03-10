from skyfield.api import load, Topos, EarthSatellite, wgs84
from astropy.coordinates import ICRS, EarthLocation
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


# 5. 计算天体在太阳系中的位置 (地心坐标，因为我们使用 earth.at(time_utc))
earth_position = earth.at(time_utc).position  # 地球自身的地心坐标，应该是 [0, 0, 0]
sun_position = earth.at(time_utc).observe(sun).position
moon_position = earth.at(time_utc).observe(moon).position
satellite_1008_position = earth.at(time_utc).observe(satellite_1008).position
satellite_32899_position = earth.at(time_utc).observe(satellite_32899).position

# 6. 计算天体在观测站的位置
earth_position = observer_location.at(time_utc).position
sun_position = observer_location.at(time_utc).observe(sun).position
moon_position = observer_location.at(time_utc).observe(moon).position
satellite_1008_position = observer_location.at(time_utc).observe(satellite_1008).position # 从地面观测站观测卫星
satellite_32899_position = observer_location.at(time_utc).observe(satellite_32899).position # 从地面观测站观测卫星


# 6. 将 skyfield 的位置转换为 astropy 的 ICRS 坐标
# skyfield 的 position 是 Cartesian 坐标，单位是 AU
earth_icrs = ICRS(earth_position.au, earth_position.au, earth_position.au, unit=u.au) # 理论上应该是 [0,0,0]
sun_icrs = ICRS(sun_position.au, sun_position.au, sun_position.au, unit=u.au)
moon_icrs = ICRS(moon_position.au, moon_position.au, moon_position.au, unit=u.au)
satellite_1008_icrs = ICRS(satellite_1008_position.au, satellite_1008_position.au, satellite_1008_position.au, unit=u.au)
satellite_32899_icrs = ICRS(satellite_32899_position.au, satellite_32899_position.au, satellite_32899_position.au, unit=u.au)

# 6. 输出结果
print(f"Time: {time_utc.iso}")
print("--------------------")
print(f"Earth (ICRS): X={earth_icrs.x:.6f}, Y={earth_icrs.y:.6f}, Z={earth_icrs.z:.6f}") # 应该接近零
print(f"Sun (ICRS): X={sun_icrs.x:.6f}, Y={sun_icrs.y:.6f}, Z={sun_icrs.z:.6f}")
print(f"Moon (ICRS): X={moon_icrs.x:.6f}, Y={moon_icrs.y:.6f}, Z={moon_icrs.z:.6f}")
#print(f"Starlink-1008 (ICRS): X={satellite_1008_icrs.x:.6f}, Y={satellite_1008_icrs.y:.6f}, Z={satellite_1008_icrs.z:.6f}")
#print(f"Starlink-32899 (ICRS): X={satellite_32899_icrs.x:.6f}, Y={satellite_32899_icrs.y:.6f}, Z={satellite_32899_icrs.z:.6f}")
print(f"Starlink-1008 (Station): X={satellite_1008_icrs.x:.6f}, Y={satellite_1008_icrs.y:.6f}, Z={satellite_1008_icrs.z:.6f}")
print(f"Starlink-32899 (Station): X={satellite_32899_icrs.x:.6f}, Y={satellite_32899_icrs.y:.6f}, Z={satellite_32899_icrs.z:.6f}")