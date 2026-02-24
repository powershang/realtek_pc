#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, request, abort

# 使用新版 LINE Bot SDK v3 API
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, PushMessageRequest,
    TextMessage, QuickReply, QuickReplyItem, MessageAction
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from database import DatabaseManager
from models import RideRequest, DriverResponse, User, OrderLog
import logging

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 打印所有重要環境變數
print("=" * 60)
print("環境變數檢查:")
print(f"LINE_CHANNEL_ACCESS_TOKEN: {'已設定' if os.getenv('LINE_CHANNEL_ACCESS_TOKEN') else '未設定'}")
print(f"LINE_CHANNEL_SECRET: {'已設定' if os.getenv('LINE_CHANNEL_SECRET') else '未設定'}")
print(f"DATABASE_URL: {'已設定' if os.getenv('DATABASE_URL') else '未設定'}")
print("=" * 60)

# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    logger.error("Line Bot credentials not found in environment variables")
    print("❌ LINE Bot 憑證未設定，程式將終止")
    exit(1)

# 新版 LINE Bot API 設定
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 資料庫管理器
print("🔧 初始化資料庫管理器...")
db_manager = DatabaseManager()

class RideMatchingService:
    """計程車媒合服務核心邏輯"""
    
    def __init__(self):
        self.db = db_manager
        
    def create_ride_request(self, passenger_id, pickup_location, dropoff_location, 
                          pickup_time, passenger_count, special_notes=""):
        """創建接送需求"""
        try:
            request_id = str(uuid.uuid4())
            ride_request = RideRequest(
                request_id=request_id,
                passenger_id=passenger_id,
                pickup_location=pickup_location,
                dropoff_location=dropoff_location,
                pickup_time=pickup_time,
                passenger_count=passenger_count,
                special_notes=special_notes,
                status='pending'
            )
            
            # 儲存到資料庫
            self.db.create_ride_request(ride_request)
            
            # 記錄操作日誌
            self._log_action(request_id, 'created', passenger_id, 
                           f"新訂單: {pickup_location} -> {dropoff_location}")
            
            # 通知所有可用司機
            self._notify_available_drivers(request_id)
            
            return request_id
            
        except Exception as e:
            logger.error(f"創建訂單失敗: {e}")
            raise
    
    def handle_driver_response(self, driver_id, request_id, response_type):
        """處理司機回覆"""
        try:
            # 檢查訂單狀態
            ride_request = self.db.get_ride_request(request_id)
            if not ride_request or ride_request.status != 'pending':
                return False, "訂單已不存在或已被處理"
            
            # 記錄司機回覆
            response_order = self.db.count_driver_responses(request_id) + 1
            driver_response = DriverResponse(
                response_id=str(uuid.uuid4()),
                request_id=request_id,
                driver_id=driver_id,
                response_type=response_type,
                response_order=response_order
            )
            
            self.db.create_driver_response(driver_response)
            
            if response_type == 'accept':
                # 如果是第一個接單的司機，立即指派
                if ride_request.assigned_driver_id is None:
                    success = self._assign_driver(request_id, driver_id)
                    if success:
                        self._log_action(request_id, 'assigned', driver_id, 
                                       f"司機 {driver_id} 接單成功")
                        return True, "接單成功！訂單已指派給您"
                else:
                    # 設為備用司機
                    self.db.set_backup_driver(driver_response.response_id, True)
                    return True, "感謝回覆！您已列入備用司機名單"
            
            return True, "回覆已記錄"
            
        except Exception as e:
            logger.error(f"處理司機回覆失敗: {e}")
            return False, "系統錯誤，請稍後再試"
    
    def cancel_by_driver(self, driver_id, request_id):
        """司機取消訂單"""
        try:
            ride_request = self.db.get_ride_request(request_id)
            if not ride_request or ride_request.assigned_driver_id != driver_id:
                return False, "無法取消此訂單"
            
            # 查找備用司機
            backup_drivers = self.db.get_backup_drivers(request_id)
            
            if backup_drivers:
                # 轉單給第一個備用司機
                next_driver_id = backup_drivers[0].driver_id
                self._assign_driver(request_id, next_driver_id)
                
                # 通知新司機
                self._notify_driver_assignment(request_id, next_driver_id)
                
                # 通知乘客司機變更
                self._notify_passenger_driver_change(request_id, next_driver_id)
                
                self._log_action(request_id, 'reassigned', next_driver_id, 
                               f"訂單從 {driver_id} 轉給 {next_driver_id}")
                
                return True, "訂單已轉給其他司機"
            else:
                # 沒有備用司機，取消訂單
                self.db.update_ride_request_status(request_id, 'cancelled')
                self._notify_passenger_cancellation(request_id)
                
                self._log_action(request_id, 'cancelled', driver_id, 
                               "司機取消且無備用司機")
                
                return True, "訂單已取消，已通知乘客"
                
        except Exception as e:
            logger.error(f"司機取消訂單失敗: {e}")
            return False, "取消失敗，請聯繫客服"
    
    def cancel_by_passenger(self, passenger_id, request_id):
        """乘客取消訂單"""
        try:
            ride_request = self.db.get_ride_request(request_id)
            if not ride_request or ride_request.passenger_id != passenger_id:
                return False, "無法取消此訂單"
            
            # 更新訂單狀態
            self.db.update_ride_request_status(request_id, 'cancelled')
            
            # 通知相關司機
            self._notify_drivers_cancellation(request_id)
            
            self._log_action(request_id, 'cancelled', passenger_id, "乘客取消訂單")
            
            return True, "訂單已成功取消"
            
        except Exception as e:
            logger.error(f"乘客取消訂單失敗: {e}")
            return False, "取消失敗，請稍後再試"
    
    def _assign_driver(self, request_id, driver_id):
        """指派司機"""
        try:
            self.db.update_ride_request_driver(request_id, driver_id)
            self.db.update_ride_request_status(request_id, 'assigned')
            
            # 通知乘客司機資訊
            self._notify_passenger_assignment(request_id, driver_id)
            
            # 通知其他司機訂單已媒合
            self._notify_other_drivers_matched(request_id, driver_id)
            
            return True
        except Exception as e:
            logger.error(f"指派司機失敗: {e}")
            return False
    
    def _notify_available_drivers(self, request_id):
        """通知所有可用司機"""
        try:
            drivers = self.db.get_active_drivers()
            ride_request = self.db.get_ride_request(request_id)
            
            message_text = self._create_driver_notification_message(ride_request)
            
            for driver in drivers:
                try:
                    # 使用新版 API 創建快速回覆按鈕
                    quick_reply = QuickReply(items=[
                        QuickReplyItem(action=MessageAction(
                            label="可接單", 
                            text=f"接單 {request_id}"
                        )),
                        QuickReplyItem(action=MessageAction(
                            label="無法接單", 
                            text=f"拒絕 {request_id}"
                        ))
                    ])
                    
                    # 使用新版 API 發送訊息
                    message = TextMessage(text=message_text, quick_reply=quick_reply)
                    request = PushMessageRequest(
                        to=driver.user_id,
                        messages=[message]
                    )
                    line_bot_api.push_message(request)
                except Exception as e:
                    logger.error(f"通知司機 {driver.user_id} 失敗: {e}")
            
            self._log_action(request_id, 'notified', 'system', 
                           f"已通知 {len(drivers)} 位司機")
                           
        except Exception as e:
            logger.error(f"通知司機失敗: {e}")
    
    def _create_driver_notification_message(self, ride_request):
        """創建司機通知訊息"""
        pickup_time = ride_request.pickup_time.strftime("%m/%d %H:%M")
        message = f"""🚖 新訂單通知

📍 上車地點: {ride_request.pickup_location}
📍 下車地點: {ride_request.dropoff_location}
🕐 預約時間: {pickup_time}
👥 乘客人數: {ride_request.passenger_count}人

"""
        if ride_request.special_notes:
            message += f"📝 特殊需求: {ride_request.special_notes}\n\n"
        
        message += "請快速回覆是否接單！"
        return message
    
    def _notify_passenger_assignment(self, request_id, driver_id):
        """通知乘客司機指派"""
        try:
            ride_request = self.db.get_ride_request(request_id)
            driver = self.db.get_user(driver_id)
            
            message = f"""✅ 媒合成功！

您的司機資訊：
🚗 司機: {driver.name}
📱 電話: {driver.phone}
💬 Line ID: {driver.line_id}
🚙 車牌: {driver.car_plate}

司機將會主動聯繫您確認接送細節。
如有任何問題，請直接聯繫司機。"""

            text_message = TextMessage(text=message)
            request = PushMessageRequest(
                to=ride_request.passenger_id,
                messages=[text_message]
            )
            line_bot_api.push_message(request)
            
        except Exception as e:
            logger.error(f"通知乘客指派失敗: {e}")
    
    def _notify_other_drivers_matched(self, request_id, assigned_driver_id):
        """通知其他司機訂單已媒合"""
        try:
            responses = self.db.get_driver_responses(request_id)
            
            for response in responses:
                if response.driver_id != assigned_driver_id:
                    try:
                        line_bot_api.push_message(
                            response.driver_id,
                            TextMessage(text="此訂單已有其他司機接單，感謝您的回覆！")
                        )
                    except Exception as e:
                        logger.error(f"通知司機 {response.driver_id} 失敗: {e}")
                        
        except Exception as e:
            logger.error(f"通知其他司機失敗: {e}")
    
    def _notify_driver_assignment(self, request_id, driver_id):
        """通知司機獲得訂單"""
        try:
            ride_request = self.db.get_ride_request(request_id)
            passenger = self.db.get_user(ride_request.passenger_id)
            
            pickup_time = ride_request.pickup_time.strftime("%m/%d %H:%M")
            message = f"""🎉 您已獲得新訂單！

乘客資訊：
👤 姓名: {passenger.name}
📱 電話: {passenger.phone}
💬 Line ID: {passenger.line_id}

訂單詳情：
📍 上車地點: {ride_request.pickup_location}
📍 下車地點: {ride_request.dropoff_location}
🕐 預約時間: {pickup_time}
👥 乘客人數: {ride_request.passenger_count}人

請主動聯繫乘客確認接送細節。"""

            if ride_request.special_notes:
                message += f"\n📝 特殊需求: {ride_request.special_notes}"

            line_bot_api.push_message(
                driver_id,
                TextMessage(text=message)
            )
            
        except Exception as e:
            logger.error(f"通知司機獲得訂單失敗: {e}")
    
    def _notify_passenger_driver_change(self, request_id, new_driver_id):
        """通知乘客司機變更"""
        try:
            ride_request = self.db.get_ride_request(request_id)
            new_driver = self.db.get_user(new_driver_id)
            
            message = f"""🔄 司機變更通知

由於原司機臨時無法前往，已為您重新安排司機：

新司機資訊：
🚗 司機: {new_driver.name}
📱 電話: {new_driver.phone}
💬 Line ID: {new_driver.line_id}
🚙 車牌: {new_driver.car_plate}

新司機將會重新聯繫您確認接送時間。
造成不便敬請見諒！"""

            line_bot_api.push_message(
                ride_request.passenger_id,
                TextMessage(text=message)
            )
            
        except Exception as e:
            logger.error(f"通知乘客司機變更失敗: {e}")
    
    def _notify_passenger_cancellation(self, request_id):
        """通知乘客訂單取消"""
        try:
            ride_request = self.db.get_ride_request(request_id)
            
            message = """❌ 訂單取消通知

很抱歉，由於司機臨時無法前往且目前沒有其他可用司機，
您的訂單已被取消。

您可以重新下單或聯繫客服尋求其他協助。
造成不便深感抱歉！"""

            line_bot_api.push_message(
                ride_request.passenger_id,
                TextMessage(text=message)
            )
            
        except Exception as e:
            logger.error(f"通知乘客取消失敗: {e}")
    
    def _notify_drivers_cancellation(self, request_id):
        """通知司機乘客取消"""
        try:
            responses = self.db.get_driver_responses(request_id)
            
            for response in responses:
                try:
                    line_bot_api.push_message(
                        response.driver_id,
                        TextMessage(text="乘客已取消此訂單，感謝您的關注！")
                    )
                except Exception as e:
                    logger.error(f"通知司機 {response.driver_id} 取消失敗: {e}")
                    
        except Exception as e:
            logger.error(f"通知司機取消失敗: {e}")
    
    def _log_action(self, request_id, action, actor_id, details):
        """記錄操作日誌"""
        try:
            log = OrderLog(
                log_id=str(uuid.uuid4()),
                request_id=request_id,
                action=action,
                actor_id=actor_id,
                details=details
            )
            self.db.create_order_log(log)
        except Exception as e:
            logger.error(f"記錄日誌失敗: {e}")

# 初始化媒合服務
matching_service = RideMatchingService()

@app.route("/callback", methods=['POST'])
def callback():
    """Line Bot Webhook"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """處理訊息事件"""
    user_id = event.source.user_id
    message_text = event.message.text.strip()
    
    try:
        # 確保用戶存在於資料庫
        user = db_manager.get_user(user_id)
        if not user:
            # 新用戶註冊流程
            handle_new_user(event)
            return
        
        # 解析訊息內容
        if message_text.startswith("接單 "):
            request_id = message_text.split(" ")[1]
            success, msg = matching_service.handle_driver_response(
                user_id, request_id, 'accept'
            )
            
        elif message_text.startswith("拒絕 "):
            request_id = message_text.split(" ")[1]
            success, msg = matching_service.handle_driver_response(
                user_id, request_id, 'reject'
            )
            
        elif message_text.startswith("取消訂單 "):
            request_id = message_text.split(" ")[1]
            if user.user_type == 'passenger':
                success, msg = matching_service.cancel_by_passenger(user_id, request_id)
            else:
                success, msg = matching_service.cancel_by_driver(user_id, request_id)
            
        elif user.user_type == 'passenger' and "機場接送" in message_text:
            # 乘客下單流程
            handle_ride_booking(event, user)
            return
            
        else:
            # 顯示功能選單
            show_main_menu(event, user)
            return
            
        # 使用新版 API 回覆訊息
        reply_message = TextMessage(text=msg)
        request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[reply_message]
        )
        line_bot_api.reply_message(request)
        
    except Exception as e:
        logger.error(f"處理訊息失敗: {e}")
        error_message = TextMessage(text="系統暫時無法處理您的請求，請稍後再試。")
        request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[error_message]
        )
        line_bot_api.reply_message(request)

def handle_new_user(event):
    """處理新用戶註冊"""
    user_id = event.source.user_id
    
    try:
        # 從 Line 獲取用戶資訊
        profile = line_bot_api.get_profile(user_id)
        
        welcome_message = f"""歡迎使用機場接送媒合服務！ {profile.display_name}

請選擇您的身份：
1️⃣ 我是乘客 - 需要機場接送服務
2️⃣ 我是司機 - 提供機場接送服務

請回覆數字選擇身份類型。"""
        
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=welcome_message)
        )
        
    except Exception as e:
        logger.error(f"處理新用戶失敗: {e}")

def handle_ride_booking(event, user):
    """處理乘客下單"""
    booking_message = """請提供您的接送需求資訊：

格式：
上車地點: [詳細地址]
下車地點: [詳細地址]  
預約時間: [MM/DD HH:MM]
乘客人數: [人數]
特殊需求: [選填]

範例：
上車地點: 台北車站東三門
下車地點: 桃園機場第二航廈
預約時間: 12/25 08:30
乘客人數: 2
特殊需求: 有大件行李"""

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=booking_message)
    )

def show_main_menu(event, user):
    """顯示主選單"""
    if user.user_type == 'passenger':
        menu_text = """🚖 機場接送服務

請選擇功能：
1️⃣ 預約機場接送
2️⃣ 查詢我的訂單
3️⃣ 取消訂單
4️⃣ 聯繫客服

請回覆對應數字或直接說明需求。"""
    else:
        menu_text = """🚗 司機服務面板

您目前的狀態：✅ 在線上

• 等待新訂單通知...
• 回覆「可接」接受訂單
• 回覆「無法接單」拒絕訂單
• 如需取消已接訂單，請聯繫客服

感謝您的服務！"""

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=menu_text)
    )

@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    try:
        print("🚀 開始啟動應用程式...")
        
        # 初始化資料庫
        db_manager.init_database()
        
        # 啟動應用
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 伺服器啟動在 http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except Exception as e:
        print(f"💥 程式啟動失敗: {e}")
        logger.error(f"程式啟動失敗: {e}") 