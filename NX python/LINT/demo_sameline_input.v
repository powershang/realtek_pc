module demo_sameline (
    input wire [7:0] data_in
);

reg [7:0] inline_reg;

// Edge Case: always and assignment on same line
always @(*) inline_reg = data_in + 8'd1;  // W164a

endmodule
