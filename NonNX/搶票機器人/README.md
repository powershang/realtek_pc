# 搶票機器人 — 拓元自動訂票程式（GUI 版）

使用 Selenium 自動化拓元售票網（tixcraft.com）購票流程，提供圖形化操作介面。

## 功能

- 自動登入、選場次、選座位
- GUI 控制面板（tkinter）
- 多執行緒執行，可隨時停止
- 驗證碼截圖輔助（`captcha_screenshot.png`）
- 設定檔管理（`config.json`）

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `gui.py` | 主程式 GUI 介面 |
| `gui_pass.py` | 略過驗證碼版本 |
| `test.py` | 核心自動化邏輯 |
| `test_pass.py` | 略過驗證碼的核心邏輯 |
| `config.json` | 帳號、場次等設定 |

## 用法

```bash
python gui.py
```

## 需求

```bash
pip install selenium
```

需安裝對應版本的 ChromeDriver。

> **注意：** 本工具僅供個人學習使用，請勿用於非法用途。
