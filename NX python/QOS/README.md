# QOS — QoS Table Register 訊號檢查器

解析 Verilog regfile 與 RTD table，計算並分析 QoS 相關 register 訊號值。

## 工具

### `qos_tbl_checker.py`

**功能：**
- 解析 Verilog regfile 與 RTD `.tbl` 檔案
- 依 register 位址計算訊號值
- 支援多 channel 位址對應（`0x180c2` ~ `0x180c5`）
- 支援 `0x18` 與 `0xb8` 位址前綴等價
- 比對兩個 RTD 檔案的差異
- 依訊號名稱或位址過濾結果

**用法：**
```bash
# 分析 register 訊號
python qos_tbl_checker.py regfile.v rtdfile.tbl

# 輸出結果至檔案
python qos_tbl_checker.py regfile.v rtdfile.tbl -o results.txt

# 過濾特定訊號
python qos_tbl_checker.py regfile.v rtdfile.tbl -f "signal_name"

# 比對兩個 RTD 檔案
python qos_tbl_checker.py --compare file1.tbl file2.tbl

# 帶 regfile 的完整比對（建議）
python qos_tbl_checker.py regfile.v file1.tbl --compare file2.tbl
```
