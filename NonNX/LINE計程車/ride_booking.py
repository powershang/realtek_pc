#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime, timedelta
from linebot.models import (
    TextSendMessage, QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent, TextComponent,
    ButtonComponent, MessageTemplateAction
)
from database import DatabaseManager
from models import RideRequest, RideStatus
from utils import MessageParser, TimeUtils, ValidationUtils, ErrorHandler, MessageFormatter
import logging

logger = logging.getLogger(__name__)

class RideBookingService:
    """乘車預約服務"""
    
    def __init__(self):
        self.db = DatabaseManager()
        # 暫存預約狀態
        self.booking_states = {}
    
    def start_booking(self, user_id):
        """開始預約流程"""
        try:
            # 初始化預約狀態
            self.booking_states[user_id] = {
                'step': 'input_details',
                'data': {}
            }
            
            booking_guide = """🚖 機場接送預約

請按照以下格式提供您的需求：

上車地點: [詳細地址]
下車地點: [詳細地址]
預約時間: [MM/DD HH:MM]
乘客人數: [人數]
特殊需求: [選填]

📝 範例：
上車地點: 台北車站東三門
下車地點: 桃園機場第二航廈
預約時間: 12/25 08:30
乘客人數: 2
特殊需求: 有大件行李

請一次輸入完整資訊："""

            return TextSendMessage(text=booking_guide)
            
        except Exception as e:
            logger.error(f"開始預約失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def handle_booking_message(self, user_id, message_text):
        """處理預約相關訊息"""
        try:
            if user_id not in self.booking_states:
                return None
            
            state = self.booking_states[user_id]
            step = state['step']
            
            if step == 'input_details':
                return self._handle_details_input(user_id, message_text)
            elif step == 'confirm_booking':
                return self._handle_booking_confirmation(user_id, message_text)
            
            return None
            
        except Exception as e:
            logger.error(f"處理預約訊息失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_details_input(self, user_id, message_text):
        """處理需求詳情輸入"""
        try:
            # 解析乘車需求
            parsed_data = MessageParser.parse_ride_request(message_text)
            
            if not parsed_data:
                error_message = """❌ 訊息格式不正確

請按照以下格式重新輸入：

上車地點: [詳細地址]
下車地點: [詳細地址]
預約時間: [MM/DD HH:MM]
乘客人數: [人數]
特殊需求: [選填]

確保所有必填欄位都有填寫。"""
                return TextSendMessage(text=error_message)
            
            # 驗證資料
            validation_result = self._validate_ride_request(parsed_data)
            if not validation_result['valid']:
                return TextSendMessage(text=validation_result['message'])
            
            # 儲存預約資料
            self.booking_states[user_id]['data'] = parsed_data
            self.booking_states[user_id]['step'] = 'confirm_booking'
            
            # 顯示確認訊息
            return self._create_booking_confirmation(parsed_data)
            
        except Exception as e:
            logger.error(f"處理需求詳情失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _validate_ride_request(self, data):
        """驗證乘車需求資料"""
        try:
            # 檢查地點
            if not ValidationUtils.validate_location(data['pickup_location']):
                return {
                    'valid': False,
                    'message': '上車地點描述太簡短，請提供更詳細的地址。'
                }
            
            if not ValidationUtils.validate_location(data['dropoff_location']):
                return {
                    'valid': False,
                    'message': '下車地點描述太簡短，請提供更詳細的地址。'
                }
            
            # 檢查時間
            if not TimeUtils.is_future_time(data['pickup_time'], buffer_minutes=30):
                return {
                    'valid': False,
                    'message': '預約時間必須至少提前30分鐘，請重新設定時間。'
                }
            
            # 檢查乘客人數
            if not ValidationUtils.validate_passenger_count(data['passenger_count']):
                return {
                    'valid': False,
                    'message': '乘客人數必須為1-8人。'
                }
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"驗證乘車需求失敗: {e}")
            return {
                'valid': False,
                'message': '資料驗證時發生錯誤，請重新輸入。'
            }
    
    def _create_booking_confirmation(self, data):
        """建立預約確認訊息"""
        try:
            pickup_time = TimeUtils.format_datetime(data['pickup_time'])
            time_until = TimeUtils.get_time_until(data['pickup_time'])
            
            confirmation_text = f"""📋 請確認您的預約資訊

📍 上車地點: {data['pickup_location']}
📍 下車地點: {data['dropoff_location']}
🕐 預約時間: {pickup_time}
⏰ 距離現在: {time_until}
👥 乘客人數: {data['passenger_count']}人"""

            if data.get('special_notes'):
                confirmation_text += f"\n📝 特殊需求: {data['special_notes']}"
            
            confirmation_text += "\n\n資訊是否正確？"
            
            quick_reply = QuickReply(items=[
                QuickReplyButton(action=MessageAction(
                    label="✅ 確認預約", 
                    text="確認預約"
                )),
                QuickReplyButton(action=MessageAction(
                    label="❌ 重新輸入", 
                    text="重新輸入"
                )),
                QuickReplyButton(action=MessageAction(
                    label="🚫 取消預約", 
                    text="取消預約"
                ))
            ])
            
            return TextSendMessage(text=confirmation_text, quick_reply=quick_reply)
            
        except Exception as e:
            logger.error(f"建立確認訊息失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _handle_booking_confirmation(self, user_id, message_text):
        """處理預約確認"""
        try:
            if message_text == "確認預約":
                return self._create_ride_request(user_id)
            elif message_text == "重新輸入":
                return self._restart_booking(user_id)
            elif message_text == "取消預約":
                return self._cancel_booking(user_id)
            else:
                return TextSendMessage(text="請選擇「確認預約」、「重新輸入」或「取消預約」。")
                
        except Exception as e:
            logger.error(f"處理預約確認失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _create_ride_request(self, user_id):
        """建立乘車需求"""
        try:
            state = self.booking_states[user_id]
            data = state['data']
            
            # 建立訂單
            request_id = str(uuid.uuid4())
            ride_request = RideRequest(
                request_id=request_id,
                passenger_id=user_id,
                pickup_location=data['pickup_location'],
                dropoff_location=data['dropoff_location'],
                pickup_time=data['pickup_time'],
                passenger_count=data['passenger_count'],
                special_notes=data.get('special_notes', ''),
                status=RideStatus.PENDING
            )
            
            # 儲存到資料庫
            self.db.create_ride_request(ride_request)
            
            # 清除預約狀態
            del self.booking_states[user_id]
            
            # 建立成功訊息
            success_message = f"""✅ 預約成功！

🆔 訂單編號: {request_id[:8]}...
📊 狀態: 等待司機接單

系統正在通知所有可用司機，
一旦有司機接單會立即通知您司機資訊。

您可以隨時輸入「查詢訂單」查看狀態，
或輸入「取消訂單 {request_id[:8]}」取消預約。"""

            return TextSendMessage(text=success_message)
            
        except Exception as e:
            logger.error(f"建立乘車需求失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _restart_booking(self, user_id):
        """重新開始預約"""
        try:
            self.booking_states[user_id] = {
                'step': 'input_details',
                'data': {}
            }
            
            return self.start_booking(user_id)
            
        except Exception as e:
            logger.error(f"重新開始預約失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def _cancel_booking(self, user_id):
        """取消預約"""
        try:
            if user_id in self.booking_states:
                del self.booking_states[user_id]
            
            return TextSendMessage(text="預約已取消。如需重新預約請輸入「機場接送」。")
            
        except Exception as e:
            logger.error(f"取消預約失敗: {e}")
            return TextSendMessage(text=ErrorHandler.get_user_friendly_error('system_error'))
    
    def is_in_booking(self, user_id):
        """檢查用戶是否在預約流程中"""
        return user_id in self.booking_states
    
    def get_user_active_orders(self, user_id):
        """取得用戶的活躍訂單"""
        try:
            orders = self.db.get_user_ride_requests(user_id)
            active_orders = [order for order in orders if order.status in [RideStatus.PENDING, RideStatus.ASSIGNED]]
            return active_orders
            
        except Exception as e:
            logger.error(f"取得用戶訂單失敗: {e}")
            return []
    
    def cancel_ride_request(self, user_id, request_id):
        """取消乘車需求"""
        try:
            # 檢查訂單是否存在且屬於該用戶
            ride_request = self.db.get_ride_request(request_id)
            if not ride_request or ride_request.passenger_id != user_id:
                return False, "找不到此訂單或您沒有權限取消。"
            
            if ride_request.status not in [RideStatus.PENDING, RideStatus.ASSIGNED]:
                return False, "此訂單狀態無法取消。"
            
            # 更新訂單狀態
            self.db.update_ride_request_status(request_id, RideStatus.CANCELLED)
            
            # 通知相關司機（如果已指派）
            if ride_request.status == RideStatus.ASSIGNED:
                self._notify_driver_cancellation(ride_request.assigned_driver_id, request_id)
            
            return True, "訂單已成功取消。"
            
        except Exception as e:
            logger.error(f"取消乘車需求失敗: {e}")
            return False, "取消失敗，請稍後再試。"
    
    def _notify_driver_cancellation(self, driver_id, request_id):
        """通知司機訂單取消"""
        try:
            from app import line_bot_api  # 避免循環導入
            
            message = f"""❌ 訂單取消通知

訂單編號: {request_id[:8]}...
乘客已取消此訂單。

感謝您的服務！"""

            line_bot_api.push_message(driver_id, TextSendMessage(text=message))
            
        except Exception as e:
            logger.error(f"通知司機取消失敗: {e}")
    
    def create_order_status_flex(self, ride_request):
        """建立訂單狀態的 Flex Message"""
        try:
            status_emoji = {
                RideStatus.PENDING: "⏳",
                RideStatus.ASSIGNED: "✅",
                RideStatus.COMPLETED: "🎉",
                RideStatus.CANCELLED: "❌"
            }
            
            status_text = {
                RideStatus.PENDING: "等待司機接單",
                RideStatus.ASSIGNED: "已指派司機",
                RideStatus.COMPLETED: "已完成",
                RideStatus.CANCELLED: "已取消"
            }
            
            pickup_time = TimeUtils.format_datetime(ride_request.pickup_time)
            
            contents = [
                TextComponent(text="📋 訂單詳情", weight="bold", size="lg"),
                TextComponent(text=" ", size="sm"),
                TextComponent(text=f"🆔 {ride_request.request_id[:8]}...", size="sm"),
                TextComponent(text=f"📍 {ride_request.pickup_location}", size="sm"),
                TextComponent(text=f"📍 {ride_request.dropoff_location}", size="sm"),
                TextComponent(text=f"🕐 {pickup_time}", size="sm"),
                TextComponent(text=f"👥 {ride_request.passenger_count}人", size="sm"),
                TextComponent(text=" ", size="sm"),
                TextComponent(
                    text=f"{status_emoji.get(ride_request.status, '❓')} {status_text.get(ride_request.status, '未知')}",
                    weight="bold",
                    size="md"
                )
            ]
            
            if ride_request.special_notes:
                contents.insert(-2, TextComponent(text=f"📝 {ride_request.special_notes}", size="sm"))
            
            # 根據狀態添加按鈕
            buttons = []
            if ride_request.status in [RideStatus.PENDING, RideStatus.ASSIGNED]:
                buttons.append(
                    ButtonComponent(
                        style="secondary",
                        action=MessageTemplateAction(
                            label="取消訂單",
                            text=f"取消訂單 {ride_request.request_id}"
                        )
                    )
                )
            
            bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=contents + buttons
                )
            )
            
            return FlexSendMessage(alt_text="訂單狀態", contents=bubble)
            
        except Exception as e:
            logger.error(f"建立訂單狀態Flex失敗: {e}")
            return None
    
    def create_booking_template_flex(self):
        """建立預約範本的 Flex Message"""
        try:
            bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(text="🚖 快速預約", weight="bold", size="lg"),
                        TextComponent(text="選擇常用路線或自訂預約", size="sm"),
                        TextComponent(text=" ", size="sm")
                    ]
                ),
                footer=BoxComponent(
                    layout="vertical",
                    contents=[
                        ButtonComponent(
                            style="primary",
                            action=MessageTemplateAction(
                                label="🛫 前往機場",
                                text="機場接送 前往機場"
                            )
                        ),
                        ButtonComponent(
                            style="primary",
                            action=MessageTemplateAction(
                                label="🛬 機場回程",
                                text="機場接送 機場回程"
                            )
                        ),
                        ButtonComponent(
                            style="secondary",
                            action=MessageTemplateAction(
                                label="📝 自訂路線",
                                text="機場接送"
                            )
                        )
                    ]
                )
            )
            
            return FlexSendMessage(alt_text="預約範本", contents=bubble)
            
        except Exception as e:
            logger.error(f"建立預約範本失敗: {e}")
            return None