module test_param #(
    parameter DATA_W = 8,
    parameter ADDR_W = 4
) (
    input  clk,
    input  rst_n,
    input  [DATA_W:0] data_in,
    output reg [DATA_W-1:0] sig_out_reg,
    output [DATA_W-1:0] sig_out_sep
);
reg sig_out_reg_nc;

// Case 1: output reg in ANSI port (with #param module)
// Case 2: output with separate reg
reg [DATA_W-1:0] sig_out_sep;
reg sig_out_sep_nc;

// Case 3: internal reg
reg [DATA_W-1:0] sig_internal;
reg sig_internal_nc;

// Case 4: internal wire
wire [DATA_W-1:0] sig_wire;
wire sig_wire_nc;

// Case 1: output reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_out_reg_nc, sig_out_reg} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_out_reg_nc, sig_out_reg} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 2: output with separate reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_out_sep_nc, sig_out_sep} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_out_sep_nc, sig_out_sep} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 3: internal reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_internal_nc, sig_internal} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_internal_nc, sig_internal} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 4: internal wire - assign
assign {sig_wire_nc, sig_wire} = data_in; // W164a fixed by lint_fixer

endmodule
