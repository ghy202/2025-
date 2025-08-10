import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import time

class SignLanguageDisplay:
    def __init__(self, root, model, sign_mapping, data_provider, gesture_sender):
        self.root = root
        self.root.title("TCF-BO-RF手语翻译系统")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        self.last_sign = None
        self.current_sequence = ""
        self.model = model
        self.sign_mapping = sign_mapping
        self.data_provider = data_provider
        self.gesture_sender = gesture_sender
        self.sensor_values = [0, 0, 0, 0]
        self.last_update_time = time.time()

        # 字体设置
        self.base_font = self._get_compatible_font()
        self.title_font = (self.base_font[0], 28, "bold")
        self.sign_font = (self.base_font[0], 48, "bold")
        self.sequence_font = (self.base_font[0], 24)
        self.info_font = (self.base_font[0], 12)
        self.status_font = (self.base_font[0], 10)

        # 颜色方案
        self.background_color = "#f0f7ff"
        self.sign_box_color = "#e6f2ff"
        self.box_border_color = "#3399ff"
        self.button_color = "#4da6ff"
        self.status_color = "#0066cc"
        self.warning_color = "#ff5500"

        # 创建UI
        self._create_widgets()
        
        # 启动实时更新
        self.update_interval = 100
        self.schedule_update()

    def _get_compatible_font(self):
        preferred_fonts = ["WenQuanYi Micro Hei", "SimHei", "Heiti TC", "Arial"]
        available_fonts = font.families()

        for font_name in preferred_fonts:
            if font_name in available_fonts:
                return font_name
        return "Arial"

    def _create_widgets(self):
        self.root.configure(bg=self.background_color)
        
        # 标题栏
        title_frame = tk.Frame(self.root, bg=self.background_color, padx=10, pady=5)
        title_frame.pack(fill=tk.X)
        
        self.title_label = tk.Label(
            title_frame,
            text="手语翻译系统",
            font=self.title_font,
            bg=self.background_color,
            fg="#0066cc",
            padx=10
        )
        self.title_label.pack(side=tk.LEFT)
        
        # 状态指示器
        self.status_label = tk.Label(
            title_frame,
            text="状态: 等待数据...",
            font=self.info_font,
            bg=self.background_color,
            fg=self.status_color,
            padx=10
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # 性能监控标签
        self.perf_label = tk.Label(
            title_frame,
            text="处理时间: 0ms",
            font=self.status_font,
            bg=self.background_color,
            fg="#666666",
            padx=5
        )
        self.perf_label.pack(side=tk.RIGHT)

        # 主显示区 - 优化布局
        main_frame = tk.Frame(self.root, bg=self.background_color, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 当前手势显示 - 扩大显示区域
        sign_frame = tk.LabelFrame(
            main_frame,
            text="当前识别手势",
            font=(self.base_font, 14),
            bg=self.background_color,
            fg="#0066cc",
            padx=10,
            pady=10
        )
        sign_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.sign_canvas = tk.Canvas(
            sign_frame,
            bg=self.sign_box_color,
            highlightthickness=1,
            highlightbackground=self.box_border_color,
            relief=tk.FLAT
        )
        self.sign_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sign_text = self.sign_canvas.create_text(
            300, 150,
            text="等待识别...",
            font=self.sign_font,
            fill="#003366",
            anchor=tk.CENTER
        )

        # 序列显示区 - 上移并扩大
        sequence_frame = tk.LabelFrame(
            main_frame,
            text="语句序列",
            font=(self.base_font, 14),
            bg=self.background_color,
            fg="#0066cc",
            padx=10,
            pady=10
        )
        sequence_frame.pack(fill=tk.X, pady=5)
        
        self.current_sequence_var = tk.StringVar(value="")
        self.sequence_display = tk.Label(
            sequence_frame,
            textvariable=self.current_sequence_var,
            font=self.sequence_font,
            bg="#ffffff",
            fg="#003366",
            relief=tk.SUNKEN,
            padx=10,
            pady=10,
            width=30,
            anchor=tk.W
        )
        self.sequence_display.pack(fill=tk.X, padx=5, pady=5)

        # 控制按钮区
        control_frame = tk.Frame(self.root, bg=self.background_color, padx=20, pady=10)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(
            control_frame,
            text="清空序列",
            command=self.clear_sequence,
            width=15,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            control_frame,
            text="保存语句",
            command=self.save_sequence,
            width=15,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        style = ttk.Style()
        style.configure(
            "TButton", 
            foreground="#ffffff", 
            background=self.button_color,
            font=(self.base_font, 12),
            padding=5
        )

    def schedule_update(self):
        self.update_display()
        self.root.after(self.update_interval, self.schedule_update)

    def update_display(self):
        start_time = time.time()
        try:
            # 获取传感器数据
            sensor_data = self.data_provider()
            if sensor_data is None:
                self.status_label.config(text="状态: 等待串口数据...", fg="orange")
                return
            
            # 使用模型进行预测
            gesture_id = self.model.predict([sensor_data])[0]
            gesture_name = self.sign_mapping.get(str(gesture_id), f"未知手势({gesture_id})")
            
            # 更新手势显示
            self.update_sign_display(gesture_name)
            
            # 更新序列
            self.update_sequence(gesture_name)
            
            # 更新状态
            self.status_label.config(
                text=f"状态: 识别成功 - {gesture_name} (ID: {gesture_id})",
                fg="green"
            )
            
        except Exception as e:
            self.status_label.config(
                text=f"状态: 错误 - {str(e)}",
                fg="red"
            )
        
        # 计算处理时间并更新性能标签
        processing_time = (time.time() - start_time) * 1000
        self.perf_label.config(text=f"处理时间: {processing_time:.1f}ms")
        
        # 动态调整更新间隔
        if processing_time > 50:
            self.update_interval = max(100, int(processing_time * 1.2))
        else:
            self.update_interval = 100

    def update_sign_display(self, sign_text):
        self.sign_canvas.itemconfig(self.sign_text, text=sign_text)
        
        canvas_width = self.sign_canvas.winfo_width()
        canvas_height = self.sign_canvas.winfo_height()
        if canvas_width > 1 and canvas_height > 1:
            self.sign_canvas.coords(self.sign_text, canvas_width/2, canvas_height/2)

    def update_sequence(self, new_sign):
        if new_sign == self.last_sign:
            self.current_sequence = new_sign
        else:
            if self.current_sequence:
                self.current_sequence += " → " + new_sign
            else:
                self.current_sequence = new_sign
        
        self.current_sequence_var.set(self.current_sequence)
        self.last_sign = new_sign

    def clear_sequence(self):
        self.current_sequence = ""
        self.current_sequence_var.set("")
        self.last_sign = None
        self.sign_canvas.itemconfig(self.sign_text, text="等待识别...")
        self.status_label.config(text="状态: 序列已清空", fg="blue")

    def save_sequence(self):
        if self.current_sequence:
            try:
                with open("output.txt", "a", encoding="utf-8") as f:
                    f.write(self.current_sequence + "\n")
                self.status_label.config(text="状态: 序列已保存到 output.txt", fg="blue")
            except Exception as e:
                self.status_label.config(text=f"状态: 保存失败 - {str(e)}", fg="red")
        else:
            self.status_label.config(text="状态: 无法保存空序列", fg="orange")