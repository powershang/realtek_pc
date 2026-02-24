module test_nonansi (clk, rst_n, data_in, sig_out_a, sig_out_b, sig_out_w);

input clk;
input rst_n;
input [8:0] data_in;
output [7:0] sig_out_a;
output [7:0] sig_out_b;
output [7:0] sig_out_w;

// Case 1: output with separate reg declaration
reg [7:0] sig_out_a;

// Case 2: output with separate reg declaration
reg [7:0] sig_out_b;

// Case 3: internal reg only
reg [7:0] sig_internal;

// Case 4: output wire with assign
wire [7:0] sig_out_w;

// Case 5: internal wire with assign
wire [7:0] sig_wire_int;

// Case 1: output reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sig_out_a <= 8'd0;
    end else begin
        sig_out_a <= data_in;
    end
end

// Case 2: output reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sig_out_b <= 8'd0;
    end else begin
        sig_out_b <= data_in;
    end
end

// Case 3: internal reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sig_internal <= 8'd0;
    end else begin
        sig_internal <= data_in;
    end
end

// Case 4: output wire - assign
assign sig_out_w = data_in;

// Case 5: internal wire - assign
assign sig_wire_int = data_in;

endmodule
