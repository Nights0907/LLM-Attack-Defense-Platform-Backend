import io
import logging
import sys

# 1. 禁用 Flask/Werkzeug 的日志写入文件，但允许控制台输出
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False  # 阻止传播到根日志记录器（避免写入文件）

# 2. 创建自定义日志记录器（只写入文件）
custom_logger = logging.getLogger("my_app_logger")
custom_logger.setLevel(logging.INFO)

# 3. 文件处理器（仅记录自定义日志）
file_handler = logging.FileHandler("app.log", mode="a")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
custom_logger.addHandler(file_handler)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码

# 记录日志的方法
def print_and_log(content):
    log_message(content)
    print(content, flush=True)


def log_message(content):

    file_stream = file_handler.stream
    file_stream.write(content)  # 写入到文件，不换行
    file_stream.flush()  # 强制刷新流


import os
import time

def generate_logs():
    file_path = 'app.log'

    # 初始定位到文件末尾（只读最新内容）
    with open(file_path, 'r') as f:
        f.seek(0, os.SEEK_END)
        last_position = f.tell()

    while True:
        try:
            with open(file_path, 'r') as f:
                f.seek(last_position)
                special_char = "ENTER"
                prev_char = None

                while True:
                    char = f.read(1)  # 逐字读取
                    if not char:  # 无新内容
                        break
                    if char == '\n':
                        yield f"data: {special_char}\n\n"
                    else:
                        yield f"data: {char}\n\n"

                    last_position = f.tell()

                # 处理文件末尾可能剩余的\r
                if prev_char:
                    yield f"data: {prev_char}\n\n"

            time.sleep(0.001)  # 极短的间隔（1ms）

        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"






