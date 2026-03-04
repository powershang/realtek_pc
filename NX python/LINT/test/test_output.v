module test_mod (
    input  clk,
    input  rst_n,
    input  [8:0] data_in,
    output reg [7:0] sig_out_reg,
    output [7:0] sig_out_sep
);
reg sig_out_reg_nc;

// Case 1: pure reg outside port list
reg [7:0] sig_reg_pure;
reg sig_reg_pure_nc;

// Case 3: separate reg for output port
reg [7:0] sig_out_sep;
reg sig_out_sep_nc;

// Case 4: reg only in body, not in port list
reg [7:0] sig_body_only;
reg sig_body_only_nc;

// Case 5: parameter-based width
parameter DATA_W = 8;
reg [DATA_W-1:0] sig_param;
reg sig_param_nc;

// Case 6: wire with assign
wire [7:0] sig_wire;
wire sig_wire_nc;

// Case 1: pure reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_reg_pure_nc, sig_reg_pure} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_reg_pure_nc, sig_reg_pure} <= sig_reg_pure + 8'd1; // W164a fixed by lint_fixer
    end
end

// Case 2: output reg in ANSI port list - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_out_reg_nc, sig_out_reg} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_out_reg_nc, sig_out_reg} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 3: output with separate reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_out_sep_nc, sig_out_sep} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_out_sep_nc, sig_out_sep} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 4: body-only reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_body_only_nc, sig_body_only} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_body_only_nc, sig_body_only} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 5: parameter width - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_param_nc, sig_param} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_param_nc, sig_param} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 6: wire - assign statement
assign {sig_wire_nc, sig_wire} = data_in; // W164a fixed by lint_fixer

// Case 7: wire inline assignment
wire [7:0] sig_wire_inline;
wire sig_wire_inline_nc;
assign {sig_wire_inline_nc, sig_wire_inline} = data_in; // W164a fixed by lint_fixer

// Case 8: reg signed
reg signed [7:0] sig_signed;
reg signed sig_signed_nc;

// Case 8: reg signed - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_signed_nc, sig_signed} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_signed_nc, sig_signed} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 9: output reg with no space (e.g. output reg[8:0])
// Declaration is in port list line 5: output reg [7:0] sig_out_reg
// This case tests reg/wire with no space before bracket
reg[7:0] sig_nospace;
reg sig_nospace_nc;

// Case 9: no-space reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_nospace_nc, sig_nospace} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_nospace_nc, sig_nospace} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 10: array element (reg signed with array range)
reg signed [7:0] sig_arr[0:3];
reg signed sig_arr_1_nc;
reg signed sig_arr_0_nc;

// Case 10: array - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_arr_0_nc, sig_arr[0]} <= 8'd0; // W164a fixed by lint_fixer
        {sig_arr_1_nc, sig_arr[1]} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_arr_0_nc, sig_arr[0]} <= data_in; // W164a fixed by lint_fixer
        {sig_arr_1_nc, sig_arr[1]} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 11: multi-RHS-width (same signal, different RHS widths per line)
reg [7:0] sig_multi;
reg [4:0] sig_multi_nc;

// Case 11: multi-RHS - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_multi_nc, sig_multi} <= 8'd0; // W164a fixed by lint_fixer
    end else if (data_in[0]) begin
        {sig_multi_nc[0], sig_multi} <= data_in; // W164a fixed by lint_fixer
    end else begin
        {sig_multi_nc, sig_multi} <= {4'd0, data_in}; // W164a fixed by lint_fixer
    end
end

endmodule
