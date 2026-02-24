#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
from models import User, RideRequest, DriverResponse, OrderLog

logger = logging.getLogger(__name__)

class DatabaseManager:
    """資料庫管理器"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        
        # 打印資料庫網址進行除錯
        print("=" * 50)
        print("Supabase 資料庫連接除錯資訊:")
        if self.database_url:
            if "supabase.co" in self.database_url:
                # 隱藏密碼，只顯示主機資訊
                parts = self.database_url.split("@")
                if len(parts) > 1:
                    host_part = parts[1].split("/")[0]
                    print(f"✅ Supabase DATABASE_URL 已設定")
                    print(f"🏢 Supabase 主機: {host_part}")
                else:
                    print(f"✅ DATABASE_URL 已設定")
            else:
                print(f"⚠️  非 Supabase 連接: {self.database_url[:50]}...")
        else:
            print("❌ DATABASE_URL 未設定")
            print("🔍 請檢查 .env 檔案是否包含正確的 Supabase DATABASE_URL")
        print("=" * 50)
        
        if not self.database_url:
            logger.error("DATABASE_URL not found in environment variables")
            
    def get_connection(self):
        """取得資料庫連接"""
        try:
            print(f"🔗 嘗試連接 Supabase 資料庫...")
            
            # Supabase 需要 SSL 連接
            if "?sslmode=" not in self.database_url:
                connection_string = self.database_url + "?sslmode=require"
            else:
                connection_string = self.database_url
                
            conn = psycopg2.connect(connection_string)
            print("✅ Supabase 資料庫連接成功！")
            return conn
            
        except Exception as e:
            print(f"❌ Supabase 資料庫連接失敗: {e}")
            logger.error(f"資料庫連接失敗: {e}")
            raise
    
    def init_database(self):
        """初始化資料庫表格"""
        try:
            print("🚀 開始初始化 Supabase 資料庫...")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 創建 users 表
            print("📋 創建 users 表...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('passenger', 'driver')),
                    name VARCHAR(255),
                    phone VARCHAR(50),
                    line_id VARCHAR(255),
                    car_plate VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 創建 ride_requests 表
            print("📋 創建 ride_requests 表...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ride_requests (
                    request_id VARCHAR(255) PRIMARY KEY,
                    passenger_id VARCHAR(255) NOT NULL,
                    pickup_location TEXT NOT NULL,
                    dropoff_location TEXT NOT NULL,
                    pickup_time TIMESTAMP NOT NULL,
                    passenger_count INTEGER NOT NULL,
                    special_notes TEXT,
                    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'assigned', 'completed', 'cancelled')),
                    assigned_driver_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (passenger_id) REFERENCES users(user_id),
                    FOREIGN KEY (assigned_driver_id) REFERENCES users(user_id)
                )
            """)
            
            # 創建 driver_responses 表
            print("📋 創建 driver_responses 表...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS driver_responses (
                    response_id VARCHAR(255) PRIMARY KEY,
                    request_id VARCHAR(255) NOT NULL,
                    driver_id VARCHAR(255) NOT NULL,
                    response_type VARCHAR(50) NOT NULL CHECK (response_type IN ('accept', 'reject')),
                    response_order INTEGER NOT NULL,
                    response_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_backup BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (request_id) REFERENCES ride_requests(request_id),
                    FOREIGN KEY (driver_id) REFERENCES users(user_id)
                )
            """)
            
            # 創建 order_logs 表
            print("📋 創建 order_logs 表...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_logs (
                    log_id VARCHAR(255) PRIMARY KEY,
                    request_id VARCHAR(255) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    actor_id VARCHAR(255),
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES ride_requests(request_id)
                )
            """)
            
            # 創建索引
            print("🔍 創建索引...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ride_requests_status ON ride_requests(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ride_requests_passenger ON ride_requests(passenger_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_driver_responses_request ON driver_responses(request_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_type_active ON users(user_type, is_active)")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Supabase 資料庫初始化完成！")
            logger.info("Supabase 資料庫初始化完成")
            
        except Exception as e:
            print(f"❌ Supabase 資料庫初始化失敗: {e}")
            logger.error(f"資料庫初始化失敗: {e}")
            raise
    
    # User 相關操作
    def create_user(self, user):
        """創建用戶"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (user_id, user_type, name, phone, line_id, car_plate, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user.user_id, user.user_type, user.name, user.phone, 
                  user.line_id, user.car_plate, user.is_active))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"創建用戶失敗: {e}")
            raise
    
    def get_user(self, user_id):
        """取得用戶資訊"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if row:
                return User(**dict(row))
            return None
            
        except Exception as e:
            logger.error(f"取得用戶失敗: {e}")
            return None
    
    def get_active_drivers(self):
        """取得所有活躍司機"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM users 
                WHERE user_type = 'driver' AND is_active = TRUE
            """)
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [User(**dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"取得活躍司機失敗: {e}")
            return []
    
    def update_user(self, user_id, **kwargs):
        """更新用戶資訊"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 動態建立更新語句
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if hasattr(User, key):
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if set_clauses:
                set_clauses.append("updated_at = %s")
                values.append(datetime.now())
                values.append(user_id)
                
                sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = %s"
                cursor.execute(sql, values)
                
                conn.commit()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"更新用戶失敗: {e}")
            raise
    
    # RideRequest 相關操作
    def create_ride_request(self, ride_request):
        """創建乘車請求"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ride_requests 
                (request_id, passenger_id, pickup_location, dropoff_location, 
                 pickup_time, passenger_count, special_notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (ride_request.request_id, ride_request.passenger_id, 
                  ride_request.pickup_location, ride_request.dropoff_location,
                  ride_request.pickup_time, ride_request.passenger_count,
                  ride_request.special_notes, ride_request.status))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"創建乘車請求失敗: {e}")
            raise
    
    def get_ride_request(self, request_id):
        """取得乘車請求"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM ride_requests WHERE request_id = %s", (request_id,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if row:
                return RideRequest(**dict(row))
            return None
            
        except Exception as e:
            logger.error(f"取得乘車請求失敗: {e}")
            return None
    
    def update_ride_request_driver(self, request_id, driver_id):
        """更新訂單指派司機"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ride_requests 
                SET assigned_driver_id = %s, updated_at = %s 
                WHERE request_id = %s
            """, (driver_id, datetime.now(), request_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"更新指派司機失敗: {e}")
            raise
    
    def update_ride_request_status(self, request_id, status):
        """更新訂單狀態"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE ride_requests 
                SET status = %s, updated_at = %s 
                WHERE request_id = %s
            """, (status, datetime.now(), request_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"更新訂單狀態失敗: {e}")
            raise
    
    def get_user_ride_requests(self, user_id, status=None):
        """取得用戶的訂單"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if status:
                cursor.execute("""
                    SELECT * FROM ride_requests 
                    WHERE passenger_id = %s AND status = %s 
                    ORDER BY created_at DESC
                """, (user_id, status))
            else:
                cursor.execute("""
                    SELECT * FROM ride_requests 
                    WHERE passenger_id = %s 
                    ORDER BY created_at DESC
                """, (user_id,))
            
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [RideRequest(**dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"取得用戶訂單失敗: {e}")
            return []
    
    # DriverResponse 相關操作
    def create_driver_response(self, driver_response):
        """創建司機回覆"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO driver_responses 
                (response_id, request_id, driver_id, response_type, response_order)
                VALUES (%s, %s, %s, %s, %s)
            """, (driver_response.response_id, driver_response.request_id,
                  driver_response.driver_id, driver_response.response_type,
                  driver_response.response_order))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"創建司機回覆失敗: {e}")
            raise
    
    def get_driver_responses(self, request_id):
        """取得訂單的所有司機回覆"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM driver_responses 
                WHERE request_id = %s 
                ORDER BY response_time ASC
            """, (request_id,))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [DriverResponse(**dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"取得司機回覆失敗: {e}")
            return []
    
    def count_driver_responses(self, request_id):
        """計算訂單的回覆數量"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM driver_responses WHERE request_id = %s", (request_id,))
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"計算回覆數量失敗: {e}")
            return 0
    
    def set_backup_driver(self, response_id, is_backup):
        """設定備用司機"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE driver_responses 
                SET is_backup = %s 
                WHERE response_id = %s
            """, (is_backup, response_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"設定備用司機失敗: {e}")
            raise
    
    def get_backup_drivers(self, request_id):
        """取得備用司機清單"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM driver_responses 
                WHERE request_id = %s AND response_type = 'accept' AND is_backup = TRUE
                ORDER BY response_time ASC
            """, (request_id,))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [DriverResponse(**dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"取得備用司機失敗: {e}")
            return []
    
    # OrderLog 相關操作
    def create_order_log(self, order_log):
        """創建訂單日誌"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO order_logs (log_id, request_id, action, actor_id, details)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_log.log_id, order_log.request_id, order_log.action,
                  order_log.actor_id, order_log.details))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"創建訂單日誌失敗: {e}")
            raise
    
    def get_order_logs(self, request_id):
        """取得訂單日誌"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM order_logs 
                WHERE request_id = %s 
                ORDER BY created_at ASC
            """, (request_id,))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [OrderLog(**dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"取得訂單日誌失敗: {e}")
            return []
    
    def cleanup_old_logs(self, days=30):
        """清理舊日誌（超過指定天數）"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM order_logs 
                WHERE created_at < NOW() - INTERVAL '%s days'
            """, (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"已清理 {deleted_count} 筆舊日誌")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理舊日誌失敗: {e}")
            return 0 