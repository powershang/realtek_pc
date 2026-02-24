#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """用戶資料模型"""
    user_id: str
    user_type: str  # 'passenger' or 'driver'
    name: Optional[str] = None
    phone: Optional[str] = None
    line_id: Optional[str] = None
    car_plate: Optional[str] = None  # 司機專用
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class RideRequest:
    """乘車請求資料模型"""
    request_id: str
    passenger_id: str
    pickup_location: str
    dropoff_location: str
    pickup_time: datetime
    passenger_count: int
    special_notes: Optional[str] = None
    status: str = 'pending'  # 'pending', 'assigned', 'completed', 'cancelled'
    assigned_driver_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class DriverResponse:
    """司機回覆資料模型"""
    response_id: str
    request_id: str
    driver_id: str
    response_type: str  # 'accept' or 'reject'
    response_order: int
    response_time: Optional[datetime] = None
    is_backup: bool = False

@dataclass
class OrderLog:
    """訂單日誌資料模型"""
    log_id: str
    request_id: str
    action: str  # 'created', 'notified', 'assigned', 'cancelled', 'completed'
    actor_id: Optional[str] = None
    details: Optional[str] = None
    created_at: Optional[datetime] = None

# 常數定義
class UserType:
    PASSENGER = 'passenger'
    DRIVER = 'driver'

class RideStatus:
    PENDING = 'pending'
    ASSIGNED = 'assigned'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class ResponseType:
    ACCEPT = 'accept'
    REJECT = 'reject'

class LogAction:
    CREATED = 'created'
    NOTIFIED = 'notified'
    ASSIGNED = 'assigned'
    REASSIGNED = 'reassigned'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed' 