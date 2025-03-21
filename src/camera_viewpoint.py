import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from skyfield.api import load, Topos
from astropy.coordinates import ICRS, GCRS, EarthLocation
from astropy.time import Time
import astropy.units as u
import math
from datetime import datetime
import yaml
import os
from src.coordinates import skyfield_to_icrs, icrs_to_gcrs, convert_au_to_km

class CameraViewpointSelector:
    """相机位置与观察点选择器"""
    
    def __init__(self, root, satellite_data, time_utc, earth, ts):
        """初始化相机位置与观察点选择器
        
        Args:
            root: Tkinter根窗口
            satellite_data: 卫星数据字典，格式为{sat_name: [gcrs_x, gcrs_y, gcrs_z]}
            time_utc: UTC时间对象
            earth: 地球天体对象
            ts: 时间尺度对象
        """
        # 使用 Tk().withdraw() 创建一个隐藏的根窗口，如果没有传入根窗口
        if not isinstance(root, tk.Tk) and not isinstance(root, tk.Toplevel):
            root = tk.Tk()
            root.withdraw()
        
        self.root = root
        self.root.title("相机位置与观察点选择器")
        self.root.geometry("1200x700")
        
        self.satellite_data = satellite_data
        self.time_utc = time_utc
        self.earth = earth
        self.ts = ts
        
        # 从文件加载地面站数据
        self.ground_stations = self.load_ground_stations()
        
        # 结果数据
        self.result = None
        
        # 当前选择
        self.camera_source = None
        self.target_source = None
        
        # 创建UI
        self.create_ui()
    
    def load_ground_stations(self):
        """从YAML文件加载地面站数据"""
        stations_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'stations.yaml')
        
        # 如果文件不存在，创建默认站点并保存
        if not os.path.exists(stations_file):
            default_stations = {
                "英国-格林威治天文台": {"lat": 51.4769, "lon": 0.0, "alt": 45.0},
                "中国-西电科大西大楼": {"lat": 34.2308, "lon": 108.9167, "alt": 414.0},
                "阿根廷-布宜诺斯艾利斯": {"lat": -34.6500, "lon": -58.3333, "alt": 2.0},
                "北极-中国黄河站": {"lat": 78.9167, "lon": 11.9333, "alt": 24.0}
            }
            
            # 保存默认站点到文件
            try:
                with open(stations_file, 'w', encoding='utf-8') as f:
                    yaml.dump(default_stations, f, allow_unicode=True, sort_keys=False)
                print(f"已创建默认地面站文件: {stations_file}")
                return default_stations
            except Exception as e:
                print(f"创建默认地面站文件失败: {str(e)}")
                # 如果保存失败，仍然返回默认站点
                return default_stations
        
        # 如果文件存在，读取文件内容
        try:
            with open(stations_file, 'r', encoding='utf-8') as f:
                stations = yaml.safe_load(f)
                print(f"已从 {stations_file} 加载 {len(stations)} 个地面站")
                return stations
        except Exception as e:
            print(f"读取地面站文件失败: {str(e)}")
            # 如果读取失败，返回默认站点
            return {
                "英国-格林威治天文台": {"lat": 51.4769, "lon": 0.0, "alt": 45.0},
                "中国-西电科大西大楼": {"lat": 34.2308, "lon": 108.9167, "alt": 414.0},
                "阿根廷-布宜诺斯艾利斯": {"lat": -34.6500, "lon": -58.3333, "alt": 2.0},
                "北极-中国黄河站": {"lat": 78.9167, "lon": 11.9333, "alt": 24.0}
            }
        
    def create_ui(self):
        """创建用户界面，添加异常处理"""
        try:
            # 主框架
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 顶部标题
            title_label = ttk.Label(main_frame, text="选择相机位置和观察点", font=("Arial", 16))
            title_label.pack(pady=10)
            
            # 分割线
            ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=5)
            
            # 内容框架 - 左右分栏
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # 左边框架 - 相机位置
            self.camera_frame = ttk.LabelFrame(content_frame, text="相机位置")
            self.camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 右边框架 - 观察点
            self.target_frame = ttk.LabelFrame(content_frame, text="观察点")
            self.target_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 添加相机位置列表
            self.create_camera_list()
            
            # 添加观察点列表
            self.create_target_list()
            
            # 底部按钮框架
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            # 确认按钮
            confirm_button = ttk.Button(button_frame, text="确认", command=self.confirm_selection)
            confirm_button.pack(side=tk.RIGHT, padx=5)
            
            # 取消按钮
            cancel_button = ttk.Button(button_frame, text="取消", command=self.root.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=5)
        except Exception as e:
            messagebox.showerror("界面创建错误", f"创建界面时发生错误: {str(e)}")
            self.root.destroy()
    
    def create_camera_list(self):
        """创建相机位置列表"""
        # 列表框架
        list_frame = ttk.Frame(self.camera_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 列表标题
        list_label = ttk.Label(list_frame, text="选择相机位置:")
        list_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 创建列表
        self.camera_listbox = tk.Listbox(list_frame, height=10)
        self.camera_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.camera_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.camera_listbox.config(yscrollcommand=scrollbar.set)
        
        # 添加地面站
        self.camera_listbox.insert(tk.END, "-- 地面站 --")
        for station_name, station_data in self.ground_stations.items():
            # 格式化地面站显示 - 使用自动生成的格式
            lat = station_data["lat"]
            lon = station_data["lon"]
            lat_str = f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}"
            lon_str = f"{abs(lon):.4f}°{'E' if lon >= 0 else 'W'}"
            display_name = f"{station_name} ({lat_str}, {lon_str})"
            
            # 存储原始名称和显示名称的映射
            if not hasattr(self, 'station_display_map'):
                self.station_display_map = {}
            self.station_display_map[display_name] = station_name
            
            self.camera_listbox.insert(tk.END, display_name)
        
        # 添加卫星
        self.camera_listbox.insert(tk.END, "-- 卫星 --")
        for sat_name in self.satellite_data:
            self.camera_listbox.insert(tk.END, sat_name)
        
        # 添加手动输入选项
        self.camera_listbox.insert(tk.END, "-- 手动输入 --")
        self.camera_listbox.insert(tk.END, "手动输入GCRS坐标")
        self.camera_listbox.insert(tk.END, "手动输入地面经纬度")
        
        # 绑定事件
        self.camera_listbox.bind('<<ListboxSelect>>', self.on_camera_select)
        
        # 坐标输入框架
        input_frame = ttk.Frame(self.camera_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # GCRS坐标输入框
        gcrs_frame = ttk.LabelFrame(input_frame, text="GCRS坐标 (km)")
        gcrs_frame.pack(fill=tk.X, pady=5)
        
        # X坐标
        ttk.Label(gcrs_frame, text="X:").grid(row=0, column=0, padx=5, pady=5)
        self.camera_x_var = tk.StringVar()
        self.camera_x_entry = ttk.Entry(gcrs_frame, textvariable=self.camera_x_var, state="disabled")
        self.camera_x_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(gcrs_frame, text="Y:").grid(row=0, column=2, padx=5, pady=5)
        self.camera_y_var = tk.StringVar()
        self.camera_y_entry = ttk.Entry(gcrs_frame, textvariable=self.camera_y_var, state="disabled")
        self.camera_y_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Z坐标
        ttk.Label(gcrs_frame, text="Z:").grid(row=0, column=4, padx=5, pady=5)
        self.camera_z_var = tk.StringVar()
        self.camera_z_entry = ttk.Entry(gcrs_frame, textvariable=self.camera_z_var, state="disabled")
        self.camera_z_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # 地面经纬度输入框
        geo_frame = ttk.LabelFrame(input_frame, text="地面经纬度 (°)")
        geo_frame.pack(fill=tk.X, pady=5)
        
        # 纬度
        ttk.Label(geo_frame, text="纬度:").grid(row=0, column=0, padx=5, pady=5)
        self.camera_lat_var = tk.StringVar()
        self.camera_lat_entry = ttk.Entry(geo_frame, textvariable=self.camera_lat_var, state="disabled")
        self.camera_lat_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 经度
        ttk.Label(geo_frame, text="经度:").grid(row=0, column=2, padx=5, pady=5)
        self.camera_lon_var = tk.StringVar()
        self.camera_lon_entry = ttk.Entry(geo_frame, textvariable=self.camera_lon_var, state="disabled")
        self.camera_lon_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 确认坐标按钮
        self.camera_confirm_button = ttk.Button(input_frame, text="确认坐标", 
                                                command=self.confirm_camera_input,
                                                state="disabled")
        self.camera_confirm_button.pack(pady=5)
    
    def create_target_list(self):
        """创建观察点列表"""
        # 列表框架
        list_frame = ttk.Frame(self.target_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 列表标题
        list_label = ttk.Label(list_frame, text="选择观察点:")
        list_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 创建列表
        self.target_listbox = tk.Listbox(list_frame, height=10)
        self.target_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.target_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.target_listbox.config(yscrollcommand=scrollbar.set)
        
        # 添加卫星
        self.target_listbox.insert(tk.END, "-- 卫星 --")
        for sat_name in self.satellite_data:
            self.target_listbox.insert(tk.END, sat_name)
        
        # 添加手动输入选项
        self.target_listbox.insert(tk.END, "-- 手动输入 --")
        self.target_listbox.insert(tk.END, "手动输入GCRS坐标")
        self.target_listbox.insert(tk.END, "手动输入地面经纬度")
        
        # 绑定事件
        self.target_listbox.bind('<<ListboxSelect>>', self.on_target_select)
        
        # 坐标输入框架
        input_frame = ttk.Frame(self.target_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # GCRS坐标输入框
        gcrs_frame = ttk.LabelFrame(input_frame, text="GCRS坐标 (km)")
        gcrs_frame.pack(fill=tk.X, pady=5)
        
        # X坐标
        ttk.Label(gcrs_frame, text="X:").grid(row=0, column=0, padx=5, pady=5)
        self.target_x_var = tk.StringVar()
        self.target_x_entry = ttk.Entry(gcrs_frame, textvariable=self.target_x_var, state="disabled")
        self.target_x_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Y坐标
        ttk.Label(gcrs_frame, text="Y:").grid(row=0, column=2, padx=5, pady=5)
        self.target_y_var = tk.StringVar()
        self.target_y_entry = ttk.Entry(gcrs_frame, textvariable=self.target_y_var, state="disabled")
        self.target_y_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Z坐标
        ttk.Label(gcrs_frame, text="Z:").grid(row=0, column=4, padx=5, pady=5)
        self.target_z_var = tk.StringVar()
        self.target_z_entry = ttk.Entry(gcrs_frame, textvariable=self.target_z_var, state="disabled")
        self.target_z_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # 地面经纬度输入框
        geo_frame = ttk.LabelFrame(input_frame, text="地面经纬度 (°)")
        geo_frame.pack(fill=tk.X, pady=5)
        
        # 纬度
        ttk.Label(geo_frame, text="纬度:").grid(row=0, column=0, padx=5, pady=5)
        self.target_lat_var = tk.StringVar()
        self.target_lat_entry = ttk.Entry(geo_frame, textvariable=self.target_lat_var, state="disabled")
        self.target_lat_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 经度
        ttk.Label(geo_frame, text="经度:").grid(row=0, column=2, padx=5, pady=5)
        self.target_lon_var = tk.StringVar()
        self.target_lon_entry = ttk.Entry(geo_frame, textvariable=self.target_lon_var, state="disabled")
        self.target_lon_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 确认坐标按钮
        self.target_confirm_button = ttk.Button(input_frame, text="确认坐标", 
                                                command=self.confirm_target_input,
                                                state="disabled")
        self.target_confirm_button.pack(pady=5)
    
    def on_camera_select(self, event):
        """处理相机位置选择事件"""
        selection = self.camera_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.camera_listbox.get(selection[0])
        
        # 重置所有输入
        self.reset_camera_inputs()
        
        # 如果选择了分隔符，直接返回
        if selected_text.startswith("--"):
            return
        
        # 处理地面站选择 - 使用映射获取原始站点名称
        if hasattr(self, 'station_display_map') and selected_text in self.station_display_map:
            station_name = self.station_display_map[selected_text]
            station_data = self.ground_stations[station_name]
            self.camera_lat_var.set(str(station_data["lat"]))
            self.camera_lon_var.set(str(station_data["lon"]))
            
            # 计算GCRS坐标
            gcrs_coords = self.geo_to_gcrs(station_data["lat"], station_data["lon"], station_data["alt"])
            self.camera_x_var.set(f"{gcrs_coords[0]:.2f}")
            self.camera_y_var.set(f"{gcrs_coords[1]:.2f}")
            self.camera_z_var.set(f"{gcrs_coords[2]:.2f}")
            
            # 保存选择
            self.camera_source = {
                "type": "ground_station",
                "name": station_name,
                "display_name": selected_text,
                "lat": station_data["lat"],
                "lon": station_data["lon"],
                "alt": station_data["alt"],
                "gcrs_coords": gcrs_coords
            }
            
            # 启用确认按钮
            self.camera_confirm_button.config(state="normal")
        
        # 处理卫星选择
        elif selected_text in self.satellite_data:
            sat_coords = self.satellite_data[selected_text]
            self.camera_x_var.set(f"{sat_coords[0]:.2f}")
            self.camera_y_var.set(f"{sat_coords[1]:.2f}")
            self.camera_z_var.set(f"{sat_coords[2]:.2f}")
            
            # 保存选择
            self.camera_source = {
                "type": "satellite",
                "name": selected_text,
                "gcrs_coords": sat_coords
            }
            
            # 启用确认按钮
            self.camera_confirm_button.config(state="normal")
        
        # 处理手动输入GCRS坐标
        elif selected_text == "手动输入GCRS坐标":
            self.enable_camera_gcrs_inputs()
            
            # 清空坐标
            self.camera_x_var.set("")
            self.camera_y_var.set("")
            self.camera_z_var.set("")
            
            # 启用确认按钮
            self.camera_confirm_button.config(state="normal")
            
            # 暂时保存选择类型
            self.camera_source = {
                "type": "manual_gcrs",
                "gcrs_coords": None
            }
        
        # 处理手动输入地面经纬度
        elif selected_text == "手动输入地面经纬度":
            self.enable_camera_geo_inputs()
            
            # 清空坐标
            self.camera_lat_var.set("")
            self.camera_lon_var.set("")
            
            # 启用确认按钮
            self.camera_confirm_button.config(state="normal")
            
            # 暂时保存选择类型
            self.camera_source = {
                "type": "manual_geo",
                "lat": None,
                "lon": None,
                "alt": 0.0,
                "gcrs_coords": None
            }
    
    def on_target_select(self, event):
        """处理观察点选择事件"""
        selection = self.target_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.target_listbox.get(selection[0])
        
        # 重置所有输入
        self.reset_target_inputs()
        
        # 如果选择了分隔符，直接返回
        if selected_text.startswith("--"):
            return
        
        # 处理地面站选择 - 使用映射获取原始站点名称
        if hasattr(self, 'station_display_map') and selected_text in self.station_display_map:
            station_name = self.station_display_map[selected_text]
            station_data = self.ground_stations[station_name]
            self.target_lat_var.set(str(station_data["lat"]))
            self.target_lon_var.set(str(station_data["lon"]))
            
            # 计算GCRS坐标
            gcrs_coords = self.geo_to_gcrs(station_data["lat"], station_data["lon"], station_data["alt"])
            self.target_x_var.set(f"{gcrs_coords[0]:.2f}")
            self.target_y_var.set(f"{gcrs_coords[1]:.2f}")
            self.target_z_var.set(f"{gcrs_coords[2]:.2f}")
            
            # 保存选择
            self.target_source = {
                "type": "ground_station",
                "name": station_name,
                "display_name": selected_text,
                "lat": station_data["lat"],
                "lon": station_data["lon"],
                "alt": station_data["alt"],
                "gcrs_coords": gcrs_coords
            }
            
            # 启用确认按钮
            self.target_confirm_button.config(state="normal")
        
        # 处理卫星选择
        elif selected_text in self.satellite_data:
            sat_coords = self.satellite_data[selected_text]
            self.target_x_var.set(f"{sat_coords[0]:.2f}")
            self.target_y_var.set(f"{sat_coords[1]:.2f}")
            self.target_z_var.set(f"{sat_coords[2]:.2f}")
            
            # 保存选择
            self.target_source = {
                "type": "satellite",
                "name": selected_text,
                "gcrs_coords": sat_coords
            }
            
            # 启用确认按钮
            self.target_confirm_button.config(state="normal")
        
        # 处理手动输入GCRS坐标
        elif selected_text == "手动输入GCRS坐标":
            self.enable_target_gcrs_inputs()
            
            # 清空坐标
            self.target_x_var.set("")
            self.target_y_var.set("")
            self.target_z_var.set("")
            
            # 启用确认按钮
            self.target_confirm_button.config(state="normal")
            
            # 暂时保存选择类型
            self.target_source = {
                "type": "manual_gcrs",
                "gcrs_coords": None
            }
        
        # 处理手动输入地面经纬度
        elif selected_text == "手动输入地面经纬度":
            self.enable_target_geo_inputs()
            
            # 清空坐标
            self.target_lat_var.set("")
            self.target_lon_var.set("")
            
            # 启用确认按钮
            self.target_confirm_button.config(state="normal")
            
            # 暂时保存选择类型
            self.target_source = {
                "type": "manual_geo",
                "lat": None,
                "lon": None,
                "alt": 0.0,
                "gcrs_coords": None
            }
    
    def reset_camera_inputs(self):
        """重置相机位置输入控件"""
        # 禁用所有输入
        self.camera_x_entry.config(state="disabled")
        self.camera_y_entry.config(state="disabled")
        self.camera_z_entry.config(state="disabled")
        self.camera_lat_entry.config(state="disabled")
        self.camera_lon_entry.config(state="disabled")
        self.camera_confirm_button.config(state="disabled")
        
        # 清除所有输入框的值
        self.camera_x_var.set("")
        self.camera_y_var.set("")
        self.camera_z_var.set("")
        self.camera_lat_var.set("")
        self.camera_lon_var.set("")
    
    def reset_target_inputs(self):
        """重置观察点输入控件"""
        # 禁用所有输入
        self.target_x_entry.config(state="disabled")
        self.target_y_entry.config(state="disabled")
        self.target_z_entry.config(state="disabled")
        self.target_lat_entry.config(state="disabled")
        self.target_lon_entry.config(state="disabled")
        self.target_confirm_button.config(state="disabled")
        
        # 清除所有输入框的值
        self.target_x_var.set("")
        self.target_y_var.set("")
        self.target_z_var.set("")
        self.target_lat_var.set("")
        self.target_lon_var.set("")
    
    def enable_camera_gcrs_inputs(self):
        """启用相机GCRS坐标输入"""
        self.camera_x_entry.config(state="normal")
        self.camera_y_entry.config(state="normal")
        self.camera_z_entry.config(state="normal")
    
    def enable_camera_geo_inputs(self):
        """启用相机地面经纬度输入"""
        self.camera_lat_entry.config(state="normal")
        self.camera_lon_entry.config(state="normal")
    
    def enable_target_gcrs_inputs(self):
        """启用观察点GCRS坐标输入"""
        self.target_x_entry.config(state="normal")
        self.target_y_entry.config(state="normal")
        self.target_z_entry.config(state="normal")
    
    def enable_target_geo_inputs(self):
        """启用观察点地面经纬度输入"""
        self.target_lat_entry.config(state="normal")
        self.target_lon_entry.config(state="normal")
    
    def confirm_camera_input(self):
        """确认相机位置手动输入"""
        if self.camera_source["type"] == "manual_gcrs":
            try:
                x = float(self.camera_x_var.get())
                y = float(self.camera_y_var.get())
                z = float(self.camera_z_var.get())
                
                # 更新坐标
                self.camera_source["gcrs_coords"] = [x, y, z]
                
                # 禁用输入但保留显示值
                self.camera_x_entry.config(state="disabled")
                self.camera_y_entry.config(state="disabled")
                self.camera_z_entry.config(state="disabled")
                self.camera_confirm_button.config(state="disabled")
                
            except ValueError:
                messagebox.showerror("输入错误", "GCRS坐标必须是有效的数字，以千米为单位")
                return
            
        elif self.camera_source["type"] == "manual_geo":
            try:
                lat = float(self.camera_lat_var.get())
                lon = float(self.camera_lon_var.get())
                
                # 检查有效范围
                if lat < -90 or lat > 90:
                    messagebox.showerror("输入错误", "纬度必须在-90到90度之间，以度为单位，以N为正，S为负")
                    return
                
                if lon < -180 or lon > 180:
                    messagebox.showerror("输入错误", "经度必须在-180到180度之间，以度为单位，以E为正，W为负")
                    return
                
                # 更新经纬度
                self.camera_source["lat"] = lat
                self.camera_source["lon"] = lon
                
                # 计算GCRS坐标
                gcrs_coords = self.geo_to_gcrs(lat, lon, 0.0)
                self.camera_source["gcrs_coords"] = gcrs_coords
                
                # 更新GCRS坐标显示
                self.camera_x_var.set(f"{gcrs_coords[0]:.2f}")
                self.camera_y_var.set(f"{gcrs_coords[1]:.2f}")
                self.camera_z_var.set(f"{gcrs_coords[2]:.2f}")
                
                # 禁用输入但保留显示值
                self.camera_lat_entry.config(state="disabled")
                self.camera_lon_entry.config(state="disabled")
                self.camera_confirm_button.config(state="disabled")
                
            except ValueError:
                messagebox.showerror("输入错误", "经纬度必须是有效的数字")
                return
    
    def confirm_target_input(self):
        """确认观察点手动输入"""
        if self.target_source["type"] == "manual_gcrs":
            try:
                x = float(self.target_x_var.get())
                y = float(self.target_y_var.get())
                z = float(self.target_z_var.get())
                
                # 更新坐标
                self.target_source["gcrs_coords"] = [x, y, z]
                
                # 禁用输入但保留显示值
                self.target_x_entry.config(state="disabled")
                self.target_y_entry.config(state="disabled")
                self.target_z_entry.config(state="disabled")
                self.target_confirm_button.config(state="disabled")
                
            except ValueError:
                messagebox.showerror("输入错误", "GCRS坐标必须是有效的数字")
                return
            
        elif self.target_source["type"] == "manual_geo":
            try:
                lat = float(self.target_lat_var.get())
                lon = float(self.target_lon_var.get())
                
                # 检查有效范围
                if lat < -90 or lat > 90:
                    messagebox.showerror("输入错误", "纬度必须在-90到90度之间")
                    return
                
                if lon < -180 or lon > 180:
                    messagebox.showerror("输入错误", "经度必须在-180到180度之间")
                    return
                
                # 更新经纬度
                self.target_source["lat"] = lat
                self.target_source["lon"] = lon
                
                # 计算GCRS坐标
                gcrs_coords = self.geo_to_gcrs(lat, lon, 0.0)
                self.target_source["gcrs_coords"] = gcrs_coords
                
                # 更新GCRS坐标显示
                self.target_x_var.set(f"{gcrs_coords[0]:.2f}")
                self.target_y_var.set(f"{gcrs_coords[1]:.2f}")
                self.target_z_var.set(f"{gcrs_coords[2]:.2f}")
                
                # 禁用输入但保留显示值
                self.target_lat_entry.config(state="disabled")
                self.target_lon_entry.config(state="disabled")
                self.target_confirm_button.config(state="disabled")
                
            except ValueError:
                messagebox.showerror("输入错误", "经纬度必须是有效的数字，以度为单位，纬度以N为正，经度以E为正")
                return
    
    def geo_to_gcrs(self, lat, lon, alt=0.0):
        """将地理坐标转换为GCRS坐标
        
        Args:
            lat: 纬度 (度)
            lon: 经度 (度)
            alt: 海拔 (米)
            
        Returns:
            list: GCRS坐标 [x, y, z] (千米)
        """
        # 转换为地心坐标系
        t = self.ts.utc(self.time_utc.year, self.time_utc.month, self.time_utc.day,
                        self.time_utc.hour, self.time_utc.minute, self.time_utc.second)
        
        # 创建地面位置
        topos = Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=alt)
        
        # 获取地面观测点
        location = self.earth + topos
        
        # 在特定时间获取位置
        position = location.at(t).position
        
        # 转换为 ICRS 坐标
        icrs_coords = skyfield_to_icrs(position)
        
        # 转换为 km 单位
        icrs_coords_km = convert_au_to_km(icrs_coords)
        
        # 转换为 GCRS 坐标
        gcrs_coords_km = icrs_to_gcrs(icrs_coords_km, t.utc_iso())
        
        # 返回GCRS坐标
        return [gcrs_coords_km.x.value, gcrs_coords_km.y.value, gcrs_coords_km.z.value]
    
    def check_same_position(self):
        """检查相机和观察点是否位于同一位置"""
        if self.camera_source is None or self.target_source is None:
            return False
        
        if self.camera_source.get("gcrs_coords") is None or self.target_source.get("gcrs_coords") is None:
            return False
        
        cam_coords = self.camera_source["gcrs_coords"]
        target_coords = self.target_source["gcrs_coords"]
        
        # 计算距离
        dist = math.sqrt((cam_coords[0] - target_coords[0])**2 + 
                         (cam_coords[1] - target_coords[1])**2 + 
                         (cam_coords[2] - target_coords[2])**2)
        
        # 如果距离小于0.5千米，认为是同一位置
        return dist < 0.5
    
    def check_earth_occlusion(self, point1, point2):
        """检查两点之间是否被地球遮挡
        
        Args:
            point1: 起点坐标 [x, y, z] (km)
            point2: 终点坐标 [x, y, z] (km)
            
        Returns:
            bool: True表示被遮挡，False表示未被遮挡
        """
        # 地球半径 (km)
        EARTH_RADIUS = 6340
        
        # 获取地球中心坐标
        t = self.ts.utc(self.time_utc.year, self.time_utc.month, self.time_utc.day,
                       self.time_utc.hour, self.time_utc.minute, self.time_utc.second)
        
        # 获取地球在GCRS中的位置
        earth_position = self.earth.at(t).position
        earth_icrs = skyfield_to_icrs(earth_position)
        earth_icrs_km = convert_au_to_km(earth_icrs)
        earth_gcrs_km = icrs_to_gcrs(earth_icrs_km, t.utc_iso())
        earth_center = np.array([earth_gcrs_km.x.value, earth_gcrs_km.y.value, earth_gcrs_km.z.value])
        
        print(f"地球中心GCRS坐标: {earth_center}")
        print(f"检查地球遮挡: 相机点={point1}, 目标点={point2}")
        
        # 将坐标转换为相对于地球中心的坐标
        p1 = np.array(point1) - earth_center
        p2 = np.array(point2) - earth_center
        
        # 计算视线向量
        d = p2 - p1
        d_len = np.linalg.norm(d)
        d_unit = d / d_len
        
        # 使用参数方程表示两点之间的连线: p = p1 + t * d_unit, 0 <= t <= d_len
        # 计算点到地心距离的最小值，确保仅在线段上寻找最小值
        
        # 计算t对应地心距离的最小值时的参数
        t_min = -np.dot(p1, d_unit)
        
        # 限制t在[0, d_len]范围内
        t_min = max(0, min(t_min, d_len))
        
        # 计算线段上距离地心最近的点
        p_min = p1 + t_min * d_unit
        
        # 计算该点到地心的距离
        min_dist = np.linalg.norm(p_min)
        
        print(f"相机与观察点连线上的最近点到地心的距离: {min_dist:.2f} km")
        print(f"地球半径(含大气层): {EARTH_RADIUS:.2f} km")
        
        # 如果最近点距离小于地球半径，说明视线被地球遮挡
        is_occluded = min_dist < EARTH_RADIUS
        
        if is_occluded:
            print("警告: 相机与观察点之间的视线被地球遮挡!")
        else:
            print("视线检查: 相机与观察点之间的视线未被地球遮挡。")
            
        return is_occluded

    def confirm_selection(self):
        """确认选择，添加更多异常处理"""
        try:
            # 检查是否选择了相机位置和观察点
            if self.camera_source is None:
                messagebox.showerror("选择错误", "请选择相机位置")
                return
            
            if self.target_source is None:
                messagebox.showerror("选择错误", "请选择观察点")
                return
            
            # 检查是否输入完成
            if self.camera_source.get("gcrs_coords") is None:
                messagebox.showerror("选择错误", "请完成相机位置输入")
                return
            
            if self.target_source.get("gcrs_coords") is None:
                messagebox.showerror("选择错误", "请完成观察点输入")
                return
            
            # 检查是否相同位置
            if self.check_same_position():
                messagebox.showerror("选择错误", "相机位置和观察点不能在同一位置")
                return
            
            # 检查是否被地球遮挡
            is_occluded = self.check_earth_occlusion(self.camera_source["gcrs_coords"], 
                                        self.target_source["gcrs_coords"])
            
            if is_occluded:
                # 如果被遮挡，弹出警告对话框，让用户选择是否继续
                result = messagebox.askyesno(
                    "警告", 
                    "相机位置和观察点之间被地球遮挡。是否仍要继续？\n\n继续可能导致渲染结果不理想。", 
                    icon='warning'
                )
                
                # 如果用户选择不继续，则返回
                if not result:
                    return
            
            # 设置结果
            self.result = {
                "camera": self.camera_source,
                "target": self.target_source
            }
            
            # 关闭窗口前确保清理所有Tkinter变量引用
            self.clean_up_variables()
            
            # 关闭窗口
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("选择错误", f"处理选择时发生错误: {str(e)}")
    
    def clean_up_variables(self):
        """清理所有Tkinter变量引用，避免线程问题"""
        try:
            # 清理相机输入变量
            if hasattr(self, 'camera_x_var'):
                self.camera_x_var.set("")
            if hasattr(self, 'camera_y_var'):
                self.camera_y_var.set("")
            if hasattr(self, 'camera_z_var'):
                self.camera_z_var.set("")
            if hasattr(self, 'camera_lat_var'):
                self.camera_lat_var.set("")
            if hasattr(self, 'camera_lon_var'):
                self.camera_lon_var.set("")
            
            # 清理目标输入变量
            if hasattr(self, 'target_x_var'):
                self.target_x_var.set("")
            if hasattr(self, 'target_y_var'):
                self.target_y_var.set("")
            if hasattr(self, 'target_z_var'):
                self.target_z_var.set("")
            if hasattr(self, 'target_lat_var'):
                self.target_lat_var.set("")
            if hasattr(self, 'target_lon_var'):
                self.target_lon_var.set("")
                
            # 移除所有变量的引用
            self.camera_x_var = None
            self.camera_y_var = None
            self.camera_z_var = None
            self.camera_lat_var = None
            self.camera_lon_var = None
            self.target_x_var = None
            self.target_y_var = None
            self.target_z_var = None
            self.target_lat_var = None
            self.target_lon_var = None
            
            # 显式删除所有UI元素的引用
            if hasattr(self, 'camera_listbox'):
                self.camera_listbox = None
            if hasattr(self, 'target_listbox'):
                self.target_listbox = None
            if hasattr(self, 'camera_confirm_button'):
                self.camera_confirm_button = None
            if hasattr(self, 'target_confirm_button'):
                self.target_confirm_button = None
            
            # 强制垃圾回收
            import gc
            gc.collect()
        except Exception as e:
            print(f"清理变量时发生错误: {str(e)}")

def select_camera_viewpoint(satellite_data, time_utc, earth, ts):
    """选择相机位置和观察点
    
    Args:
        satellite_data: 卫星数据字典，格式为 {sat_name: [gcrs_x, gcrs_y, gcrs_z]}
        time_utc: UTC时间对象
        earth: 地球天体对象
        ts: 时间尺度对象
        
    Returns:
        dict: 选择结果，包含 'camera' 和 'target' 两个键
              每个键对应的值是包含 'gcrs_coords' 键的字典
              'gcrs_coords' 是 [x, y, z] 格式的坐标 (单位: km)
              如果用户取消选择，返回 None
    """
    try:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 创建选择器
        selector = CameraViewpointSelector(root, satellite_data, time_utc, earth, ts)
        
        # 显示窗口
        root.deiconify()
        
        # 将焦点设置到新窗口
        root.focus_force()
        
        # 在mainloop之前记录result的默认值为None
        selector.result = None
        
        # 在主线程中运行mainloop
        root.mainloop()
        
        # 获取结果并保存到局部变量
        result = selector.result
        
        # 确保所有Tkinter相关资源被释放
        try:
            # 删除选择器对象中的root引用
            if hasattr(selector, 'root'):
                selector.root = None
                
            # 确保窗口已销毁
            if root and root.winfo_exists():
                root.quit()
                root.destroy()
                
            # 强制垃圾回收
            import gc
            gc.collect()
            
            # 确保tkinter资源完全释放
            import sys
            if '_tkinter' in sys.modules and hasattr(tk, '_default_root') and tk._default_root:
                tk._default_root = None
        except Exception:
            pass
        
        return result
    except Exception as e:
        messagebox.showerror("选择错误", f"选择相机位置和观察点时发生错误: {str(e)}")
        return None 