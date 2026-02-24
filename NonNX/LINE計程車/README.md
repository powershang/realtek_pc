# Line 官方帳號計程車媒合系統

一個完整的機場接送自動化媒合平台，透過 Line 官方帳號連接乘客與司機，實現自動派單、搶單、轉單等功能。

## 📋 專案概述

本系統提供以下核心功能：
- 🚖 乘客透過 Line 官方帳號下單機場接送服務
- 👥 自動通知多位司機搶單
- ⚡ 即時媒合第一個接單的司機
- 🔄 支援司機取消與自動轉單
- 📊 完整的訂單追蹤與狀態管理
- 📱 友善的 Line Bot 互動介面

## 🏗️ 技術架構

### 後端技術棧
- **框架**: Flask (Python 3.8+)
- **資料庫**: PostgreSQL 15
- **Line SDK**: line-bot-sdk-python 3.5.0
- **部署平台**: Render.com
- **Web Server**: Gunicorn

### 資料庫設計
```sql
-- 主要資料表
users               # 用戶資料（乘客/司機）
ride_requests       # 乘車需求
driver_responses    # 司機回覆記錄
order_logs         # 訂單操作日誌
```

### 系統架構圖
```
Line Official Account
        ↓
   Webhook (Flask)
        ↓
  Business Logic
        ↓
   PostgreSQL DB
        ↓
 Message Broadcasting
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 克隆專案
git clone <repository-url>
cd line-taxi-matching-system

# 安裝依賴
pip install -r requirements.txt
```

### 2. 環境變數設定

複製 `env_example.txt` 並重新命名為 `.env`，填入以下資訊：

```env
# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=your_line_bot_access_token
LINE_CHANNEL_SECRET=your_line_bot_channel_secret

# 資料庫設定
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# 應用程式設定
FLASK_ENV=development
PORT=5000
```

### 3. 資料庫初始化

```bash
python -c "from database import DatabaseManager; DatabaseManager().init_database()"
```

### 4. 本地開發

```bash
python app.py
```

應用程式將在 `http://localhost:5000` 啟動

## 🌐 Render.com 部署

### 1. 建立 Render 服務

1. 登入 [Render.com](https://render.com)
2. 連接您的 GitHub 儲存庫
3. 建立 PostgreSQL 資料庫服務
4. 建立 Web 服務

### 2. 環境變數設定

在 Render 服務面板中設定以下環境變數：

```
LINE_CHANNEL_ACCESS_TOKEN=<your_token>
LINE_CHANNEL_SECRET=<your_secret>
DATABASE_URL=<render_postgresql_url>
FLASK_ENV=production
```

### 3. Line Bot Webhook 設定

1. 進入 [Line Developers Console](https://developers.line.biz/)
2. 設定 Webhook URL: `https://your-app-name.onrender.com/callback`
3. 啟用 Webhook 接收訊息

## 📱 使用說明

### 乘客使用流程

1. **加入好友**: 掃描 Line Bot QR Code
2. **身份註冊**: 選擇「我是乘客」
3. **下單**: 發送機場接送需求
   ```
   上車地點: 台北車站東三門
   下車地點: 桃園機場第二航廈
   預約時間: 12/25 08:30
   乘客人數: 2
   特殊需求: 有大件行李
   ```
4. **等待媒合**: 系統自動通知司機
5. **獲得司機資訊**: 收到司機聯絡方式

### 司機使用流程

1. **加入好友**: 掃描 Line Bot QR Code
2. **身份註冊**: 選擇「我是司機」並填寫資料
3. **接收通知**: 收到新訂單推播
4. **回覆接單**: 點擊「可接單」或「無法接單」
5. **獲得訂單**: 第一個接單者獲得乘客資訊

## 🔧 核心功能詳解

### 自動媒合流程

```python
# 媒合邏輯示例
1. 乘客下單 → 創建訂單記錄
2. 廣播通知 → 推送給所有活躍司機
3. 司機回覆 → 記錄回覆順序
4. 第一接單 → 自動指派司機
5. 通知結果 → 告知乘客與其他司機
```

### 轉單機制

```python
# 轉單邏輯
if 司機取消:
    backup_drivers = 獲取備用司機清單()
    if backup_drivers:
        轉單給下一位司機()
    else:
        通知乘客無法媒合()
```

### 錯誤處理

- **網路錯誤**: 自動重試機制
- **資料庫錯誤**: 友善錯誤提示
- **Line API 限制**: 流量控制與錯誤處理
- **用戶輸入錯誤**: 格式驗證與引導修正

## 📊 監控與維護

### 日誌系統
- 所有操作記錄在 `order_logs` 表
- 支援訂單狀態追蹤
- 錯誤日誌自動記錄

### 效能監控
```bash
# 查看應用狀態
curl https://your-app.onrender.com/health

# 回應範例
{
  "status": "healthy", 
  "timestamp": "2024-01-01T12:00:00"
}
```

### 資料庫維護
```python
# 清理舊日誌
from database import DatabaseManager
db = DatabaseManager()
db.cleanup_old_logs(days=30)  # 清理30天前的日誌
```

## ⚠️ 注意事項與限制

### Line API 限制
- **免費方案**: 每月1000則推播訊息
- **回覆訊息**: 無限制，但須在30秒內回覆
- **群播限制**: 建議分批發送避免API限制

### Render.com 限制
- **免費方案**: 
  - 15分鐘無活動會休眠
  - PostgreSQL 容量限制 1GB
  - 每月750小時運行時間

### 擴展建議
- **付費升級**: 生產環境建議使用付費方案
- **快取機制**: 加入 Redis 提升效能
- **負載平衡**: 多實例部署處理高流量
- **監控系統**: 整合 Sentry 或 Datadog

## 🔒 安全考量

- ✅ Webhook 簽章驗證
- ✅ 環境變數保護敏感資訊
- ✅ SQL 注入防護
- ✅ 用戶權限驗證
- ✅ HTTPS 加密傳輸

## 🤝 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📝 版本歷史

- **v1.0.0** - 初始版本
  - 基礎媒合功能
  - Line Bot 整合
  - 資料庫設計

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡資訊

- **開發者**: [Your Name]
- **Email**: [your.email@example.com]
- **專案連結**: [https://github.com/yourusername/line-taxi-matching](https://github.com/yourusername/line-taxi-matching)

---

**⭐ 如果這個專案對您有幫助，請不吝給個星星！** 