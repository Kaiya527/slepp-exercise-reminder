#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉定时提醒脚本 - GitHub Actions 版本

环境变量：
- DINGTALK_WEBHOOK: 钉钉Webhook地址
- DINGTALK_SECRET: 钉钉加签密钥
- REMINDER_TYPE: 提醒类型 (morning/noon/afternoon/bedtime/garden)
- WEEKDAY: 星期几 (0=周日, 1=周一, ..., 6=周六)
- USER_NAME: 用户名称
"""

import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from datetime import datetime


def generate_sign(timestamp: str, secret: str) -> str:
    """生成钉钉加签"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


def send_message(webhook: str, secret: str, content: str) -> dict:
    """发送钉钉消息"""
    timestamp = str(round(time.time() * 1000))
    sign = generate_sign(timestamp, secret)
    url = f"{webhook}&timestamp={timestamp}&sign={sign}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "msgtype": "text",
        "text": {"content": content}
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    return response.json()


def get_reminder_content(reminder_type: str, user_name: str, weekday: int) -> str:
    """根据类型生成提醒内容"""
    
    weekday_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    today = weekday_names[weekday]
    is_garden_day = weekday in [1, 4]  # 周一=1, 周四=4
    
    if reminder_type == "morning":
        if is_garden_day:
            return f"""【运动提醒】早安打卡时间到！

亲爱的{user_name}，美好的一天从运动开始！

今日打卡计划（{today}·花园劳动日）：
✓ 站桩 15-20分钟（去花园前可减量）
✓ 静坐 5分钟（安神定志）
✓ 晨起伸展 3分钟（活动身体）

⚠️ 今天是{today}，花园劳动日！
记得安排好时间去花园劳动，这是今天最重要的打卡项！

状态如何？精力充沛就完成全部，累了就先站桩就好。🌱

——失眠调理运动指导"""
        else:
            return f"""【运动提醒】早安打卡时间到！

亲爱的{user_name}，美好的一天从运动开始！

今日打卡计划（{today}）：
✓ 站桩 30分钟（核心打卡项）
✓ 静坐 5-10分钟（安神定志）
✓ 晨起伸展 3-5分钟（活动身体）

状态如何？精力充沛就完成全部，累了就先站桩就好。🌱

——失眠调理运动指导"""
    
    elif reminder_type == "noon":
        return f"""【运动提醒】午间打卡时间

亲爱的{user_name}，忙碌了一上午，休息一下吧！

中午打卡计划：
✓ 饭后散步 10-15分钟（轻松走动）
✓ 坐姿放松 5分钟（颈肩拉伸）

不想动？静坐5分钟也可以。放松就好！🌿

——失眠调理运动指导"""
    
    elif reminder_type == "afternoon":
        if is_garden_day:
            return f"""【运动提醒】下午打卡时间

亲爱的{user_name}，今天去了花园劳动，下午可以轻松活动：

✓ 户外散步 20-30分钟（可选）
✓ 瑜伽拉伸 15分钟（可选）

劳动了一天，好好休息！如果累了就放松一下。☀️

——失眠调理运动指导"""
        else:
            return f"""【运动提醒】下午打卡时间

亲爱的{user_name}，下午活动时间到！

下午打卡计划：
✓ 户外散步 20-30分钟（调节情绪）
  或 瑜伽拉伸 15-20分钟
✓ 艾灸 20-30分钟（每周2-3次可选）

今天压力怎么样？焦虑就去户外走走，"走几步就平静下来"。☀️

——失眠调理运动指导"""
    
    elif reminder_type == "bedtime":
        return f"""【运动提醒】睡前打卡时间

亲爱的{user_name}，该放松下来，准备睡觉了！

睡前打卡计划：
✓ 睡前放松 15-20分钟
   • 瑜伽拉伸 或 泡脚
   • 4-7-8呼吸法
✓ 静坐 5-10分钟（清空思绪）

今天辛苦了！放松身体，清空思绪，今晚好梦。🌙

——失眠调理运动指导"""
    
    elif reminder_type == "garden":
        return f"""【运动提醒】今天是花园劳动日！

亲爱的{user_name}，{today}的特别安排：

早晨：
✓ 站桩 15-30分钟（可减量）
✓ 静坐 5分钟

白天：
✓ 花园劳动（核心打卡项！）
  - 体力锻炼 ✓
  - 心理疗愈 ✓
  - 日照补充 ✓
  - 接地气 ✓

睡前：
✓ 睡前放松 15-20分钟

花园劳动是今天最重要的打卡项，其他可以简化！🌿

——失眠调理运动指导"""
    
    return f"【提醒】亲爱的{user_name}，该运动打卡啦！🌱"


def main():
    """主函数"""
    # 读取环境变量
    webhook = os.getenv("DINGTALK_WEBHOOK")
    secret = os.getenv("DINGTALK_SECRET")
    reminder_type = os.getenv("REMINDER_TYPE", "morning")
    weekday = int(os.getenv("WEEKDAY", datetime.now().weekday()))
    user_name = os.getenv("USER_NAME", "朋友")
    
    if not webhook or not secret:
        print("错误：缺少 DINGTALK_WEBHOOK 或 DINGTALK_SECRET 环境变量")
        return 1
    
    # 生成提醒内容
    content = get_reminder_content(reminder_type, user_name, weekday)
    
    # 发送消息
    try:
        result = send_message(webhook, secret, content)
        if result.get("errcode") == 0:
            print(f"✓ 提醒发送成功！类型: {reminder_type}")
            return 0
        else:
            print(f"✗ 发送失败: {result}")
            return 1
    except Exception as e:
        print(f"✗ 发送异常: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
