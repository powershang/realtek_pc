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
    ├── wire inline assign → 拆成三行（保留原寬度 + _nc + assign）
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

`_nc` **不繼承** `signed`，永遠宣告為 unsigned：

```verilog
reg signed [7:0] sig_signed;
reg sig_signed_nc;                 // ← 沒有 signed
{sig_signed_nc, sig_signed} <= data_in; // W164a fixed
```

> **為何不繼承 signed？**
> `_nc` 是廢棄 bit，synthesis tool 優化掉它時，若它帶有 `signed`，
> tool 會對 RHS 做 signed 解讀，造成原始 signal 高位的 driver 與 golden 不同
> → LEC Non-equivalent。`signed` 對廢棄 bit 毫無意義，反而有害。

---

### Array element：sig_arr[0]

array element 的 `_nc` 命名規則為 `信號名_index_nc`：

```verilog
reg signed [7:0] sig_arr[0:3];
reg sig_arr_0_nc;                  // ← sig_arr[0] → sig_arr_0_nc（不繼承 signed）
reg sig_arr_1_nc;

{sig_arr_0_nc, sig_arr[0]} <= data_in; // W164a fixed
{sig_arr_1_nc, sig_arr[1]} <= data_in; // W164a fixed
```

---

### Non-ANSI port style（output + 分開的 reg 宣告）

Verilog 有兩種 port 宣告風格，兩種都支援：

**ANSI style**（新式）— port 型別與位元數寫在 module header：
```verilog
module foo (
    output reg [7:0] sig_out   // 一行包含型別 + 位元數
);
```

**Non-ANSI style**（舊式）— port 名稱與型別分開宣告：
```verilog
module foo (sig_out);
    output            sig_out;  // port 宣告（只有方向）
    reg        [7:0]  sig_out;  // reg 宣告（另一行，在 body）
```

程式優先在 module body 找 `reg/wire` 宣告；找不到才往 port list 找 `output/output reg`。
Non-ANSI 的 `reg` 宣告在 body，可以直接在其下方插入 `_nc`，不需要找 `);`。

---

### module #(parameter) 標頭

有 parameter 的模組：

```verilog
module foo #(
    parameter W = 8
)(
    output reg [7:0] sig_out_reg,
    ...
);
```

port list 結尾是 `);`（帶分號）。程式用「找到含分號的 `);`」來定位，
避免誤把 `#(...)` 裡面的 `)` 當成 port list 結尾，把 `_nc` 插在錯誤位置。

---

### posedge always vs comb always 修法差異

兩種 always 對 `_nc` 的處理策略不同：

**posedge always**：

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sig <= 8'd0;        // 不在 err.txt，但屬於 reset branch → 一律用 max_nc 修
    end else begin
        sig <= data_in;     // 在 err.txt → 按 per-line nc 修
    end
end
```

reset branch（第一個 `if` 的 body）無條件全修，避免 reset 行漏修。

**comb always**：

```verilog
always @(*) begin
    if (sel) sig = data_a;  // 在 err.txt（9-bit RHS）
    else     sig = data_b;  // 不在 err.txt（8-bit RHS）← 仍需修
end
```

block 內**所有** assignment 全部用 max_nc 修。若只修 err.txt 報的那行，
`_nc` 在 else branch 沒有被 driven → synthesis 推斷出 latch。

---

### no-begin always（不支援，跳過）

```verilog
always @(posedge clk)
    sig <= data_in;   // 沒有 begin/end
```

程式無法正確找出 block 範圍，**完全跳過並印警告**，不插入任何 `_nc`。
需手動補上 `begin/end` 後再重跑工具。

---

### 宣告行有 inline block comment

```verilog
reg [6:0] /*old_sig,*/ new_sig;
```

`/* ... */` 夾在宣告中間會讓 regex 無法 match。
程式在 match 前先用 `re.sub` 去掉 `/* ... */`，找到行號後不修改原始行內容。

---

### wire inline 多行 RHS

```verilog
wire [7:0] sig = func_a(x) |
                 func_b(y);   // ← ; 在第二行
```

程式只替換第一行的 LHS 部分（`wire [7:0] sig =` → `assign {sig_nc, sig} =`），
其餘行不動，並向後掃描找到 `;` 所在行補上 comment，不需要解析完整 RHS。

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

## 版本演進 — 各 commit 解決的 RTL 問題

> **注意：** v1.0 ~ v1.2 在 git 建立之前就已開發完成，沒有獨立 commit。
> Initial commit (`b0d7e73`) 進入 git 時已是 v2.1 的狀態。
> 以下依 git log 順序，逐一說明每個 commit 改了什麼、解決了哪些 RTL 問題。

---

### commit `b0d7e73` — Initial commit（v1.x ~ v2.1 累積成果）

**v1.0 ~ v1.2（pre-git）的基礎功能：**
- 解析 err.txt，支援單行與多行 W164a 錯誤格式
- reg 在 always block 內：插入 `reg _nc` + 修所有 assignments
- `wire + assign`：插入 `wire _nc` + 修 assign 行
- `output reg`（port list 內宣告）：`_nc` 插在 `);` 之後
- 支援 inline always（無 begin/end 但 assignment 緊跟在 always 同行）

**v2.0 新增（pre-git）：**
- 支援 Non-ANSI port style（`output sig; reg [7:0] sig;` 分開宣告）
- 支援 `module #(parameter)` 標頭（舊版誤把 `#(...)` 的 `)` 當 port list 結尾）
- 支援 `reg signed` / `wire signed`（`_nc` 繼承 `signed` 關鍵字）
- 支援 wire inline assign：`wire [7:0] sig = expr;`（此版用加寬法，v2.3 再改）
- 支援多 bit 寬度差（不限 1-bit）
- 目錄批次模式（`-d` / `-i`）

**v2.1 新增（pre-git）：**
- 支援 array element：`sig[0]` → `sig_0_nc`
- Per-line nc bit-select：同一 signal 有不同 RHS 寬度時，`_nc` 宣告用 max 寬度，每行只取實際需要的 bits，避免 LHS 比 RHS 更寬產生新的 W164a

**解決的 RTL 問題：**
- 手動修 W164a 容易漏行、改錯位元數，工具確保全部 assignments 一起改
- Non-ANSI 風格的 port + reg 分開宣告，舊版找不到 reg 宣告位置
- `#(param)` 模組：舊版誤把參數列的 `)` 當 port list 結尾，`_nc` 插錯位置
- array element 的 `_nc` 命名衝突（多個 index 共用同一 `_nc` 名）
- 同 signal 不同行 nc 寬度不同時，LHS 過寬導致新的 width mismatch

---

### commit `c48096b` — docs: add README（無 RTL 邏輯變更）

各子目錄新增 README.md 說明用途，`lint_fixer.py` 本身沒有修改。

---

### commit `9e56842` — v2.2：posedge vs comb always 區分

**改動：**
- `find_always_block` 新增 `has_begin` 回傳值
- 新增 `find_first_if_block`：找 posedge always 內的 reset branch（第一個 `if`）
- posedge always：reset branch 無條件用 max_nc 修；其他行只修 err.txt 報的
- comb always（`always @(*)`）：掃出 block 內**所有**對該 signal 的 assignment，全部用 max_nc 修

**解決的 RTL 問題：**

1. **comb always 產生 `_nc` latch**
   ```verilog
   // err.txt 只報 sel=1 那行，v2.1 只改那一行：
   always @(*) begin
       if (sel) {sig_nc, sig} = data_a;  // ← 有修
       else          sig  = data_b;      // ← 沒修 → sig_nc 在 else branch 沒有 driven
   end
   // synthesis 看到 sig_nc 在某些路徑沒被 assign → 推斷出 latch！
   // v2.2 強制把同 block 內所有 sig 的 assignments 全部補上 {sig_nc, sig}
   ```

2. **no-begin always 插了 `_nc` 但沒改 assignment → RTL 半殘**
   ```verilog
   always @(posedge clk)
       sig <= data_in;   // 沒有 begin/end
   // v2.1：插入 reg sig_nc; 但 find_always_block 範圍不含 assignment → assignment 沒改
   // → sig_nc 宣告了但永遠沒被 drive，synthesis 報 undriven net
   // v2.2：偵測到 has_begin=False 就整個 skip + 印警告，完全不動
   ```

---

### commit `066ca57` — v2.3：wire inline assign 改用 `_nc` split 法

**改動：**
- 移除 `fix_wire_inline_assign`（加寬法）
- `wire [7:0] sig = expr;` 改拆成三行：`wire [7:0] sig;` + `wire sig_nc;` + `assign {sig_nc, sig} = expr;`

**解決的 RTL 問題：**

```verilog
// v2.2 加寬法：wire [7:0] sig = expr; → wire [8:0] sig = expr;
// 下游 RTL 若有：assign {flag, data} = sig;  (flag 1-bit, data 8-bit)
// sig 從 8-bit 變 9-bit → {flag, data} 總寬 9-bit，剛好等於 9-bit sig，不報錯
// 但語意改變：原本 sig[7:0] 對應 data[7:0]，現在 sig[8] 多出來對應 flag
// → 連線關係靜默錯位，synthesis 不報錯但電路行為錯誤
//
// v2.3 保留 wire [7:0]，只加 _nc 吸收多餘 bit，下游連線完全不受影響
```

---

### commit `8e1b2af` — v2.4：多行 wire inline + block comment 支援

**改動：**
- 移除 `strip_wire_inline_assign`；改用 in-place LHS substitution
- `find_signal_declaration` match 前先 `re.sub` 去掉 `/* ... */`

**解決的 RTL 問題：**

1. **多行 RHS 產生 `= None;` → synthesis 直接報錯**
   ```verilog
   // 實際 RTL 常見多行 assign：
   wire [7:0] sig = func_a(x) |
                    func_b(y);   // ← ; 在第二行
   // v2.3 strip 函式找不到 ; → rhs_expr = None
   // 輸出：assign {sig_nc, sig} = None;  ← 非法 Verilog，synthesis 報 parse error
   // v2.4 不解析 RHS，直接 in-place 替換 LHS 部分，; 在哪行都能正確加 comment
   ```

2. **inline block comment 導致 signal 靜默跳過、W164a 沒修到**
   ```verilog
   reg [6:0] /*old_sig,*/ new_sig;
   // v2.3 regex 遇到 /* ... */ 無法 match → 找不到宣告 → skip + 不印警告
   // → W164a 留在 RTL 裡，lint 還是報，使用者以為工具壞了
   // v2.4 先 strip block comment 再 match，原始行不動，宣告正確找到
   ```

---

### commit（v2.5）— signed `_nc` 造成 LEC 失敗

**改動：**
- `_nc` 宣告移除 `signed`，永遠為 unsigned

**解決的 RTL 問題：**

```verilog
// 原始 signal 是 signed，舊版產生：
reg signed [51:0] out22_reg;
reg signed [1:0] out22_nc;       // ← 有 signed（v2.4 以前的 bug）

{out22_nc, out22_reg} <= 54_bit_expr;

// synthesis tool 把 out22_nc 優化掉時，因為它是 signed，
// 對 54_bit_expr 做 signed 解讀，把 sign bit（rhs[53]）
// 傳播到 out22_reg 高位（out22_reg[51]、out22_reg[50]）
// 與 golden RTL 不同 → LEC Non-equivalent

// v2.5 修法：_nc 宣告改為 unsigned
reg [1:0] out22_nc;              // ← 不繼承 signed
// synthesis 不再做 signed 解讀，out22_reg 高位 driver 與 golden 一致
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
