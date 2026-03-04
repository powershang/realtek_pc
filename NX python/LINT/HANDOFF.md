# W164a Lint Fixer - Handoff Document

## Project Overview

Automatically fixes W164a (width mismatch) lint errors in Verilog RTL files.
When LHS width < RHS width, the tool adds `_nc` (no-connect) dummy bits to absorb overflow.

**Repository:** https://github.com/WORKRT/LINT.git

---

## File Structure

```
LINT/
├── lint_fixer.py                    # Main script
├── HANDOFF.md                       # This handoff document
├── .gitignore
├── test/
│   ├── test_input.v                 # ANSI port style test (9 cases)
│   ├── test_output.v                # Expected output for ANSI test
│   ├── test_err.txt                 # Error file for ANSI test
│   ├── test_input_nonansi.v         # Non-ANSI port style test (5 cases)
│   ├── test_output_nonansi.v        # Expected output for non-ANSI test
│   ├── test_err_nonansi.txt         # Error file for non-ANSI test
│   ├── test_input_param.v           # Module with #(parameters) test (4 cases)
│   ├── test_output_param.v          # Expected output for param test
│   ├── test_err_param.txt           # Error file for param test
│   ├── test_input_comb.v            # Comb always test (2 cases)
│   ├── test_output_comb.v           # Expected output for comb test
│   └── test_err_comb.txt            # Error file for comb test
├── demo_*.v / demo_*.txt            # Legacy demo files (not in git)
├── err.txt                          # Legacy error file (not in git)
└── bug2.png                         # Bug screenshot reference (not in git)
```

---

## Usage

```bash
# Single file mode
python lint_fixer.py <err_file> <verilog_file> [-o output.v]

# Directory mode (recursive)
python lint_fixer.py <err_file> -d <rtl_directory> [-i]

# Examples
python lint_fixer.py err.txt input.v -o output.v
python lint_fixer.py err.txt -d ./rtl              # output to rtl_fixed_lint/
python lint_fixer.py err.txt -d ./rtl -i           # overwrite in place
```

---

## Supported Error Format

```
[4735]  W164a  N.A  error  path/file.v  457  10  LHS: 'signal' width 8 is less than RHS: '(expr)' width 9
```

Also supports multi-line format where file path and error details are on separate lines.

---

## Transformation Rules

### 1. reg / output reg (inside always block)
Adds `_nc` declaration + concatenates on LHS. Behavior differs by always type:

**posedge always** — reset branch (first `if`) always gets `max_nc_width`; other lines only if reported in err.txt:
```verilog
// Before
reg [7:0] counter;
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        counter <= 8'd0;          // NOT in err.txt, but still fixed (reset)
    else
        counter <= data_in;       // in err.txt -> fixed with per-line nc
end

// After
reg [7:0] counter;
reg counter_nc;
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        {counter_nc, counter} <= 8'd0;    // W164a fixed by lint_fixer (max_nc)
    else
        {counter_nc, counter} <= data_in; // W164a fixed by lint_fixer
end
```

**comb always** (`always @(*)`) — ALL assignments in the block get `max_nc_width`, even unreported ones.
This prevents the `_nc` wire from becoming a latch (if `_nc` is not driven in every branch, synthesis infers a latch):
```verilog
// Before
reg [7:0] sig;
always @(*) begin
    if (sel) sig = data_a;   // in err.txt (9-bit RHS)
    else     sig = data_b;   // NOT in err.txt (8-bit RHS, same width)
end

// After
reg [7:0] sig;
reg sig_nc;
always @(*) begin
    if (sel) {sig_nc, sig} = data_a; // W164a fixed by lint_fixer
    else     {sig_nc, sig} = data_b; // W164a fixed by lint_fixer (prevent latch)
end
```

**no-begin always** — NOT supported. The tool skips these blocks with a warning message and does NOT insert any `_nc` declaration.

### 2. wire with assign
Adds `wire _nc` declaration + concatenates on LHS.
```verilog
// Before
wire [7:0] sig_wire;
assign sig_wire = data_in;      // data_in is 9-bit

// After
wire [7:0] sig_wire;
wire sig_wire_nc;
assign {sig_wire_nc, sig_wire} = data_in; // W164a fixed by lint_fixer
```

### 3. wire inline assignment
Splits the inline assignment into a separate declaration, `_nc` dummy signal, and `assign` statement.
The original wire width is preserved (widening would change downstream LHS bit widths).
```verilog
// Before
wire [7:0] sig = data_in;      // data_in is 9-bit

// After
wire [7:0] sig;
wire sig_nc;
assign {sig_nc, sig} = data_in; // W164a fixed by lint_fixer
```

### 4. reg signed / wire signed
Preserves `signed` keyword in `_nc` declaration.
```verilog
// Before
reg signed [7:0] sig_signed;

// After
reg signed [7:0] sig_signed;
reg signed sig_signed_nc;
{sig_signed_nc, sig_signed} <= data_in; // W164a fixed by lint_fixer
```

### 5. Array elements
Array element signals like `sig[0]` get `_N_nc` naming:
```verilog
// Before
reg signed [7:0] sig_arr[0:3];
sig_arr[0] <= data_in;

// After
reg signed [7:0] sig_arr[0:3];
reg signed sig_arr_0_nc;
{sig_arr_0_nc, sig_arr[0]} <= data_in; // W164a fixed by lint_fixer
```

### 6. Multi-bit width difference
Supports any width difference (not just 1-bit). If LHS=8, RHS=11, nc_width=3:
```verilog
reg [2:0] sig_nc;   // 3-bit _nc
{sig_nc, sig} <= expr;
```

### 7. Per-line nc bit customization
When the same signal has multiple W164a errors with different RHS widths, the `_nc` declaration uses the **max** width, but each assignment line uses only the bits it actually needs:
```verilog
// sig is 8-bit, data_in is 9-bit, {4'd0, data_in} is 13-bit
// _nc declared with max nc_width = 13-8 = 5 bits
reg [4:0] sig_nc;

// 9-bit RHS: only 1 nc bit needed -> sig_nc[0]
{sig_nc[0], sig} <= data_in; // W164a fixed by lint_fixer

// 13-bit RHS: full 5 nc bits needed -> sig_nc
{sig_nc, sig} <= {4'd0, data_in}; // W164a fixed by lint_fixer
```
This prevents LHS from becoming wider than RHS on lines with smaller width differences.

---

## Test Cases Summary

### test_input.v (ANSI port style) - 11 cases
| Case | Signal | Type | Description |
|------|--------|------|-------------|
| 1 | sig_reg_pure | reg | Pure reg in body, always block |
| 2 | sig_out_reg | output reg | ANSI port list output reg |
| 3 | sig_out_sep | output + reg | Output with separate reg declaration |
| 4 | sig_body_only | reg | Internal reg only |
| 5 | sig_param | reg | Parameter-based width (DATA_W-1:0) |
| 6 | sig_wire | wire | Wire with assign statement |
| 7 | sig_wire_inline | wire | Wire inline assignment (widen width) |
| 8 | sig_signed | reg signed | Signed reg declaration |
| 9 | sig_nospace | reg | No space before bracket (reg[7:0]) |
| 10 | sig_arr[0/1] | reg signed array | Array element with _N_nc naming |
| 11 | sig_multi | reg | Multi-RHS-width: per-line nc bit-select |
| - | sig_missing | N/A | Signal not in file (warning + skip) |

### test_input_nonansi.v (Non-ANSI port style) - 5 cases
| Case | Signal | Description |
|------|--------|-------------|
| 1 | sig_out_a | output + separate reg after module() |
| 2 | sig_out_b | Same as case 1 |
| 3 | sig_internal | Internal reg only |
| 4 | sig_out_w | output + separate wire + assign |
| 5 | sig_wire_int | Internal wire + assign |

### test_input_param.v (Module with #(parameters)) - 4 cases
| Case | Signal | Description |
|------|--------|-------------|
| 1 | sig_out_reg | output reg in ANSI port with #() params |
| 2 | sig_out_sep | output + separate reg |
| 3 | sig_internal | Internal reg |
| 4 | sig_wire | Internal wire + assign |

### test_input_comb.v (Comb always) - 2 cases
| Case | Signal | Description |
|------|--------|-------------|
| comb-1 | sig_comb1 | comb `if/else`: reported branch (9-bit) + unreported branch (8-bit) |
| comb-2 | sig_comb2 | comb `case`: two reported (9-bit, 10-bit) + two unreported (8-bit) |

Both cases verify that ALL branches are fixed with max_nc to prevent latch on `_nc`.

---

## Core Functions

### `parse_lint_errors(err_file)`
Parses error report file. Supports single-line and multi-line W164a formats.
Returns list of dicts: `{file_path, line_num, lhs_signal, lhs_width, rhs_width, rhs_expr}`

### `find_signal_declaration(lines, signal_name)`
Finds signal declaration. Searches reg/wire first (body), then output/output reg (port list).
Supports `signed` keyword.
Returns: `(line_num, decl_type, width, is_signed)`

### `find_module_port_list_end(lines)`
Finds `);` ending the module port list. Correctly skips `#(parameters)` by requiring `);` (with semicolon).

### `find_always_block(lines, line_num)`
Finds always block boundaries by counting begin/end depth.
Returns: `(start_line, end_line, has_begin)` — `has_begin=False` means no `begin/end` wrapper (not supported).

### `find_first_if_block(lines, block_start, block_end)`
Finds the first `if` statement body (reset branch) inside an always block.
Uses `depth - ends <= 0` detection so `end else begin` on a single line is correctly handled.
Returns: `(if_body_start, if_body_end)` or `(None, None)` if no `if` or no `begin`.

### `find_all_assignments_to_signal(lines, signal, start, end)`
Finds all assignments to a signal within a range. Skips already-fixed lines.

### `_nc_bits_expr(nc_signal, nc_width, max_nc_width)`
Builds the nc bit-select expression: `sig_nc` (full), `sig_nc[0]` (1-bit), or `sig_nc[N-1:0]` (partial).

### `fix_assignment_line(line, signal, old_width, new_width, max_nc_width=0)`
Transforms `signal <= expr;` to `{signal_nc, signal} <= expr; // W164a fixed by lint_fixer`
When `max_nc_width > nc_width`, uses per-line bit-select on `_nc`.

### `fix_assign_line(line, signal, old_width, new_width, max_nc_width=0)`
Transforms `assign signal = expr;` to `assign {signal_nc, signal} = expr; // W164a fixed by lint_fixer`
When `max_nc_width > nc_width`, uses per-line bit-select on `_nc`.

### `add_nc_declaration(lines, signal, decl_line, decl_type, nc_width, is_signed)`
Inserts `_nc` declaration after original signal. If declaration is inside port list, inserts after `);`.

### `parse_array_signal(signal_name)`
Parses `prod[0]` -> `('prod', '0', 'prod_0_nc')`. Non-array signals return `(name, None, 'name_nc')`.

### `process_verilog_file(lines, errors)`
Main processing loop. Groups all errors per signal, uses max RHS width for `_nc` declaration, and passes per-line `nc_width`/`max_nc_width` to fix functions. Handles line offset tracking from insertions.
Flow: wire_inline_assign -> assign -> always_block (in priority order).

For always_block path:
1. Call `find_always_block` **before** inserting `_nc` — if `has_begin=False`, skip with warning.
2. Insert `_nc` declaration, re-find block (line numbers shifted).
3. Detect posedge vs comb from always sensitivity list.
4. **posedge**: fix reset branch via `find_first_if_block` with max_nc; fix err.txt lines with per-line nc.
5. **comb**: fix all assignments via `find_all_assignments_to_signal` with max_nc.

---

## Bug Fixes History

1. **#() port list detection** - `find_module_port_list_end` was returning at the first `)` which matched `#(params)` closing paren instead of the actual port list. Fixed by requiring `);` with semicolon.

2. **wire inline assign error_line offset** - When `_nc` is inserted AFTER the error line (same line as declaration), `error_line` should NOT be incremented. Fixed by checking insert position relative to error line.

3. **find_signal_declaration for wire inline** - `wire [7:0] sig = expr;` wasn't matched because `=` wasn't in the allowed trailing characters. Fixed by adding `=` to pattern.

4. **no-begin always block incorrectly modified** - Old code would insert `_nc` and attempt fixes even when the always block had no `begin/end`. Fixed by checking `has_begin` (new return value from `find_always_block`) BEFORE inserting `_nc`; skips with warning if false.

5. **comb always missing unreported branches** - Old code only fixed lines reported in err.txt. For comb always, unreported branches (e.g., the `else` branch) must also get `_nc` concatenation or synthesis infers a latch on `_nc`. Fixed by scanning ALL assignments in comb always blocks.

6. **nonansi err.txt line numbers off by 1** - `test_err_nonansi.txt` had wrong line numbers (31, 40, 49 instead of 30, 39, 48) for posedge assignment lines. Old scan-based code was immune to this; new per-line nc logic exposed it. Fixed by correcting line numbers in test file.

7. **wire inline assign widened signal width** - Old approach widened `wire [7:0] sig = expr;` to `wire [8:0] sig = expr;`. This changes the declared bit width, breaking downstream code that uses `sig` as LHS. Replaced with `_nc` split approach: strip to `wire [7:0] sig;` + insert `wire sig_nc;` + `assign {sig_nc, sig} = expr;`. `fix_wire_inline_assign` removed; replaced by `strip_wire_inline_assign`.

8. **splitlines() convention** - `process_verilog_file` reads lines with `f.read().splitlines()` (no trailing `\n` on each element) and writes with `'\n'.join(fixed_lines) + '\n'`. All inserted/modified lines must NOT include `\n`; blank lines are stored as `''`. Violated by the new wire inline path — `strip_wire_inline_assign` was returning `decl_part + ';\n'` and `assign_ln` had `\n`. Fixed by removing all `\n` from inserted strings.

9. **inline block comment breaks declaration search** - `find_signal_declaration` failed to match lines containing `/* ... */` block comments (e.g. `reg [6:0] /*idx_stage1,*/ idx_stage2, ...`). Fixed by stripping inline block comments with `re.sub(r'/\*.*?\*/', '', line)` before running the regex, while keeping the original line index for the return value.

10. **multi-line wire inline assign produces `= None;`** - v2.3 `strip_wire_inline_assign` required `;` on the same line to extract `rhs_expr`. Multi-line assignments (RHS spans multiple lines, `;` on a later line) returned `rhs_expr = None`, corrupting RTL with `assign {sig_nc, sig} = None;`. Fixed in v2.4 by dropping `strip_wire_inline_assign` entirely: instead, regex-match only the LHS up to `=`, substitute it in-place to `assign {nc, sig} =`, keep everything after `=` on the first line verbatim, and scan ahead for the `;` line to append the comment.

---

## Running Tests

```bash
cd "C:\python_work\realtek_pc\NX python\LINT"

# ANSI test
python lint_fixer.py test/test_err.txt test/test_input.v -o test/tmp.v
diff test/test_output.v test/tmp.v

# Non-ANSI test
python lint_fixer.py test/test_err_nonansi.txt test/test_input_nonansi.v -o test/tmp.v
diff test/test_output_nonansi.v test/tmp.v

# Param module test
python lint_fixer.py test/test_err_param.txt test/test_input_param.v -o test/tmp.v
diff test/test_output_param.v test/tmp.v

# Comb always test
python lint_fixer.py test/test_err_comb.txt test/test_input_comb.v -o test/tmp.v
diff test/test_output_comb.v test/tmp.v

# Clean up
rm test/tmp.v
```

All 4 test suites should produce empty diff (no differences).

> **Note on Windows diff:** `diff` on Windows may show false differences due to CRLF vs LF line endings.
> Use `python -c "..."` comparison with `splitlines()` for reliable results on Windows.

---

## Known Limitations

1. **Parameter width in _nc** - When signal uses parameter width like `[DATA_W-1:0]`, the `_nc` is declared as `reg sig_nc;` (1-bit) since we can't evaluate the parameter expression at parse time.
2. **RHS not modified** - Only LHS gets `_nc` concatenation; RHS expression is kept as-is.
3. **Single module per file** - `find_module_port_list_end` only finds the first module.
4. **no-begin always block not supported** - `always @(...) signal <= expr;` (no `begin/end`) is skipped with a warning. The `_nc` declaration is NOT inserted. Must add `begin/end` manually first.
5. **Single-line if body in reset branch** - `find_first_if_block` only finds reset branch when `if (!rst_n) begin ... end` uses `begin/end`. Single-line `if (!rst_n) sig <= 0;` (no begin) is not detected; reset line won't be fixed.

---

## Version History

- **v1.0** - Initial version, multi-line error format
- **v1.1** - Fix inline always block
- **v1.2** - Support single-line error format
- **v2.0** - Major rewrite:
  - Directory mode (`-d`, `-i` flags)
  - Non-ANSI port style support
  - Module with `#(parameters)` support
  - Wire inline assignment support (widen width)
  - `reg signed` / `wire signed` support
  - Multi-bit width difference support
  - `// W164a fixed by lint_fixer` comment on every fixed line
  - No-space declarations (`reg[8:0]`, `signed[31:0]`)
  - 3 test suites (ANSI, Non-ANSI, Param) with 18 total test cases
- **v2.1** - Array elements + per-line nc:
  - Array element support (`sig[0]` -> `sig_0_nc`)
  - Per-line nc bit-select: `_nc` declared at max width, each line uses only needed bits
  - Prevents LHS > RHS overcorrection when same signal has different RHS widths
  - 3 test suites with 22 total test cases
- **v2.2** - posedge vs comb always distinction + no-begin guard:
  - `find_always_block` now returns `has_begin` (3rd value); no-begin blocks are skipped with warning
  - New `find_first_if_block`: detects reset branch (first `if` body) inside posedge always
  - **posedge always**: reset branch fixed with max_nc unconditionally; other lines only from err.txt
  - **comb always**: ALL assignments fixed with max_nc to prevent `_nc` latch at synthesis
  - New comb test suite (`test_input_comb.v`): if/else and case with mixed reported/unreported branches
  - Fixed `test_err_nonansi.txt` line numbers (were off by 1, exposed by new per-line nc logic)
  - 4 test suites with 24 total test cases
- **v2.3** - wire inline assign: `_nc` split approach (replaces width-widening):
  - `wire [7:0] sig = expr;` now becomes `wire [7:0] sig;` + `wire sig_nc;` + `assign {sig_nc, sig} = expr;`
  - Preserves original wire bit width so downstream LHS uses are not broken
  - Removed `fix_wire_inline_assign`; added `strip_wire_inline_assign`
  - `test/test_output.v` Case 7 updated (1 line → 3 lines)
- **v2.4** - multi-line wire inline assign fix:
  - v2.3 `strip_wire_inline_assign` failed for multi-line assignments (no `;` on first line), producing `assign {sig_nc, sig} = None;`
  - New approach: regex-match only the LHS up to `=`, substitute in-place, keep rest of line verbatim, scan ahead for `;` to add comment
  - Removed `strip_wire_inline_assign`; no new functions added
  - Single-line wire inline output identical to v2.3
