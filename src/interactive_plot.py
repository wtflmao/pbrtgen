#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交互式天体与卫星轨道可视化工具
使用Plotly创建3D可视化
"""

import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os
import threading
import traceback
import time
from skyfield.api import load, EarthSatellite
from astropy.coordinates import ICRS, GCRS, CartesianRepresentation
from astropy.time import Time
import astropy.units as u
import math  # 添加数学库
import csv

class SolarSystemVisualizer:
    def __init__(self, selected_satellites, time_utc, satellite_tle_data, ts, earth):
        """初始化可视化器
        
        Args:
            selected_satellites: 已选择的卫星列表，格式为 [(model_name, sat_name, model_uuid, sat_position)]
            time_utc (datetime): 可视化的UTC时间点
            satellite_tle_data (dict): TLE数据字典，格式为 {卫星名: [tle1_line, tle2_line]}
            ts: 时间尺度对象
            earth: 地球天体对象，用于计算轨道
        """
        self.selected_satellites = selected_satellites
        self.time_utc = time_utc
        self.satellite_tle_data = satellite_tle_data
        self.ts = ts
        self.earth = earth
        
        # 设置天体半径（单位：km）
        self.earth_radius = 6378.0
        
        # 默认轨道绘制设置 - 将在计算时动态调整
        self.default_orbit_points = 40  # 默认轨道点数量
        self.default_orbit_hours = 1.5  # 默认轨道绘制时长 (小时)
        
        print(f"正在准备可视化 {len(self.selected_satellites)} 个选定的卫星...")
    
    def _calculate_orbital_period(self, satellite):
        """计算卫星轨道周期
        
        Args:
            satellite: Skyfield卫星对象
            
        Returns:
            float: 轨道周期 (小时)
        """
        try:
            # Skyfield的model.no_kozai是弧度/分钟
            # 转换为圈/天: (弧度/分钟) * (分钟/天) / (2π弧度/圈)
            rad_per_min = satellite.model.no_kozai
            min_per_day = 24 * 60
            rad_per_circle = 2 * math.pi
            
            # 计算平均运动（圈/天）
            mean_motion = rad_per_min * min_per_day / rad_per_circle
            
            # 计算周期 (小时) = 24小时/（圈/天）
            period_hours = 24.0 / mean_motion
            
            return period_hours
        except Exception as e:
            print(f"计算轨道周期时出错: {str(e)}")
            return 1.5  # 默认值
    
    def _get_orbit_settings(self, satellite, sat_name):
        """根据卫星轨道特性确定轨道绘制参数
        
        Args:
            satellite: Skyfield卫星对象
            sat_name: 卫星名称
            
        Returns:
            tuple: (轨道点数量, 轨道时长(小时), 轨道名称后缀)
        """
        try:
            # 计算轨道周期(小时)
            period_hours = self._calculate_orbital_period(satellite)
            
            # 根据轨道周期动态调整轨道显示参数
            if period_hours <= 3:  # 近地轨道 (LEO)
                orbit_hours = min(period_hours * 0.9, 3)  # 最多轨道周期的90%，但不超过3小时
                orbit_points = 30
                orbit_type = "LEO"
            elif period_hours <= 12:  # 中轨道 (MEO)
                orbit_hours = min(period_hours * 0.9, 12)  # 轨道周期的90%，但不超过12小时
                orbit_points = 60
                orbit_type = "MEO"
            else:  # 高轨道或地球同步轨道 (GEO/HEO)
                orbit_hours = min(period_hours * 0.9, 24)  # 轨道周期的90%，但不超过24小时
                orbit_points = 80
                orbit_type = "GEO/HEO"
            
            # 确保时间和点数合理
            orbit_hours = max(1.0, orbit_hours)  # 至少1小时
            orbit_points = max(20, orbit_points)  # 至少20个点
            
            period_str = f"{period_hours:.1f}h"
            orbit_str = f"{orbit_hours:.1f}h"
            
            print(f"卫星 {sat_name}: 轨道周期={period_str}, 轨道类型={orbit_type}, 显示时长={orbit_str}, 点数={orbit_points}")
            
            return orbit_points, orbit_hours, f"轨道周期: {period_str}"
        except Exception as e:
            print(f"确定轨道参数时出错: {str(e)}")
            return self.default_orbit_points, self.default_orbit_hours, ""
    
    def _calculate_past_orbit(self, tle_lines, satellite_name, earth):
        """计算卫星过去轨迹点
        
        Args:
            tle_lines: 卫星的TLE数据
            satellite_name: 卫星名称
            earth: 地球天体对象
            
        Returns:
            tuple: 轨道点列表和轨道信息 (positions, orbit_info)
        """
        try:
            # 创建卫星对象
            satellite = EarthSatellite(tle_lines[0], tle_lines[1], satellite_name, self.ts)
            
            # 根据轨道特性确定轨道绘制参数
            orbit_points, orbit_hours, orbit_info = self._get_orbit_settings(satellite, satellite_name)
            
            # 计算过去轨道点的时间间隔
            time_step = orbit_hours * 3600 / orbit_points  # 秒
            
            # 准备CSV输出
            # 确保debug目录存在
            #debug_dir = os.path.join(os.getcwd(), 'debug_orbits')
            #os.makedirs(debug_dir, exist_ok=True)
            
            # 创建CSV文件
            #csv_filename = os.path.join(debug_dir, f'{satellite_name}_orbit_debug.csv')
            
            # 计算过去的轨道点
            positions = []
            debug_rows = []
            
            # 首先计算确切的当前时刻位置（最后一个点）
            current_t = self.ts.utc(self.time_utc.year, self.time_utc.month, self.time_utc.day,
                                   self.time_utc.hour, self.time_utc.minute, self.time_utc.second)
            current_position = (earth + satellite).at(current_t)
            pos_au = current_position.position.au
            
            # 转换为ICRS坐标 - 使用CartesianRepresentation
            cart = CartesianRepresentation(pos_au[0] * u.au, pos_au[1] * u.au, pos_au[2] * u.au)
            
            # 转换为公里单位
            au_to_km = 149597870.7
            cart_km = CartesianRepresentation(
                cart.x * au_to_km * u.km / u.au,
                cart.y * au_to_km * u.km / u.au,
                cart.z * au_to_km * u.km / u.au
            )
            sat_icrs_km = ICRS(cart_km)
            
            # 转换为GCRS坐标
            utc_iso = current_t.utc_iso()
            time_obj = Time(utc_iso, format='isot', scale='utc')
            sat_gcrs_km = sat_icrs_km.transform_to(GCRS(obstime=time_obj))
            
            # 确切的当前位置
            current_x = float(sat_gcrs_km.cartesian.x.value)
            current_y = float(sat_gcrs_km.cartesian.y.value)
            current_z = float(sat_gcrs_km.cartesian.z.value)
            
            # 计算历史轨道点
            for i in range(orbit_points):  # 不包括当前位置，单独计算
                # 计算时间点 (从过去到当前时间)
                time_offset = -(orbit_points - i) * time_step  # 负值表示过去的时间
                past_time = self.time_utc + timedelta(seconds=time_offset)
                
                # 转换为skyfield时间
                t = self.ts.utc(past_time.year, past_time.month, past_time.day,
                               past_time.hour, past_time.minute, past_time.second)
                
                # 计算卫星位置 - 使用与main.py相同的方法
                satellite_position = (earth + satellite).at(t)
                
                # 正确获取position的值，要指定单位
                pos_au = satellite_position.position.au
                
                # 转换为ICRS坐标 - 使用CartesianRepresentation
                cart = CartesianRepresentation(pos_au[0] * u.au, pos_au[1] * u.au, pos_au[2] * u.au)
                
                # 转换为公里单位
                au_to_km = 149597870.7
                cart_km = CartesianRepresentation(
                    cart.x * au_to_km * u.km / u.au,
                    cart.y * au_to_km * u.km / u.au,
                    cart.z * au_to_km * u.km / u.au
                )
                sat_icrs_km = ICRS(cart_km)
                
                # 转换为GCRS坐标
                utc_iso = t.utc_iso()
                time_obj = Time(utc_iso, format='isot', scale='utc')
                sat_gcrs_km = sat_icrs_km.transform_to(GCRS(obstime=time_obj))
                
                # 坐标值
                x = float(sat_gcrs_km.cartesian.x.value)
                y = float(sat_gcrs_km.cartesian.y.value)
                z = float(sat_gcrs_km.cartesian.z.value)
                
                # 添加到位置列表
                positions.append((x, y, z))
                
                ## 准备调试行
                #debug_rows.append({
                #    'timestamp': past_time.strftime('%Y-%m-%d %H:%M:%S'),
                #    'x_km': x,
                #    'y_km': y,
                #    'z_km': z
                #})
            
            # 添加当前时刻的确切位置（最后一个点）
            positions.append((current_x, current_y, current_z))
            #debug_rows.append({
            #    'timestamp': self.time_utc.strftime('%Y-%m-%d %H:%M:%S'),
            #    'x_km': current_x,
            #    'y_km': current_y,
            #    'z_km': current_z
            #})
            
            # 打印最后一行数据
            print(f"[DEBUG] 卫星 {satellite_name} 当前位置: [{current_x:.1f}, {current_y:.1f}, {current_z:.1f}]")
                
            ## 写入CSV文件
            #with open(csv_filename, 'w', newline='') as csvfile:
            #    # 使用DictWriter以便于阅读
            #    fieldnames = ['timestamp', 'x_km', 'y_km', 'z_km']
            #    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
            #    # 写入表头
            #    writer.writeheader()
                
            #    # 写入所有行
            #    writer.writerows(debug_rows)
            
            print(f"[DEBUG] 已将卫星 {satellite_name} 的轨道点写入 {csv_filename}")
            
            return positions, orbit_info
        except Exception as e:
            print(f"计算卫星 {satellite_name} 过去轨道时出错: {traceback.format_exc()}")
            return [], ""
            
    def create_3d_visualization(self):
        """创建3D可视化图表
        
        Returns:
            plotly.graph_objects.Figure: Plotly图表对象
        """
        try:
            print("开始创建3D可视化...")
            # 创建绘图对象
            fig = make_subplots(
                rows=1, cols=1,
                specs=[[{'type': 'scene'}]]
            )
            
            print("计算地球位置...")
            # 计算地球在选定UTC时间的位置
            t = self.ts.utc(self.time_utc.year, self.time_utc.month, self.time_utc.day,
                            self.time_utc.hour, self.time_utc.minute, self.time_utc.second)
            
            # 使用与main.py相同的坐标转换方法
            earth_position = self.earth.at(t)
            # 正确获取position的值，要指定单位
            pos_au = earth_position.position.au
            
            # 确保导入astropy.units
            from astropy.coordinates import CartesianRepresentation
            import astropy.units as u
            
            # 转换为ICRS坐标 - 使用CartesianRepresentation
            cart = CartesianRepresentation(pos_au[0] * u.au, pos_au[1] * u.au, pos_au[2] * u.au)
            
            # 转换为公里单位
            au_to_km = 149597870.7
            cart_km = CartesianRepresentation(
                cart.x * au_to_km * u.km / u.au,
                cart.y * au_to_km * u.km / u.au,
                cart.z * au_to_km * u.km / u.au
            )
            earth_icrs_km = ICRS(cart_km)
            
            # 转换为GCRS坐标
            utc_iso = t.utc_iso()
            time_obj = Time(utc_iso, format='isot', scale='utc')
            earth_gcrs_km = earth_icrs_km.transform_to(GCRS(obstime=time_obj))
            
            # 获取地球在GCRS坐标系中的位置（单位：km）
            earth_x = float(earth_gcrs_km.cartesian.x.value)
            earth_y = float(earth_gcrs_km.cartesian.y.value)
            earth_z = float(earth_gcrs_km.cartesian.z.value)
            
            print(f"地球位置: X={earth_x:.6f} km, Y={earth_y:.6f} km, Z={earth_z:.6f} km")

            # 绘制地球 - 使用计算得到的实际坐标
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            x = earth_x + self.earth_radius * np.cos(u) * np.sin(v)
            y = earth_y + self.earth_radius * np.sin(u) * np.sin(v)
            z = earth_z + self.earth_radius * np.cos(v)
            
            fig.add_trace(
                go.Surface(
                    x=x, y=y, z=z,
                    colorscale=[[0, 'rgb(0, 0, 255)'], [1, 'rgb(0, 100, 255)']],
                    opacity=0.8,
                    showscale=False,
                    name='Earth'
                )
            )
                    
            print(f"绘制 {len(self.selected_satellites)} 个选定的卫星...")
            # 绘制每个选定的卫星
            for i, (model_name, sat_name, model_uuid, sat_position) in enumerate(self.selected_satellites):
                try:
                    print(f"处理卫星 {i+1}/{len(self.selected_satellites)}: {sat_name}")
                    
                    # 获取卫星当前坐标 - 先保存初始坐标
                    initial_sat_x, initial_sat_y, initial_sat_z = sat_position
                    sat_x, sat_y, sat_z = initial_sat_x, initial_sat_y, initial_sat_z
                    
                    # 先计算过去的轨道点
                    if sat_name in self.satellite_tle_data:
                        past_positions, orbit_info = self._calculate_past_orbit(
                            self.satellite_tle_data[sat_name], 
                            sat_name,
                            self.earth  # 传递地球对象
                        )
                        
                        if past_positions:
                            # 提取坐标分量
                            xs, ys, zs = zip(*past_positions)
                            
                            # 使用轨道计算的最后一个点(当前位置)更新卫星位置坐标
                            # 这保证卫星总是在轨道的末端
                            sat_x, sat_y, sat_z = past_positions[-1]
                            
                            # 轨道显示名称
                            orbit_display_name = f'{sat_name} - {orbit_info}'
                            
                            # 绘制轨道线
                            fig.add_trace(
                                go.Scatter3d(
                                    x=xs, y=ys, z=zs,
                                    mode='lines',
                                    line=dict(
                                        color=self._get_satellite_color(sat_name),
                                        width=2, 
                                        dash='dash'
                                    ),
                                    name=orbit_display_name,
                                    showlegend=True
                                )
                            )
                            
                            # 输出初始坐标和计算的当前坐标的差异
                            print(f"卫星 {sat_name} 坐标比较:")
                            print(f"  初始坐标: [{initial_sat_x:.1f}, {initial_sat_y:.1f}, {initial_sat_z:.1f}]")
                            print(f"  计算坐标: [{sat_x:.1f}, {sat_y:.1f}, {sat_z:.1f}]")
                    
                    # 之后再绘制卫星标记，使用更新后的坐标
                    fig.add_trace(
                        go.Scatter3d(
                            x=[sat_x], y=[sat_y], z=[sat_z],
                            mode='markers+text',
                            text=[sat_name],
                            textposition='top center',
                            marker=dict(
                                size=5,
                                color=self._get_satellite_color(sat_name),
                                symbol='diamond',
                                line=dict(color='rgba(0, 0, 0, 0.5)', width=1)
                            ),
                            name=f"{sat_name} ({model_name})"
                        )
                    )
                    
                    print(f"已绘制卫星 {sat_name} 位置和过去轨道")
                    
                except Exception as e:
                    print(f"绘制卫星 {sat_name} 失败: {e}")
            
            print("设置图表布局...")
            # 设置图表布局
            fig.update_layout(
                title=f'卫星轨道可视化 - UTC {self.time_utc.strftime("%Y-%m-%d %H:%M:%S")}',
                scene=dict(
                    xaxis_title='X (km)',
                    yaxis_title='Y (km)',
                    zaxis_title='Z (km)',
                    aspectmode='data',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                legend=dict(
                    x=0.01,
                    y=0.99,
                    traceorder='normal',
                    font=dict(family='sans-serif', size=12, color='black'),
                    bgcolor='rgba(255, 255, 255, 0.5)',
                    bordercolor='rgba(0, 0, 0, 0.5)',
                    borderwidth=1
                ),
                margin=dict(l=0, r=0, b=0, t=40),
                template='plotly_white'
            )
            
            print("3D可视化创建完成")
            return fig
        except Exception as e:
            print(f"创建3D可视化失败: {traceback.format_exc()}")
            # 创建一个最小的图形对象并返回
            fig = go.Figure()
            fig.add_annotation(
                text=f"创建可视化失败: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def save_visualization(self, filename='satellite_visualization.html'):
        """保存可视化为HTML文件并打开
        
        Args:
            filename (str): 输出的HTML文件名
            
        Returns:
            bool: 是否成功保存并打开可视化
        """
        try:
            fig = self.create_3d_visualization()
            fig.write_html(filename, auto_open=False)
            print(f"可视化已保存到 {filename}")
            
            # 获取绝对路径
            abs_path = os.path.abspath(filename)
            # 使用webbrowser模块打开HTML文件
            webbrowser.open('file://' + abs_path, new=2)
            print(f"已在浏览器中打开可视化文件: {abs_path}")
            return True
        except Exception as e:
            print(f"保存可视化文件失败: {traceback.format_exc()}")
            return False

    def _get_satellite_color(self, satellite_name):
        """为卫星选择唯一的颜色
        
        Args:
            satellite_name: 卫星名称
        
        Returns:
            str: 颜色字符串
        """
        # 定义一组不同的颜色，避免蓝色
        color_palette = [
            'rgb(255, 0, 0)',     # 红色
            'rgb(0, 255, 0)',     # 绿色
            'rgb(255, 165, 0)',   # 橙色
            'rgb(128, 0, 128)',   # 紫色
            'rgb(255, 192, 203)', # 粉色
            'rgb(255, 255, 0)',   # 黄色
            'rgb(0, 255, 255)',   # 青色
            'rgb(255, 0, 255)',   # 品红
            'rgb(165, 42, 42)',   # 棕色
            'rgb(0, 128, 0)'      # 深绿
        ]
        
        # 使用哈希值确保同一个卫星总是获得相同的颜色
        color_index = hash(satellite_name) % len(color_palette)
        return color_palette[color_index]


def visualize_in_new_thread(selection_result, time_utc, satellite_positions, tle_data, ts, earth, wait_time=10):
    """在新线程中运行可视化，并允许主线程继续执行但在最后等待可视化完成
    
    Args:
        selection_result: 用户选择的结果，包含模型-卫星配对
        time_utc: 选择的时间
        satellite_positions: 卫星位置字典 {sat_name: [x, y, z]}
        tle_data: 卫星TLE数据字典
        ts: 时间尺度对象
        earth: 地球天体对象，用于计算轨道
        wait_time (int): 主线程等待可视化的最大时间（秒）
    
    Returns:
        threading.Event: 可视化完成事件，可用于主线程等待
    """
    # 创建一个事件对象，用于通知主线程可视化已完成
    visualization_done = threading.Event()
    
    def run_visualization():
        try:
            print("开始生成卫星轨道可视化...")
            
            # 准备选定的卫星数据，包含模型名、卫星名、模型UUID和卫星位置
            selected_satellites = []
            for model_name, sat_name, model_uuid in selection_result['pairs']:
                if sat_name in satellite_positions:
                    selected_satellites.append((model_name, sat_name, model_uuid, satellite_positions[sat_name]))
                    print(f"添加卫星: {sat_name} 位置: {satellite_positions[sat_name]}")
                else:
                    print(f"警告: 卫星 {sat_name} 位置信息不存在")
            
            # 如果没有选定的卫星，显示警告
            if not selected_satellites:
                print("警告: 没有找到选定卫星的位置信息")
                visualization_done.set()
                return
                
            # 创建可视化器对象，传入选定的卫星、时间和TLE数据
            visualizer = SolarSystemVisualizer(
                selected_satellites,
                time_utc,
                tle_data,
                ts,
                earth  # 传递地球对象
            )
            
            # 生成并保存可视化
            success = visualizer.save_visualization()
            if success:
                print("卫星轨道可视化已完成并在浏览器中打开")
            else:
                print("卫星轨道可视化创建失败")
        except Exception as e:
            print(f"可视化过程中发生错误: {traceback.format_exc()}")
        finally:
            # 不论成功与否，都设置事件，通知主线程已完成
            visualization_done.set()
    
    # 创建并启动新线程
    thread = threading.Thread(target=run_visualization)
    thread.daemon = True  # 设置为守护线程，这样主程序退出时不会阻塞
    thread.start()
    
    print("可视化已在新线程中启动")
    return visualization_done  # 返回事件对象，主线程可以等待它

# 添加用于坐标转换的函数
def skyfield_to_icrs(position):
    """将skyfield位置转换为ICRS坐标"""
    # 使用正确的方式创建ICRS坐标
    cart = CartesianRepresentation(position[0] * u.au, position[1] * u.au, position[2] * u.au)
    return ICRS(cart)

def convert_au_to_km(icrs):
    """将AU单位的ICRS坐标转换为km单位"""
    au_to_km = 149597870.7  # 1 AU = 149597870.7 km
    # 使用正确的方式创建ICRS坐标
    cart = icrs.cartesian
    cart_km = CartesianRepresentation(
        cart.x * au_to_km * u.km / u.au,
        cart.y * au_to_km * u.km / u.au,
        cart.z * au_to_km * u.km / u.au
    )
    return ICRS(cart_km)

def icrs_to_gcrs(icrs_km, time_str):
    """将ICRS坐标转换为GCRS坐标"""
    time = Time(time_str, format='isot', scale='utc')
    return icrs_km.transform_to(GCRS(obstime=time)) 