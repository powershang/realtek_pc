module demo_w164a_test (
    input wire clk,
    input wire rst_n,
    input wire enable,
    input wire [7:0] data_in
);

// Signal declarations
reg [7:0] counter_a;
reg counter_a_nc;
reg [7:0] counter_b;
reg counter_b_nc;
wire [7:0] sum_result;
reg [7:0] acc_reg;
reg acc_reg_nc;

// Combinational logic - counter_a (Test Case 1: Addition)
always @(*) begin
    if (rst_n == 1'b0)
        {counter_a_nc, counter_a} = 9'd0;
    else if (enable)
        {counter_a_nc, counter_a} = {1'b0, data_in} + 9'd1;  // W164a: 8-bit = 9-bit
    else
        {counter_a_nc, counter_a} = {1'b0, data_in};
end

// Combinational logic - counter_b (Test Case 2: Multiple signals)
always @(*) begin
    if (rst_n == 1'b0)
        {counter_b_nc, counter_b} = 9'd0;
    else if (enable)
        {counter_b_nc, counter_b} = {1'b0, counter_a} + 9'd1;  // W164a: 8-bit = 9-bit
    else
        {counter_b_nc, counter_b} = {1'b0, counter_a};
end

// Sequential logic (Test Case 6: Non-blocking)
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        {acc_reg_nc, acc_reg} <= 9'd0;
    else if (enable)
        {acc_reg_nc, acc_reg} <= {1'b0, acc_reg} + 9'd1;  // W164a: 8-bit = 9-bit
    else
        {acc_reg_nc, acc_reg} <= {1'b0, acc_reg};
end

endmodule
