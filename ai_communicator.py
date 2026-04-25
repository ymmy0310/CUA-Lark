import requests
import base64
import json
import os
from typing import Dict, Optional
from config import AI_CONFIG, SYSTEM_PROMPT


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
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_CONFIG['api_key']}"
    }
    
    payload = {
        "model": AI_CONFIG['endpoint_id'],
        "messages": messages,
        "temperature": AI_CONFIG['temperature'],
        "max_tokens": AI_CONFIG['max_tokens']
    }
    
    try:
        # 发送请求
        print(f"🚀 正在发送请求到AI...")
        print(f"📤 API地址: {AI_CONFIG['api_endpoint']}")
        print(f"📤 接入点ID: {AI_CONFIG['endpoint_id']}")
        print(f"📤 消息长度: {len(str(payload))}")
        
        response = requests.post(AI_CONFIG['api_endpoint'], headers=headers, json=payload)
        
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


if __name__ == '__main__':
    print("AI通信模块测试")
    print("请先配置 config.py 中的API信息")
    print("然后运行主程序测试")
