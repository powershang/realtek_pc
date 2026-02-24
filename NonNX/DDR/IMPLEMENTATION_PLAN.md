# DDR Register Comparison Tool - GUI & Windows Executable Plan

## Overview
將現有的 DDR Register Comparison CLI 工具轉換為 GUI 應用程式，並打包成 Windows 可執行檔 (.exe)。

---

## 技術選擇

### GUI Framework: **Tkinter**
- Python 內建，無需額外安裝
- 打包後檔案較小 (~15-20MB vs PyQt 的 100MB+)
- 功能足夠應付此工具需求（檔案選擇、文字顯示、按鈕）
- 授權友善，無商業限制

### 打包工具: **PyInstaller**
- 支援 `--onefile` 產生單一 .exe 檔
- 支援 `--windowed` 隱藏命令列視窗
- 社群支援度高，問題容易解決
- 自動處理 tkinter 相依性

---

## GUI 介面設計

```
+------------------------------------------------------------------+
|  DDR Register Comparison Tool                              [_][X] |
+------------------------------------------------------------------+
|  File Selection                                                   |
|  +--------------------------------------------------------------+ |
|  | File 1 (*.tbl): [________________________] [Browse...]       | |
|  | File 2 (*.tbl): [________________________] [Browse...]       | |
|  | Regfile (*.v):  [________________________] [Browse...] [x]   | |
|  +--------------------------------------------------------------+ |
|                                                                   |
|  [Compare]  [Clear]  [Export Report...]                          |
|                                                                   |
|  +--------------------------------------------------------------+ |
|  | Results (Scrollable Text Area)                               | |
|  | ========================================                     | |
|  | Register Comparison Report                                   | |
|  | ...                                                          | |
|  +--------------------------------------------------------------+ |
|                                                                   |
|  Status: Ready                                                    |
+------------------------------------------------------------------+
```

### 主要功能
1. **檔案選擇** - 三個輸入框 + Browse 按鈕選擇 .tbl 和 .v 檔
2. **Compare 按鈕** - 執行比較並顯示結果
3. **Clear 按鈕** - 清除所有輸入和結果
4. **Export Report 按鈕** - 將結果儲存為 .txt/.log 檔
5. **結果顯示區** - 可捲動的文字區域，使用等寬字體
6. **狀態列** - 顯示目前狀態和差異數量

---

## 實作步驟

### 步驟 1: 重構核心邏輯
修改 `register_comparer.py`，將 `print_*` 函式改為 `format_*` 函式

### 步驟 2: 建立 GUI 應用程式
新增 `gui_app.py`

### 步驟 3: 建立主程式進入點
新增 `main.py`

### 步驟 4: 打包成 Windows 執行檔
```
pip install pyinstaller
pyinstaller --onefile --windowed --name "DDR_Register_Comparer" main.py
```

---

## 檔案結構 (實作後)

```
DDR/
├── register_comparer.py   # 核心邏輯 (修改: 新增 format_* 函式)
├── gui_app.py             # GUI 應用程式 (新增)
├── main.py                # 主程式進入點 (新增)
├── build.bat              # 打包腳本 (新增)
└── dist/
    └── DDR_Register_Comparer.exe  # 打包產出
```
