# Line 計程車媒合系統 - 部署指南

## 🚀 Render.com 部署步驟

### 1. 前置準備

#### 1.1 Line Bot 設定
1. 登入 [Line Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Channel (Messaging API)
3. 記錄以下資訊：
   - Channel Access Token
   - Channel Secret
4. 設定 Webhook URL (稍後填入)

#### 1.2 GitHub 準備
1. 將專案代碼推送到 GitHub 儲存庫
2. 確保以下檔案存在：
   - `requirements.txt`
   - `app.py`
   - `render.yaml`

### 2. Render.com 設定

#### 2.1 建立帳號
1. 前往 [Render.com](https://render.com)
2. 使用 GitHub 帳號註冊
3. 授權 Render 存取您的 GitHub 儲存庫

#### 2.2 建立 PostgreSQL 資料庫
1. 在 Render Dashboard 點擊 "New +"
2. 選擇 "PostgreSQL"
3. 設定資料庫：
   ```
   Name: line-taxi-db
   Database: line_taxi_production
   User: line_user
   Region: Singapore (最接近台灣)
   Plan: Free
   ```
4. 點擊 "Create Database"
5. 等待建立完成，記錄 "External Database URL"

#### 2.3 建立 Web Service
1. 在 Dashboard 點擊 "New +"
2. 選擇 "Web Service"
3. 連接 GitHub 儲存庫：
   ```
   Repository: 您的專案儲存庫
   Branch: main 或 master
   ```
4. 設定服務：
   ```
   Name: line-taxi-bot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   Plan: Free
   ```

#### 2.4 設定環境變數
在 Web Service 設定頁面的 Environment 區段添加：

```env
LINE_CHANNEL_ACCESS_TOKEN=你的Line Bot Channel Access Token
LINE_CHANNEL_SECRET=你的Line Bot Channel Secret
DATABASE_URL=postgresql://...（從步驟2.2複製）
FLASK_ENV=production
PORT=10000
```

### 3. 部署與測試

#### 3.1 初次部署
1. 點擊 "Create Web Service"
2. Render 會自動：
   - 拉取 GitHub 代碼
   - 安裝依賴套件
   - 啟動應用程式
3. 等待部署完成（通常需要 3-5 分鐘）

#### 3.2 取得服務 URL
部署完成後，您會獲得一個 URL：
```
https://your-service-name.onrender.com
```

#### 3.3 設定 Line Bot Webhook
1. 回到 Line Developers Console
2. 在您的 Channel 設定中：
   ```
   Webhook URL: https://your-service-name.onrender.com/callback
   Use webhook: 啟用
   ```
3. 點擊 "Verify" 測試連接

#### 3.4 初始化資料庫
使用 Render Web Service 的 Shell 功能：
1. 在 Service 頁面點擊 "Shell"
2. 執行：
   ```bash
   python -c "from database import DatabaseManager; DatabaseManager().init_database()"
   ```

### 4. 測試系統功能

#### 4.1 基本健康檢查
訪問：`https://your-service-name.onrender.com/health`
應該回傳：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 4.2 Line Bot 測試
1. 掃描 Line Bot QR Code 加為好友
2. 發送任意訊息測試回覆
3. 測試註冊流程（乘客/司機）
4. 測試下單流程

### 5. 監控與維護

#### 5.1 查看應用程式日誌
在 Render Service 頁面的 "Logs" 分頁可以查看：
- 應用程式啟動日誌
- 錯誤訊息
- API 請求記錄

#### 5.2 資料庫管理
使用 Render PostgreSQL 的連接資訊：
```bash
# 本地連接資料庫（需安裝 psql）
psql postgresql://username:password@hostname:port/database
```

#### 5.3 自動部署設定
在 GitHub 儲存庫設定自動部署：
1. 推送到 main 分支自動觸發部署
2. 在 Render Service 設定中啟用 "Auto-Deploy"

### 6. 注意事項與限制

#### 6.1 Render Free Plan 限制
- **服務休眠**: 15分鐘無活動會自動休眠
- **冷啟動**: 休眠後首次請求需要 30-60 秒喚醒
- **運行時間**: 每月限制 750 小時
- **資料庫**: PostgreSQL 限制 1GB 儲存空間

#### 6.2 Line API 限制
- **免費推播**: 每月 1000 則訊息
- **回覆時限**: 必須在 30 秒內回覆
- **群組推播**: 建議批次發送避免頻率限制

#### 6.3 生產環境建議
- **升級付費方案**: 避免服務休眠
- **監控設定**: 使用 Sentry 或其他監控工具
- **備份策略**: 定期備份資料庫
- **錯誤處理**: 完善的例外處理機制

### 7. 故障排除

#### 7.1 常見問題

**問題**: Webhook 驗證失敗
```
解決方案:
1. 檢查 Channel Secret 是否正確
2. 確認 URL 可以正常訪問
3. 檢查 SSL 憑證是否有效
```

**問題**: 資料庫連接失敗
```
解決方案:
1. 檢查 DATABASE_URL 格式
2. 確認資料庫服務是否正常運行
3. 檢查網路連接
```

**問題**: 應用程式無法啟動
```
解決方案:
1. 檢查 requirements.txt 依賴
2. 查看部署日誌找出錯誤原因
3. 確認環境變數設定正確
```

#### 7.2 除錯技巧

**啟用除錯模式**（僅開發環境）:
```python
# 在 app.py 中
if os.getenv('FLASK_ENV') == 'development':
    app.debug = True
```

**查看詳細日誌**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 8. 升級與擴展

#### 8.1 效能優化
- 使用 Redis 快取常用資料
- 實施資料庫連接池
- 優化 SQL 查詢

#### 8.2 功能擴展
- 支援多語言
- 加入支付系統
- 實時位置追蹤
- 評價系統

#### 8.3 架構升級
- 微服務架構
- 訊息佇列系統
- 負載平衡器
- CDN 加速

### 9. 安全性檢查清單

- ✅ HTTPS 強制使用
- ✅ 環境變數保護敏感資訊
- ✅ Webhook 簽章驗證
- ✅ SQL 注入防護
- ✅ 用戶權限驗證
- ✅ API 請求頻率限制
- ✅ 錯誤訊息不洩露敏感資訊

### 10. 支援與聯絡

如果在部署過程中遇到問題：

1. **文檔參考**: 
   - [Render.com 官方文檔](https://render.com/docs)
   - [Line Messaging API 文檔](https://developers.line.biz/en/docs/messaging-api/)

2. **社群支援**:
   - Render Discord 社群
   - Line Developers 社群

3. **專案問題**:
   - 在 GitHub Issues 中提出問題
   - 聯繫專案維護者

---

**🎉 恭喜！您的 Line 計程車媒合系統已成功部署！** 