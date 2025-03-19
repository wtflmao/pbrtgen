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
    """设置 LookAt 参数。

    Args:
        cam_coord (list): 相机坐标 [x, y, z]。
        to_coord (list, optional): 观察点坐标 [x, y, z]。默认为 [0.0, 0.0, 0.0]。
        up_coord (list, optional): 向上向量坐标 [x, y, z]。默认为 [0.0, 0.0, 1.0]。

    Returns:
        list: 包含 LookAt 参数行的列表。
    """
    if to_coord is None:
        to_coord = [0.0, 0.0, 0.0]
    if up_coord is None:
        up_coord = [0.0, 0.0, 1.0]
    global rs_items
    rs_items += 1
    return [f'LookAt {cam_coord[0]}  {cam_coord[1]}  {cam_coord[2]}',
            f'       {to_coord[0]}  {to_coord[1]}  {to_coord[2]}',
            f'       {up_coord[0]}  {up_coord[1]}  {up_coord[2]}']

def set_camera(cam_type=None, fov=None):
    """设置相机参数。

    Args:
        cam_type (str, optional): 相机类型。默认为 'perspective'。
        fov (float, optional): 视场角 (FOV)。默认为 60.0。

    Returns:
        list: 包含相机参数行的列表。
    """
    if cam_type is None:
        cam_type = 'perspective'
    if fov is None:
        fov = 60.0
    global rs_items
    rs_items += 1
    return [f'Camera "{cam_type}" "float fov" {fov}']

def set_sampler(type=None, samples=None):
    """设置采样器参数。

    Args:
        type (str, optional): 采样器类型。默认为 'halton'。
        samples (int, optional): 像素采样数。默认为 64。

    Returns:
        list: 包含采样器参数行的列表。
    """
    if type is None:
        type = 'halton'
    if samples is None:
        samples = 64
    global rs_items
    rs_items += 1
    return [f'Sampler "{type}" "integer pixelsamples" {samples}']

def set_integrator(type=None, maxdepth=None):
    """设置积分器参数。

    Args:
        type (str, optional): 积分器类型。默认为 'volpath'。
        maxdepth (int, optional): 最大深度。默认为 5。

    Returns:
        list: 包含积分器参数行的列表。
    """
    if type is None:
        type = 'volpath'
    if maxdepth is None:
        maxdepth = 5
    global rs_items
    rs_items += 1
    return [f'Integrator "{type}" "integer maxdepth" {maxdepth}']

def set_film(x=None, y=None, diagonal=None):
    """设置胶片参数。

    Args:
        x (int, optional): X 分辨率。默认为 800。
        y (int, optional): Y 分辨率。默认为 600。
        diagonal (float, optional): 对角线长度 (毫米)。默认为 70.0。

    Returns:
        list: 包含胶片参数行的列表。
    """
    if x is None:
        x = 800
    if y is None:
        y = 600
    if diagonal is None:
        diagonal = 70.0 # millimeter
    global rs_items
    rs_items += 1
    return [f'Film "spectral" "string filename" "1.exr"',
            f'     "integer xresolution" [{x}]',
            f'     "integer yresolution" [{y}]',
            f'     "float diagonal" [{diagonal}]',]

def set_pixel_filter():
    """设置像素过滤器参数。

    Returns:
        list: 包含像素过滤器参数行的列表。
    """
    global rs_items
    rs_items += 1
    return [f'PixelFilter "gaussian" "float xradius" 1 "float yradius" 1']

def set_color_space(space=None):
    """设置色彩空间参数。

    Args:
        space (str, optional): 色彩空间。默认为 'rec2020'。

    Returns:
        list: 包含色彩空间参数行的列表。
    """
    if space is None:
        space = 'rec2020'
    global rs_items
    rs_items += 1
    return []#[f'ColorSpace "{space}"']

def rendering_settings_checker():
    """检查渲染设置是否已全部设置。

    Returns:
        bool: 如果渲染设置已全部设置，则返回 True，否则返回 False。
    """
    global rs_items
    if rs_items >= 0:
        return True
    return False

def r_settings_overwriter(path, list_of_lists):
    """覆盖渲染设置文件。

    Args:
        path (str): 文件路径。
        list_of_lists (list): 包含渲染设置行的列表的列表。

    Returns:
        list: 如果渲染设置未更改或 list_of_lists 为空，则返回空列表。
    """
    if rendering_settings_checker() is False:
        return []
    if len(list_of_lists) >= 1:
        pass
    else:
        return []
    from .file_write import overwrite_file, write_line_to_file_loop_with_newline
    overwrite_file(path, "")
    for mylist in list_of_lists:
        for line in mylist:
            write_line_to_file_loop_with_newline(path, line)
        write_line_to_file_loop_with_newline(path, '')
    print('r_settings write done')