# GENTOP — Verilog Port 連線分析器 v1（Pattern-Based）

透過 Port 名稱的 Pattern 比對，從 Verilog 檔案中搜尋 port，並自動產生 Realtek 連線腳本。

> **v2 版本** 請參考 [GENTOP_V2](../GENTOP_V2/)，功能更完整。

## 工具

### `rtk_conn_by_pattern.py`

**用法：**
```bash
python rtk_conn_by_pattern.py <verilog_file> <port_types> <direction> "<pattern1>" ["<pattern2>" ...]
```

**參數：**
- `port_types`：`input`、`output`、`inout`、`wire`（逗號分隔）
- `direction`：
  - `wire` — 產生連線腳本（receive port）
  - `io` — 產生 input/output 宣告（send port）
- `pattern`：支援萬用字元，如 `dfi_*`、`*_data`

**範例：**
```bash
# 產生所有 output port 中符合 "dfi_*" 的連線腳本
python rtk_conn_by_pattern.py design.v output wire "dfi_*"

# 產生 input/output port 中符合 "mc_*" 或 "dfi_*" 的 io 宣告
python rtk_conn_by_pattern.py design.v input,output io "mc_*" "dfi_*"

# 產生所有 inout port 中符合 "*_data" 的連線腳本
python rtk_conn_by_pattern.py design.v inout wire "*_data"
```

## 輸出格式

支援單 bit 與 bus 寬度訊號，自動辨識並產生對應的 wire 宣告或連線語句。
