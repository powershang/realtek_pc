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

### Case 3：wire inline assignment（直接加寬）

這種寫法宣告和賦值在同一行，不需要 `_nc`，直接把 wire 位元數加寬：

```verilog
// Before
wire [7:0] sig_wire_inline = data_in;   // data_in 9-bit → W164a

// After
wire [8:0] sig_wire_inline = data_in;   // W164a fixed by lint_fixer
```

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

## 已知限制

| 狀況 | 行為 |
|------|------|
| always 沒有 `begin...end`，assignment 在下一行 | 可以修（block 範圍剛好涵蓋到） |
| always 沒有 `begin...end`，中間夾了 `if` 或其他行 | **不會修**（block 找到的範圍只有 always @ 後的第一行） |
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

python lint_fixer.py test/test_err.txt       test/test_input.v       -o test/tmp.v && diff test/test_output.v       test/tmp.v
python lint_fixer.py test/test_err_nonansi.txt test/test_input_nonansi.v -o test/tmp.v && diff test/test_output_nonansi.v test/tmp.v
python lint_fixer.py test/test_err_param.txt  test/test_input_param.v  -o test/tmp.v && diff test/test_output_param.v  test/tmp.v

rm test/tmp.v
```

三條指令皆無輸出（diff 為空）代表全部 pass。
