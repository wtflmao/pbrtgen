# SPDX-License-Identifier: MIT
from skyfield.api import load, Topos, EarthSatellite, wgs84
from astropy.coordinates import ICRS, EarthLocation, GCRS
from astropy.time import Time
import astropy.units as u
import yaml
import requests
import tkinter as tk
from tkinter import ttk
import datetime
from datetime import datetime as dt
import json
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from settings import settings

from .celestial_objects import load_ephemeris, get_celestial_object
from .coordinates import skyfield_to_icrs, icrs_to_gcrs, convert_au_to_km
from .time_utils import get_timescale, get_utc_time
from .tle_data import get_tle_data, load_tle_data, get_satellite
from .file_write import *
from .rendering_settings import *
from .world_settings import *
from src.interactive_plot import visualize_in_new_thread
from src.camera_viewpoint import select_camera_viewpoint
from src.rendering_settings_view import get_rendering_settings
import webbrowser
import threading
import subprocess
import gc
import time

# 1. 加载 JPL DE 星历数据
eph = load_ephemeris() # from Year 1849 to Year 2150
earth = get_celestial_object(eph, 'earth')
sun = get_celestial_object(eph, 'sun')
moon = get_celestial_object(eph, 'moon')

# 2. 定义时间 (2025年3月10日 UTC+8 08:00)
ts = get_timescale() # 获取 skyfield 的 timescale
"""
time_utc = get_utc_time(ts, 2025, 3, 10, 8, 0, 0) # 使用 skyfield 的 timescale 创建 Time 对象

# 3. 定义 Starlink 卫星的 TLE 数据 
TLE = {
    'STARLINK-1008': [
        '1 44714C 19074B   25068.82340278  .00023551  00000+0  15777-2 0   687', 
        '2 44714  53.0541  24.5636 0001323  91.3133  52.2749 15.06379808    12'
    ],
    'STARLINK-32899': [
        '1 62994C 25031P   25068.72965278 -.00277140  00000+0 -65975-2 0   681',
        '2 62994  43.0001  46.1320 0001076 273.3956 308.7151 15.41042779    11'
    ]
}

satellite_1008 = EarthSatellite(TLE['STARLINK-1008'][0], TLE['STARLINK-1008'][1], 'Starlink-1008', load.timescale())
satellite_32899 = EarthSatellite(TLE['STARLINK-32899'][0], TLE['STARLINK-32899'][1], 'Starlink-32899', load.timescale())

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
"""
# 10. 构建 .pbrt 文件的渲染设置与公共场景设置

r_settings = [['# PBRTgen 0.0.1', '# by github.com/wtflmao', '\n'],
              set_lookat([30000, 30000, 30000], [0, 0, 0], None),
              set_camera(None, 60.0),
              set_sampler(None, None),
              set_integrator(None, None),
              set_film(1366, 768, None),
              set_pixel_filter(),
              set_color_space(None),
              ['WorldBegin']]
r_settings_overwriter('rendering_settings.pbrt', r_settings)

# 以下世界设置会在用户选择时间后更新，并在处理模型变换时应用
w_settings = [] # 初始化为空列表，稍后填充

# 从配置文件获取TLE下载地址

# 获取TLE数据，使用缓存机制
latest_tle_data = get_tle_data(settings.get('tle', {}).get('CELESTRAK_TLE_URL'))
# 加载TLE数据
latest_tle_data = load_tle_data(latest_tle_data)

# 11. 构建 .pbrt 文件的卫星设置

# 从settings.yaml读取API信息
def load_api_settings():
    with open('settings.yaml', 'r', encoding='utf-8') as file:
        settings = yaml.safe_load(file)
    api_base_url = settings['api']['API_BASE_URL']
    api_version = settings['api']['API_VERSION']
    api_key = settings['api']['API_KEY']
    return api_base_url, api_version, api_key

# 获取云端模型列表
def get_cloud_models(api_base_url, api_version, api_key):
    model_url = f"{api_base_url}{api_version}/model"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(model_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取模型列表失败: {e}")
        return []

# 模型-TLE配对选择GUI
class ModelTLESelector:
    def __init__(self, root, models, tle_data):
        self.root = root
        self.root.title("模型-TLE配对选择器")
        self.root.geometry("1200x700")
        
        self.models = models
        self.tle_data = tle_data
        self.filtered_tle_names = list(tle_data.keys())  # 用于搜索过滤
        
        # 存储选择的模型和TLE配对
        self.selected_pairs = []
        
        # 当前选择的模型序号
        self.current_model_index = 0
        
        # 当前选择的模型名称(用于TLE选择阶段)
        self.current_pairing_model = None
        self.current_pairing_model_uuid = None  # 添加UUID存储
        
        # 标记哪些模型和TLE已被选择
        self.selected_models = set()
        self.selected_tles = set()
        
        # 是否处于选择TLE阶段
        self.is_tle_selection_stage = False
        
        self.create_ui()
    
    def create_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部时间选择器
        time_frame = ttk.LabelFrame(main_frame, text="UTC时间选择")
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 使用当前UTC时间作为默认值
        now = dt.now(datetime.timezone.utc)
        
        time_selector_frame = ttk.Frame(time_frame)
        time_selector_frame.pack(padx=5, pady=5)
        
        # 年月日
        ttk.Label(time_selector_frame, text="年:").grid(row=0, column=0)
        self.year_var = tk.StringVar(value=now.year)
        ttk.Spinbox(time_selector_frame, from_=1900, to=2100, textvariable=self.year_var, width=5).grid(row=0, column=1)
        
        ttk.Label(time_selector_frame, text="月:").grid(row=0, column=2)
        self.month_var = tk.StringVar(value=now.month)
        ttk.Spinbox(time_selector_frame, from_=1, to=12, textvariable=self.month_var, width=3).grid(row=0, column=3)
        
        ttk.Label(time_selector_frame, text="日:").grid(row=0, column=4)
        self.day_var = tk.StringVar(value=now.day)
        ttk.Spinbox(time_selector_frame, from_=1, to=31, textvariable=self.day_var, width=3).grid(row=0, column=5)
        
        # 时分秒
        ttk.Label(time_selector_frame, text="时:").grid(row=0, column=6)
        self.hour_var = tk.StringVar(value=now.hour)
        ttk.Spinbox(time_selector_frame, from_=0, to=23, textvariable=self.hour_var, width=3).grid(row=0, column=7)
        
        ttk.Label(time_selector_frame, text="分:").grid(row=0, column=8)
        self.minute_var = tk.StringVar(value=now.minute)
        ttk.Spinbox(time_selector_frame, from_=0, to=59, textvariable=self.minute_var, width=3).grid(row=0, column=9)
        
        ttk.Label(time_selector_frame, text="秒:").grid(row=0, column=10)
        self.second_var = tk.StringVar(value=now.second)
        ttk.Spinbox(time_selector_frame, from_=0, to=59, textvariable=self.second_var, width=3).grid(row=0, column=11)
        
        # 添加UTC时间说明
        utc_note = ttk.Label(time_selector_frame, text="(所有时间均为UTC时间，而非本地时间)", foreground="red")
        utc_note.grid(row=1, column=0, columnspan=12, pady=(5,0))
        
        # 选择区域（分为左右两栏）
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左栏 - 模型列表
        model_frame = ttk.LabelFrame(selection_frame, text="云端模型")
        model_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 模型列表
        self.model_listbox = tk.Listbox(model_frame, selectmode=tk.SINGLE, height=20)
        self.model_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        model_scrollbar = ttk.Scrollbar(model_frame, orient=tk.VERTICAL, command=self.model_listbox.yview)
        model_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.model_listbox.config(yscrollcommand=model_scrollbar.set)
        
        # 模型信息显示区域
        model_info_frame = ttk.LabelFrame(model_frame, text="模型信息")
        model_info_frame.pack(fill=tk.X, padx=5, pady=5)
        self.model_info_text = tk.Text(model_info_frame, height=10, width=50, wrap=tk.WORD)
        self.model_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.model_info_text.config(state=tk.DISABLED)
        
        # 右栏 - TLE列表
        tle_frame = ttk.LabelFrame(selection_frame, text="TLE数据")
        tle_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # TLE搜索框
        search_frame = ttk.Frame(tle_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_tle_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # TLE列表框架
        tle_list_frame = ttk.Frame(tle_frame)
        tle_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # TLE列表
        self.tle_listbox = tk.Listbox(tle_list_frame, selectmode=tk.SINGLE, height=20)
        self.tle_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tle_scrollbar = ttk.Scrollbar(tle_list_frame, orient=tk.VERTICAL, command=self.tle_listbox.yview)
        tle_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tle_listbox.config(yscrollcommand=tle_scrollbar.set)
        
        # 当前选择状态信息
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="请选择模型：")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.pairing_label = ttk.Label(status_frame, text="")
        self.pairing_label.pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.select_button = ttk.Button(button_frame, text="选择", command=self.select_item)
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="重选", command=self.reset_current_selection)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.finish_button = ttk.Button(button_frame, text="完成配对", command=self.finish_pairing)
        self.finish_button.pack(side=tk.RIGHT, padx=5)
        
        # 加载数据
        self.load_data()
        
        # 绑定事件
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        self.model_listbox.bind('<Motion>', self.on_model_hover)
    
    def filter_tle_list(self, *args):
        """根据搜索框内容筛选TLE列表"""
        search_term = self.search_var.get().upper()  # 转为大写以进行不区分大小写的搜索
        
        # 清空当前列表
        self.tle_listbox.delete(0, tk.END)
        
        # 重置筛选后的TLE名称列表
        self.filtered_tle_names = []
        
        # 添加匹配的TLE
        for tle_name in self.tle_data.keys():
            if search_term in tle_name:
                self.tle_listbox.insert(tk.END, tle_name)
                self.filtered_tle_names.append(tle_name)
        
        # 更新已选择项的显示状态
        self.update_listbox_states()
    
    def load_data(self):
        # 加载模型列表
        for i, model in enumerate(self.models):
            model_name = model.get('name', f'模型 {i+1}')
            self.model_listbox.insert(tk.END, model_name)
        
        # 加载TLE数据
        for tle_name in self.tle_data.keys():
            self.tle_listbox.insert(tk.END, tle_name)
        
        # 更新筛选后的TLE名称列表
        self.filtered_tle_names = list(self.tle_data.keys())
    
    def on_model_select(self, event):
        if not self.is_tle_selection_stage:
            selection = self.model_listbox.curselection()
            if selection:
                index = selection[0]
                model = self.models[index]
                self.show_model_info(model)
    
    def on_model_hover(self, event):
        if not self.is_tle_selection_stage:
            index = self.model_listbox.nearest(event.y)
            if 0 <= index < len(self.models):
                model = self.models[index]
                self.show_model_info(model)
    
    def show_model_info(self, model):
        self.model_info_text.config(state=tk.NORMAL)
        self.model_info_text.delete(1.0, tk.END)
        
        name = model.get('name', '未知')
        description = model.get('zh_CN', {}).get('description', model.get('en_US', {}).get('description', '无描述'))
        model_type = model.get('model_type', '未知')
        uuid = model.get('uuid', '未知')
        
        info_text = f"名称: {name}\n"
        info_text += f"类型: {model_type}\n"
        info_text += f"UUID: {uuid}\n"
        info_text += f"描述: {description}\n"
        
        self.model_info_text.insert(1.0, info_text)
        self.model_info_text.config(state=tk.DISABLED)
    
    def update_listbox_states(self):
        # 更新模型列表状态
        for i in range(self.model_listbox.size()):
            if i in self.selected_models:
                self.model_listbox.itemconfig(i, {'bg': 'light gray', 'fg': 'gray'})
            else:
                self.model_listbox.itemconfig(i, {'bg': 'white', 'fg': 'black'})
        
        # 更新TLE列表状态
        for i in range(self.tle_listbox.size()):
            tle_name = self.filtered_tle_names[i] if i < len(self.filtered_tle_names) else ""
            if tle_name in self.selected_tles:
                self.tle_listbox.itemconfig(i, {'bg': 'light gray', 'fg': 'gray'})
            else:
                self.tle_listbox.itemconfig(i, {'bg': 'white', 'fg': 'black'})
    
    def select_item(self):
        if not self.is_tle_selection_stage:
            # 选择模型阶段
            selection = self.model_listbox.curselection()
            if not selection:
                messagebox.showinfo("提示", "请先选择一个模型")
                return
            
            index = selection[0]
            if index in self.selected_models:
                messagebox.showinfo("提示", "该模型已被选择")
                return
            
            model = self.models[index]
            model_name = model.get('name')
            model_uuid = model.get('uuid')  # 获取UUID
            
            # 标记已选择的模型
            self.selected_models.add(index)
            self.current_model_index += 1
            
            # 切换到TLE选择阶段
            self.is_tle_selection_stage = True
            self.current_pairing_model = model_name
            self.current_pairing_model_uuid = model_uuid  # 存储UUID
            
            # 更新状态显示
            self.status_label.config(text=f"为模型 '{model_name}' 选择TLE数据：")
            self.update_listbox_states()
        else:
            # 选择TLE阶段
            selection = self.tle_listbox.curselection()
            if not selection:
                messagebox.showinfo("提示", "请选择一个TLE数据")
                return
            
            index = selection[0]
            tle_name = self.filtered_tle_names[index]  # 使用筛选后的列表获取真实的TLE名称
            
            if tle_name in self.selected_tles:
                messagebox.showinfo("提示", "该TLE数据已被选择")
                return
            
            # 添加配对，包含UUID
            self.selected_tles.add(tle_name)
            self.selected_pairs.append((self.current_pairing_model, tle_name, self.current_pairing_model_uuid))
            
            # 重置为模型选择阶段
            self.is_tle_selection_stage = False
            self.current_pairing_model = None
            self.current_pairing_model_uuid = None
            
            # 更新状态显示
            self.status_label.config(text="请选择模型：")
            self.pairing_label.config(text=f"已配对: {len(self.selected_pairs)}")
            
            # 更新列表状态
            self.update_listbox_states()
    
    def reset_current_selection(self):
        if self.is_tle_selection_stage:
            # 重置当前TLE选择
            self.is_tle_selection_stage = False
            self.current_pairing_model = None
            self.current_pairing_model_uuid = None
            
            # 移除最后选择的模型
            if self.selected_models:
                last_model_index = max(self.selected_models)
                self.selected_models.remove(last_model_index)
                # 恢复该模型的显示状态
                self.model_listbox.itemconfig(last_model_index, {'bg': 'white', 'fg': 'black'})
            
            # 更新状态显示
            self.status_label.config(text="请选择模型：")
            self.update_listbox_states()
        else:
            # 无模型选择状态下按重选无效
            pass
    
    def finish_pairing(self):
        if self.is_tle_selection_stage:
            messagebox.showinfo("提示", "请先完成当前模型的TLE配对或点击重选")
            return
        
        if not self.selected_pairs:
            messagebox.showinfo("提示", "请至少进行一次模型-TLE配对")
            return
        
        # 获取选择的时间
        try:
            selected_time = datetime.datetime(
                int(self.year_var.get()),
                int(self.month_var.get()),
                int(self.day_var.get()),
                int(self.hour_var.get()),
                int(self.minute_var.get()),
                int(self.second_var.get())
            )
        except ValueError as e:
            messagebox.showerror("时间错误", f"无效的日期时间: {e}")
            return
        
        # 返回结果并关闭窗口
        self.result = {
            "time": selected_time,
            "pairs": self.selected_pairs
        }
        self.root.destroy()

# 主函数
def select_models_and_tles():
    # 读取API设置
    api_base_url, api_version, api_key = load_api_settings()
    
    # 获取云端模型列表
    models = get_cloud_models(api_base_url, api_version, api_key)
    
    # TLE数据
    tle_data = latest_tle_data  # 使用从Celestrak下载的TLE数据
    
    # 创建GUI
    root = tk.Tk()
    selector = ModelTLESelector(root, models, tle_data)
    root.mainloop()
    
    # 获取结果
    if hasattr(selector, 'result'):
        print("选择结果:")
        selected_time = selector.result['time']
        print(f"选择的UTC时间: {selected_time}")
        
        print("模型-TLE配对:")
        for model_name, tle_name, model_uuid in selector.result['pairs']:
            print(f"模型: {model_name} (UUID: {model_uuid}) - TLE: {tle_name}")
        
        return selector.result
    else:
        print("用户取消了选择")
        return None

# 运行选择器
selection_result = select_models_and_tles()

def process_material_names(content, model_uuid):
    """处理材料名称，替换空字符串为唯一名称
    
    Args:
        content: 文件内容
        model_uuid: 模型的UUID
        
    Returns:
        str: 处理后的内容
    """
    import uuid
    import re
    
    # 查找所有MakeNamedMaterial ""语句
    empty_materials = re.findall(r'MakeNamedMaterial\s*""', content)
    if len(empty_materials) > 1:
        raise ValueError("发现多个空字符串命名的材料定义")
    elif len(empty_materials) == 0:
        return content  # 没有需要处理的情况
    
    # 生成唯一材料名，以模型UUID前8位开头
    model_uuid_prefix = model_uuid[:8]
    new_name = f"{model_uuid_prefix}-auto-{uuid.uuid4().hex[:8]}"
    
    # 替换材料定义 - 只替换MakeNamedMaterial ""
    content = re.sub(
        r'MakeNamedMaterial\s*""',
        f'MakeNamedMaterial "{new_name}"',
        content,
        count=1  # 只替换第一个出现
    )
    
    # 替换材料引用 - 只替换NamedMaterial ""，而不是所有的" "
    content = re.sub(
        r'NamedMaterial\s*""',
        f'NamedMaterial "{new_name}"',
        content
    )
    
    return content

time_utc = get_utc_time(ts, 2025, 3, 10, 8, 0, 0) # mock

# 处理模型变换、下载并生成场景文件
def transform_and_create_scene_files(selection_result, api_base_url, api_version, api_key):
    """处理模型变换、下载模型并生成场景文件
    
    Args:
        selection_result: 用户选择的结果
        api_base_url: API基础URL
        api_version: API版本
        api_key: API密钥
    
    Returns:
        str: 合并后的PBRT文件路径
    """
    if not selection_result:
        print("没有选择结果，无法继续")
        return None
    
    # 获取用户选择的时间
    selected_time = selection_result['time']
    time_utc = get_utc_time(ts, 
                         selected_time.year, 
                         selected_time.month, 
                         selected_time.day, 
                         selected_time.hour, 
                         selected_time.minute, 
                         selected_time.second)
    
    print(f"使用UTC时间: {time_utc.utc_iso()} 计算天体位置")
    
    # 使用用户选择的时间计算天体位置
    # 计算天体在地心系中的位置 (地心坐标)
    earth_position = earth.at(time_utc).position
    sun_position = sun.at(time_utc).position
    moon_position = moon.at(time_utc).position
    
    # 将 skyfield 的位置转换为 astropy 的 ICRS 坐标
    earth_icrs = skyfield_to_icrs(earth_position)
    sun_icrs = skyfield_to_icrs(sun_position)
    moon_icrs = skyfield_to_icrs(moon_position)
    
    # 转换为 km 单位
    earth_icrs_km = convert_au_to_km(earth_icrs)
    sun_icrs_km = convert_au_to_km(sun_icrs)
    moon_icrs_km = convert_au_to_km(moon_icrs)
    
    # 转换为 GCRS 坐标 (单位: 千米 km)
    earth_gcrs_km = icrs_to_gcrs(earth_icrs_km, time_utc.utc_iso())
    sun_gcrs_km = icrs_to_gcrs(sun_icrs_km, time_utc.utc_iso())
    moon_gcrs_km = icrs_to_gcrs(moon_icrs_km, time_utc.utc_iso())
    
    # 准备卫星位置数据，用于相机和观察点选择
    satellite_positions = {}
    
    # 处理每个卫星的位置
    for model_name, tle_name, model_uuid in selection_result['pairs']:
        print(f"计算卫星 {tle_name} 的位置...")
        
        # 创建卫星对象
        satellite = EarthSatellite(latest_tle_data[tle_name][0], latest_tle_data[tle_name][1], tle_name, ts)
        
        # 计算卫星位置
        satellite_position = (earth + satellite).at(time_utc).position
        
        # 转换为ICRS坐标
        satellite_icrs = skyfield_to_icrs(satellite_position)
        satellite_icrs_km = convert_au_to_km(satellite_icrs)
        
        # 转换为GCRS坐标
        satellite_gcrs_km = icrs_to_gcrs(satellite_icrs_km, time_utc.utc_iso())
        
        # 存储卫星位置
        satellite_positions[tle_name] = [
            float(satellite_gcrs_km.x.value), 
            float(satellite_gcrs_km.y.value), 
            float(satellite_gcrs_km.z.value)
        ]
        
        # 打印卫星位置信息
        print(f"卫星 {tle_name} GCRS坐标 (km): X={satellite_gcrs_km.x:.6f}, Y={satellite_gcrs_km.y:.6f}, Z={satellite_gcrs_km.z:.6f}")
    
    # 启动相机和观察点选择界面
    print("正在启动相机位置和观察点选择界面...")
    camera_viewpoint_result = select_camera_viewpoint(satellite_positions, selected_time, earth, ts)
    
    if not camera_viewpoint_result:
        print("用户取消了相机和观察点选择，使用默认值")
        # 默认相机位置和观察点 (默认相机位置在30000,30000,30000，观察点在地球中心)
        camera_position = [30000, 30000, 30000]
        target_position = [0, 0, 0]
    else:
        print("用户已选择相机位置和观察点")
        camera_position = camera_viewpoint_result["camera"]["gcrs_coords"]
        target_position = camera_viewpoint_result["target"]["gcrs_coords"]
        print(f"相机位置: X={camera_position[0]:.2f}, Y={camera_position[1]:.2f}, Z={camera_position[2]:.2f}")
        print(f"观察点: X={target_position[0]:.2f}, Y={target_position[1]:.2f}, Z={target_position[2]:.2f}")
    
    # 启动渲染设置界面
    print("正在启动渲染设置界面...")
    # 不要在这里清理tkinter资源，这会导致新窗口无法正常显示
    rendering_settings_result = get_rendering_settings()
    
    if not rendering_settings_result:
        print("用户取消了渲染设置，使用默认值")
        # 默认渲染设置
        fov = 60.0
        resolution_x = 1366
        resolution_y = 768
        pixel_samples = 64
        max_depth = 5
    else:
        print("用户已选择渲染设置")
        fov = rendering_settings_result["fov"]
        resolution_x = rendering_settings_result["resolution_x"]
        resolution_y = rendering_settings_result["resolution_y"]
        pixel_samples = rendering_settings_result["pixel_samples"]
        max_depth = rendering_settings_result["max_depth"]
        print(f"视场角: {fov} 度")
        print(f"分辨率: {resolution_x} x {resolution_y} 像素")
        print(f"像素采样次数: {pixel_samples}")
        print(f"最大反射次数: {max_depth}")
    
    # 基于用户选择的时间更新世界设置
    w_settings = [set_bkg_light_source(None, 0.0001),
                 set_attrubute_the_sun([sun_gcrs_km.x.value, sun_gcrs_km.y.value, sun_gcrs_km.z.value], None),
                 set_attrubute_the_moon([moon_gcrs_km.x.value, moon_gcrs_km.y.value, moon_gcrs_km.z.value], None),
                 set_attrubute_the_earth([earth_gcrs_km.x.value, earth_gcrs_km.y.value, earth_gcrs_km.z.value], None, None, None)]

    # 确保渲染设置文件存在
    if not os.path.exists('rendering_settings.pbrt'):
        print("渲染设置文件不存在，重新生成")
        r_settings = [['# PBRTgen 0.0.1', '# by github.com/wtflmao', '\n'],
                      set_lookat(camera_position, target_position, None),
                      set_camera(None, fov),
                      set_sampler(None, pixel_samples),
                      set_integrator(None, max_depth),
                      set_film(resolution_x, resolution_y, None),
                      set_pixel_filter(),
                      set_color_space(None),
                      ['WorldBegin']]
        r_settings_overwriter('rendering_settings.pbrt', r_settings)
    else:
        # 读取现有设置文件并更新相关部分
        with open('rendering_settings.pbrt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换相机设置
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            if lines[i].startswith('LookAt'):
                # 跳过原有的3行LookAt设置
                i += 3
                # 添加新的LookAt设置
                new_lines.append(f'LookAt {camera_position[0]}  {camera_position[1]}  {camera_position[2]}')
                new_lines.append(f'       {target_position[0]}  {target_position[1]}  {target_position[2]}')
                new_lines.append('       0  0  1')
            elif lines[i].startswith('Camera '):
                # 替换相机设置
                new_lines.append(f'Camera "perspective" "float fov" {fov}')
                i += 1
            elif lines[i].startswith('Sampler '):
                # 替换采样器设置
                new_lines.append(f'Sampler "halton" "integer pixelsamples" {pixel_samples}')
                i += 1
            elif lines[i].startswith('Integrator '):
                # 替换积分器设置
                new_lines.append(f'Integrator "volpath" "integer maxdepth" {max_depth}')
                i += 1
            elif lines[i].startswith('Film '):
                # 替换电影设置（可能跨多行）
                new_lines.append('Film "spectral" "string filename" "1.exr"')
                new_lines.append(f'     "integer xresolution" [{resolution_x}]')
                new_lines.append(f'     "integer yresolution" [{resolution_y}]')
                new_lines.append('     "float diagonal" [70]')
                
                # 跳过原有的Film行
                while i < len(lines) and not (lines[i].startswith('PixelFilter') or lines[i].startswith('ColorSpace') or lines[i].startswith('WorldBegin')):
                    i += 1
                continue
            else:
                new_lines.append(lines[i])
                i += 1
        
        # 重写文件
        with open('rendering_settings.pbrt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("已更新渲染设置文件")

    # 读取渲染设置文件
    with open('rendering_settings.pbrt', 'r', encoding='utf-8') as f:
        rendering_settings_content = f.read()
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # 创建最终的合并文件
    output_file_path = "popo.pbrt"
    
    # 如果文件已存在，先删除
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    
    # 先写入公共头部
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(rendering_settings_content)
        # 添加天体设置
        f.write("\n# 天体设置\n\n")
    
    # 应用世界设置（天体）
    w_settings_appender(output_file_path, w_settings)
    
    # 添加模型标记
    with open(output_file_path, 'a', encoding='utf-8') as f:
        f.write("\n# 模型部分开始\n\n")
    
    # 处理每个模型-TLE配对
    for model_name, tle_name, model_uuid in selection_result['pairs']:
        print(f"处理模型 {model_name} (UUID: {model_uuid}) 与 TLE {tle_name} 的配对...")
        
        # 创建卫星对象
        satellite = EarthSatellite(latest_tle_data[tle_name][0], latest_tle_data[tle_name][1], tle_name, ts)
        
        # 计算卫星位置
        satellite_position = (earth + satellite).at(time_utc).position
        
        # 转换为ICRS坐标
        satellite_icrs = skyfield_to_icrs(satellite_position)
        satellite_icrs_km = convert_au_to_km(satellite_icrs)
        
        # 转换为GCRS坐标
        satellite_gcrs_km = icrs_to_gcrs(satellite_icrs_km, time_utc.utc_iso())
        
        # 打印卫星位置信息
        print(f"卫星 {tle_name} GCRS坐标 (km): X={satellite_gcrs_km.x:.6f}, Y={satellite_gcrs_km.y:.6f}, Z={satellite_gcrs_km.z:.6f}")
        
        # 构建转换请求数据
        transform_data = {
            "uuid": model_uuid,
            "translate": [float(satellite_gcrs_km.x.value), float(satellite_gcrs_km.y.value), float(satellite_gcrs_km.z.value)]
        }
        
        # 发送转换请求
        transform_url = f"{api_base_url}{api_version}/transform"
        try:
            transform_response = requests.post(transform_url, headers=headers, json=transform_data)
            transform_response.raise_for_status()
            
            print(f"模型 {model_name} 转换成功，正在下载模型文件...")
            
            # 下载模型文件
            model_url = f"{api_base_url}{api_version}/model/momo/{model_uuid}"
            model_response = requests.get(model_url, headers=headers)
            model_response.raise_for_status()

            # 创建临时文件前先处理材料名称
            raw_content = model_response.content.decode('utf-8')
            try:
                processed_content = process_material_names(raw_content, model_uuid)
                print(f"已处理模型 {model_name} 的材料名称")
            except ValueError as e:
                print(f"材料处理失败: {e}")
                continue
            
            # 创建临时文件，使用处理后的内容
            temp_file_path = f"temp_{model_uuid}.pbrt"
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)  # 使用处理后的内容而不是原始内容
            
            print(f"模型文件下载成功，保存为临时文件 {temp_file_path}")
            
            # 将模型文件追加到合并文件中
            with open(output_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n# {tle_name} - {model_uuid} - {model_name} Starts\n")
                with open(temp_file_path, 'r', encoding='utf-8') as model_file:
                    f.write(model_file.read())
                f.write(f"\n# {tle_name} - {model_uuid} - {model_name} Ends\n\n")
            
            # 删除临时文件
            os.remove(temp_file_path)
            
        except requests.exceptions.RequestException as e:
            print(f"处理模型 {model_name} 失败: {e}")
            continue
    
    print(f"合并场景文件 {output_file_path} 生成成功")
    return output_file_path

# 计算文件哈希值
def calculate_file_hash(file_path):
    """计算文件的SHA-256哈希值
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件的SHA-256哈希值
    """
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 逐块读取文件并更新哈希
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# 将PBRT文件提交到渲染服务
def render_pbrt_file(api_base_url, api_version, api_key, pbrt_file_path):
    """将PBRT文件提交到渲染服务
    
    Args:
        api_base_url: API基础URL
        api_version: API版本
        api_key: API密钥
        pbrt_file_path: PBRT文件路径
        
    Returns:
        str: 渲染结果文件路径，如果渲染失败则为None
    """
    # 计算文件哈希值
    file_hash = calculate_file_hash(pbrt_file_path)
    print(f"文件 {pbrt_file_path} 的哈希值: {file_hash}")
    
    # 准备请求
    render_url = f"{api_base_url}{api_version}/debug/render"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # 准备文件和参数
    with open(pbrt_file_path, 'rb') as f:
        files = {'pbrtFile': (os.path.basename(pbrt_file_path), f, 'text/plain')}
        data = {'hash': file_hash}
        
        try:
            # 发送渲染请求
            print(f"正在提交 {pbrt_file_path} 进行渲染...")
            response = requests.post(render_url, headers=headers, files=files, data=data)
            response.raise_for_status()
            
            # 保存渲染结果
            result_file_path = f"{file_hash}.exr"
            with open(result_file_path, 'wb') as result_file:
                result_file.write(response.content)
            
            print(f"渲染成功，结果保存为 {result_file_path}")
            
            # 自动打开EXR文件
            open_exr_file(result_file_path)
            
            return result_file_path
            
        except requests.exceptions.RequestException as e:
            print(f"渲染失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"状态码: {e.response.status_code}")
                print(f"错误信息: {e.response.text}")
            return None

# 自动打开EXR文件
def open_exr_file(exr_path):
    """尝试打开EXR文件
    
    Args:
        exr_path: EXR文件路径
    """
    try:
        # 获取绝对路径
        abs_path = os.path.abspath(exr_path)
        
        # 在Windows上尝试使用默认关联程序打开
        if os.name == 'nt':
            os.startfile(abs_path)
        # 在macOS上使用open命令
        elif os.name == 'posix' and 'darwin' in os.sys.platform:
            subprocess.call(['open', abs_path])
        # 在Linux上使用xdg-open
        elif os.name == 'posix':
            subprocess.call(['xdg-open', abs_path])
        
        print(f"已尝试打开EXR文件: {abs_path}")
    except Exception as e:
        print(f"无法自动打开EXR文件: {e}")
        print(f"请手动打开文件: {exr_path}")

# 在transform_and_create_scene_files函数末尾添加文件后处理步骤
def post_process_pbrt_file(output_file_path):
    """后处理PBRT文件，确保AttributeEnd和AttributeBegin之间有换行
    
    Args:
        output_file_path: PBRT文件路径
    """
    try:
        with open(output_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 AttributeEndAttributeBegin 为 AttributeEnd\nAttributeBegin
        modified_content = content.replace('AttributeEndAttributeBegin', 'AttributeEnd\nAttributeBegin')
        
        # 如果内容发生变化，则重新写入文件
        if modified_content != content:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"已处理文件 {output_file_path}，添加了换行")
        else:
            print(f"文件 {output_file_path} 无需修改")
    except Exception as e:
        print(f"处理文件 {output_file_path} 时发生错误: {e}")

def cleanup_tk_resources():
    """清理Tkinter资源，确保在后续线程中不会出现tkinter问题"""
    try:
        # 在主线程中关闭所有可能打开的Tkinter窗口和变量
        # 这是为了避免在新线程中使用Tkinter变量时出现线程错误
        import tkinter as tk
        import sys
        import gc
        
        # 检查是否存在_tkinter模块，并且有active的tcl解释器
        if '_tkinter' in sys.modules:
            # 尝试销毁所有toplevel窗口
            if hasattr(tk, '_default_root') and tk._default_root:
                for widget in tk._default_root.winfo_children():
                    if isinstance(widget, tk.Toplevel):
                        try:
                            widget.destroy()
                        except Exception:
                            pass
                
                # 获取所有Tk实例并销毁它们
                for obj in list(tk._default_root._tclCommands) if hasattr(tk._default_root, '_tclCommands') else []:
                    try:
                        if hasattr(tk._default_root, 'eval'):
                            tk._default_root.eval(f'rename {obj} ""')
                    except Exception:
                        pass
                
                # 销毁主窗口
                try:
                    tk._default_root.destroy()
                except Exception:
                    pass
                
                # 清空_default_root引用
                tk._default_root = None
        
        # 执行两次垃圾回收，确保所有循环引用被清理
        gc.collect()
        gc.collect()
        
        print("已清理Tkinter资源")
    except Exception as e:
        print(f"清理Tkinter资源时出现错误 (忽略): {str(e)}")
        
    # 强制等待一小段时间，确保Tk资源完全释放
    time.sleep(0.5)

# 在渲染前调用后处理函数
if selection_result:
    # 读取API设置
    api_base_url, api_version, api_key = load_api_settings()
    
    # 处理模型变换、下载并生成场景文件
    pbrt_file_path = transform_and_create_scene_files(selection_result, api_base_url, api_version, api_key)
    
    # 后处理PBRT文件
    post_process_pbrt_file(pbrt_file_path)
    
    # 如果成功生成场景文件，则提交渲染
    if pbrt_file_path:
        # 准备卫星位置数据字典
        satellite_positions = {}
        for model_name, sat_name, model_uuid in selection_result['pairs']:
            # 获取并创建卫星对象
            satellite = EarthSatellite(latest_tle_data[sat_name][0], latest_tle_data[sat_name][1], sat_name, ts)
            
            # 计算卫星位置
            satellite_position = (earth + satellite).at(time_utc).position
            sat_icrs = skyfield_to_icrs(satellite_position)
            sat_icrs_km = convert_au_to_km(sat_icrs)
            sat_gcrs_km = icrs_to_gcrs(sat_icrs_km, time_utc.utc_iso())
            
            # 存储卫星位置
            satellite_positions[sat_name] = [
                float(sat_gcrs_km.x.value), 
                float(sat_gcrs_km.y.value), 
                float(sat_gcrs_km.z.value)
            ]
        
        # 提交渲染之前，先清理所有Tkinter资源
        cleanup_tk_resources()
        
        # 启动可视化线程，确保Tkinter资源已完全清理
        print("正在生成轨道可视化...")
        visualization_done = visualize_in_new_thread(
            selection_result,
            selection_result['time'],
            satellite_positions,
            latest_tle_data,  # 传递TLE数据
            ts,  # 传递时间尺度对象
            earth  # 传递地球对象
        )
        
        # 提交渲染 - 这是一个阻塞操作，让它在可视化生成的同时进行
        print("正在提交渲染请求...")
        exr_file_path = render_pbrt_file(api_base_url, api_version, api_key, pbrt_file_path)
        
        # 检查渲染结果
        if exr_file_path:
            print(f"渲染流程完成，结果文件: {exr_file_path}")
        else:
            print("渲染失败")
        
        # 如果可视化尚未完成，等待一段时间
        if not visualization_done.is_set():
            print("正在等待轨道可视化完成...")
            visualization_done.wait(30)  # 最多等待30秒
            
        print("流程完成。")
    else:
        print("场景文件生成失败，无法渲染")


