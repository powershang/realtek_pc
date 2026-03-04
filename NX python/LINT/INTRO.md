# W164a Lint Fixer - 修法介紹

## 什麼是 W164a？

W164a 是 LHS（左邊）位元數比 RHS（右邊）少的 width mismatch 警告。

```verilog
reg [7:0] counter;
counter <= counter + 8'd1;   // RHS 是 9-bit，LHS 只有 8-bit → W164a
```

lint 工具回報格式如下：

```
[1001]  W164a  N.A  error  foo.v  30  10  LHS: 'counter' width 8 is less than RHS: 'counter + 8'd1' width 9
```

---

## 修法核心概念：加 `_nc` 接住多餘的位元

修法不改 RHS，只在 LHS 補一個 **no-connect dummy bit** 來吸收溢出的位元：

```verilog
// Before
reg [7:0] counter;
counter <= counter + 8'd1;

// After
reg [7:0] counter;
reg counter_nc;                                 // 新增：接住第 9 bit
{counter_nc, counter} <= counter + 8'd1;       // W164a fixed by lint_fixer
```

---

## 整體處理流程

```
parse err.txt
    ↓
依 signal 分組（同一個 signal 可能有多個 error）
    ↓
對每個 signal：
    ↓
找 declaration（找 reg/wire 宣告在哪一行）
    ↓
判斷 assignment 類型
    ├── wire inline assign → 直接加寬 wire 位元數
    ├── assign statement  → 插入 wire _nc + 改 assign 行
    └── always block       → 插入 reg _nc + 改 block 內所有 assignments
```

---

## 三種 Case 的修法

### Case 1：always block 內的 reg

**步驟：**
1. 找到 `reg [7:0] signal;` 宣告在哪行
2. 在宣告的下一行插入 `reg signal_nc;`
3. 找到這個 signal 所在的 always block 範圍（靠 begin/end 計算深度）
4. 在 block 內找出**所有**對 signal 的 assignments，全部改成 `{signal_nc, signal} <= ...`

```verilog
// Before
reg [7:0] sig_reg_pure;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sig_reg_pure <= 8'd0;       // line 28
    end else begin
        sig_reg_pure <= sig_reg_pure + 8'd1;  // line 30 ← error line
    end
end

// After
reg [7:0] sig_reg_pure;
reg sig_reg_pure_nc;                // ← 插在宣告下一行

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_reg_pure_nc, sig_reg_pure} <= 8'd0;             // W164a fixed
    end else begin
        {sig_reg_pure_nc, sig_reg_pure} <= sig_reg_pure + 8'd1; // W164a fixed
    end
end
```

> **注意：** 雖然 err.txt 只報 line 30，程式仍然找出 block 內所有對這個 signal 的 assignment 一起改掉。

---

### Case 2：wire + assign statement

**步驟：**
1. 找到 `wire [7:0] signal;` 宣告
2. 插入 `wire signal_nc;`
3. 改 assign 那一行

```verilog
// Before
wire [7:0] sig_wire;

assign sig_wire = data_in;       // data_in 是 9-bit → W164a

// After
wire [7:0] sig_wire;
wire sig_wire_nc;                // ← 插入

assign {sig_wire_nc, sig_wire} = data_in; // W164a fixed by lint_fixer
```

---

### Case 3：wire inline assignment（拆開宣告 + _nc）

這種寫法宣告和賦值在同一行。v2.3 起改為拆開成三行，保留原始位元數：

```verilog
// Before
wire [7:0] sig_wire_inline = data_in;   // data_in 9-bit → W164a

// After (v2.3+)
wire [7:0] sig_wire_inline;             // 保留原寬度
wire sig_wire_inline_nc;                // _nc 吸收多餘 bit
assign {sig_wire_inline_nc, sig_wire_inline} = data_in; // W164a fixed by lint_fixer
```

> **為何不直接加寬？** 若把 `wire [7:0]` 改成 `wire [8:0]`，下游 RTL 中用到
> `sig_wire_inline` 的所有 LHS 連線寬度都會跟著改變，可能造成新的連線錯誤。

---

## 特殊情況

### output reg（宣告在 port list）

`output reg [7:0] sig_out_reg` 在 port list 裡，不能在 port list 內插入 `_nc`。
程式找到 `);` 的位置，把 `_nc` 插在 `);` 後面。

```verilog
module test_mod (
    ...
    output reg [7:0] sig_out_reg,   // 宣告在 port list 內
    ...
);
reg sig_out_reg_nc;                 // ← _nc 插在 ); 之後，而非 port list 內
```

---

### reg signed / wire signed

`_nc` 會繼承 `signed` 關鍵字：

```verilog
reg signed [7:0] sig_signed;
reg signed sig_signed_nc;          // ← signed 保留
{sig_signed_nc, sig_signed} <= data_in; // W164a fixed
```

---

### Array element：sig_arr[0]

array element 的 `_nc` 命名規則為 `信號名_index_nc`：

```verilog
reg signed [7:0] sig_arr[0:3];
reg signed sig_arr_0_nc;           // ← sig_arr[0] → sig_arr_0_nc
reg signed sig_arr_1_nc;

{sig_arr_0_nc, sig_arr[0]} <= data_in; // W164a fixed
{sig_arr_1_nc, sig_arr[1]} <= data_in; // W164a fixed
```

---

### 同一個 signal 有不同 RHS 寬度（per-line nc bit-select）

如果同一個 signal 在不同地方被賦值，RHS 的寬度不一樣：

```
sig_multi (8-bit) ← data_in     (9-bit)   → nc_width = 1
sig_multi (8-bit) ← {4'd0, data_in} (13-bit) → nc_width = 5
```

`_nc` 宣告用**最大差值**（5-bit），但每行只取實際需要的 bit：

```verilog
reg [7:0] sig_multi;
reg [4:0] sig_multi_nc;           // ← 用最大 nc_width = 5

// RHS 9-bit，只需 1 個 nc bit
{sig_multi_nc[0], sig_multi} <= data_in;       // W164a fixed

// RHS 13-bit，需要全部 5 個 nc bits
{sig_multi_nc, sig_multi} <= {4'd0, data_in};  // W164a fixed
```

這樣可以避免 `{sig_multi_nc, sig_multi}` 比 RHS 還寬造成新的 lint error。

---

## 程式怎麼找 always block 範圍

`find_always_block` 用 **begin/end 深度計數**：

```
遇到 begin → depth + 1
遇到 end   → depth - 1
depth 降回 0 且已超過 always @ 那行 → 這行就是 block 結尾
```

```
always @(posedge clk) begin   depth: 0→1
    if (!rst_n) begin         depth: 1→2
        sig <= 0;
    end else begin            depth: 2→1  (end) / (begin) 2→2
        sig <= data_in;
    end                       depth: 2→1
end                           depth: 1→0  ← block 結尾在這行
```

---

---

## 版本演進 — 各版解決的 RTL 問題

### Initial commit (v2.0 ~ v2.1) — 基礎修法建立

**新增功能：**
- 支援 ANSI / Non-ANSI port style
- 支援 `module #(parameter)` 標頭
- 支援 `reg signed` / `wire signed`（`_nc` 繼承 signed）
- 支援 array element：`sig[0]` → `sig_0_nc`
- 支援多 RHS 寬度（per-line nc bit-select）
- 目錄批次處理模式（`-d` / `-i`）

**解決的 RTL 問題：**
- 基本 W164a 自動修復，手動改 RTL 容易漏掉或改錯
- 多個 error 共用同一個 signal 時，`_nc` 寬度不夠大的問題

---

### v2.2 (commit `9e56842`) — posedge vs comb always 區分

**新增功能：**
- 偵測 always 是 posedge 還是 `always @(*)`
- comb always：掃出 block 內**所有**對該 signal 的 assignment，全部補 `_nc`
- posedge always：reset branch（第一個 `if`）無條件補 max_nc；其他行只補 err.txt 報的
- `find_always_block` 新增 `has_begin` 回傳值；沒有 `begin...end` 的 always block 跳過並印警告

**解決的 RTL 問題：**

1. **comb always latch 問題**
   ```verilog
   // err.txt 只報 sel=1 那行，舊版只修那一行：
   always @(*) begin
       if (sel) {sig_nc, sig} = data_a;  // ← 有修
       else          sig = data_b;        // ← 沒修 → sig_nc 在 else branch 沒有 driven
   end
   // 結果：synthesis 對 sig_nc 推斷出 latch！新版全部修掉。
   ```

2. **no-begin always block 殘破 RTL 問題**
   ```verilog
   // 舊版：插入 _nc 宣告後，找不到 assignment → RTL 半修不修
   always @(posedge clk)
       sig <= data_in;   // 沒有 begin/end → 舊版插了 _nc 但沒改 assignment
   // 新版：直接跳過並印警告，不插入任何東西，讓使用者手動加 begin/end
   ```

---

### v2.3 (commit `066ca57`) — wire inline assign 改用 _nc split 法

**新增功能：**
- `wire [7:0] sig = expr;` 改為拆成三行：宣告 + `wire sig_nc` + `assign {sig_nc, sig} = expr`
- 移除舊的 `fix_wire_inline_assign`（加寬法）

**解決的 RTL 問題：**

直接加寬 wire 會改變該 signal 的宣告寬度，影響下游所有使用到它的連線：

```verilog
// 舊版加寬法造成的問題：
// wire [7:0] sig_wire_inline 被改成 wire [8:0]
// 下游有：assign {a, b} = sig_wire_inline;  // a 是 1-bit, b 是 8-bit
// → sig_wire_inline 從 8-bit 變 9-bit，downstream LHS 總寬不夠 → 新的 W164a 或連線錯誤

// 新版 _nc split 保留 wire [7:0]，下游完全不受影響
```

---

### v2.4 (commit `8e1b2af`) — 多行 wire inline + block comment 支援

**新增功能：**
- wire inline assign 的 RHS 可以跨多行（`;` 不在同一行）
- `find_signal_declaration` 在 match 前先 strip inline block comment `/* ... */`

**解決的 RTL 問題：**

1. **多行 RHS 產生 `= None;` 的 corrupt RTL**
   ```verilog
   // 實際 RTL 中常見多行 assign：
   wire [7:0] sig = func_a(x) |
                    func_b(y);   // ← ; 在第二行
   // v2.3 的 strip 函式找不到 ; → rhs_expr = None
   // → assign {sig_nc, sig} = None;  ← synthesis 直接報錯
   // v2.4 改為 in-place LHS substitution，不需要解析 RHS，任意行數都能正確處理
   ```

2. **inline block comment 導致 signal 找不到**
   ```verilog
   reg [6:0] /*idx_stage1,*/ idx_stage2, idx_stage3;
   // 舊版 regex 因為 /* ... */ 的存在無法 match → 該 signal 被靜默跳過
   // → W164a 留在 RTL 裡沒修到
   // v2.4 先用 re.sub 去掉 block comment 再 match，原始行不動
   ```

---

## 已知限制

| 狀況 | 行為 |
|------|------|
| always 沒有 `begin...end` | **跳過並印警告**，不插入 `_nc`（v2.2 後）|
| 同一個 signal 被多個不同 always block 使用 | 只修有 error 那個 block |
| parameter 寬度如 `[DATA_W-1:0]` | `_nc` 宣告為 1-bit（無法在 parse 階段計算 parameter 值） |
| 一個檔案有多個 module | 只正確處理第一個 module 的 port list 結尾 |

---

## 執行方式

```bash
# 單檔模式
python lint_fixer.py err.txt input.v -o output.v

# 目錄模式（output 到 rtl_fixed_lint/）
python lint_fixer.py err.txt -d ./rtl

# 目錄模式（原地覆寫）
python lint_fixer.py err.txt -d ./rtl -i
```

---

## 測試

```bash
cd "NX python/LINT"

python lint_fixer.py test/test_err.txt          test/test_input.v          -o test/tmp.v && diff test/test_output.v          test/tmp.v
python lint_fixer.py test/test_err_nonansi.txt  test/test_input_nonansi.v  -o test/tmp.v && diff test/test_output_nonansi.v  test/tmp.v
python lint_fixer.py test/test_err_param.txt    test/test_input_param.v    -o test/tmp.v && diff test/test_output_param.v    test/tmp.v
python lint_fixer.py test/test_err_comb.txt     test/test_input_comb.v     -o test/tmp.v && diff test/test_output_comb.v     test/tmp.v

rm test/tmp.v
```

四條指令皆無輸出（diff 為空）代表全部 pass。
