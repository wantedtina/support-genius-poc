import yaml
import json


def load_config(path):
    """
    根据文件扩展名加载YAML或JSON配置文件。

    :param path: 配置文件的路径
    :return: 配置数据（字典格式）
    """
    if path.endswith('.yaml') or path.endswith('.yml'):
        with open(path, 'r', encoding='utf-8') as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    elif path.endswith('.json'):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        raise ValueError("Unsupported configuration file format. Please use YAML or JSON.")

