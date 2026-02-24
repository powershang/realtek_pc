# RTLdiss — RTL 電路研究筆記

RTL 電路設計的研究與解析筆記，目前包含 AXI Bridge 的實作研究。

## 內容

### AXI Bridge

- `axi_bridge.txt` — AXI Bridge 標準實作（FIFO-based，含 full/empty 控制）
- `axi_brigde_my_version.txt` — 個人改寫版本

**電路介面：**
```
輸入：clk, rst_n
寫入：winc, din → wfull
讀取：rinc → rempty, dout
```

採用 2-bit Gray Code 指標實作同步 FIFO，適用於跨 clock domain 的資料傳輸。
