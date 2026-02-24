module demo_edge_cases (
    input wire clk,
    input wire rst_n,
    input wire [7:0] data_in
);

// Signal declarations
reg [7:0] simple_reg;
reg [7:0] reg_a;
reg [7:0] reg_b;

// Edge Case 1: Always without begin/end (single statement)
always @(*)
    simple_reg = data_in + 8'd1;  // W164a: no begin/end

// Edge Case 2: Multiple registers in same always block
always @(*) begin
    reg_a = data_in + 8'd1;   // W164a
    reg_b = reg_a + 8'd1;     // W164a
end

endmodule
