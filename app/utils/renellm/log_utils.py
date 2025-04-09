import logging
import os
import time

logging.getLogger('werkzeug').disabled = True  # 禁用 Flask 默认的日志输出
logging.getLogger().handlers = []  # 清空所有日志处理器（不记录控制台输出）

# 配置 logging，记录到文件
file_handler = logging.FileHandler('app.log', mode='a')
file_handler.setFormatter(logging.Formatter('%(message)s'))  # 只输出消息，不加时间戳等
logging.getLogger().addHandler(file_handler)
logging.basicConfig(level=logging.INFO)  # 设置日志级别


# 记录日志的方法
def print_and_log(content):
    print(content)
    log_message(content,False)

def log_message(content, is_stream=False):
    """
    记录日志。根据 is_stream 决定是否换行。
    is_stream=True 表示流式输出，不换行
    """
    file_stream = file_handler.stream
    # 如果是流式输出，不加换行符
    if is_stream:
        file_stream.write(content)  # 写入到文件，不换行
    else:
        file_stream.write(content + '\n')  # 普通日志，添加换行符
    file_stream.flush()  # 强制刷新流

# 实时返回日志流

def generate_logs():
    """实时监控文件变化（包括行内更新）"""
    file_path = 'app.log'
    last_size = 0
    last_position = 0

    while True:
        current_size = os.path.getsize(file_path)
        # 文件大小发生变化（新增内容或被覆盖）
        if current_size != last_size:
            with open(file_path, 'r') as f:
                # 定位到上次读取位置
                if current_size >= last_size:  # 文件增大（追加模式）
                    f.seek(last_position)
                    new_content = f.read()
                    last_position = f.tell()
                else:  # 文件变小（被清空或覆盖）
                    f.seek(0)
                    new_content = f.read()
                    last_position = len(new_content)
                if new_content:
                    yield f"data: {new_content}\n\n"
            last_size = current_size
        else:
            yield ":heartbeat:\n\n"  # 保持连接的心跳包

        time.sleep(0.1)  # 检测间隔

