import yaml

# 读取settings.yaml配置
with open('settings.yaml', 'r') as file:
    settings = yaml.safe_load(file)