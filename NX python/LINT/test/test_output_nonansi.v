module test_nonansi (clk, rst_n, data_in, sig_out_a, sig_out_b, sig_out_w);

input clk;
input rst_n;
input [8:0] data_in;
output [7:0] sig_out_a;
output [7:0] sig_out_b;
output [7:0] sig_out_w;

// Case 1: output with separate reg declaration
reg [7:0] sig_out_a;
reg sig_out_a_nc;

// Case 2: output with separate reg declaration
reg [7:0] sig_out_b;
reg sig_out_b_nc;

// Case 3: internal reg only
reg [7:0] sig_internal;
reg sig_internal_nc;

// Case 4: output wire with assign
wire [7:0] sig_out_w;
wire sig_out_w_nc;

// Case 5: internal wire with assign
wire [7:0] sig_wire_int;
wire sig_wire_int_nc;

// Case 1: output reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_out_a_nc, sig_out_a} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_out_a_nc, sig_out_a} <= data_in; // W164a fixed by lint_fixer
    end
end

// Case 2: output reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        {sig_out_b_nc, sig_out_b} <= 8'd0; // W164a fixed by lint_fixer
    end else begin
        {sig_out_b_nc, sig_out_b} <= data_in; // W164a fixed by lint_fixer
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

// Case 4: output wire - assign
assign {sig_out_w_nc, sig_out_w} = data_in; // W164a fixed by lint_fixer

// Case 5: internal wire - assign
assign {sig_wire_int_nc, sig_wire_int} = data_in; // W164a fixed by lint_fixer

endmodule
