# W164a Lint Fixer

Auto-fix W164a (width mismatch) lint errors in Verilog RTL files.

## What It Does

Reads a lint error report and the corresponding Verilog source files, then automatically patches LHS assignments to eliminate W164a warnings (LHS width < RHS width).

### Fix Rules

The tool **only modifies the LHS** of assignments. The RHS expression is never changed.

- **`always` block assignments** (`<=` / `=`): Adds a `_nc` (no-connect) dummy signal and concatenates it on the LHS.
  All assignments to the same signal within the same always block are fixed together.
  ```verilog
  // Before
  sig <= data_in;
  // After
  {sig_nc, sig} <= data_in; // W164a fixed by lint_fixer
  ```

- **`assign` statements**: Same approach -- adds `_nc` declaration and concatenates on LHS.
  ```verilog
  // Before
  assign sig = data_in;
  // After
  assign {sig_nc, sig} = data_in; // W164a fixed by lint_fixer
  ```

- **`wire` inline assignments** (`wire [N:0] sig = expr;`): Widens the wire declaration to match RHS width. No `_nc` is added.
  ```verilog
  // Before
  wire [7:0] sig = data_in;    // data_in is 9-bit
  // After
  wire [8:0] sig = data_in; // W164a fixed by lint_fixer
  ```

- **`reg signed` / `wire signed`**: The `signed` keyword is preserved on the `_nc` declaration.
  ```verilog
  // Before
  reg signed [7:0] sig;
  // After
  reg signed [7:0] sig;
  reg signed sig_nc;
  ```

- **Array elements** (`sig[0]`, `sig[1]`, ...): Each element gets its own `_N_nc` signal.
  ```verilog
  // Before
  sig_arr[0] <= data_in;
  // After
  reg signed sig_arr_0_nc;
  {sig_arr_0_nc, sig_arr[0]} <= data_in; // W164a fixed by lint_fixer
  ```

- **Per-line nc bit-select**: When the same signal has multiple errors with different RHS widths, `_nc` is declared at the max width, but each assignment line uses only the bits it needs. This prevents LHS > RHS overcorrection.
  ```verilog
  // sig is 8-bit; data_in is 9-bit, {4'd0, data_in} is 13-bit
  reg [4:0] sig_nc;  // max nc = 5 bits
  {sig_nc[0], sig} <= data_in;         // only 1 nc bit needed
  {sig_nc, sig}    <= {4'd0, data_in}; // full 5 nc bits needed
  ```

### What It Skips

If the signal name from the error report **cannot be found** in the Verilog source (no matching `reg`, `wire`, `output reg`, or `output` declaration), the tool prints a warning and skips that error. No modification is made.

```
Warning: Could not find declaration for sig_missing, skipping
```

### Important: User Must Verify

The tool blindly adds `_nc` bits based on the width difference reported by the lint tool. **Users are responsible for verifying that the LHS bit count is correct** after the fix. The tool does not analyze whether the width mismatch is intentional or whether truncation was the desired behavior.

Every modified line is marked with `// W164a fixed by lint_fixer` so you can easily search and review all changes.

## Supported Patterns

- ANSI port style: `module foo (input clk, output reg [7:0] sig);`
- Non-ANSI port style: `module foo (clk, sig);` with separate `input` / `output` / `reg` declarations
- Modules with parameters: `module foo #(parameter W = 8) (...)`;
- Parameter-based widths: `reg [DATA_W-1:0] sig;`
- Multi-bit width differences (not limited to 1-bit)
- Array elements: `sig[0]` -> `sig_0_nc`
- No-space declarations: `reg[8:0]`, `signed[31:0]`
- Per-line nc bit-select for signals with multiple RHS widths

## Usage

```bash
# Single file
lint_fixer.py sglint.warn.rpt input.v -o output.v

# Directory (recursive), output to rtl_fixed_lint/
lint_fixer.py sglint.warn.rpt -d ./rtl

# Directory, in-place overwrite
lint_fixer.py sglint.warn.rpt -d ./rtl -i
```

## Error File Format

The error file is the warning report from **SGLint** -- just feed `sglint.warn.rpt` directly as the first argument. The tool automatically extracts all W164a entries from the report and matches them to the corresponding `.v` source files for fixing.

In directory mode (`-d`), it scans the RTL directory for matching filenames referenced in the report -- no need to specify each file manually.

Standard SGLint output (single-line):
```
[4735]  W164a  N.A  error  file.v  457  10  LHS: 'signal' width 8 is less than RHS: 'expr' width 9
```

Multi-line format is also supported:
```
[4735]  W164a  N.A  error  file.v
        457  10  LHS: 'signal' width 8 is less than RHS: 'expr' width 9
```
