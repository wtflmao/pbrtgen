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

# 定义共享材质 (Define Shared Materials)
# 五参数模型BRDF，仅为"substrate" and "coatedconductor"材质受支持. "substrate"材质用于模拟电介质, "coatedconductor"用来模拟金属表面.

# 涂料 (Coated Paint)
MakeNamedMaterial "sat_coatedpaint"
  "string type" "coatedconductor"  # 或者 "substrate"  (选择一个合适的基底材质，两者都支持五参数)
  "spectrum Kd" [0.7 0.7 0.7]   # 涂料的漫反射颜色 (根据实际情况调整)
  "spectrum Ks" [0.1 0.1 0.1]   # 涂料的镜面反射颜色 (通常较低)
  "float uroughness" 0.05 # 涂料的 u 方向粗糙度 (根据光滑程度调整)
  "float vroughness" 0.05 # 涂料的 v 方向粗糙度
  "bool remaproughness" "false"

# 金属骨架 (Metallic Skeleton)
MakeNamedMaterial "metalic_skeleton"
  "string type" "coatedconductor"   # 或者 "metal" (如果 PBRT-v4 支持)
  "spectrum eta" [0.2 0.4 1.3] #mock 金属折射率 (根据具体金属调整, 这是 mock 值) 调整的时候注意eta和k的长度要一致。
  "spectrum k" [1.5 2.0 3.5]     #mock 金属吸收系数 (根据具体金属调整, 这是 mock 值)
  "float uroughness" 0.01      # 金属的 u 方向粗糙度 (根据抛光程度调整)
  "float vroughness" 0.01      # 金属的 v 方向粗糙度
  "bool remaproughness" "false"

# 硅太阳能板 (Silicon Solar Panel)
MakeNamedMaterial "solarpanel"
  "string type" "coatedconductor" # 也可以是 "substrate", 用来模拟电介质
  "spectrum Kd" [0.1 0.1 0.3]   # 深蓝色 (Dark blueish color)
  "spectrum Ks" [0.2 0.2 0.2]   # 适度的镜面反射
  "float uroughness" 0.02      # 较为光滑
  "float vroughness" 0.02
  "bool remaproughness" "false"

# Measured 材质和预先计算好的 BRDF 数据
MakeNamedMaterial "Measured_test"
  "string type" "measured"
  "string filename" "mock_brdf_data.bsdf"   # 使用占位符文件名， 替换为实际的 .bsdf 文件路径和名称, e.g., "aluminum-oxide.bsdf"
                                            # PBRT-v4支持的Measured BRDF 数据为.bsdf二进制文件，使用Dupuy and Jakob's approach
                                            # https://rgl.epfl.ch/materials 网站所下载的为.binary，并不是同一个文件格式，无法直接调用。

# ... (可以添加更多共享材质，例如隔热材料等) ...
# 人造卫星 1 (Satellite 1)
AttributeBegin
  Translate 30000 10000 20000  # 卫星位置 (Mock position)
  Rotate 45 0 1 0 # 示例旋转 (Example rotation)
  
  # 注意: PBRT 本身不直接支持在 OBJ 文件内部指定不同部分的材质!  
Shape "obj" "string filename" "satellite1.obj"

#因为PBRT-v4不能在obj模型内部指定材质(和v3不同)，所以处理复杂obj模型，且内部不同组件需要不同材质时，需要模型本身在建模软件里拆分成多个obj.
#因此，我们需要在Blender这类建模软件里把obj先拆开，然后分别导出。
#假设我们已经把satellite1.obj拆成了satellite1_paint.obj (涂层部分), satellite1_skeleton.obj (骨架部分), satellite1_solar.obj (太阳能板部分)
AttributeBegin
    Shape "obj" "string filename" "satellite1_paint.obj"
    NamedMaterial "sat_coatedpaint" #使用共享的涂层材质
AttributeEnd

AttributeBegin
     Shape "obj" "string filename" "satellite1_skeleton.obj"
     NamedMaterial "metalic_skeleton" #使用金属骨骼材质
AttributeEnd

AttributeBegin
     Shape "obj" "string filename" "satellite1_solar.obj"
     NamedMaterial "solarpanel" #使用硅太阳能板材质
AttributeEnd
AttributeEnd

# 人造卫星 2 (Satellite 2) - 类似处理
AttributeBegin
  Translate -20000 -15000 25000 # 卫星位置 (Mock position)
  Rotate -30 1 0 1  # 示例旋转

  # 同样，假设 satellite2.obj 也被拆分成了多个 OBJ 文件
  Shape "obj" "string filename" "satellite2.obj" #即使拆开了，也需要一个主要的obj文件先导入。
  
  AttributeBegin
    Shape "obj" "string filename" "satellite2_paint.obj"
     NamedMaterial "sat_coatedpaint"
  AttributeEnd
 
  AttributeBegin
    Shape "obj" "string filename" "satellite2_skeleton.obj"
    NamedMaterial "metalic_skeleton"
  AttributeEnd

  AttributeBegin
     Shape "obj" "string filename" "satellite2_solar.obj"
     NamedMaterial "solarpanel"
  AttributeEnd
AttributeEnd

"""

ws_items = -4

from .rendering_settings import rendering_settings_checker

def prerequisite_checker():
    """检查先决条件。

    Returns:
        bool: 如果渲染设置检查通过，则返回 True，否则返回 False。
    """
    if rendering_settings_checker() is False:
        return False
    return True

def world_settings_checker():
    """检查世界设置是否已更改。

    Returns:
        bool: 如果世界设置已更改，则返回 True，否则返回 False。
    """
    global ws_items
    if ws_items >= 0:
        return True
    return False

def set_bkg_light_source(filename=None, scale=1.0):
    """设置背景光源。

    Args:
        filename (str, optional): 背景光源文件名。默认为 'milkyway_2020_8k_equalarea.exr'。
        scale (float, optional): 光源缩放比例。默认为 1.0。

    Returns:
        list: 包含背景光源设置行的列表。
    """
    if filename is None:
        filename = 'milkyway_2020_8k_equalarea.exr'
    if prerequisite_checker() is False:
        return []
    global ws_items
    ws_items += 1
    return [f'LightSource "infinite" "string filename" "${filename}"',
            f'            "float scale" [${scale}]']

def set_attrubute_the_sun(pos, power, radius=None):
    """设置太阳的属性。

    Args:
        pos (object): 太阳的位置，包含 x, y, z 属性。
        power (float): 太阳的功率。
        radius (float, optional): 太阳的半径。默认为 695500.0 (km)。

    Returns:
        list: 包含太阳属性设置行的列表。
    """
    if prerequisite_checker() is False:
        return []
    if radius is None:
        radius = 695500.0 # km
    global ws_items
    ws_items += 1
    return [f'# The sun',
            f'AttributeBegin',
            f'  Translate ${pos.x} ${pos.y} ${pos.z}',
            f'  AreaLightSource "diffuse" "spectrum L" "stdillum-D65"', #  使用内置光谱 "stdillum-D65" 近似太阳光谱
                                                                        #  注意: 真实的太阳光谱需要使用 spectrum.txt 文件，这里为了方便使用内置近似
            f'                  "float power" [${power}]',              #  太阳光度，瓦特 (Solar luminosity in Watts)
            f'                  "bool twosided false',                  #  单面发光 (One-sided emission)
            f'  Shape "sphere" "float radius" ${radius}',
            f'AttributeEnd']

def set_attrubute_the_earth(pos, rot_angle=None, rot_axis=None, radius=None):
    """设置地球的属性。

    Args:
        pos (object): 地球的位置，包含 x, y, z 属性。
        rot_angle (float, optional): 地球自转轴倾斜角度。默认为 23.5 度。
        rot_axis (list, optional): 地球自转轴。默认为 [1, 0, 0] (X 轴)。
        radius (float, optional): 地球的半径。默认为 6378.0 (km)。

    Returns:
        list: 包含地球属性设置行的列表。
    """
    if prerequisite_checker() is False:
        return []
    if radius is None:
        radius = 6378.0 # km
    if rot_angle is None and rot_axis is None:
        rot_angle = 23.5
        rot_axis = [1, 0, 0] # X-axis
    if rot_angle is None and rot_axis is not None:
        return []
    if rot_angle is not None and rot_axis is None:
        return []
    global ws_items
    ws_items += 1
    return [f'# The earth',
            f'AttributeBegin',
            f'  Translate ${pos.x} ${pos.y} ${pos.z}',
            f'  Rotate ${rot_angle} ${rot_axis[0]} ${rot_axis[1]} ${rot_axis[2]}',
            f'  MakeNamedMaterial "earthMaterial"',
            f'    "string type" "coateddiffuse',    #  使用涂层漫反射材质模拟地球表面 (Coated Diffuse material for Earth's surface simulation)
            f'    "rgb reflectance" [0.1 0.2 0.3]', #  地球平均反照率近似值，蓝色调为主 (Approximate Earth albedo, bluish tone)
            f'    "float roughness" 0.15',          #  适中粗糙度 (Moderate roughness)
            f'    "float thickness" 0.001',         #  涂层厚度 (Coating thickness)
            f'    "rgb albedo" [0.1 0.2 0.3]',      #  涂层下的漫反射层反照率 (Albedo of diffuse base layer under coating)
            f'    "float g" 0.0',                   #  涂层内部散射各项异性参数 (Coating internal scattering asymmetry)
            f'    "integer maxdepth" 5',            #  涂层内部最大散射反弹次数 (Max scattering bounces inside coating)
            f'  NamedMaterial "earthMaterial"',     #  应用命名材质 (Apply named material)
            f'  Shape "sphere" "float radius" ${radius}',
            f'AttributeEnd']

def set_attrubute_the_moon(pos, radius=None):
    """设置月球的属性。

    Args:
        pos (object): 月球的位置，包含 x, y, z 属性。
        radius (float, optional): 月球的半径。默认为 1737.5 (km)。

    Returns:
        list: 包含月球属性设置行的列表。
    """
    if prerequisite_checker() is False:
        return []
    if radius is None:
        radius = 1737.5 # km
    global ws_items
    ws_items += 1
    return [f'# The earth',
            f'AttributeBegin',
            f'  Translate ${pos.x} ${pos.y} ${pos.z}',
            f'  MakeNamedMaterial "moonMaterial"',
            f'    "string type" "diffuse',
            f'    "rgb reflectance" [0.5 0.5 0.5]', #  月球平均反照率近似值，灰色调 (Approximate Moon albedo, grayish tone)
            f'  NamedMaterial "moonMaterial"',      #  应用命名材质 (Apply named material)
            f'  Shape "sphere" "float radius" ${radius}',
            f'AttributeEnd']

def w_settings_appender(path, list_of_lists):
    """将世界设置附加到文件。

    Args:
        path (str): 文件路径。
        list_of_lists (list): 包含世界设置行的列表的列表。

    Returns:
        list: 如果世界设置未更改或 list_of_lists 为空，则返回空列表。
    """
    if world_settings_checker() is False:
        return []
    if len(list_of_lists) >= 1:
        pass
    else:
        return []
    from .file_write import write_lines_to_file_loop
    for item in list_of_lists:
        for line in item:
            write_lines_to_file_loop(path, line)
        write_lines_to_file_loop(path, '\n')
    print('w_settings write done')



