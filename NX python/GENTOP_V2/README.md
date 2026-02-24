# GENTOP_V2 — Verilog 連線產生器 v2

GENTOP 的增強版，支援 Comment 標記與 Pattern 兩種方式產生 Realtek 連線腳本，並新增 DPI Pad 合併、Port 差異比對等功能。

## 工具清單

### `rtk_conn_by_comment.py` — Comment 標記連線產生器

解析 Verilog 中帶有特殊 comment 標記的訊號，自動轉換為 Realtek 格式。

支援兩種 comment 類型：
- `// realtekshane wire` — 產生 wire 連線
- `// realtekshane port` — 產生 port 宣告

**用法：**
```bash
python rtk_conn_by_comment.py <verilog_file>
```

---

### `rtk_conn_by_pattern.py` — Pattern 連線產生器（v2）

功能同 GENTOP v1，為 v2 的改進版本。

---

### `rtk_conn_gen_align_bitwidth.py` — 位元寬度對齊連線產生器

自動對齊訊號位元寬度並產生連線腳本。

---

### `module_chk_port_diff.py` — Module Port 差異比對

比對兩個 Verilog module 的 port 差異，找出新增或移除的 port。

**用法：**
```bash
python module_chk_port_diff.py <new_file.v> <old_file.v>
```

---

### `module_wire_name_prefixer.py` — Wire 名稱前綴加入器

批次為 module 內的 wire 名稱加上指定前綴。

---

### `merge_dpi_pad.py` — DPI Pad 合併工具

使用 `module_chk_port_diff.py` 找出新增的 inout 訊號，並自動產生：
- `.name(name)` 連線語句
- `wire name;` 宣告
- `assign name = 1'b1;`（含 vcc/vdd 的訊號）
- `assign name = 1'b0;`（含 gnd 的訊號）

**用法：**
```bash
python merge_dpi_pad.py <new_file.v> <old_file.v>
```
