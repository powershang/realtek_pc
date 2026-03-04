module test_comb (
    input  [8:0] data_a,
    input  [7:0] data_b,
    input  [1:0] sel,
    output reg [7:0] sig_comb1
);

// Case comb-2: internal reg (body declaration)
reg [7:0] sig_comb2;

// Case comb-1: comb always if/else
// sig_comb1 = data_a (9-bit) reported; sig_comb1 = data_b (8-bit) unreported
// Unreported else branch must also get nc bit to prevent latch
always @(*) begin
    if (sel[0])
        sig_comb1 = data_a;
    else
        sig_comb1 = data_b;
end

// Case comb-2: comb always case, multiple RHS widths
// 9-bit and 10-bit branches reported; 8-bit branches unreported
// All branches must use max_nc (2 bits) to prevent latch
always @(*) begin
    case (sel)
        2'b00: sig_comb2 = data_b;
        2'b01: sig_comb2 = data_a;
        2'b10: sig_comb2 = {1'b0, data_a};
        default: sig_comb2 = 8'd0;
    endcase
end

endmodule
