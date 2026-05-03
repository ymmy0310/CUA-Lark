# -*- coding: utf-8 -*-
"""配置管理器 - 保存和加载API配置"""

import json
import os

CONFIG_FILE = 'config_api.json'

# 常用API地址预设
API_PRESETS = {
    "火山引擎（豆包）": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    "自定义API": "",
}


def load_config():
    """从文件加载配置，如果不存在返回None"""
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  加载配置失败: {e}")
        return None


def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️  保存配置失败: {e}")
        return False


def is_configured():
    """检查是否已配置"""
    config = load_config()
    if not config:
        return False
    return (config.get('api_key') and 
            config.get('api_key') != 'ark-你的-API-Key-在这里' and
            config.get('endpoint_id') and
            config.get('endpoint_id') != 'ep-你的-接入点-ID-在这里')


def apply_config():
    """应用配置（更新 config.py 中的 AI_CONFIG）"""
    # 我们不在 config.py 中直接修改，而是让 ai_communicator.py 直接使用这个配置管理器
    # 这样更安全！
    return load_config()


def create_default_config():
    """创建默认配置"""
    return {
        "api_endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "api_key": "ark-你的-API-Key-在这里",
        "endpoint_id": "ep-你的-接入点-ID-在这里",
        "temperature": 0.1,
        "max_tokens": 2000,
    }
