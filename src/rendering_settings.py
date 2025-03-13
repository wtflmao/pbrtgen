"""

# 渲染设置 (Rendering Settings)
LookAt 22690.42 43300.78  45590.13 # 相机位置 (远离地球，可以俯瞰地球) (Camera position, far from Earth to view solar system)
       0 0 0        # 观察点 (地球中心)           (Look at point, Earth's center)
       0 1 0       # 向上向量 (Y 轴向上)           (Up vector, Y-axis up)
Camera "perspective" "float fov" 60  # 透视相机，较小视场角 (Perspective camera, smaller FOV)

Sampler "halton" "integer pixelsamples" 64 # Halton 采样器，降低噪点 (Halton sampler, reduce noise)
Integrator "volpath" "integer maxdepth" 5 # 体积路径追踪积分器 (Volumetric path tracing integrator)
Film "spectral" "string filename" "solarsystem.png" # RGB 胶片，输出文件名 (RGB film, output filename)
     "integer xresolution" [1920] "integer yresolution" [1080] # 高清分辨率 (HD Resolution)
     "float diagonal" [70] # 对角线长度，毫米 (Diagonal length in mm)

PixelFilter "gaussian" "float xradius" 1 "float yradius" 1 # 高斯滤波器 (Gaussian filter)

# 色彩空间 (Color Space)
ColorSpace "rec2020" # 使用 rec2020 色彩空间 (Use rec2020 color space)

"""

rs_items = -7


def set_lookat(cam_coord, to_coord=None, up_coord=None):
    if to_coord is None:
        to_coord = [0.0, 0.0, 0.0]
    if up_coord is None:
        up_coord = [0.0, 0.0, 1.0]
    global rs_items
    rs_items += 1
    return [f'LookAt ${cam_coord[0]}  ${cam_coord[1]}  ${cam_coord[2]}',
            f'       ${cam_coord[0]}  ${cam_coord[1]}  ${cam_coord[2]}',
            f'       ${cam_coord[0]}  ${cam_coord[1]}  ${cam_coord[2]}']

def set_camera(cam_type=None, fov=None):
    if cam_type is None:
        cam_type = 'perspective'
    if fov is None:
        fov = 60.0
    global rs_items
    rs_items += 1
    return [f'Camera "${cam_type}" "float fov" ${fov}']

def set_sampler(type=None, samples=None):
    if type is None:
        type = 'halton'
    if samples is None:
        samples = 64
    global rs_items
    rs_items += 1
    return [f'Sampler "${type}" "integer pixelsamples" ${samples}']

def set_integrator(type=None, maxdepth=None):
    if type is None:
        type = 'volpath'
    if maxdepth is None:
        maxdepth = 5
    global rs_items
    rs_items += 1
    return [f'Integrator "${type}" "integer maxdepth" ${maxdepth}']

def set_film(x=None, y=None, diagonal=None):
    if x is None:
        x = 800
    if y is None:
        y = 600
    if diagonal is None:
        diagonal = 70.0 # millimeter
    global rs_items
    rs_items += 1
    return [f'Film "spectral" "string filename" "1.exr"',
            f'     "integer xresulution" [${x}]',
            f'     "integer yresulution" [${y}]',
            f'     "float diagonal" [${diagonal}]',]

def set_pixel_filter():
    global rs_items
    rs_items += 1
    return [f'PixelFilter "gaussian" "float xradius" 1 "float yradius" 1']

def set_color_space(space=None):
    if space is None:
        space = 'rec2020'
    global rs_items
    rs_items += 1
    return [f'ColorSpace "${space}"']

def rendering_settings_checker():
    global rs_items
    if rs_items >= 0:
        return True
    return False