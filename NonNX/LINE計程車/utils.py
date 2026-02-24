#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class MessageParser:
    """訊息解析器"""
    
    @staticmethod
    def parse_ride_request(message_text: str) -> Optional[Dict]:
        """解析乘客的接送需求訊息"""
        try:
            # 移除多餘空白和換行
            text = re.sub(r'\s+', ' ', message_text.strip())
            
            # 解析模式
            patterns = {
                'pickup_location': r'上車地點[:：]\s*([^\n]+)',
                'dropoff_location': r'下車地點[:：]\s*([^\n]+)',
                'pickup_time': r'預約時間[:：]\s*([^\n]+)',
                'passenger_count': r'乘客人數[:：]\s*(\d+)',
                'special_notes': r'特殊需求[:：]\s*([^\n]+)'
            }
            
            result = {}
            
            for key, pattern in patterns.items():
                match = re.search(pattern, message_text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if key == 'passenger_count':
                        result[key] = int(value)
                    elif key == 'pickup_time':
                        parsed_time = MessageParser.parse_datetime(value)
                        if parsed_time:
                            result[key] = parsed_time
                    else:
                        result[key] = value
            
            # 檢查必要欄位
            required_fields = ['pickup_location', 'dropoff_location', 'pickup_time', 'passenger_count']
            if all(field in result for field in required_fields):
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"解析乘車需求失敗: {e}")
            return None
    
    @staticmethod
    def parse_datetime(time_str: str) -> Optional[datetime]:
        """解析時間字串"""
        try:
            # 常見時間格式
            patterns = [
                r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})',  # MM/DD HH:MM
                r'(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})',  # MM-DD HH:MM
                r'(\d{2})(\d{2})\s+(\d{1,2}):(\d{2})',       # MMDD HH:MM
            ]
            
            current_year = datetime.now().year
            
            for pattern in patterns:
                match = re.search(pattern, time_str)
                if match:
                    month, day, hour, minute = map(int, match.groups())
                    
                    # 基本驗證
                    if 1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59:
                        target_time = datetime(current_year, month, day, hour, minute)
                        
                        # 如果時間已過，設為明年
                        if target_time < datetime.now():
                            target_time = target_time.replace(year=current_year + 1)
                        
                        return target_time
            
            return None
            
        except Exception as e:
            logger.error(f"解析時間失敗: {e}")
            return None
    
    @staticmethod
    def parse_command(message_text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析指令訊息"""
        try:
            text = message_text.strip()
            
            # 接單指令
            if text.startswith("接單"):
                parts = text.split()
                if len(parts) >= 2:
                    return "accept_order", parts[1]
            
            # 拒絕指令
            elif text.startswith("拒絕"):
                parts = text.split()
                if len(parts) >= 2:
                    return "reject_order", parts[1]
            
            # 取消指令
            elif text.startswith("取消訂單"):
                parts = text.split()
                if len(parts) >= 2:
                    return "cancel_order", parts[1]
            
            return None, None
            
        except Exception as e:
            logger.error(f"解析指令失敗: {e}")
            return None, None

class TimeUtils:
    """時間工具類"""
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """格式化日期時間"""
        return dt.strftime("%m/%d %H:%M")
    
    @staticmethod
    def format_datetime_full(dt: datetime) -> str:
        """完整格式化日期時間"""
        return dt.strftime("%Y/%m/%d %H:%M:%S")
    
    @staticmethod
    def is_future_time(dt: datetime, buffer_minutes: int = 30) -> bool:
        """檢查是否為未來時間（含緩衝時間）"""
        buffer_time = datetime.now() + timedelta(minutes=buffer_minutes)
        return dt > buffer_time
    
    @staticmethod
    def get_time_until(target_time: datetime) -> str:
        """取得到目標時間的剩餘時間描述"""
        now = datetime.now()
        diff = target_time - now
        
        if diff.total_seconds() < 0:
            return "已過期"
        
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天{hours}小時"
        elif hours > 0:
            return f"{hours}小時{minutes}分鐘"
        else:
            return f"{minutes}分鐘"

class MessageFormatter:
    """訊息格式化器"""
    
    @staticmethod
    def format_ride_request_summary(ride_request) -> str:
        """格式化乘車需求摘要"""
        pickup_time = TimeUtils.format_datetime(ride_request.pickup_time)
        
        summary = f"""📋 訂單摘要

🆔 訂單編號: {ride_request.request_id[:8]}...
📍 上車地點: {ride_request.pickup_location}
📍 下車地點: {ride_request.dropoff_location}
🕐 預約時間: {pickup_time}
👥 乘客人數: {ride_request.passenger_count}人
📊 狀態: {MessageFormatter._get_status_emoji(ride_request.status)}"""

        if ride_request.special_notes:
            summary += f"\n📝 特殊需求: {ride_request.special_notes}"
        
        return summary
    
    @staticmethod
    def format_driver_info(driver) -> str:
        """格式化司機資訊"""
        return f"""👨‍💼 司機資訊

🚗 司機姓名: {driver.name}
📱 聯絡電話: {driver.phone}
💬 Line ID: {driver.line_id}
🚙 車牌號碼: {driver.car_plate}"""
    
    @staticmethod
    def format_order_status_update(request_id: str, old_status: str, new_status: str) -> str:
        """格式化訂單狀態更新訊息"""
        old_emoji = MessageFormatter._get_status_emoji(old_status)
        new_emoji = MessageFormatter._get_status_emoji(new_status)
        
        return f"""🔄 訂單狀態更新

🆔 訂單: {request_id[:8]}...
{old_emoji} {old_status} → {new_emoji} {new_status}"""
    
    @staticmethod
    def _get_status_emoji(status: str) -> str:
        """取得狀態對應的表情符號"""
        emoji_map = {
            'pending': '⏳ 等待接單',
            'assigned': '✅ 已指派',
            'completed': '🎉 已完成',
            'cancelled': '❌ 已取消'
        }
        return emoji_map.get(status, '❓ 未知狀態')

class ValidationUtils:
    """驗證工具類"""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """驗證手機號碼格式"""
        pattern = r'^09\d{8}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_car_plate(plate: str) -> bool:
        """驗證車牌號碼格式（台灣）"""
        # 簡化版車牌驗證
        pattern = r'^[A-Z]{2,3}-?\d{4}$|^\d{4}-?[A-Z]{2}$'
        return bool(re.match(pattern, plate.upper()))
    
    @staticmethod
    def validate_passenger_count(count: int) -> bool:
        """驗證乘客人數"""
        return 1 <= count <= 8
    
    @staticmethod
    def validate_location(location: str) -> bool:
        """驗證地點描述"""
        return len(location.strip()) >= 3

class ErrorHandler:
    """錯誤處理器"""
    
    @staticmethod
    def get_user_friendly_error(error_type: str) -> str:
        """取得用戶友好的錯誤訊息"""
        error_messages = {
            'invalid_format': '訊息格式不正確，請參考範例重新輸入。',
            'invalid_time': '時間格式錯誤或時間已過期，請重新設定。',
            'invalid_phone': '手機號碼格式錯誤，請輸入09開頭的10位數字。',
            'invalid_plate': '車牌號碼格式錯誤，請確認格式正確。',
            'invalid_count': '乘客人數應為1-8人。',
            'order_not_found': '找不到此訂單，請確認訂單編號。',
            'permission_denied': '您沒有權限執行此操作。',
            'system_error': '系統暫時無法處理您的請求，請稍後再試。',
            'database_error': '資料庫連接異常，請稍後再試。',
            'line_api_error': 'Line API 呼叫失敗，請稍後再試。'
        }
        return error_messages.get(error_type, '發生未知錯誤，請聯繫客服。') 