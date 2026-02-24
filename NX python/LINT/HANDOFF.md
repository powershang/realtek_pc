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
│   └── test_err_param.txt           # Error file for param test
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
Adds `_nc` declaration + concatenates on LHS for ALL assignments in the always block.
```verilog
// Before
reg [7:0] counter;
always @(posedge clk) begin
    counter <= counter + 8'd1;
end

// After
reg [7:0] counter;
reg counter_nc;
always @(posedge clk) begin
    {counter_nc, counter} <= counter + 8'd1; // W164a fixed by lint_fixer
end
```

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
Widens the wire declaration to match RHS (no `_nc` needed).
```verilog
// Before
wire [7:0] sig = data_in;      // data_in is 9-bit

// After
wire [8:0] sig = data_in; // W164a fixed by lint_fixer
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
Returns: `(start_line, end_line)`

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

### `fix_wire_inline_assign(line, signal, old_width, new_width)`
Transforms `wire [7:0] sig = expr;` to `wire [8:0] sig = expr; // W164a fixed by lint_fixer`

### `add_nc_declaration(lines, signal, decl_line, decl_type, nc_width, is_signed)`
Inserts `_nc` declaration after original signal. If declaration is inside port list, inserts after `);`.

### `parse_array_signal(signal_name)`
Parses `prod[0]` -> `('prod', '0', 'prod_0_nc')`. Non-array signals return `(name, None, 'name_nc')`.

### `process_verilog_file(lines, errors)`
Main processing loop. Groups all errors per signal, uses max RHS width for `_nc` declaration, and passes per-line `nc_width`/`max_nc_width` to fix functions. Handles line offset tracking from insertions.
Flow: wire_inline_assign -> assign -> always_block (in priority order).

---

## Bug Fixes History

1. **#() port list detection** - `find_module_port_list_end` was returning at the first `)` which matched `#(params)` closing paren instead of the actual port list. Fixed by requiring `);` with semicolon.

2. **wire inline assign error_line offset** - When `_nc` is inserted AFTER the error line (same line as declaration), `error_line` should NOT be incremented. Fixed by checking insert position relative to error line.

3. **find_signal_declaration for wire inline** - `wire [7:0] sig = expr;` wasn't matched because `=` wasn't in the allowed trailing characters. Fixed by adding `=` to pattern.

---

## Running Tests

```bash
cd "D:\python_work\side_project\NX python\LINT"

# ANSI test
python lint_fixer.py test/test_err.txt test/test_input.v -o test/tmp.v
diff test/test_output.v test/tmp.v

# Non-ANSI test
python lint_fixer.py test/test_err_nonansi.txt test/test_input_nonansi.v -o test/tmp.v
diff test/test_output_nonansi.v test/tmp.v

# Param module test
python lint_fixer.py test/test_err_param.txt test/test_input_param.v -o test/tmp.v
diff test/test_output_param.v test/tmp.v

# Clean up
rm test/tmp.v
```

All 3 test suites should produce empty diff (no differences).

---

## Known Limitations

1. **Parameter width in _nc** - When signal uses parameter width like `[DATA_W-1:0]`, the `_nc` is declared as `reg sig_nc;` (1-bit) since we can't evaluate the parameter expression at parse time.
2. **RHS not modified** - Only LHS gets `_nc` concatenation; RHS expression is kept as-is.
3. **Single module per file** - `find_module_port_list_end` only finds the first module.

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
