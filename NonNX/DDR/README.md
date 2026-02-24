# DDR Register Comparison Tool

DDR 暫存器比較工具，用於比較兩個 register dump 檔案 (.tbl) 的差異。

## 安裝需求

- Python 3.8+
- tkinter (GUI 版本需要)

## 使用方式

### GUI 版本

```bash
python main.py
```

或直接執行打包後的執行檔：
```
dist\DDR_Register_Comparer.exe
```

### CLI 版本

```bash
# 比較兩個檔案
python register_comparer.py file1.tbl file2.tbl

# 使用預設檔案 (SW_SDP.tbl vs SW_DDP.tbl)
python register_comparer.py

# 指定 regfile 進行 register name mapping
python register_comparer.py file1.tbl file2.tbl --regfile dc_mc1_regfile.v

# 顯示 register map 參考表
python register_comparer.py --show-map
```

#### CLI 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `file1` | 第一個 .tbl 檔案 | SW_SDP.tbl |
| `file2` | 第二個 .tbl 檔案 | SW_DDP.tbl |
| `--regfile`, `-r` | Regfile 路徑 (*.v) | dc_mc1_regfile.v |
| `--ddr-type`, `-t` | DDR 類型 (LPDDR4/LPDDR5) | LPDDR4 |
| `--show-map` | 顯示 register map | - |

## 打包成執行檔

```bash
# 執行 build script
build.bat
```

或手動執行：
```bash
python generate_embedded_regmap.py
pyinstaller --onefile --windowed --name "DDR_Register_Comparer" --clean main.py
```

輸出檔案：`dist\DDR_Register_Comparer.exe`

**注意**：Build 前請確保 `dc_mc1_regfile.v` 存在於專案根目錄。

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `main.py` | GUI 程式進入點 |
| `gui_app.py` | GUI 介面實作 |
| `register_comparer.py` | CLI 版本 / 核心比較邏輯 |
| `generate_embedded_regmap.py` | 生成內建 regmap (打包用) |
| `embedded_regmap.py` | 內建 register map 資料 |
| `dc_mc1_regfile.v` | Register 定義檔 |

## 支援的 DDR 類型

- LPDDR4
- LPDDR5
