# -*- coding: utf-8 -*-
"""
飞书长连接接收消息客户端
通过 WebSocket 长连接接收用户在飞书聊天中发给机器人的消息，
驱动 gui_app 执行任务，实现飞书全流程交互。

架构：
  main 线程:  tkinter GUI (gui_app.py)
  后台线程:   WebSocket 长连接监听
  任务线程:   CUA 任务执行

交互时序：
  用户飞书发消息 → WS 收到 → gui_app.external_run()
  → 迷你控制条显示 → CUA 执行 → AI 提问
  → feishu_callback 发消息给用户 → 用户飞书回复
  → WS 收到 → gui_app.receive_feishu_reply()
  → CUA 继续 → 完成 → 飞书收到结果
"""

import os
import json
import threading
import logging
import time
import tkinter as tk
import requests
import lark_oapi as lark
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

APP_ID = os.environ.get("FEISHU_APP_ID", "")
APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")

gui_app = None
current_open_id = None


def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            logger.error(f"获取 token HTTP 错误: {resp.status_code}")
            return None
        data = resp.json()
        if data.get("code") != 0:
            logger.error(f"获取 token 失败: {data.get('msg')}")
            return None
        return data.get("tenant_access_token")
    except Exception as e:
        logger.error(f"获取 token 异常: {e}")
        return None


def send_message_to_user(open_id, content):
    """通过飞书 API 发送消息给用户"""
    logger.info(f"发送消息: open_id={open_id}, content={content[:50]}...")
    token = get_tenant_access_token()
    if not token:
        logger.error("无法获取 tenant_access_token")
        return

    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "receive_id": open_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("回复消息成功")
        else:
            logger.error(f"回复消息失败: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"发送消息异常: {e}")


def make_feishu_callback(open_id):
    """
    创建 feishu_callback 闭包，捕获 open_id
    当 AI 需要用户输入时，通过此回调将提问发送到飞书
    """

    def callback(prompt):
        question = f"🤔 {prompt}\n\n请直接回复此消息提供信息。"
        send_message_to_user(open_id, question)

    return callback


def on_message_received(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    """
    接收消息 v2.0 事件回调（WebSocket 线程）
    提取文本消息，驱动 gui_app 执行任务
    """
    global current_open_id

    try:
        event = data.event
        message = event.message

        if message.message_type != "text":
            return

        content = json.loads(message.content)
        user_task = content.get("text", "").strip()
        if not user_task:
            return

        open_id = event.sender.sender_id.open_id
        logger.info(f"收到用户消息 [open_id={open_id}]: {user_task}")

        if gui_app is None:
            logger.error("gui_app 未初始化，无法处理任务")
            return

        if gui_app.is_waiting_for_input and open_id == current_open_id:
            gui_app.root.after(0, gui_app.receive_feishu_reply, user_task)
            return

        current_open_id = open_id
        feishu_cb = make_feishu_callback(open_id)

        gui_app.root.after(0, gui_app.external_run, user_task, feishu_cb)

    except Exception as e:
        logger.error(f"处理消息异常: {e}")


def start_ws_listener():
    """启动 WebSocket 长连接监听（后台线程）"""
    if not APP_ID or not APP_SECRET:
        logger.error("缺少环境变量 FEISHU_APP_ID 或 FEISHU_APP_SECRET")
        return

    def ws_run():
        logger.info("飞书长连接客户端启动中...")
        logger.info(f"APP_ID: {APP_ID}")

        try:
            event_handler = EventDispatcherHandler.builder(APP_ID, APP_SECRET) \
                .register_p2_im_message_receive_v1(on_message_received) \
                .build()

            client = lark.ws.Client(
                app_id=APP_ID,
                app_secret=APP_SECRET,
                event_handler=event_handler,
                log_level=lark.LogLevel.INFO
            )

            logger.info("长连接客户端已启动，等待消息...")
            client.start()
        except Exception as e:
            logger.error(f"长连接异常: {e}")

    thread = threading.Thread(target=ws_run, daemon=True)
    thread.start()
    logger.info("WebSocket 监听线程已启动")


def main():
    """
    主入口：启动 GUI + WebSocket 监听
    tkinter 必须在主线程运行，WebSocket 在后台 daemon 线程运行
    """
    global gui_app

    import gui_app as gui_module

    root = tk.Tk()
    gui_app = gui_module.FeishuCUAGUI(root)

    start_ws_listener()

    gui_app.log("📡 飞书长连接监听已自动启动")

    root.mainloop()


if __name__ == "__main__":
    main()
