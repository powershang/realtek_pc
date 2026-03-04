#!/usr/bin/env python3.11
"""
W164a Width Mismatch Lint Fixer

Automatically fixes W164a (width mismatch) lint errors in Verilog RTL files
by applying _nc dummy bit concatenation on the LHS.

Transformation Example:
    Before:
        reg [7:0] counter;
        always @(posedge clk) begin
            counter <= counter + 8'd1;  // W164a: LHS width 8 < RHS width 9
        end

    After:
        reg [7:0] counter;
        reg counter_nc;  // added
        always @(posedge clk) begin
            {counter_nc, counter} <= {1'b0, counter} + 9'd1;  // fixed
        end

    For assign statements (simple fix, only LHS modified):
        Before: assign out = a + b;
        After:  assign {out_nc, out} = a + b;

Usage:
    # Single file mode
    lint_fixer.py <err_file> <verilog_file> [-o output.v]

    # Directory mode (recursive)
    lint_fixer.py <err_file> -d <rtl_directory> [-i]

Examples:
    # Fix single file, output to demo_output.v
    lint_fixer.py err.txt demo_input.v -o demo_output.v

    # Fix single file, output to demo_input_fixed.v (default)
    lint_fixer.py err.txt demo_input.v

    # Fix all matching .v files in directory, output to rtl_fixed_lint/
    lint_fixer.py err.txt -d ./rtl

    # Fix all matching .v files in place (overwrite originals)
    lint_fixer.py err.txt -d ./rtl -i

Arguments:
    err_file      Lint error report file (e.g., err.txt)
    verilog_file  Input Verilog file (single file mode)
    -d, --directory  Process all matching .v files recursively
    -o, --output     Output file path (single file mode only)
    -i, --inplace    Modify files in place (directory mode)
"""

import re
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set


def parse_array_signal(signal_name: str) -> Tuple[str, Optional[str], str]:
    """
    Parse a signal name that may include an array index.

    Examples:
        'prod[0]'     -> ('prod', '0', 'prod_0_nc')
        'prod_odd[2]' -> ('prod_odd', '2', 'prod_odd_2_nc')
        'counter'     -> ('counter', None, 'counter_nc')

    Returns:
        - base_name: signal name without array index
        - array_index: index string (None if not an array element)
        - nc_name: name for the _nc signal
    """
    match = re.match(r'^(\w+)\[(\d+)\]$', signal_name)
    if match:
        base_name = match.group(1)
        array_index = match.group(2)
        nc_name = f"{base_name}_{array_index}_nc"
        return base_name, array_index, nc_name
    return signal_name, None, f"{signal_name}_nc"


def parse_lint_errors(err_file: str) -> List[Dict]:
    """
    Parse err.txt to extract W164a error information.

    Supports two formats:
    1. Single-line: [4735]  W164a  N.A  error  file.v  457  10  LHS: 'sig' width 8 ...
    2. Multi-line:  [4735]  W164a  N.A  error  file.v
                            457  10  LHS: 'sig' width 8 ...

    Returns list of dicts with:
        - file_path: source file path
        - line_num: line number of error
        - lhs_signal: LHS signal name
        - lhs_width: LHS width
        - rhs_width: RHS width
        - rhs_expr: RHS expression
    """
    errors = []

    with open(err_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try single-line format first (all info on one line)
    # Example: [4735]  W164a  N.A  error  path/file.v  457  10  LHS: 'signal' width 8 is less than RHS: '(expr)' width 9 ...
    # Use [ \t] to ensure we don't match across lines for file/line parts
    # RHS may contain quotes (e.g., 8'd1), so use .+? with lookahead
    single_line_pattern = (
        r'\[\d+\]\s+W164a\s+\S+\s+\S+\s+'  # [4735]  W164a  N.A  error
        r'(\S+\.v)[ \t]+'                   # file path ending in .v (no newline)
        r'(\d+)[ \t]+\d+[ \t]+'             # line_num  col_num (no newline)
        r"LHS:\s*'([^']+)'\s+width\s+(\d+)\s+is\s+less\s+than\s+RHS:\s*'(.+?)'\s+width\s+(\d+)"
    )

    for match in re.finditer(single_line_pattern, content):
        source_file = match.group(1)
        line_num = int(match.group(2))
        lhs_signal = match.group(3)
        lhs_width = int(match.group(4))
        rhs_expr = match.group(5)
        rhs_width = int(match.group(6))

        errors.append({
            'file_path': source_file,
            'line_num': line_num,
            'lhs_signal': lhs_signal,
            'lhs_width': lhs_width,
            'rhs_width': rhs_width,
            'rhs_expr': rhs_expr
        })

    # If no single-line matches, try multi-line format
    if not errors:
        # Find all file headers with their positions
        file_pattern = r'\[\d+\]\s+W164a\s+\S+\s+\S+\s+(.+\.v)\s*$'
        file_headers = []
        for match in re.finditer(file_pattern, content, re.MULTILINE):
            file_headers.append({
                'file_path': match.group(1).strip(),
                'start_pos': match.end()
            })

        if not file_headers:
            print("Warning: Could not find W164a errors in error report")
            return errors

        # Pattern to match individual error details on separate lines
        error_pattern = r"^\s*(\d+)\s+\d+\s+LHS:\s*'([^']+)'\s+width\s+(\d+)\s+is\s+less\s+than\s+RHS:\s*'(.+?)'\s+width\s+(\d+)"

        for match in re.finditer(error_pattern, content, re.MULTILINE):
            error_pos = match.start()

            # Find which file header this error belongs to
            source_file = file_headers[0]['file_path']  # default
            for i, header in enumerate(file_headers):
                if error_pos > header['start_pos']:
                    # Check if there's a next header and error is before it
                    if i + 1 < len(file_headers):
                        if error_pos < file_headers[i + 1]['start_pos']:
                            source_file = header['file_path']
                            break
                    else:
                        source_file = header['file_path']
                        break

            line_num = int(match.group(1))
            lhs_signal = match.group(2)
            lhs_width = int(match.group(3))
            rhs_expr = match.group(4)
            rhs_width = int(match.group(5))

            errors.append({
                'file_path': source_file,
                'line_num': line_num,
                'lhs_signal': lhs_signal,
                'lhs_width': lhs_width,
                'rhs_width': rhs_width,
                'rhs_expr': rhs_expr
            })

    return errors


def find_signal_declaration(lines: List[str], signal_name: str) -> Tuple[Optional[int], Optional[str], Optional[int], bool]:
    """
    Find where a signal is declared in the file.

    Search priority: reg/wire first (body declarations), then output/output reg
    (port list declarations). This ensures we prefer body declarations over
    port list declarations when both exist.

    For array elements (e.g. prod[0]), searches for the base name (prod)
    with an array range suffix (e.g. prod[0:3]).

    Returns:
        - line_num: line number (0-indexed) of declaration
        - decl_type: 'reg' or 'wire'
        - width: bit width of signal (None if single bit)
        - is_signed: True if declared with 'signed' keyword
    """
    # For array elements, search using base name
    base_name, array_index, _ = parse_array_signal(signal_name)
    sig_escaped = re.escape(base_name)

    # Optional signed keyword, optional width part
    # Use \s* to handle cases with no space (e.g. reg[8:0], signed[31:0])
    signed_part = r'(signed\s*)?'
    width_part = r'(\[([^\]]+):([^\]]+)\]\s*)?'

    # Trailing: allow [, ;, comma, ), =, or end-of-line
    # [ is needed for array declarations like prod[0:3]
    trailing = r'($|[;,)=\[])'

    # First pass: look for reg/wire declarations (typically outside port list)
    body_pattern = rf'\b(reg|wire)\s*{signed_part}{width_part}(?:\w+\s*,\s*)*{sig_escaped}\s*{trailing}'
    for i, line in enumerate(lines):
        stripped = re.sub(r'/\*.*?\*/', '', line)  # remove inline block comments
        match = re.search(body_pattern, stripped)
        if match:
            decl_type = match.group(1)
            is_signed = match.group(2) is not None
            width = _extract_width(match.group(3), match.group(4))
            return i, decl_type, width, is_signed

    # Second pass: look for output reg / output declarations (port list)
    port_trailing = r'($|[;,)\[])'
    port_pattern = rf'\b(output\s+reg|output)\s*{signed_part}{width_part}(?:\w+\s*,\s*)*{sig_escaped}\s*{port_trailing}'
    for i, line in enumerate(lines):
        stripped = re.sub(r'/\*.*?\*/', '', line)  # remove inline block comments
        match = re.search(port_pattern, stripped)
        if match:
            decl_type = 'reg' if 'reg' in match.group(1) else 'wire'
            is_signed = match.group(2) is not None
            width = _extract_width(match.group(3), match.group(4))
            return i, decl_type, width, is_signed

    return None, None, None, False


def _extract_width(msb_str: Optional[str], lsb_str: Optional[str]) -> Optional[int]:
    """Extract numeric width from MSB:LSB strings. Returns None if not pure numeric."""
    if msb_str is None or lsb_str is None:
        return 1
    try:
        return int(msb_str) - int(lsb_str) + 1
    except ValueError:
        return None


def find_module_port_list_end(lines: List[str]) -> Optional[int]:
    """Find the ending line of module port list (...); (0-indexed)

    Handles modules with #(parameters) by looking for ');' to identify
    the true end of the port list, not just the first ')' at depth 0.
    """
    in_module = False
    paren_depth = 0
    found_any_paren = False
    last_close_line = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'\bmodule\b', stripped):
            in_module = True
        if in_module:
            paren_depth += line.count('(') - line.count(')')
            if '(' in line:
                found_any_paren = True
            if found_any_paren and paren_depth <= 0 and ')' in line:
                last_close_line = i
                # Check if this line has ');' - that's the true port list end
                if re.search(r'\)\s*;', line):
                    return i
    # Fallback: return the last ')' at depth 0 (non-ANSI without ';' on same line)
    return last_close_line


def find_always_block(lines: List[str], line_num: int) -> Tuple[int, int, bool]:
    """
    Find the always block containing the given line number.

    Returns (start_line, end_line, has_begin) - 0-indexed.
    has_begin is False when the always block has no begin/end wrapper,
    meaning only a single statement follows the always @(...).
    """
    # Search backwards for 'always'
    start = line_num
    for i in range(line_num, -1, -1):
        if re.search(r'\balways\s*@', lines[i]):
            start = i
            break

    # Search forwards for matching 'end'
    end = line_num
    depth = 0
    has_begin = False
    for i in range(start, len(lines)):
        line = lines[i]
        # Count begin/end
        depth += len(re.findall(r'\bbegin\b', line))
        depth -= len(re.findall(r'\bend\b', line))
        if depth > 0:
            has_begin = True
        if depth <= 0 and i > start:
            end = i
            break

    return start, end, has_begin


def find_all_assignments_to_signal(lines: List[str], signal_name: str,
                                    start_line: int, end_line: int) -> List[int]:
    """
    Find all lines within range that have assignments to the given signal.

    Returns list of line numbers (0-indexed)
    """
    assignment_lines = []

    # Pattern matches: signal = expr or signal <= expr
    # But not {something, signal} = (already modified)
    # Also handles inline always: always @(*) signal = expr
    # Use =(?!=) to exclude == comparison
    pattern = rf'(?:^|\s){re.escape(signal_name)}\s*(<=|=(?!=))'
    already_fixed = r'\{[^}]*' + re.escape(signal_name) + r'\s*\}\s*(=|<=)'

    for i in range(start_line, end_line + 1):
        if i < len(lines):
            line = lines[i]
            # Skip if already fixed (has {signal_nc, signal} = pattern)
            if re.search(already_fixed, line):
                continue
            if re.search(pattern, line):
                assignment_lines.append(i)

    return assignment_lines


def _nc_bits_expr(nc_signal: str, nc_width: int, max_nc_width: int) -> str:
    """
    Build the _nc bit-select expression for LHS concatenation.

    When nc_width == max_nc_width, use the full signal: sig_nc
    When nc_width < max_nc_width, use a bit-select: sig_nc[nc_width-1:0]
    When nc_width == 1 and max_nc_width > 1, use: sig_nc[0]
    """
    if nc_width >= max_nc_width:
        return nc_signal
    elif nc_width == 1:
        return f"{nc_signal}[0]"
    else:
        return f"{nc_signal}[{nc_width - 1}:0]"


def fix_assignment_line(line: str, signal_name: str, old_width: int, new_width: int,
                        max_nc_width: int = 0) -> str:
    """
    Transform an assignment line to fix width mismatch.
    Only modify LHS, keep RHS unchanged.

    Before: signal <= expr;
    After:  {signal_nc, signal} <= expr; // W164a fixed by lint_fixer

    When max_nc_width > nc_width, uses bit-select on _nc:
        {signal_nc[0], signal} <= expr;   (1 of 4 nc bits)
        {signal_nc[2:0], signal} <= expr; (3 of 4 nc bits)
    """
    _, _, nc_signal = parse_array_signal(signal_name)
    nc_width = new_width - old_width
    if max_nc_width <= 0:
        max_nc_width = nc_width

    pattern = rf'^(.*?)({re.escape(signal_name)})\s*(=|<=)\s*(.+?)(;.*)$'
    match = re.match(pattern, line)
    if not match:
        return line

    prefix = match.group(1)
    operator = match.group(3)
    rhs_expr = match.group(4).strip()
    trailing = match.group(5)

    # Append comment marker after semicolon (preserve existing trailing comments)
    if '//' in trailing:
        trailing = trailing.rstrip() + ' | W164a fixed by lint_fixer'
    else:
        trailing = trailing.rstrip() + ' // W164a fixed by lint_fixer'

    nc_expr = _nc_bits_expr(nc_signal, nc_width, max_nc_width)
    new_line = f"{prefix}{{{nc_expr}, {signal_name}}} {operator} {rhs_expr}{trailing}"
    return new_line


def add_nc_declaration(lines: List[str], signal_name: str, decl_line: int,
                       decl_type: str, nc_width: int = 1,
                       is_signed: bool = False) -> List[str]:
    """
    Add _nc signal declaration after the original signal declaration.

    Args:
        nc_width: bit width of the _nc signal (rhs_width - lhs_width)
        is_signed: whether the original signal is declared as signed

    For array elements (e.g. prod[0]), nc name is prod_0_nc.
    """
    _, _, nc_signal = parse_array_signal(signal_name)

    # Check if _nc declaration already exists
    nc_pattern = rf'\b{re.escape(nc_signal)}\b'
    for line in lines:
        if re.search(nc_pattern, line):
            return lines  # Already declared

    # If declaration is inside module port list, insert _nc after ); instead
    port_list_end = find_module_port_list_end(lines)
    if port_list_end is not None and decl_line <= port_list_end:
        insert_line = port_list_end + 1  # Insert after );
    else:
        insert_line = decl_line + 1  # Default: insert after declaration

    # Get indentation
    indent_match = re.match(r'^([ \t]*)', lines[insert_line] if insert_line < len(lines) else lines[decl_line])
    indent = indent_match.group(1) if indent_match else ''

    signed_str = ' signed' if is_signed else ''
    if nc_width > 1:
        new_decl = f"{indent}{decl_type}{signed_str} [{nc_width - 1}:0] {nc_signal};"
    else:
        new_decl = f"{indent}{decl_type}{signed_str} {nc_signal};"

    lines.insert(insert_line, new_decl)

    return lines


def is_assign_statement(line: str) -> bool:
    """Check if a line is a continuous assign statement."""
    return bool(re.search(r'^\s*assign\s+', line))


def is_wire_inline_assign(line: str, signal_name: str) -> bool:
    """Check if a line is a wire declaration with inline assignment."""
    pattern = rf'^\s*wire\s+(\[.*?\]\s+)?{re.escape(signal_name)}\s*='
    return bool(re.search(pattern, line))



def fix_assign_line(line: str, signal_name: str, old_width: int, new_width: int,
                    max_nc_width: int = 0) -> str:
    """
    Transform an assign statement to fix width mismatch.

    Simple fix: only modify LHS, keep RHS unchanged.
    Before: assign signal = expr;
    After:  assign {signal_nc, signal} = expr; // W164a fixed by lint_fixer
    """
    _, _, nc_signal = parse_array_signal(signal_name)
    nc_width = new_width - old_width
    if max_nc_width <= 0:
        max_nc_width = nc_width

    # Pattern to match: assign signal = expr;
    pattern = rf'^(\s*assign\s+)({re.escape(signal_name)})\s*(=)\s*(.+?)(;.*)$'

    match = re.match(pattern, line)
    if not match:
        return line

    prefix = match.group(1)  # "assign "
    operator = match.group(3)
    rhs_expr = match.group(4).strip()
    trailing = match.group(5)

    # Append comment marker after semicolon (preserve existing trailing comments)
    if '//' in trailing:
        trailing = trailing.rstrip() + ' | W164a fixed by lint_fixer'
    else:
        trailing = trailing.rstrip() + ' // W164a fixed by lint_fixer'

    nc_expr = _nc_bits_expr(nc_signal, nc_width, max_nc_width)
    new_line = f"{prefix}{{{nc_expr}, {signal_name}}} {operator} {rhs_expr}{trailing}"
    return new_line


def find_first_if_block(lines: List[str], block_start: int, block_end: int
                        ) -> Tuple[Optional[int], Optional[int]]:
    """
    Find the first 'if' statement body within an always block.

    Used to identify the reset branch in a posedge always block so that
    _nc signals are properly reset even if the reset line is not in err.txt.

    Detection method: stops when (depth - ends_on_this_line) drops to 0,
    which correctly handles 'end else begin' on a single line.

    Returns (if_body_start, if_body_end) as 0-indexed line numbers.
    Returns (None, None) if no 'if' found or if body has no 'begin'.
    """
    # Find first 'if' line inside the always block (skip the always @ line)
    if_line = None
    for i in range(block_start + 1, block_end + 1):
        if re.search(r'\bif\b', lines[i]):
            if_line = i
            break

    if if_line is None or 'begin' not in lines[if_line]:
        return None, None  # no if, or single-line if body (not supported)

    # Find if body end: depth drops to 0 via 'end' before any 'begin' on same line
    depth = 0
    for i in range(if_line, block_end + 1):
        ends   = len(re.findall(r'\bend\b', lines[i]))
        begins = len(re.findall(r'\bbegin\b', lines[i]))
        if depth - ends <= 0 and i > if_line:
            return if_line, i   # body ends here (e.g. at 'end else begin' line)
        depth += begins - ends

    return if_line, block_end   # fallback



def process_verilog_file(lines: List[str], errors: List[Dict]) -> List[str]:
    """
    Process all W164a errors and fix the Verilog file.
    """
    # Track which signals have been processed
    processed_signals: Set[str] = set()

    # Track line offset due to insertions
    line_offset = 0

    # Group all errors by signal name
    # Collect per-line RHS widths and find the max for _nc declaration
    signal_errors: Dict[str, List[Dict]] = {}
    for err in errors:
        signal = err['lhs_signal']
        if signal not in signal_errors:
            signal_errors[signal] = []
        signal_errors[signal].append(err)

    for signal, err_list in signal_errors.items():
        if signal in processed_signals:
            continue

        # Use first error for common fields; max RHS width for _nc declaration
        old_width = err_list[0]['lhs_width']
        max_rhs_width = max(e['rhs_width'] for e in err_list)
        max_nc_width = max_rhs_width - old_width

        # Build line_num -> rhs_width map for per-line customization
        line_rhs_map: Dict[int, int] = {}
        for e in err_list:
            ln = e['line_num']
            # If multiple errors on same line, take max
            if ln not in line_rhs_map or e['rhs_width'] > line_rhs_map[ln]:
                line_rhs_map[ln] = e['rhs_width']

        # Use first error's line as representative error line
        error_line = err_list[0]['line_num'] - 1 + line_offset  # Convert to 0-indexed

        print(f"Processing signal: {signal} (width {old_width} -> max {max_rhs_width})")

        # Find signal declaration
        decl_line, decl_type, _, is_signed = find_signal_declaration(lines, signal)

        if decl_line is None:
            print(f"  Warning: Could not find declaration for {signal}, skipping")
            continue
        else:
            sign_str = ' signed' if is_signed else ''
            print(f"  Found declaration at line {decl_line + 1}: {decl_type}{sign_str}")

        # Determine assignment type and handle accordingly
        if is_wire_inline_assign(lines[error_line], signal):
            # Wire inline assign: substitute LHS in-place, insert wire decls before it
            print(f"  Wire inline assign at line {error_line + 1}")

            _, _, nc_signal = parse_array_signal(signal)
            nc_expr = _nc_bits_expr(nc_signal, max_nc_width, max_nc_width)
            signed_str = ' signed' if is_signed else ''

            # Match LHS up to '='
            sig_escaped = re.escape(signal)
            lhs_pattern = rf'^([ \t]*)wire\s+(?:signed\s+)?(?:\[[^\]]+\]\s+)?{sig_escaped}\s*='
            m = re.match(lhs_pattern, lines[error_line])
            if not m:
                print(f"  Warning: Could not parse wire inline for {signal}, skipping")
                continue

            indent = m.group(1)
            # wire_decl: everything before '=' trimmed, with ';'
            wire_decl = lines[error_line][:m.end() - 1].rstrip() + ';'
            # assign_line: substitute LHS, keep everything from '=' onward
            rhs_from_eq = lines[error_line][m.end():].lstrip()
            assign_line = f"{indent}assign {{{nc_expr}, {signal}}} = {rhs_from_eq}"

            # Add comment on the ';' line
            if ';' in assign_line:
                # single-line: comment on same line
                assign_line = re.sub(r';(\s*)$', '; // W164a fixed by lint_fixer', assign_line)
            else:
                # multi-line: scan ahead for the ';' line
                for _j in range(error_line + 1, min(error_line + 50, len(lines))):
                    if ';' in lines[_j]:
                        lines[_j] = re.sub(r';(\s*)$', '; // W164a fixed by lint_fixer', lines[_j])
                        break

            # nc declaration
            if max_nc_width > 1:
                nc_decl = f"{indent}wire{signed_str} [{max_nc_width - 1}:0] {nc_signal};"
            else:
                nc_decl = f"{indent}wire{signed_str} {nc_signal};"

            # Replace inline wire with assign, then insert declarations before it
            lines[error_line] = assign_line
            lines.insert(error_line, nc_decl)
            lines.insert(error_line, wire_decl)
            line_offset += 2

            print(f"    Fixed: wire inline -> decl + nc + assign")

        elif is_assign_statement(lines[error_line]):
            # Continuous assign: insert _nc with max width, then fix assign per-line
            lines = add_nc_declaration(lines, signal, decl_line, decl_type, max_nc_width, is_signed)
            line_offset += 1
            # _nc inserted before error_line (decl is always before assign)
            error_line += 1
            print(f"  Assign statement at line {error_line + 1}")
            # Look up per-line RHS width
            orig_line_num = err_list[0]['line_num']
            per_line_rhs = line_rhs_map.get(orig_line_num, max_rhs_width)
            original = lines[error_line]
            lines[error_line] = fix_assign_line(original, signal, old_width, per_line_rhs, max_nc_width)
            if lines[error_line] != original:
                print(f"    Fixed line {error_line + 1}")

        else:
            # Inside always block: check for begin/end before modifying anything
            block_start, block_end, has_begin = find_always_block(lines, error_line)
            print(f"  Always block: lines {block_start + 1} to {block_end + 1}")

            if not has_begin:
                print(f"  Warning: always block has no begin/end, skipping (not supported)")
                processed_signals.add(signal)
                continue

            # Insert _nc with max width
            port_list_end = find_module_port_list_end(lines)
            if port_list_end is not None and decl_line <= port_list_end:
                nc_insert_line = port_list_end + 1
            else:
                nc_insert_line = decl_line + 1
            lines = add_nc_declaration(lines, signal, decl_line, decl_type, max_nc_width, is_signed)
            line_offset += 1
            if nc_insert_line <= error_line:
                error_line += 1

            # Re-find block after insertion (line numbers shifted)
            block_start, block_end, _ = find_always_block(lines, error_line)

            is_posedge = bool(re.search(r'\balways\s*@\s*\(posedge', lines[block_start]))

            if is_posedge:
                # posedge: fix reset branch (first if) with max_nc, then fix
                # only err.txt reported lines with per-line nc_width
                reset_start, reset_end = find_first_if_block(lines, block_start, block_end)
                if reset_start is not None:
                    reset_lines = find_all_assignments_to_signal(
                        lines, signal, reset_start, reset_end)
                    for asgn_line in reset_lines:
                        original = lines[asgn_line]
                        lines[asgn_line] = fix_assignment_line(
                            original, signal, old_width, max_rhs_width, max_nc_width)
                        if lines[asgn_line] != original:
                            print(f"    Fixed reset line {asgn_line + 1} "
                                  f"(nc bits: {max_nc_width})")

                already_fixed_pat = (r'\{[^}]*' + re.escape(signal) + r'\s*\}\s*(=|<=)')
                for orig_ln, rhs_w in sorted(line_rhs_map.items()):
                    asgn_line = orig_ln - 1 + line_offset
                    if re.search(already_fixed_pat, lines[asgn_line]):
                        continue  # already fixed in reset branch
                    nc_w = rhs_w - old_width
                    original = lines[asgn_line]
                    lines[asgn_line] = fix_assignment_line(
                        original, signal, old_width, rhs_w, max_nc_width)
                    if lines[asgn_line] != original:
                        print(f"    Fixed line {asgn_line + 1} "
                              f"(nc bits: {nc_w} of {max_nc_width})")

            else:
                # comb always: fix ALL assignments with max_nc_width
                # Every branch must drive _nc to avoid creating a latch on _nc
                all_asgn_lines = find_all_assignments_to_signal(
                    lines, signal, block_start, block_end)
                print(f"  Comb block: {len(all_asgn_lines)} assignments to {signal}")
                for asgn_line in all_asgn_lines:
                    original = lines[asgn_line]
                    lines[asgn_line] = fix_assignment_line(
                        original, signal, old_width, max_rhs_width, max_nc_width)
                    if lines[asgn_line] != original:
                        print(f"    Fixed line {asgn_line + 1} (nc bits: {max_nc_width})")

        processed_signals.add(signal)

    return lines


def process_single_file(verilog_path: Path, errors: List[Dict], output_path: Optional[Path] = None,
                        inplace: bool = False, output_dir: Optional[Path] = None) -> bool:
    """
    Process a single Verilog file and fix W164a errors.

    Args:
        verilog_path: Input Verilog file path
        errors: List of parsed errors
        output_path: Explicit output path (single file mode)
        inplace: If True, overwrite original file
        output_dir: Directory for output files (directory mode)

    Returns True if fixes were applied, False otherwise.
    """
    target_filename = verilog_path.name

    # Filter errors to only those matching this file
    file_errors = [err for err in errors if Path(err['file_path']).name == target_filename]

    if not file_errors:
        return False

    print(f"\n{'='*60}")
    print(f"Processing: {verilog_path}")
    print(f"Found {len(file_errors)} error(s)")
    for err in file_errors:
        print(f"  Line {err['line_num']}: {err['lhs_signal']} "
              f"(width {err['lhs_width']} < {err['rhs_width']})")

    # Read file
    with open(verilog_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    print(f"File has {len(lines)} lines")

    # Process and fix
    print("Applying fixes...")
    fixed_lines = process_verilog_file(lines, file_errors)

    # Determine output file
    if inplace:
        out_path = verilog_path
    elif output_path:
        out_path = output_path
    elif output_dir:
        # Directory mode: output to specified directory (keep original filename)
        out_path = output_dir / verilog_path.name
    else:
        out_path = verilog_path.with_name(verilog_path.stem + '_fixed' + verilog_path.suffix)

    # Write output
    print(f"Writing output to: {out_path}")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines) + '\n')

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Fix W164a width mismatch lint errors in Verilog files'
    )
    parser.add_argument('err_file', help='Lint error file (err.txt)')
    parser.add_argument('verilog_file', nargs='?', help='Input Verilog file (single file mode)')
    parser.add_argument('-d', '--directory', help='Process all matching .v files in directory (recursive)')
    parser.add_argument('-o', '--output', help='Output file (single file mode only)')
    parser.add_argument('-i', '--inplace', action='store_true', help='Modify files in place (directory mode)')

    args = parser.parse_args()

    # Validate arguments
    if not args.verilog_file and not args.directory:
        parser.error("Either verilog_file or --directory must be specified")

    if args.verilog_file and args.directory:
        parser.error("Cannot use both verilog_file and --directory")

    if args.directory and args.output:
        parser.error("--output cannot be used with --directory mode")

    # Parse lint errors
    print(f"Parsing lint errors from: {args.err_file}")
    all_errors = parse_lint_errors(args.err_file)

    if not all_errors:
        print("No W164a errors found in error file")
        sys.exit(1)

    print(f"Found {len(all_errors)} W164a error(s) in error file")

    # Get unique filenames from errors
    error_filenames = set(Path(err['file_path']).name for err in all_errors)
    print(f"Files with errors: {', '.join(sorted(error_filenames))}")

    if args.directory:
        # Directory mode: find and process all matching .v files
        dir_path = Path(args.directory)
        if not dir_path.is_dir():
            print(f"Error: Directory not found: {args.directory}")
            sys.exit(1)

        # Scan directory recursively for .v files
        all_v_files = list(dir_path.rglob('*.v'))
        print(f"\nFound {len(all_v_files)} .v file(s) in {dir_path}")

        # Filter to files that have errors
        matching_files = [f for f in all_v_files if f.name in error_filenames]
        print(f"Matching files with errors: {len(matching_files)}")

        if not matching_files:
            print("No matching Verilog files found in directory")
            sys.exit(0)

        # Process each matching file
        # Output to rtl_fixed_lint/ subdirectory in current working directory
        if not args.inplace:
            output_dir = Path.cwd() / 'rtl_fixed_lint'
            output_dir.mkdir(exist_ok=True)
            print(f"Output directory: {output_dir}")
        else:
            output_dir = None

        fixed_count = 0
        for vfile in matching_files:
            if process_single_file(vfile, all_errors, inplace=args.inplace, output_dir=output_dir):
                fixed_count += 1

        print(f"\n{'='*60}")
        if args.inplace:
            print(f"Done! Modified {fixed_count} file(s) in place")
        else:
            print(f"Done! Fixed {fixed_count} file(s), output to: {output_dir}")

    else:
        # Single file mode
        verilog_path = Path(args.verilog_file)
        if not verilog_path.exists():
            print(f"Error: Verilog file not found: {args.verilog_file}")
            sys.exit(1)

        output_path = Path(args.output) if args.output else None

        if not process_single_file(verilog_path, all_errors, output_path, args.inplace):
            print(f"No W164a errors found for {verilog_path.name}")
            sys.exit(0)

        print("\nDone!")


if __name__ == '__main__':
    main()
