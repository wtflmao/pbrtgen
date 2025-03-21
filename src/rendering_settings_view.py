import tkinter as tk
from tkinter import ttk, messagebox
import gc

class RenderingSettingsView:
    """渲染设置视图类，用于配置PBRT渲染参数"""
    
    def __init__(self, root=None):
        """初始化渲染设置视图
        
        Args:
            root: Tkinter根窗口，如果为None则创建新窗口
        """
        # 使用传入的root或创建一个新的Toplevel窗口
        if root is None or (not isinstance(root, tk.Tk) and not isinstance(root, tk.Toplevel)):
            self.own_root = True
            self.parent = tk.Tk()
            self.parent.withdraw()  # 隐藏主窗口
            self.root = tk.Toplevel(self.parent)
        else:
            self.own_root = False
            self.parent = root
            self.root = tk.Toplevel(root)
            
        self.root.title("渲染设置")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 使窗口显示在前台
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        
        # 设置默认值
        self.fov = tk.DoubleVar(value=60.0)
        self.resolution_x = tk.IntVar(value=1366)
        self.resolution_y = tk.IntVar(value=768)
        self.pixel_samples = tk.IntVar(value=64)
        self.max_depth = tk.IntVar(value=5)
        
        # 存储结果
        self.result = None
        
        # 创建UI
        self.create_ui()
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标题
        title_label = ttk.Label(main_frame, text="渲染设置", font=("Arial", 16))
        title_label.pack(pady=(0, 20))
        
        # 设置框架
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # 视场角设置
        fov_frame = ttk.Frame(settings_frame)
        fov_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(fov_frame, text="视场角 (FOV):", width=20).pack(side=tk.LEFT)
        fov_scale = ttk.Scale(
            fov_frame, 
            from_=0.01, 
            to=170.0, 
            variable=self.fov, 
            orient=tk.HORIZONTAL,
            length=200
        )
        fov_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        fov_entry = ttk.Entry(fov_frame, textvariable=self.fov, width=6)
        fov_entry.pack(side=tk.LEFT)
        ttk.Label(fov_frame, text="度").pack(side=tk.LEFT)
        
        # 分辨率设置
        resolution_frame = ttk.LabelFrame(settings_frame, text="渲染分辨率")
        resolution_frame.pack(fill=tk.X, pady=10)
        
        # X分辨率
        ttk.Label(resolution_frame, text="宽度:").grid(row=0, column=0, padx=5, pady=5)
        resolution_x_entry = ttk.Entry(resolution_frame, textvariable=self.resolution_x, width=8)
        resolution_x_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(resolution_frame, text="像素").grid(row=0, column=2, padx=5, pady=5)
        
        # Y分辨率
        ttk.Label(resolution_frame, text="高度:").grid(row=0, column=3, padx=5, pady=5)
        resolution_y_entry = ttk.Entry(resolution_frame, textvariable=self.resolution_y, width=8)
        resolution_y_entry.grid(row=0, column=4, padx=5, pady=5)
        ttk.Label(resolution_frame, text="像素").grid(row=0, column=5, padx=5, pady=5)
        
        # 常用分辨率快速选择
        resolution_buttons_frame = ttk.Frame(resolution_frame)
        resolution_buttons_frame.grid(row=1, column=0, columnspan=6, pady=5)
        
        ttk.Button(resolution_buttons_frame, text="SD (640x480)", 
                 command=lambda: self.set_resolution(1366, 768)).pack(side=tk.LEFT, padx=5)
        ttk.Button(resolution_buttons_frame, text="HD (1366x768)", 
                 command=lambda: self.set_resolution(1366, 768)).pack(side=tk.LEFT, padx=5)
        ttk.Button(resolution_buttons_frame, text="FHD (1920x1080)", 
                 command=lambda: self.set_resolution(1920, 1080)).pack(side=tk.LEFT, padx=5)
        ttk.Button(resolution_buttons_frame, text="4K (3840x2160)", 
                 command=lambda: self.set_resolution(3840, 2160)).pack(side=tk.LEFT, padx=5)
        ttk.Button(resolution_buttons_frame, text="1:1 (800x800)", 
                 command=lambda: self.set_resolution(800, 800)).pack(side=tk.LEFT, padx=5)
        ttk.Button(resolution_buttons_frame, text="1:1 (1600*1600)", 
                 command=lambda: self.set_resolution(1600, 1600)).pack(side=tk.LEFT, padx=5)
        
        # 采样设置
        sampling_frame = ttk.LabelFrame(settings_frame, text="采样设置")
        sampling_frame.pack(fill=tk.X, pady=10)
        
        # 像素采样次数
        ttk.Label(sampling_frame, text="像素采样次数:").grid(row=0, column=0, padx=5, pady=5)
        pixel_samples_spinbox = ttk.Spinbox(
            sampling_frame, 
            from_=4, 
            to=2048, 
            textvariable=self.pixel_samples,
            width=8,
            increment=4
        )
        pixel_samples_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        # 快速预设按钮
        ttk.Button(sampling_frame, text="低 (16)", 
                 command=lambda: self.pixel_samples.set(16)).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(sampling_frame, text="中 (64)", 
                 command=lambda: self.pixel_samples.set(64)).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(sampling_frame, text="高 (256)", 
                 command=lambda: self.pixel_samples.set(256)).grid(row=0, column=4, padx=5, pady=5)
        
        # 最大反射次数
        ttk.Label(sampling_frame, text="最大反射次数:").grid(row=1, column=0, padx=5, pady=5)
        max_depth_spinbox = ttk.Spinbox(
            sampling_frame, 
            from_=1, 
            to=20, 
            textvariable=self.max_depth,
            width=8
        )
        max_depth_spinbox.grid(row=1, column=1, padx=5, pady=5)
        
        # 预设按钮
        ttk.Button(sampling_frame, text="低 (3)", 
                 command=lambda: self.max_depth.set(3)).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(sampling_frame, text="中 (5)", 
                 command=lambda: self.max_depth.set(5)).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(sampling_frame, text="高 (16)", 
                 command=lambda: self.max_depth.set(16)).grid(row=1, column=4, padx=5, pady=5)
        
        # 性能提示
        warning_label = ttk.Label(
            settings_frame, 
            text="注意: 高分辨率、高采样次数和高反射次数会显著增加渲染时间", 
            foreground="red"
        )
        warning_label.pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # 确认按钮
        confirm_button = ttk.Button(button_frame, text="确认", command=self.confirm)
        confirm_button.pack(side=tk.RIGHT, padx=5)
    
    def set_resolution(self, x, y):
        """设置分辨率
        
        Args:
            x: 宽度分辨率
            y: 高度分辨率
        """
        self.resolution_x.set(x)
        self.resolution_y.set(y)
    
    def cancel(self):
        """取消设置，关闭窗口"""
        self.result = None
        self.clean_up_variables()
        self.root.destroy()
    
    def confirm(self):
        """确认设置，保存结果并关闭窗口"""
        try:
            # 验证输入
            fov = float(self.fov.get())
            resolution_x = int(self.resolution_x.get())
            resolution_y = int(self.resolution_y.get())
            pixel_samples = int(self.pixel_samples.get())
            max_depth = int(self.max_depth.get())
            
            # 验证值范围
            if fov < 20.0 or fov > 120.0:
                messagebox.showerror("输入错误", "视场角应在20到120度之间")
                return
            
            if resolution_x < 100 or resolution_x > 10000:
                messagebox.showerror("输入错误", "宽度分辨率应在100到10000之间")
                return
                
            if resolution_y < 100 or resolution_y > 10000:
                messagebox.showerror("输入错误", "高度分辨率应在100到10000之间")
                return
            
            if pixel_samples < 4 or pixel_samples > 2048:
                messagebox.showerror("输入错误", "像素采样次数应在4到2048之间")
                return
                
            if max_depth < 1 or max_depth > 20:
                messagebox.showerror("输入错误", "最大反射次数应在1到20之间")
                return
            
            # 保存结果
            self.result = {
                "fov": fov,
                "resolution_x": resolution_x,
                "resolution_y": resolution_y,
                "pixel_samples": pixel_samples,
                "max_depth": max_depth
            }
            
            # 清理变量并关闭窗口
            self.clean_up_variables()
            self.root.destroy()
            
        except ValueError as e:
            messagebox.showerror("输入错误", f"请输入有效的数值: {str(e)}")
    
    def clean_up_variables(self):
        """清理tkinter变量引用，避免内存泄漏和线程问题"""
        try:
            # 清理变量引用
            self.fov = None
            self.resolution_x = None
            self.resolution_y = None
            self.pixel_samples = None
            self.max_depth = None
            
            # 释放grab，避免其他窗口无法获取焦点
            try:
                self.root.grab_release()
            except:
                pass
            
            # 如果是自己创建的窗口，清理父窗口
            if self.own_root and hasattr(self, 'parent') and self.parent:
                try:
                    self.parent.destroy()
                except:
                    pass
            
            # 强制垃圾回收
            gc.collect()
            gc.collect()
            
        except Exception as e:
            print(f"清理渲染设置视图资源时出错: {e}")
            # 错误不影响主程序运行
    
    def show(self):
        """显示窗口并返回结果
        
        Returns:
            dict: 包含渲染设置的字典，如果用户取消则返回None
        """
        # 确保窗口显示在前台
        self.root.deiconify()
        self.root.focus_force()
        self.root.lift()
        self.root.grab_set()  # 模态对话框
        
        # 如果使用自己创建的root，等待窗口关闭
        if self.own_root:
            self.parent.wait_window(self.root)
        else:
            self.root.wait_window()
        
        # 返回结果
        return self.result

def get_rendering_settings():
    """获取渲染设置
    
    Returns:
        dict: 包含渲染设置的字典，如果用户取消则返回None
    """
    try:
        # 创建设置视图
        settings_view = RenderingSettingsView(None)
        
        # 显示窗口并获取结果
        result = settings_view.show()
        
        return result
    except Exception as e:
        messagebox.showerror("错误", f"获取渲染设置时发生错误: {str(e)}")
        return None 