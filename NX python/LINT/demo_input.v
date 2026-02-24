module demo_w164a_test (
    input wire clk,
    input wire rst_n,
    input wire enable,
    input wire [7:0] data_in
);

// Signal declarations
reg [7:0] counter_a;
reg [7:0] counter_b;
wire [7:0] sum_result;
reg [7:0] acc_reg;

// Combinational logic - counter_a (Test Case 1: Addition)
always @(*) begin
    if (rst_n == 1'b0)
        counter_a = 8'd0;
    else if (enable)
        counter_a = data_in + 8'd1;  // W164a: 8-bit = 9-bit
    else
        counter_a = data_in;
end

// Combinational logic - counter_b (Test Case 2: Multiple signals)
always @(*) begin
    if (rst_n == 1'b0)
        counter_b = 8'd0;
    else if (enable)
        counter_b = counter_a + 8'd1;  // W164a: 8-bit = 9-bit
    else
        counter_b = counter_a;
end

// Sequential logic (Test Case 6: Non-blocking)
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        acc_reg <= 8'd0;
    else if (enable)
        acc_reg <= acc_reg + 8'd1;  // W164a: 8-bit = 9-bit
    else
        acc_reg <= acc_reg;
end

endmodule
