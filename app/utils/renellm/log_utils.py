import json
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
    log_message(content)
    # print(content, flush=True)


def log_message(content,is_stream = True):

    file_stream = file_handler.stream
    if is_stream:
        file_stream.write(content)  # 写入到文件，不换行
    else:
        file_stream.write(content)  # 写入到文件，不换行
    file_stream.flush()  # 强制刷新流


import os
import time

#
# def generate_logs():
#     file_path = 'app.log'
#
#     # 初始定位到文件末尾（只读最新内容）
#     with open(file_path, 'r') as f:
#         f.seek(0, os.SEEK_END)
#         last_position = f.tell()
#
#     while True:
#         try:
#             with open(file_path, 'r') as f:
#                 f.seek(last_position)
#                 while True:
#                     char = f.read(1)  # 逐字读取
#                     if not char:  # 无新内容
#                         break
#                     yield f"data: {char}\n\n"  # 每个字符作为独立事件推送
#                     last_position = f.tell()
#             time.sleep(0.001)  # 极短的间隔（1ms）
#         except Exception as e:
#             yield f"data: Error: {str(e)}\n\n"

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