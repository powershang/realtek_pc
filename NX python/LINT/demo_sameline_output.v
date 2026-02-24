module demo_sameline (
    input wire [7:0] data_in
);

reg [7:0] inline_reg;
reg inline_reg_nc;

// Edge Case: always and assignment on same line
always @(*) {inline_reg_nc, inline_reg} = {1'b0, data_in} + 9'd1;  // W164a

endmodule
