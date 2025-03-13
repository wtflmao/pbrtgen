"""
# 太阳系场景 (Solar System Scene)
# 单位: km (Units: km)
# 坐标系: 地球质心坐标系 (Geocentric Coordinate System)
#    原点: 地球质心 (Origin: Earth's center of mass)
#    X-Y 平面: 地球公转平面 (X-Y Plane: Ecliptic plane)
#    Z 轴: 垂直于公转平面，构成右手系 (Z-axis: Perpendicular to ecliptic, right-handed system)

# ** 注意 **: 使用 Mock 数据填充太阳和月球位置 (Using Mock data for Sun and Moon positions)
#          后期需要替换为实际的星历计算或 API 调用 (Replace with actual ephemeris data later)

WorldBegin # 世界定义开始 (World definition begins)

# 银河 HDR 背景光源 (Milky Way HDR Background Light)
# 假设 galaxy.exr 文件位于与 .pbrt 文件相同的目录下 (Assuming galaxy.exr is in the same directory as .pbrt file)
LightSource "infinite" "string filename" "milkyway_2020_8k_equalarea.exr"
            "float scale" [0.5] # 使用 scale 调整整体亮度，移除 rgb L  (Use scale to adjust brightness, removed rgb L)

# 太阳 (Sun)
AttributeBegin # 太阳属性块开始 (Sun attribute block starts)
  # 太阳位置 (Sun Position) - 使用 Mock 数据 (Using Mock data)
  Translate 1.28780140e+08 -6.67163443e+07 -2.89217364e+07

  # 太阳光谱光源 (Sun Spectrum Light Source)
  # 使用内置光谱 "stdillum-D65" 近似太阳光谱 (Using built-in spectrum "stdillum-D65" to approximate solar spectrum)
  # 注意: 真实的太阳光谱需要使用 spectrum.txt 文件，这里为了方便使用内置近似 (Note: Real solar spectrum needs spectrum.txt, using built-in for convenience)
  AreaLightSource "diffuse" "spectrum L" "stdillum-D65"
                    "float power" [3.828e+26] # 太阳光度，瓦特 (Solar luminosity in Watts)
                    "bool twosided" false # 单面发光 (One-sided emission)

  # 太阳几何形状 (Sun Geometry) - 移除 Material "interface"  (Removed Material "interface")
  Shape "sphere" "float radius" 695500 # 太阳半径 695500 km (Sun radius in km)
AttributeEnd # 太阳属性块结束 (Sun attribute block ends)

# 地球 (Earth)
AttributeBegin # 地球属性块开始 (Earth attribute block starts)
  # 地球位置 (Earth Position) - 地球位于坐标原点 (Earth is at the origin)
  Translate 0 0 0

  # **地球自转轴倾斜** (Earth's Axial Tilt) - 绕 X 轴旋转 23.5 度 (Rotate 23.5 degrees around X-axis)
  # 注意：这里只是一个静态倾斜演示。真实的自转轴方向会随时间变化。
  Rotate 23.5 1 0 0

  # 地球材质 (Earth Material) - 使用涂层漫反射材质模拟地球表面 (Coated Diffuse material for Earth's surface simulation)
  # 为了更逼真，可以考虑使用纹理贴图来控制反照率、粗糙度等参数。
  MakeNamedMaterial "earthMaterial" # 定义命名材质 (Define named material)
    "string type" "coateddiffuse"
    "rgb reflectance" [0.1 0.2 0.3]  #  地球平均反照率近似值，蓝色调为主 (Approximate Earth albedo, bluish tone)
    "float roughness" 0.15         #  适中粗糙度 (Moderate roughness)
    "float thickness" 0.001        #  涂层厚度 (Coating thickness)
    "rgb albedo" [0.1 0.2 0.3]    #  涂层下的漫反射层反照率 (Albedo of diffuse base layer under coating)
    "float g" 0.0                 #  涂层内部散射各项异性参数 (Coating internal scattering asymmetry)
    "integer maxdepth" 5          #  涂层内部最大散射反弹次数 (Max scattering bounces inside coating)
  NamedMaterial "earthMaterial" # 应用命名材质 (Apply named material)

  # 地球几何形状 (Earth Geometry)
  Shape "sphere" "float radius" 6378.0 # 地球平均半径 6378.0 km (Earth's average radius in km)
AttributeEnd # 地球属性块结束 (Earth attribute block ends)

# 月球 (Moon)
AttributeBegin # 月球属性块开始 (Moon attribute block starts)
  # 月球位置 (Moon Position) - 使用 Mock 数据 (Using Mock data)
  Translate -285149.79 -250407.05 -138357.25

  # 月球材质 (Moon Material) - 使用漫反射材质模拟月球表面 (Diffuse material for Moon's surface simulation)
  # 月球表面相对粗糙，颜色偏灰 (Moon surface is relatively rough, grayish color)
  MakeNamedMaterial "moonMaterial" # 定义命名材质 (Define named material)
    "string type" "diffuse"
    "rgb reflectance" [0.5 0.5 0.5] # 月球平均反照率近似值，灰色调 (Approximate Moon albedo, grayish tone)
  NamedMaterial "moonMaterial" # 应用命名材质 (Apply named material)

  # 月球几何形状 (Moon Geometry)
  Shape "sphere" "float radius" 1737.5 # 月球半径 1737.5 km (Moon radius in km)
AttributeEnd # 月球属性块结束 (Moon attribute block ends)

"""

ws_items = -10

from .rendering_settings import rendering_settings_checker

def prerequisite_checker():
    if rendering_settings_checker() is False:
        return False
    return True

def world_settings_checker():
    global ws_items
    if ws_items >= 0:
        return True
    return False

def set_bkg_light_source(filename=None, scale=1.0):
    if filename is None:
        filename = 'milkyway_2020_8k_equalarea.exr'
    if rendering_settings_checker() is False:
        return []
    global ws_items
    ws_items += 1
    return [f'LightSource "infinite" "string filename" "${filename}"',
            f'            "float scale" [${scale}]']

