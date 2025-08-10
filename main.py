import tkinter as tk
from network import load_model, load_sign_mapping, train_model, save_model, save_sign_mapping
from ui import SignLanguageDisplay
import serial
import time
import os
import numpy as np
import threading

SERIAL_PORT = '/dev/ttyS1'
BAUD_RATE = 9600
ser = None
last_sensor_data = None  # 存储最新的传感器数据
sensor_data_lock = threading.Lock()  # 用于线程安全的锁
send_enabled = True  # 控制发送是否启用

def init_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"串口已连接: {SERIAL_PORT} @ {BAUD_RATE} bps")
        return True
    except Exception as e:
        print(f"串口连接失败: {str(e)}")
        return False

def read_serial_data():
    """从串口读取传感器数据，只返回最新数据"""
    global last_sensor_data
    if ser is None:
        if not init_serial():
            return None
    
    try:
        # 读取所有可用的行，只保留最后一行
        while ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line:
                values = line.split(',')
                if len(values) == 5:
                    # 只取后4个值(A1-A4)，忽略A0
                    sensor_data = [int(val) for val in values[1:]]
                    with sensor_data_lock:
                        last_sensor_data = sensor_data
                    return sensor_data
        
        # 如果没有新数据，返回上次读取的数据
        with sensor_data_lock:
            return last_sensor_data
    except Exception as e:
        print(f"读取串口数据错误: {str(e)}")
        return None

def transform_sensor_values(sensor_data):
    """将原始ADC值转换为舵机控制值（根据拟合公式）"""
    if sensor_data is None or len(sensor_data) < 4:
        return None
    
    # 原始ADC值
    a1, a2, a3, a4 = sensor_data
    
    # 应用拟合公式转换
    # 通道1 (A1): y = 4.5x - 440
    
    transformed_a1 = int(-3.9130 * a1 +3073.913)
    
    # 通道2 (A2): y = 1.9565x + 373.913
    transformed_a2 = int(-2 * a2 + 2500)
    
    # 通道3 (A3): y = 2.8125x + 100
    transformed_a3 = int(-3.333 * a3 + 2866.667)
    
    # 通道4 (A4): y = -1.2784x + 2310.088
    transformed_a4 = int(1.4286 * a4 + 514.286)
    
    # 确保值在有效范围内 (1000-1900)
    transformed_a1 = max(1000, min(1900, transformed_a1))
    transformed_a2 = max(1000, min(1900, transformed_a2))
    transformed_a3 = max(1000, min(1900, transformed_a3))
    transformed_a4 = max(1000, min(1900, transformed_a4))
    
    return [transformed_a1, transformed_a2, transformed_a3, transformed_a4]

def format_sensor_data(sensor_data):
    """格式化传感器数据为协议帧:
       A5 5A 0A + [5x uint16 小端序] + SUM8(payload)
       顺序: A4, A3, A2, A0(与A2相同), A1
    """
    if sensor_data is None or len(sensor_data) < 4:
        return None

    # 提取转换后的值
    transformed_a1, transformed_a2, transformed_a3, transformed_a4 = sensor_data
    
    # 按顺序创建值列表: A4, A3, A2, A0(等于A2), A1
    values = [
        transformed_a4,  # A4
        transformed_a3,  # A3
        transformed_a2,  # A2
        transformed_a2,  # A0 (与A2相同)
        transformed_a1   # A1
    ]

    # 帧头
    frame = bytearray([0xA5, 0x5A, 0x0A])

    # 负载（10字节）：每个uint16"小端序"：低字节在前，高字节在后
    payload = bytearray()
    for v in values:
        # 确保值在0-65535范围内
        v = max(0, min(int(v), 65535))
        # 小端序：先低字节，后高字节
        payload.append(v & 0xFF)        # 低8位
        payload.append((v >> 8) & 0xFF) # 高8位

    # SUM8：对10个负载字节求和，取低8位
    sum8 = sum(payload) & 0xFF

    # 组帧：帧头 + 负载 + 校验
    frame += payload
    frame.append(sum8)

    return bytes(frame)

def send_sensor_data():
    """定时发送传感器数据到串口（十六进制格式）"""
    global ser, last_sensor_data, send_enabled
    
    if not send_enabled:
        # 800ms后再次尝试
        threading.Timer(0.8, send_sensor_data).start()
        return
    
    if ser is None:
        if not init_serial():
            # 800ms后再次尝试
            threading.Timer(0.8, send_sensor_data).start()
            return
    
    try:
        # 获取最新的传感器数据
        with sensor_data_lock:
            sensor_data = last_sensor_data
        
        if sensor_data is None:
            # 800ms后再次尝试
            threading.Timer(0.8, send_sensor_data).start()
            return
        
        # 转换原始ADC值为舵机控制值
        transformed_data = transform_sensor_values(sensor_data)
        
        # 格式化数据为十六进制字节流
        hex_data = format_sensor_data(transformed_data)
        if hex_data is None:
            # 800ms后再次尝试
            threading.Timer(0.8, send_sensor_data).start()
            return
        
        # 发送十六进制数据
        ser.write(hex_data)
        print(f"已发送传感器数据: {hex_data.hex().upper()}")
    except Exception as e:
        print(f"发送传感器数据失败: {str(e)}")
    
    # 800ms后再次发送
    threading.Timer(0.8, send_sensor_data).start()

def main():
    global ser, send_enabled
    model_file = 'model.joblib'
    mapping_file = 'sign_mapping.json'
    
    if not os.path.exists(model_file) or not os.path.exists(mapping_file):
        print("训练模型...")
        model, sign_mapping = train_model()
        save_model(model, model_file)
        save_sign_mapping(sign_mapping, mapping_file)
        print("模型训练完成并已保存")
    else:
        print("加载现有模型...")
        model = load_model(model_file)
        sign_mapping = load_sign_mapping(mapping_file)
    
    # 初始化串口
    init_serial()
    
    # 启动传感器数据发送线程
    threading.Timer(0.8, send_sensor_data).start()
    
    root = tk.Tk()
    app = SignLanguageDisplay(root, model, sign_mapping, read_serial_data, None)
    root.mainloop()
    
    # 停止发送
    send_enabled = False
    
    if ser and ser.is_open:
        ser.close()

if __name__ == "__main__":
    main()