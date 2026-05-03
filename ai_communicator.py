# -*- coding: utf-8 -*-
import requests
import base64
import json
import os
import time
from typing import Dict, Optional
from config import SYSTEM_PROMPT, TASK_PLANNING_PROMPT, TASK_UNDERSTANDING_PROMPT
import config_manager


def call_api_with_retry(api_func, max_retries=5):
    """
    为API调用增加指数退避重试机制的装饰器/封装函数
    :param api_func: 实际发送请求的函数，返回response对象
    :param max_retries: 最大重试次数
    """
    for attempt in range(max_retries):
        response = api_func()  # 这里执行你的 requests.post 逻辑
        if response.status_code != 429:
            return response  # 如果不是限流错误，直接返回
        
        # 计算等待时间： 2^attempt 秒，并加上一点随机抖动，避免所有重试同时爆发
        wait_time = (2 ** attempt) + (attempt * 0.1)
        print(f"⚠️ 触发限流 (429)，等待 {wait_time:.1f} 秒后进行第 {attempt + 1} 次重试...")
        time.sleep(wait_time)
    
    print("❌ 重试次数已用完，请求最终失败。")
    return None  # 或者抛出异常


def get_ai_config():
    """获取AI配置，优先使用配置管理器中的配置"""
    config = config_manager.load_config()
    if config:
        return config
    # 如果没有配置文件，回退到config.py
    from config import AI_CONFIG
    return AI_CONFIG


def encode_image_to_base64(image_path: str) -> str:
    """将图片编码为base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def send_to_ai(user_task: str, screenshot_path: str, screen_w: int, screen_h: int, conversation_history: list = None) -> Dict:
    """
    发送任务和截图给AI，返回JSON指令
    
    :param user_task: 用户任务描述
    :param screenshot_path: 截图文件路径
    :param screen_w: 屏幕宽度
    :param screen_h: 屏幕高度
    :param conversation_history: 对话历史（可选）
    :return: AI返回的JSON指令
    """
    # 获取配置
    config = get_ai_config()
    
    # 编码截图为base64
    image_base64 = encode_image_to_base64(screenshot_path)
    
    # 构建消息
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    
    # 添加对话历史
    if conversation_history:
        messages.extend(conversation_history)
    
    # 添加当前任务和截图，包含屏幕尺寸（火山方舟格式）
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": f"用户任务：{user_task}\n\n【屏幕尺寸：{screen_w}x{screen_h}】\n\n请根据当前屏幕截图，决定下一步操作。"},
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            }
        ]
    })
    
    # 构建API请求
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {config['api_key']}"
    }
    
    payload = {
        "model": config['endpoint_id'],
        "messages": messages,
        "temperature": config['temperature'],
        "max_tokens": config['max_tokens']
    }
    
    try:
        # 发送请求
        print(f"🚀 正在发送请求到AI...")
        print(f"📤 API地址: {config['api_endpoint']}")
        print(f"📤 接入点ID: {config['endpoint_id']}")
        print(f"📤 消息长度: {len(str(payload))}")
        
        # 使用指数退避重试机制发送请求
        def make_request():
            return requests.post(config['api_endpoint'], headers=headers, json=payload)
        
        response = call_api_with_retry(make_request)
        if response is None:
            raise Exception("API请求失败，重试次数已用完")
        
        # 详细的响应信息
        print(f"📥 响应状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"📥 响应内容: {response.text}")
        
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # 尝试解析为JSON
        try:
            command = json.loads(ai_response)
            print(f"✅ 收到AI指令: {json.dumps(command, ensure_ascii=False)}")
            return command
        except json.JSONDecodeError:
            print(f"⚠️  AI返回的不是有效JSON: {ai_response}")
            # 如果AI返回了Markdown格式，尝试提取JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                try:
                    command = json.loads(json_match.group())
                    print(f"✅ 从响应中提取到JSON: {json.dumps(command, ensure_ascii=False)}")
                    return command
                except:
                    pass
            raise ValueError("无法解析AI返回的JSON")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        raise
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        raise


def plan_task(task: str) -> Optional[list]:
    """
    使用AI规划任务步骤
    
    :param task: 用户任务描述
    :return: 任务步骤列表，失败返回None
    """
    # 获取配置
    config = get_ai_config()
    
    print(f"📋 开始任务规划: {task}")
    
    # 构建消息
    messages = [
        {"role": "system", "content": TASK_PLANNING_PROMPT.format(task=task)},
    ]
    
    # 构建API请求
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {config['api_key']}"
    }
    
    payload = {
        "model": config['endpoint_id'],
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    try:
        # 使用指数退避重试机制发送请求
        def make_request():
            return requests.post(config['api_endpoint'], headers=headers, json=payload)
        
        response = call_api_with_retry(make_request)
        if response is None:
            print("❌ 任务规划请求失败，重试次数已用完")
            return None
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # 尝试解析为JSON
        try:
            plan_data = json.loads(ai_response)
            if "plan" in plan_data and isinstance(plan_data["plan"], list):
                print(f"✅ 任务规划完成，共 {len(plan_data['plan'])} 个步骤")
                for i, step in enumerate(plan_data['plan'], 1):
                    print(f"  {i}. {step}")
                return plan_data["plan"]
        except json.JSONDecodeError:
            print(f"⚠️  AI返回的不是有效JSON，尝试提取...")
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                try:
                    plan_data = json.loads(json_match.group())
                    if "plan" in plan_data and isinstance(plan_data["plan"], list):
                        print(f"✅ 任务规划完成，共 {len(plan_data['plan'])} 个步骤")
                        for i, step in enumerate(plan_data['plan'], 1):
                            print(f"  {i}. {step}")
                        return plan_data["plan"]
                except:
                    pass
        
        print(f"⚠️  无法解析任务规划，跳过规划阶段")
        return None
            
    except Exception as e:
        print(f"❌ 任务规划失败: {e}")
        return None


def understand_task(task: str) -> Optional[dict]:
    """
    使用AI理解任务，分析信息完整性，返回理解结果
    
    :param task: 用户任务描述
    :return: 理解结果字典，包含 understanding, task_type, required_info, 
             provided_info, missing_info, plan_summary, is_complete, suggestion
             失败返回None
    """
    # 获取配置
    config = get_ai_config()
    
    print(f"🧠 开始任务理解分析: {task}")
    
    # 构建消息
    messages = [
        {"role": "system", "content": TASK_UNDERSTANDING_PROMPT.format(task=task)},
    ]
    
    # 构建API请求
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {config['api_key']}"
    }
    
    payload = {
        "model": config['endpoint_id'],
        "messages": messages,
        "temperature": 0.1,  # 低温确保稳定性
        "max_tokens": 1500
    }
    
    try:
        # 使用指数退避重试机制发送请求
        def make_request():
            return requests.post(config['api_endpoint'], headers=headers, json=payload)
        
        response = call_api_with_retry(make_request)
        if response is None:
            print("❌ 任务理解请求失败，重试次数已用完")
            return None
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # 尝试解析为JSON
        try:
            understanding_data = json.loads(ai_response)
            required_fields = ['understanding', 'task_type', 'required_info', 
                             'provided_info', 'missing_info', 'plan_summary', 
                             'is_complete', 'suggestion']
            if all(field in understanding_data for field in required_fields):
                print(f"✅ 任务理解完成")
                print(f"   任务类型: {understanding_data['task_type']}")
                print(f"   信息完整: {'是' if understanding_data['is_complete'] else '否'}")
                print(f"   缺失信息: {understanding_data['missing_info']}")
                return understanding_data
        except json.JSONDecodeError:
            print(f"⚠️  AI返回的不是有效JSON，尝试提取...")
            import re
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                try:
                    understanding_data = json.loads(json_match.group())
                    required_fields = ['understanding', 'task_type', 'required_info', 
                                     'provided_info', 'missing_info', 'plan_summary', 
                                     'is_complete', 'suggestion']
                    if all(field in understanding_data for field in required_fields):
                        print(f"✅ 任务理解完成")
                        return understanding_data
                except:
                    pass
        
        print(f"⚠️  无法解析任务理解结果，跳过确认阶段")
        return None
            
    except Exception as e:
        print(f"❌ 任务理解失败: {e}")
        return None

