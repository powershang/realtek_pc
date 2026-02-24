module demo_edge_cases (
    input wire clk,
    input wire rst_n,
    input wire [7:0] data_in
);

// Signal declarations
reg [7:0] simple_reg;
reg simple_reg_nc;
reg [7:0] reg_a;
reg reg_a_nc;
reg [7:0] reg_b;
reg reg_b_nc;

// Edge Case 1: Always without begin/end (single statement)
always @(*)
    {simple_reg_nc, simple_reg} = {1'b0, data_in} + 9'd1;  // W164a: no begin/end

// Edge Case 2: Multiple registers in same always block
always @(*) begin
    {reg_a_nc, reg_a} = {1'b0, data_in} + 9'd1;   // W164a
    {reg_b_nc, reg_b} = {1'b0, reg_a} + 9'd1;     // W164a
end

endmodule
