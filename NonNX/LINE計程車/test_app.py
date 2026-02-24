#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, timedelta
from models import User, RideRequest, UserType, RideStatus
from utils import MessageParser, TimeUtils, ValidationUtils

class TestMessageParser(unittest.TestCase):
    """測試訊息解析器"""
    
    def test_parse_ride_request_valid(self):
        """測試有效的乘車需求解析"""
        message = """上車地點: 台北車站東三門
下車地點: 桃園機場第二航廈
預約時間: 12/25 08:30
乘客人數: 2
特殊需求: 有大件行李"""
        
        result = MessageParser.parse_ride_request(message)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['pickup_location'], '台北車站東三門')
        self.assertEqual(result['dropoff_location'], '桃園機場第二航廈')
        self.assertEqual(result['passenger_count'], 2)
        self.assertEqual(result['special_notes'], '有大件行李')
    
    def test_parse_ride_request_invalid(self):
        """測試無效的乘車需求解析"""
        message = "我要搭車"
        result = MessageParser.parse_ride_request(message)
        self.assertIsNone(result)
    
    def test_parse_datetime(self):
        """測試時間解析"""
        time_str = "12/25 08:30"
        result = MessageParser.parse_datetime(time_str)
        self.assertIsNotNone(result)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 25)
        self.assertEqual(result.hour, 8)
        self.assertEqual(result.minute, 30)
    
    def test_parse_command(self):
        """測試指令解析"""
        command, param = MessageParser.parse_command("接單 abc123")
        self.assertEqual(command, "accept_order")
        self.assertEqual(param, "abc123")

class TestTimeUtils(unittest.TestCase):
    """測試時間工具"""
    
    def test_format_datetime(self):
        """測試時間格式化"""
        dt = datetime(2023, 12, 25, 8, 30)
        result = TimeUtils.format_datetime(dt)
        self.assertEqual(result, "12/25 08:30")
    
    def test_is_future_time(self):
        """測試未來時間檢查"""
        future_time = datetime.now() + timedelta(hours=1)
        past_time = datetime.now() - timedelta(hours=1)
        
        self.assertTrue(TimeUtils.is_future_time(future_time, buffer_minutes=0))
        self.assertFalse(TimeUtils.is_future_time(past_time, buffer_minutes=0))

class TestValidationUtils(unittest.TestCase):
    """測試驗證工具"""
    
    def test_validate_phone(self):
        """測試電話號碼驗證"""
        self.assertTrue(ValidationUtils.validate_phone("0912345678"))
        self.assertFalse(ValidationUtils.validate_phone("123456789"))
        self.assertFalse(ValidationUtils.validate_phone("09123456789"))
    
    def test_validate_car_plate(self):
        """測試車牌驗證"""
        self.assertTrue(ValidationUtils.validate_car_plate("ABC-1234"))
        self.assertTrue(ValidationUtils.validate_car_plate("1234-AB"))
        self.assertFalse(ValidationUtils.validate_car_plate("123"))
    
    def test_validate_passenger_count(self):
        """測試乘客人數驗證"""
        self.assertTrue(ValidationUtils.validate_passenger_count(2))
        self.assertTrue(ValidationUtils.validate_passenger_count(8))
        self.assertFalse(ValidationUtils.validate_passenger_count(0))
        self.assertFalse(ValidationUtils.validate_passenger_count(9))

class TestModels(unittest.TestCase):
    """測試資料模型"""
    
    def test_user_creation(self):
        """測試用戶創建"""
        user = User(
            user_id="test123",
            user_type=UserType.PASSENGER,
            name="測試用戶"
        )
        
        self.assertEqual(user.user_id, "test123")
        self.assertEqual(user.user_type, UserType.PASSENGER)
        self.assertEqual(user.name, "測試用戶")
        self.assertTrue(user.is_active)
    
    def test_ride_request_creation(self):
        """測試乘車請求創建"""
        pickup_time = datetime.now() + timedelta(hours=2)
        
        ride_request = RideRequest(
            request_id="req123",
            passenger_id="passenger123",
            pickup_location="台北車站",
            dropoff_location="桃園機場",
            pickup_time=pickup_time,
            passenger_count=2
        )
        
        self.assertEqual(ride_request.request_id, "req123")
        self.assertEqual(ride_request.passenger_id, "passenger123")
        self.assertEqual(ride_request.status, RideStatus.PENDING)

if __name__ == '__main__':
    # 設定測試環境變數
    import os
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'test_token'
    os.environ['LINE_CHANNEL_SECRET'] = 'test_secret'
    
    unittest.main() 