#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from linebot.models import (
    TextSendMessage, QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent, TextComponent,
    ButtonComponent, MessageTemplateAction, PostbackAction
)
from database import DatabaseManager
from models import User, UserType
from utils import ValidationUtils, ErrorHandler
import logging

logger = logging.getLogger(__name__)

class UserRegistrationService:
    """用戶註冊服務"""
    
    def __init__(self):
        self.db = DatabaseManager()
        # 暫存用戶註冊狀態
        self.registration_states = {}
    
    def start_registration(self, user_id, profile=None):
        """開始註冊流程"""
        try:
            # 初始化註冊狀態
            self.registration_states[user_id] = {
                'step': 'choose_type',
                'data': {},
                'profile': profile
            }
            
            welcome_message = f"""🎉 歡迎使用機場接送媒合服務！

請選擇您的身份類型："""

            quick_reply = QuickReply(items=[
                QuickReplyButton(action=MessageAction(
                    label="🚗 我是乘客", 
                    text="註冊乘客"
                )),
                QuickReplyButton(action=MessageAction(
                    label="🚖 我是司機", 
                    text="註冊司機"
                ))
            ])
            
            return TextSendMessage(text=welcome_message, quick_reply=quick_reply)
            
        except Exception as e:
            logger.error(f"開始註冊失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def handle_registration_message(self, user_id, message_text):
        """處理註冊相關訊息"""
        try:
            if user_id not in self.registration_states:
                return None
            
            state = self.registration_states[user_id]
            step = state['step']
            
            if message_text == "註冊乘客":
                return self._handle_passenger_registration(user_id)
            elif message_text == "註冊司機":
                return self._handle_driver_registration_start(user_id)
            elif step == 'driver_name':
                return self._handle_driver_name_input(user_id, message_text)
            elif step == 'driver_phone':
                return self._handle_driver_phone_input(user_id, message_text)
            elif step == 'driver_line_id':
                return self._handle_driver_line_id_input(user_id, message_text)
            elif step == 'driver_car_plate':
                return self._handle_driver_car_plate_input(user_id, message_text)
            
            return None
            
        except Exception as e:
            logger.error(f"處理註冊訊息失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_passenger_registration(self, user_id):
        """處理乘客註冊"""
        try:
            state = self.registration_states[user_id]
            profile = state.get('profile')
            
            # 建立乘客用戶
            user = User(
                user_id=user_id,
                user_type=UserType.PASSENGER,
                name=profile.display_name if profile else "乘客",
                is_active=True
            )
            
            self.db.create_user(user)
            
            # 清除註冊狀態
            del self.registration_states[user_id]
            
            success_message = f"""✅ 乘客註冊完成！

歡迎 {user.name}！您現在可以使用以下功能：

🚖 預約機場接送
📋 查詢訂單狀態
❌ 取消訂單

請輸入「機場接送」開始預約服務，或直接說明您的需求。"""

            return TextSendMessage(text=success_message)
            
        except Exception as e:
            logger.error(f"乘客註冊失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_driver_registration_start(self, user_id):
        """開始司機註冊流程"""
        try:
            self.registration_states[user_id]['step'] = 'driver_name'
            
            message = """🚖 司機註冊

為了提供更好的服務，請提供以下資料：

請輸入您的真實姓名："""

            return TextSendMessage(text=message)
            
        except Exception as e:
            logger.error(f"開始司機註冊失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_driver_name_input(self, user_id, name):
        """處理司機姓名輸入"""
        try:
            if len(name.strip()) < 2:
                return TextSendMessage(text="姓名至少需要2個字元，請重新輸入：")
            
            self.registration_states[user_id]['data']['name'] = name.strip()
            self.registration_states[user_id]['step'] = 'driver_phone'
            
            message = """請輸入您的手機號碼：

格式：09xxxxxxxx（10位數字）"""

            return TextSendMessage(text=message)
            
        except Exception as e:
            logger.error(f"處理司機姓名失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_driver_phone_input(self, user_id, phone):
        """處理司機電話輸入"""
        try:
            phone = phone.strip().replace('-', '').replace(' ', '')
            
            if not ValidationUtils.validate_phone(phone):
                return TextSendMessage(text="手機號碼格式錯誤，請輸入09開頭的10位數字：")
            
            self.registration_states[user_id]['data']['phone'] = phone
            self.registration_states[user_id]['step'] = 'driver_line_id'
            
            message = """請輸入您的 Line ID：

這將用於乘客聯繫您，請確保正確無誤。"""

            return TextSendMessage(text=message)
            
        except Exception as e:
            logger.error(f"處理司機電話失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_driver_line_id_input(self, user_id, line_id):
        """處理司機Line ID輸入"""
        try:
            line_id = line_id.strip()
            
            if len(line_id) < 3:
                return TextSendMessage(text="Line ID 格式不正確，請重新輸入：")
            
            self.registration_states[user_id]['data']['line_id'] = line_id
            self.registration_states[user_id]['step'] = 'driver_car_plate'
            
            message = """請輸入您的車牌號碼：

格式範例：ABC-1234 或 1234-AB"""

            return TextSendMessage(text=message)
            
        except Exception as e:
            logger.error(f"處理司機Line ID失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_driver_car_plate_input(self, user_id, car_plate):
        """處理司機車牌輸入"""
        try:
            car_plate = car_plate.strip().upper()
            
            if not ValidationUtils.validate_car_plate(car_plate):
                return TextSendMessage(text="車牌號碼格式錯誤，請重新輸入（例：ABC-1234）：")
            
            # 完成司機註冊
            return self._complete_driver_registration(user_id, car_plate)
            
        except Exception as e:
            logger.error(f"處理司機車牌失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _complete_driver_registration(self, user_id, car_plate):
        """完成司機註冊"""
        try:
            state = self.registration_states[user_id]
            data = state['data']
            profile = state.get('profile')
            
            # 建立司機用戶
            user = User(
                user_id=user_id,
                user_type=UserType.DRIVER,
                name=data['name'],
                phone=data['phone'],
                line_id=data['line_id'],
                car_plate=car_plate,
                is_active=True
            )
            
            self.db.create_user(user)
            
            # 清除註冊狀態
            del self.registration_states[user_id]
            
            success_message = f"""✅ 司機註冊完成！

歡迎加入我們的司機團隊！

👨‍💼 您的資料：
🚗 姓名: {user.name}
📱 電話: {user.phone}
💬 Line ID: {user.line_id}
🚙 車牌: {user.car_plate}

🔔 系統功能：
• 即時接收新訂單通知
• 快速回覆接單或拒絕
• 自動媒合乘客
• 訂單狀態管理

您現在已上線，等待新訂單中...
當有新訂單時會立即通知您！"""

            return TextSendMessage(text=success_message)
            
        except Exception as e:
            logger.error(f"完成司機註冊失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def is_in_registration(self, user_id):
        """檢查用戶是否在註冊流程中"""
        return user_id in self.registration_states
    
    def cancel_registration(self, user_id):
        """取消註冊流程"""
        if user_id in self.registration_states:
            del self.registration_states[user_id]
            return TextSendMessage(text="註冊已取消。如需重新註冊請重新開始。")
        return None
    
    def create_registration_summary_flex(self, user_data, user_type):
        """建立註冊摘要的 Flex Message"""
        try:
            if user_type == UserType.DRIVER:
                contents = [
                    TextComponent(text="司機註冊確認", weight="bold", size="lg"),
                    TextComponent(text=" ", size="sm"),
                    TextComponent(text=f"姓名: {user_data['name']}", size="sm"),
                    TextComponent(text=f"電話: {user_data['phone']}", size="sm"),
                    TextComponent(text=f"Line ID: {user_data['line_id']}", size="sm"),
                    TextComponent(text=f"車牌: {user_data.get('car_plate', '')}", size="sm"),
                ]
            else:
                contents = [
                    TextComponent(text="乘客註冊確認", weight="bold", size="lg"),
                    TextComponent(text="準備完成註冊", size="sm"),
                ]
            
            bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=contents + [
                        ButtonComponent(
                            style="primary",
                            action=MessageTemplateAction(
                                label="確認註冊",
                                text="確認註冊"
                            )
                        ),
                        ButtonComponent(
                            style="secondary",
                            action=MessageTemplateAction(
                                label="取消註冊",
                                text="取消註冊"
                            )
                        )
                    ]
                )
            )
            
            return FlexSendMessage(alt_text="註冊確認", contents=bubble)
            
        except Exception as e:
            logger.error(f"建立註冊摘要失敗: {e}")
            return None 