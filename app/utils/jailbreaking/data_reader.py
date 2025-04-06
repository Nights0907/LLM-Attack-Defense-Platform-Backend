import csv

def data_reader(file_path):
    # 假设文件名为 data.csv
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # 自动读取表头
        goals = []
        targets = []
        for row in reader:
            goals.append(row['goal'])          # 提取 goal 列
            targets.append(row['target'])      # 提取 target 列
    return goals,targets