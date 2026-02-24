// Demo top module
module top_module (
    input [2:0] scan_si_dpi_dll_top_wrap_crt_dc1,
    output [26:0] scan_so_dpi_dll_top_wrap_crt_dc1,
    input scan_cp3_1_clk,
    output scan_cp3_2_clk
);

// Instance 1: dc1_dpi_scan_clk - only has scan clock related pins
dc1_dpi_scan_clk dc1_dpi_scan_clk_inst (
    .scan_cp3_1_clk(scan_cp3_1_clk),
    .scan_cp3_2_clk(scan_cp3_2_clk),
    .scan_cp3_3_clk(scan_cp3_3_clk),
    .scan_cp3_4_clk(scan_cp3_4_clk)
);

// Instance 2: dpi_dll_top_wrap - has scan si/so related pins
dpi_dll_top_wrap dpi_dll_top_wrap_inst (
    .scan_test_si(scan_si_dpi_dll_top_wrap_crt_dc1),
    .scan_test_so(scan_so_dpi_dll_top_wrap_crt_dc1),
    .scan_mode_dpi_dll_top_wrap_dc1(scan_mode_dpi_dll_top_wrap_dc1)
);

endmodule 