# Register Signal Parser

這個工具可以解析 Verilog regfile 和 QoS table，找出每個 register 地址對應的訊號值。

## 功能

- 解析 Verilog regfile (`dc_mc1_regfile.v`) 中的 `assign` 語句
- 解析 QoS table (`QoS_384_4K120_v1.tbl`) 中的地址-值對應關係  
- 根據 bit field 定義計算每個訊號的實際值
- 支援多種過濾和查詢方式
- 可導出結果到文件

## 文件說明

### 核心文件
- `register_signal_parser.py` - 基本版本，專注於 ch3 範例驗證
- `signal_analyzer.py` - 增強版本，支援命令行參數和多種過濾方式

### 輸入文件
- `dc_mc1_regfile.v` - Verilog register file，包含訊號到 register 的映射
- `QoS_384_4K120_v1.tbl` - QoS 配置表，包含地址到值的映射

## 使用方法

### 基本用法

```bash
# 查看所有訊號
python signal_analyzer.py

# 顯示幫助信息
python signal_analyzer.py --help
```

### 按 Channel 過濾

```bash
# 查看 ch3 的所有訊號
python signal_analyzer.py --channel ch3

# 查看 ch0 的所有訊號（含詳細bit範圍資訊）
python signal_analyzer.py --channel ch0 --details
```

### 按地址過濾

```bash
# 查看特定地址的訊號
python signal_analyzer.py --address 180c2acc --details

# 查看地址範圍的訊號  
python signal_analyzer.py --address-range 180c2ac0:180c2ad0 --details
```

### 按訊號名稱過濾

```bash
# 查看包含 "cmd_extend" 的所有訊號
python signal_analyzer.py --signal cmd_extend

# 查看包含 "ostd" 的所有訊號
python signal_analyzer.py --signal ostd
```

### 導出結果

```bash
# 導出 ch3 訊號到文件
python signal_analyzer.py --channel ch3 --export ch3_analysis.txt

# 導出特定地址範圍到文件
python signal_analyzer.py --address-range 180c2a60:180c2aff --export qos_channels.txt
```

## 輸出格式

### 命令行輸出

```
=== Address 0x180C2ACC (Value: 0x40008081) ===
ch3_cmd_extend_num                  = reg180c2acc[31:28]      = 4      (0x4)
ch3_extend_bl_max                   = reg180c2acc[25:20]      = 0      (0x0)
ch3_ostd_bl_max                     = reg180c2acc[19:8]       = 128    (0x80)
ch3_ostd_cmd_max                    = reg180c2acc[7:4]        = 8      (0x8)
ch3_outstand_en                     = reg180c2acc[0]          = 1      (0x1)
```

### 文件輸出

導出的文件包含：
- 地址和對應的 register 值
- 每個訊號的名稱、bit 範圍和計算出的值
- 十進制和十六進制格式的值

## 範例驗證

根據用戶提供的範例：

**地址**: `0x180c2acc`  
**值**: `0x40008081`

解析結果：
- `ch3_cmd_extend_num = reg180c2acc[31:28] = 4`
- `ch3_extend_bl_max = reg180c2acc[25:20] = 0`  
- `ch3_ostd_bl_max = reg180c2acc[19:8] = 128`
- `ch3_ostd_cmd_max = reg180c2acc[7:4] = 8`
- `ch3_outstand_en = reg180c2acc[0] = 1`

✅ **驗證通過！**

## 命令行參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `--regfile` | 指定 regfile 路徑 | `--regfile my_regfile.v` |
| `--qos` | 指定 QoS table 路徑 | `--qos my_qos.tbl` |
| `--channel` | 按 channel 過濾 | `--channel ch3` |
| `--address` | 按特定地址過濾 | `--address 180c2acc` |
| `--address-range` | 按地址範圍過濾 | `--address-range 180c2ac0:180c2aff` |
| `--signal` | 按訊號名稱模式過濾 | `--signal cmd_extend` |
| `--details` | 顯示詳細的 bit 範圍資訊 | `--details` |
| `--export` | 導出結果到文件 | `--export results.txt` |

## 技術細節

### Bit Field 提取算法

對於 bit range `[start:end]`：
```python
mask = (1 << (start - end + 1)) - 1
value = (register_value >> end) & mask
```

對於單一 bit `[n]`：
```python
value = (register_value >> n) & 1
```

### 支援的格式

- **Verilog assign 語句**: `assign signal_name = reg180c2acc[31:28];`
- **QoS table 語句**: `rtd_outl(0x180c2acc,0x40008081);`
- **地址格式**: 支援大小寫混合的十六進制地址

## 故障排除

1. **找不到文件**: 確認 `dc_mc1_regfile.v` 和 `QoS_384_4K120_v1.tbl` 在當前目錄
2. **沒有結果**: 檢查過濾條件是否正確，嘗試不使用過濾器
3. **編碼問題**: 程序使用 UTF-8 編碼並忽略錯誤字元

## 範例腳本

```bash
# 快速查看 ch3 的關鍵訊號
python signal_analyzer.py --channel ch3 --signal "cmd_extend|ostd_bl_max|outstand_en"

# 分析所有 channel 的 cmd_extend_num 設定
python signal_analyzer.py --signal cmd_extend_num --export cmd_extend_analysis.txt

# 查看特定地址範圍的完整配置
python signal_analyzer.py --address-range 180c2a60:180c2b9f --details --export all_channels.txt
``` 