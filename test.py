import serial
import time
import threading

# 配置串口参数
SERIAL_PORT = '/dev/ttyS1'  # 根据实际情况修改串口
BAUD_RATE = 9600
TIMEOUT = 1
SEND_INTERVAL = 0.8  # 发送间隔，单位：秒

# 要发送的固定十六进制数据 (原始数据)
# 对应: A5 5A 0A DC 05 40 06 A4 06 6C 07 D0 07 1B
BASE_HEX_DATA = [
    0xA5, 0x5A, 0x0A, 0xDC, 
    0x05, 0x40, 0x06, 0xA4, 
    0x06, 0x6C, 0x07, 0xD0, 
    0x07, 0x1B
]

# 添加常见的串口结束符 (回车\r + 换行\n)
# 对应十六进制: 0x0D (CR) 和 0x0A (LF)
TERMINATOR = [0x0D, 0x0A]

# 组合数据和结束符，转换为字节对象
SEND_DATA = bytes(BASE_HEX_DATA + TERMINATOR)

# 全局变量
ser = None
running = True

def init_serial():
    """初始化串口连接"""
    global ser
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=TIMEOUT
        )
        if ser.is_open:
            print(f"成功连接到串口: {SERIAL_PORT} @ {BAUD_RATE} bps")
            return True
        return False
    except Exception as e:
        print(f"串口初始化失败: {str(e)}")
        return False

def send_data():
    """发送带结束符的十六进制数据到STM32"""
    global ser, running
    
    while running:
        if ser is None or not ser.is_open:
            # 尝试重新连接
            if not init_serial():
                time.sleep(SEND_INTERVAL)
                continue
        
        try:
            # 直接发送字节数据（包含结束符）
            bytes_sent = ser.write(SEND_DATA)
            # 打印发送的十六进制数据（包含结束符），便于调试
            hex_str = ' '.join(f'{b:02X}' for b in SEND_DATA)
            print(f"发送数据 ({bytes_sent} 字节): {hex_str}")
        except Exception as e:
            print(f"发送数据失败: {str(e)}")
            # 发送失败时尝试重新连接
            if ser and ser.is_open:
                ser.close()
            ser = None
        
        # 等待下一次发送
        time.sleep(SEND_INTERVAL)

def main():
    global running
    
    print("STM32带结束符的十六进制串口通信程序启动...")
    print(f"目标串口: {SERIAL_PORT}")
    print(f"波特率: {BAUD_RATE}")
    print(f"发送间隔: {SEND_INTERVAL}秒")
    print(f"发送数据 (含结束符): {''.join(f'{b:02X}' for b in SEND_DATA)}")
    print("结束符: 0x0D (CR) 和 0x0A (LF)")
    print("按Ctrl+C退出程序")
    
    # 启动发送线程
    send_thread = threading.Thread(target=send_data, daemon=True)
    send_thread.start()
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序正在退出...")
        running = False
        send_thread.join()
        
        # 关闭串口
        if ser and ser.is_open:
            ser.close()
            print("串口已关闭")
        print("程序已退出")

if __name__ == "__main__":
    main()
    