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

// Case 1: output reg in ANSI port (with #param module)
// Case 2: output with separate reg
reg [DATA_W-1:0] sig_out_sep;

// Case 3: internal reg
reg [DATA_W-1:0] sig_internal;

// Case 4: internal wire
wire [DATA_W-1:0] sig_wire;

// Case 1: output reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sig_out_reg <= 8'd0;
    end else begin
        sig_out_reg <= data_in;
    end
end

// Case 2: output with separate reg - always block
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sig_out_sep <= 8'd0;
    end else begin
        sig_out_sep <= data_in;
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

// Case 4: internal wire - assign
assign sig_wire = data_in;

endmodule
