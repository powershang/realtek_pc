module test_comb (
    input  [8:0] data_a,
    input  [7:0] data_b,
    input  [1:0] sel,
    output reg [7:0] sig_comb1
);
reg sig_comb1_nc;

// Case comb-2: internal reg (body declaration)
reg [7:0] sig_comb2;
reg [1:0] sig_comb2_nc;

// Case comb-1: comb always if/else
// sig_comb1 = data_a (9-bit) reported; sig_comb1 = data_b (8-bit) unreported
// Unreported else branch must also get nc bit to prevent latch
always @(*) begin
    if (sel[0])
        {sig_comb1_nc, sig_comb1} = data_a; // W164a fixed by lint_fixer
    else
        {sig_comb1_nc, sig_comb1} = data_b; // W164a fixed by lint_fixer
end

// Case comb-2: comb always case, multiple RHS widths
// 9-bit and 10-bit branches reported; 8-bit branches unreported
// All branches must use max_nc (2 bits) to prevent latch
always @(*) begin
    case (sel)
        2'b00: {sig_comb2_nc, sig_comb2} = data_b; // W164a fixed by lint_fixer
        2'b01: {sig_comb2_nc, sig_comb2} = data_a; // W164a fixed by lint_fixer
        2'b10: {sig_comb2_nc, sig_comb2} = {1'b0, data_a}; // W164a fixed by lint_fixer
        default: {sig_comb2_nc, sig_comb2} = 8'd0; // W164a fixed by lint_fixer
    endcase
end

endmodule
