#!/usr/bin/env python3
"""
內建的 Register Map 資料
此檔案由 generate_embedded_regmap.py 自動產生，請勿手動修改

使用方式:
    from embedded_regmap import get_embedded_reg_map
    reg_map = get_embedded_reg_map()
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# 定義與 register_comparer.py 相同的資料結構
@dataclass
class BitField:
    """Register bit field 定義"""
    name: str
    high_bit: int
    low_bit: int

    def __str__(self):
        if self.high_bit == self.low_bit:
            return f"{self.name}[{self.high_bit}]"
        else:
            return f"{self.name}[{self.high_bit}:{self.low_bit}]"


@dataclass
class RegisterInfo:
    """Register 資訊"""
    offset: int
    fields: List[BitField] = field(default_factory=list)

    def get_field_value(self, value: int, field_name: str) -> Optional[int]:
        """取得特定 field 的值"""
        for f in self.fields:
            if f.name == field_name:
                mask = (1 << (f.high_bit - f.low_bit + 1)) - 1
                return (value >> f.low_bit) & mask
        return None


# 內建的 Register Map 資料 (由 generate_embedded_regmap.py 產生)
# 格式: {offset: [(name, high_bit, low_bit), ...]}
EMBEDDED_REGMAP_DATA: Dict[int, List[tuple]] = {
    0x2020: [("mem_num_cfg", 24, 24), ("lpddr5_en", 6, 6), ("lpddr4_en", 5, 5), ("lpddr3_en", 4, 4), ("ddr4_en", 1, 1), ("ddr3_en", 0, 0)],
    0x2028: [("mcx2_option", 31, 28), ("mcx2_mc1_act_cnt", 27, 24), ("mcx2_mc2_act_cnt", 23, 20), ("mcx2_mc1_act_sel", 19, 19), ("qos_cmd_mode", 16, 16), ("mcx2_mode", 9, 8), ("mcx1_2cke_en", 1, 1), ("mcx2_en", 0, 0)],
    0x202c: [("parser_int_en", 0, 0)],
    0x2030: [("geardown_en", 28, 28), ("geardown_pre_set_en", 27, 27), ("ddr4_x8", 2, 2), ("ddr4_x8_bg1_sel", 1, 0)],
    0x2034: [("ddrx_rst", 17, 17), ("ddrx_cke", 16, 16), ("ref_cmd_rst_delay_num", 15, 12), ("ddr_wck_en", 2, 2), ("ddr_wck_toggle", 1, 0)],
    0x2038: [("cfmt_security_en", 0, 0)],
    0x203c: [("cs_mrs_out_mode", 9, 8), ("ca_toggle_rate", 7, 5), ("cs_swap", 4, 4), ("lock_cs_1", 1, 1), ("lock_cs_0", 0, 0)],
    0x2040: [("pda_mode_dram_sel", 27, 24), ("pda_mode_en", 20, 20), ("rd_ecc_en", 19, 19), ("wr_ecc_en", 18, 18), ("rd_dbi_en", 17, 17), ("wr_dbi_en", 16, 16), ("wr_dbi_dq_byte_1", 15, 8), ("wr_dbi_dq_byte_0", 7, 0)],
    0x2044: [("odt_post_num", 26, 24), ("odt_lock_high", 17, 17), ("odt_en", 16, 16), ("udq_msb_sel", 13, 12), ("udq_lsb_sel", 9, 8), ("ldq_msb_sel", 5, 4), ("ldq_lsb_sel", 1, 0)],
    0x2050: [("ch_stop_req", 10, 0)],
    0x2060: [("max_conti_ref_num", 31, 28), ("ref_regulate", 23, 23), ("per_bank_ref_en", 17, 17), ("all_bank_ref_en", 16, 16), ("ref_pop_num", 10, 8), ("ref_pul_num", 2, 0)],
    0x2064: [("ref_2ref_d", 31, 24), ("immd_ref_aft_calib", 23, 23), ("ref_idle_mode", 21, 21), ("ref_idle_en", 20, 20), ("ref_idle_time", 11, 0)],
    0x2068: [("ref_rx_rst_cnt", 13, 8), ("ref_tx_rst_cnt", 5, 0)],
    0x2080: [("parser_algo", 31, 28), ("bank_full_option", 24, 24), ("act_bl_remain_thr", 23, 12), ("act_bl_calc", 10, 10), ("mask_tmccd", 9, 8), ("mask_tmccd_en", 7, 7), ("dis_ap", 5, 5), ("dis_preacc", 4, 4), ("dis_acc", 3, 3), ("dis_acc_interlave", 2, 2), ("dis_cmd_grp_in_order", 1, 1), ("en_cmd_bg_in_order", 0, 0)],
    0x2088: [("hppr_mode", 25, 25), ("sppr_mode", 24, 24), ("ddr4_cmd_bg_in_order", 1, 1), ("lpddr4_wmask_in_order", 0, 0)],
    0x2090: [("bank_free_tmrp_rd", 15, 8), ("bank_free_tmrp_wr", 7, 0)],
    0x2098: [("bank_free_bl_adj", 23, 23), ("bank_free_offset_updn", 22, 22), ("bank_free_offset", 21, 16), ("bank_free_tmrprcd_rd", 15, 8), ("bank_free_tmrprcd_wr", 7, 0)],
    0x20a0: [("bg_balance_1", 21, 16), ("bg_balance_0", 13, 8), ("bg_balance_en", 0, 0)],
    0x20f0: [("no_scramble", 8, 8), ("global_scramble_en", 4, 4), ("emi_scramble_en", 0, 0)],
    0x2100: [("cmd_start", 31, 31), ("cmd_execute_posi", 9, 8), ("cmd_num", 2, 0)],
    0x2110: [("cmd_ctl_cmd_1", 31, 0)],
    0x2114: [("cmd_ctl_cmd_2", 31, 0)],
    0x2118: [("cmd_ctl_cmd_3", 31, 0)],
    0x211c: [("cmd_ctl_cmd_4", 31, 0)],
    0x2120: [("cmd_ctl_cmd_5", 31, 0)],
    0x2130: [("cmd_ctl_t1", 31, 16), ("cmd_ctl_t0", 15, 0)],
    0x2138: [("cmd_ctl_t3", 31, 16), ("cmd_ctl_t2", 15, 0)],
    0x2140: [("cmd_ctl_t5", 31, 16), ("cmd_ctl_t4", 15, 0)],
    0x2200: [("tmras", 23, 16), ("tmrcl", 13, 8), ("tmcl", 5, 0)],
    0x2208: [("tmrrd", 28, 24), ("tmrp", 21, 16), ("tmrcdrd", 13, 8), ("tmrc", 7, 0)],
    0x2210: [("tmccd", 27, 24), ("tmrtp", 22, 16), ("tmwtr", 12, 8), ("tmwr", 5, 0)],
    0x2218: [("tmfaw", 31, 24), ("tmrp_a_sel", 17, 17), ("tmrc_sel", 16, 16), ("tmwrp_a", 15, 8), ("tmrrp_a", 7, 0)],
    0x2220: [("tmdqsck", 31, 28), ("tmrp_ab", 25, 20), ("tmwtr_l", 16, 12), ("tmrrd_l", 8, 4), ("tmccd_l", 3, 0)],
    0x2228: [("tmodt_on", 23, 20), ("tmodtl_on", 16, 12), ("tmrpst", 9, 8), ("tmccdmw", 5, 0)],
    0x222c: [("tmaad", 31, 28), ("tmccdmw_dbk_in_sbg", 27, 24), ("tmccdmw_dbk_in_dbg", 23, 20), ("tmccdmw_sbk_in_sbg", 19, 15), ("tmrtw_dbg", 13, 8), ("tmrtw_sbg", 5, 0)],
    0x2230: [("tmrank0_w2r", 29, 24), ("tmrank0_w2w", 21, 16), ("tmrank0_r2w", 13, 8), ("tmrank0_r2r", 5, 0)],
    0x2234: [("reg_rk_wait_exit_bl_cnt", 31, 22), ("reg_rk_wait_extend_self_bl_cnt", 21, 12), ("pbkref_postpone", 11, 11), ("dynamic_rank_acc", 10, 10), ("tm_rank0_acc_time", 9, 0)],
    0x2238: [("tmrank1_w2r", 29, 24), ("tmrank1_w2w", 21, 16), ("tmrank1_r2w", 13, 8), ("tmrank1_r2r", 5, 0)],
    0x2240: [("reg_rk_wait_extend_other_bl_cnt", 25, 16), ("pbk_exec_period_en", 14, 14), ("pbk_wait_bank_empty_en", 13, 13), ("pbk_ref_lock_bk_ignore", 12, 12), ("tm_rank1_acc_time", 9, 0)],
    0x2244: [("lp5_tm_rank_arb_en", 1, 1), ("lp4_tm_rank_arb_en", 0, 0)],
    0x2248: [("tm_wckpre_toggle_fs_pre", 28, 24), ("tm_wckenlfs", 20, 16), ("tm_wckpre_static", 12, 8), ("tm_wckpre_toggle_fs", 4, 0)],
    0x22a0: [("t_refi", 31, 16), ("t_refc", 10, 0)],
    0x22a4: [("t_refi_max", 31, 16), ("t_no_ref_max", 15, 0)],
    0x22a8: [("tmpbr2act", 31, 24), ("tmrefi_pb", 22, 12), ("tmrfc_pb", 8, 0)],
    0x22ac: [("tmrefi_pb_timeout", 22, 12), ("tmpbr2pbr", 8, 0)],
    0x2300: [("t_odt_dfi", 28, 24), ("t_ca_dfi", 20, 16), ("t_write_dfi_en", 12, 8), ("t_read_dfi_en", 4, 0)],
    0x2304: [("t_gck_enable", 13, 13), ("t_gck_write_dfi_en", 12, 8), ("t_gck_read_dfi_en", 4, 0)],
    0x2710: [("qos_dbg_sel", 27, 24), ("qos_dummy", 23, 16)],
    0x2718: [("modr_dbg_en", 31, 31), ("modr_dbg_sel", 29, 24)],
    0x271c: [("mc_force_int", 9, 8), ("mc_force_int_en", 1, 0)],
    0x2720: [("parser_rbus_dbg_bg1_sel", 14, 12), ("parser_rbus_dbg_bg0_sel", 10, 8), ("parser_rbus_dbg_sel", 4, 0)],
    0x2734: [("phy_dbg_sel", 5, 0)],
    0x273c: [("fake_rd_id", 23, 16), ("fake_rd_id_en", 0, 0)],
    0x2740: [("dummy_wdg_rst_fw0", 31, 0)],
    0x2744: [("dummy_wdg_rst_fw1", 31, 0)],
    0x2748: [("dummy_wdg_rst_fw2", 31, 0)],
    0x274c: [("dummy_wdg_rst_fw3", 31, 0)],
    0x2750: [("dummy_fw0", 31, 0)],
    0x2754: [("dummy_fw1", 31, 0)],
    0x2758: [("dummy_fw2", 31, 0)],
    0x275c: [("dummy_fw3", 31, 0)],
    0x2760: [("dummy_fw4", 31, 0)],
    0x2764: [("dummy_fw5", 31, 0)],
    0x2768: [("dummy_fw6", 31, 0)],
    0x276c: [("dummy_fw7", 31, 0)],
    0x2770: [("dummy_fw8", 31, 0)],
    0x2774: [("dummy_fw9", 31, 0)],
    0x2778: [("dummy_fw10", 31, 0)],
    0x277c: [("dummy_fw11", 31, 0)],
    0x2780: [("dummy_fw12", 31, 0)],
    0x2784: [("dummy_fw13", 31, 0)],
    0x2788: [("dummy_fw14", 31, 0)],
    0x278c: [("dummy_fw15", 31, 0)],
    0x2800: [("limit_ostd_cmd_max_lv2_0", 31, 28), ("limit_cmd_extend_num_lv2_0", 27, 24), ("limit_ostd_cmd_max_0", 23, 20), ("limit_cmd_extend_num_0", 19, 16), ("limit_ref_list_0", 15, 2), ("limit_en_0", 1, 0)],
    0x2804: [("limit_ostd_cmd_max_lv2_1", 31, 28), ("limit_cmd_extend_num_lv2_1", 27, 24), ("limit_ostd_cmd_max_1", 23, 20), ("limit_cmd_extend_num_1", 19, 16), ("limit_ref_list_1", 15, 2), ("limit_en_1", 1, 0)],
    0x2808: [("limit_ostd_cmd_max_lv2_2", 31, 28), ("limit_cmd_extend_num_lv2_2", 27, 24), ("limit_ostd_cmd_max_2", 23, 20), ("limit_cmd_extend_num_2", 19, 16), ("limit_ref_list_2", 15, 2), ("limit_en_2", 1, 0)],
    0x280c: [("limit_ostd_cmd_max_lv2_3", 31, 28), ("limit_cmd_extend_num_lv2_3", 27, 24), ("limit_ostd_cmd_max_3", 23, 20), ("limit_cmd_extend_num_3", 19, 16), ("limit_ref_list_3", 15, 2), ("limit_en_3", 1, 0)],
    0x2810: [("limit_ostd_cmd_max_lv2_4", 31, 28), ("limit_cmd_extend_num_lv2_4", 27, 24), ("limit_ostd_cmd_max_4", 23, 20), ("limit_cmd_extend_num_4", 19, 16), ("limit_ref_list_4", 15, 2), ("limit_en_4", 1, 0)],
    0x2814: [("limit_ostd_cmd_max_lv2_5", 31, 28), ("limit_cmd_extend_num_lv2_5", 27, 24), ("limit_ostd_cmd_max_5", 23, 20), ("limit_cmd_extend_num_5", 19, 16), ("limit_ref_list_5", 15, 2), ("limit_en_5", 1, 0)],
    0x2818: [("limit_ostd_cmd_max_lv2_6", 31, 28), ("limit_cmd_extend_num_lv2_6", 27, 24), ("limit_ostd_cmd_max_6", 23, 20), ("limit_cmd_extend_num_6", 19, 16), ("limit_ref_list_6", 15, 2), ("limit_en_6", 1, 0)],
    0x281c: [("limit_ostd_cmd_max_lv2_7", 31, 28), ("limit_cmd_extend_num_lv2_7", 27, 24), ("limit_ostd_cmd_max_7", 23, 20), ("limit_cmd_extend_num_7", 19, 16), ("limit_ref_list_7", 15, 2), ("limit_en_7", 1, 0)],
    0x2820: [("limit_ostd_cmd_max_lv2_8", 31, 28), ("limit_cmd_extend_num_lv2_8", 27, 24), ("limit_ostd_cmd_max_8", 23, 20), ("limit_cmd_extend_num_8", 19, 16), ("limit_ref_list_8", 15, 2), ("limit_en_8", 1, 0)],
    0x2824: [("limit_ostd_cmd_max_lv2_9", 31, 28), ("limit_cmd_extend_num_lv2_9", 27, 24), ("limit_ostd_cmd_max_9", 23, 20), ("limit_cmd_extend_num_9", 19, 16), ("limit_ref_list_9", 15, 2), ("limit_en_9", 1, 0)],
    0x2828: [("limit_ostd_cmd_max_lv2_10", 31, 28), ("limit_cmd_extend_num_lv2_10", 27, 24), ("limit_ostd_cmd_max_10", 23, 20), ("limit_cmd_extend_num_10", 19, 16), ("limit_ref_list_10", 15, 2), ("limit_en_10", 1, 0)],
    0x2840: [("limit_data_num_lv2_0", 31, 16), ("limit_data_num_0", 15, 0)],
    0x2844: [("limit_data_num_lv2_1", 31, 16), ("limit_data_num_1", 15, 0)],
    0x2848: [("limit_data_num_lv2_2", 31, 16), ("limit_data_num_2", 15, 0)],
    0x284c: [("limit_data_num_lv2_3", 31, 16), ("limit_data_num_3", 15, 0)],
    0x2850: [("limit_data_num_lv2_4", 31, 16), ("limit_data_num_4", 15, 0)],
    0x2854: [("limit_data_num_lv2_5", 31, 16), ("limit_data_num_5", 15, 0)],
    0x2858: [("limit_data_num_lv2_6", 31, 16), ("limit_data_num_6", 15, 0)],
    0x285c: [("limit_data_num_lv2_7", 31, 16), ("limit_data_num_7", 15, 0)],
    0x2860: [("limit_data_num_lv2_8", 31, 16), ("limit_data_num_8", 15, 0)],
    0x2864: [("limit_data_num_lv2_9", 31, 16), ("limit_data_num_9", 15, 0)],
    0x2868: [("limit_data_num_lv2_10", 31, 16), ("limit_data_num_10", 15, 0)],
    0x2880: [("limit_timer_cycle_0", 15, 0)],
    0x2884: [("limit_timer_cycle_1", 15, 0)],
    0x2888: [("limit_timer_cycle_2", 15, 0)],
    0x288c: [("limit_timer_cycle_3", 15, 0)],
    0x2890: [("limit_timer_cycle_4", 15, 0)],
    0x2894: [("limit_timer_cycle_5", 15, 0)],
    0x2898: [("limit_timer_cycle_6", 15, 0)],
    0x289c: [("limit_timer_cycle_7", 15, 0)],
    0x28a0: [("limit_timer_cycle_8", 15, 0)],
    0x28a4: [("limit_timer_cycle_9", 15, 0)],
    0x28a8: [("limit_timer_cycle_10", 15, 0)],
    0x2a00: [("hi_priority_id6_en", 22, 22), ("hi_priority_id3_en", 19, 19), ("hi_priority_id2_en", 18, 18), ("hi_priority_id1_en", 17, 17), ("hi_priority_id0_en", 16, 16), ("dis_tracking_gp1_id_en", 15, 15), ("dis_tracking_gp0_id_en", 14, 14), ("dis_tracking_id0_en", 13, 13), ("dis_tracking_id1_en", 12, 12), ("ch_ref_bl_gt_sel", 11, 11), ("ch_un_match_id_pg_wt", 10, 10), ("ch_tag_tracking", 9, 9), ("ch_dir_cont_chg_sel", 8, 8), ("ch_parser_cmd_limt_sel", 7, 7), ("ch_dir_short_dly_en", 6, 6), ("ch_dir_cont_bl_mode", 5, 4), ("tracking_sel", 3, 3), ("bank_wr_sel", 2, 2), ("channel_id_weight_en", 1, 1), ("channel_rw_weight_en", 0, 0)],
    0x2a04: [("wms_bk_we_map", 1, 1), ("wms_bf_bl_sel", 0, 0)],
    0x2a10: [("hi_priority_id3", 31, 24), ("hi_priority_id2", 23, 16), ("hi_priority_id1", 15, 8), ("hi_priority_id0", 7, 0)],
    0x2a14: [("hi_priority_mask_id6", 31, 24), ("hi_priority_id6", 23, 16)],
    0x2a18: [("ch_dir_max_bl", 31, 20), ("reg_ch_rw_match_mask_cycel_sel", 18, 16), ("reg_ch_wr_chg_wait_time", 12, 8), ("reg_wr_chg_revert_en", 4, 4)],
    0x2a1c: [("total_rw_bl_low_bound_2", 28, 16)],
    0x2a20: [("total_rw_bl_low_bound_w", 28, 16), ("total_rw_bl_low_bound_r", 12, 0)],
    0x2a24: [("long_bl_thr", 21, 16), ("short_rw_ps_bl_thr", 12, 8), ("short_rw_bl_thr", 7, 0)],
    0x2a28: [("ref_mask_dir", 31, 30), ("ddr4_cmd_inorder_en", 24, 24), ("ref_mask_ch", 23, 20), ("ref_mask_urg2_ch", 16, 8), ("ref_mask_id3_en", 7, 7), ("ref_mask_id2_en", 6, 6), ("ref_mask_id1_en", 5, 5), ("ref_mask_id0_en", 4, 4), ("ch_ahead_en", 0, 0)],
    0x2a2c: [("ch_parser_total_bl_max", 25, 16), ("ch_ddr4_balance_cmd_max", 7, 4), ("ch_parser_cmd_max", 3, 0)],
    0x2a30: [("ddr4_balance_bl_thr", 21, 16), ("ddr4_db_tracking", 2, 2), ("ddr4_fast_con", 1, 1), ("ddr4_balance_con", 0, 0)],
    0x2a34: [("ch_max_id_bl_thr", 25, 16), ("ch_max_id_bl_en", 0, 0)],
    0x2a3c: [("dis_tracking_gp0_id", 23, 20), ("dis_tracking_gp1_id", 19, 16), ("dis_tracking_id1", 15, 8), ("dis_tracking_id0", 7, 0)],
    0x2a60: [("ch0_bg_insert_mapping", 31, 28), ("ch0_page_insert_mapping", 27, 24), ("ch0_bank_free_mapping", 23, 20), ("ch0_dir_insert_mapping", 19, 16), ("ch0_r2w_dir_insert_mapping", 15, 12), ("ch0_acc_trigger_sel", 11, 11), ("ch0_acc_mode", 10, 10), ("ch0_acc_clr_mode", 9, 8), ("ch0_urg2_wr_brk_en", 7, 7), ("ch0_urg2_strong_en", 4, 4), ("ch0_oldest_timer_2_en", 3, 3), ("ch0_oldest_timer_en", 2, 2), ("ch0_oldest_cmd_select_en", 1, 1)],
    0x2a64: [("ch0_quota_bw_ini", 31, 24), ("ch0_bw_quota_max", 15, 8)],
    0x2a68: [("ch0_oldest_time_2", 31, 20), ("ch0_oldest_time", 19, 8), ("ch0_bw_acc_unit", 3, 0)],
    0x2a6c: [("ch0_cmd_extend_num", 31, 28), ("ch0_extend_bl_max", 25, 20), ("ch0_ostd_bl_max", 19, 8), ("ch0_ostd_cmd_max", 7, 4), ("ch0_outstand_en", 0, 0)],
    0x2a70: [("ch0_wr_brk_time", 9, 0)],
    0x2a74: [("ch0_wms_bg_insert_mapping", 31, 28), ("ch0_wms_page_insert_mapping", 27, 24), ("ch0_wms_bank_free_mapping", 23, 20), ("ch0_wms_dir_insert_mapping", 19, 16), ("ch0_wms_r2w_dir_insert_mapping", 15, 12), ("ch0_wmask_insert_mapping", 11, 8)],
    0x2a80: [("ch1_bg_insert_mapping", 31, 28), ("ch1_page_insert_mapping", 27, 24), ("ch1_bank_free_mapping", 23, 20), ("ch1_dir_insert_mapping", 19, 16), ("ch1_r2w_dir_insert_mapping", 15, 12), ("ch1_acc_trigger_sel", 11, 11), ("ch1_acc_mode", 10, 10), ("ch1_acc_clr_mode", 9, 8), ("ch1_urg2_wr_brk_en", 7, 7), ("ch1_urg2_strong_en", 4, 4), ("ch1_oldest_timer_2_en", 3, 3), ("ch1_oldest_timer_en", 2, 2), ("ch1_oldest_cmd_select_en", 1, 1)],
    0x2a84: [("ch1_quota_bw_ini", 31, 24), ("ch1_bw_quota_max", 15, 8)],
    0x2a88: [("ch1_oldest_time_2", 31, 20), ("ch1_oldest_time", 19, 8), ("ch1_bw_acc_unit", 3, 0)],
    0x2a8c: [("ch1_cmd_extend_num", 31, 28), ("ch1_extend_bl_max", 25, 20), ("ch1_ostd_bl_max", 19, 8), ("ch1_ostd_cmd_max", 7, 4), ("ch1_outstand_en", 0, 0)],
    0x2a90: [("ch1_wr_brk_time", 9, 0)],
    0x2a94: [("ch1_wms_bg_insert_mapping", 31, 28), ("ch1_wms_page_insert_mapping", 27, 24), ("ch1_wms_bank_free_mapping", 23, 20), ("ch1_wms_dir_insert_mapping", 19, 16), ("ch1_wms_r2w_dir_insert_mapping", 15, 12), ("ch1_wmask_insert_mapping", 11, 8)],
    0x2aa0: [("ch2_bg_insert_mapping", 31, 28), ("ch2_page_insert_mapping", 27, 24), ("ch2_bank_free_mapping", 23, 20), ("ch2_dir_insert_mapping", 19, 16), ("ch2_r2w_dir_insert_mapping", 15, 12), ("ch2_acc_trigger_sel", 11, 11), ("ch2_acc_mode", 10, 10), ("ch2_acc_clr_mode", 9, 8), ("ch2_urg2_wr_brk_en", 7, 7), ("ch2_urg2_strong_en", 4, 4), ("ch2_oldest_timer_2_en", 3, 3), ("ch2_oldest_timer_en", 2, 2), ("ch2_oldest_cmd_select_en", 1, 1)],
    0x2aa4: [("ch2_quota_bw_ini", 31, 24), ("ch2_bw_quota_max", 15, 8)],
    0x2aa8: [("ch2_oldest_time_2", 31, 20), ("ch2_oldest_time", 19, 8), ("ch2_bw_acc_unit", 3, 0)],
    0x2aac: [("ch2_cmd_extend_num", 31, 28), ("ch2_extend_bl_max", 25, 20), ("ch2_ostd_bl_max", 19, 8), ("ch2_ostd_cmd_max", 7, 4), ("ch2_outstand_en", 0, 0)],
    0x2ab0: [("ch2_wr_brk_time", 9, 0)],
    0x2ab4: [("ch2_wms_bg_insert_mapping", 31, 28), ("ch2_wms_page_insert_mapping", 27, 24), ("ch2_wms_bank_free_mapping", 23, 20), ("ch2_wms_dir_insert_mapping", 19, 16), ("ch2_wms_r2w_dir_insert_mapping", 15, 12), ("ch2_wmask_insert_mapping", 11, 8)],
    0x2ac0: [("ch3_bg_insert_mapping", 31, 28), ("ch3_page_insert_mapping", 27, 24), ("ch3_bank_free_mapping", 23, 20), ("ch3_dir_insert_mapping", 19, 16), ("ch3_r2w_dir_insert_mapping", 15, 12), ("ch3_acc_trigger_sel", 11, 11), ("ch3_acc_mode", 10, 10), ("ch3_acc_clr_mode", 9, 8), ("ch3_urg2_wr_brk_en", 7, 7), ("ch3_urg2_strong_en", 4, 4), ("ch3_oldest_timer_2_en", 3, 3), ("ch3_oldest_timer_en", 2, 2), ("ch3_oldest_cmd_select_en", 1, 1)],
    0x2ac4: [("ch3_quota_bw_ini", 31, 24), ("ch3_bw_quota_max", 15, 8)],
    0x2ac8: [("ch3_oldest_time_2", 31, 20), ("ch3_oldest_time", 19, 8), ("ch3_bw_acc_unit", 3, 0)],
    0x2acc: [("ch3_cmd_extend_num", 31, 28), ("ch3_extend_bl_max", 25, 20), ("ch3_ostd_bl_max", 19, 8), ("ch3_ostd_cmd_max", 7, 4), ("ch3_outstand_en", 0, 0)],
    0x2ad0: [("ch3_wr_brk_time", 9, 0)],
    0x2ad4: [("ch3_wms_bg_insert_mapping", 31, 28), ("ch3_wms_page_insert_mapping", 27, 24), ("ch3_wms_bank_free_mapping", 23, 20), ("ch3_wms_dir_insert_mapping", 19, 16), ("ch3_wms_r2w_dir_insert_mapping", 15, 12), ("ch3_wmask_insert_mapping", 11, 8)],
    0x2ae0: [("ch4_bg_insert_mapping", 31, 28), ("ch4_page_insert_mapping", 27, 24), ("ch4_bank_free_mapping", 23, 20), ("ch4_dir_insert_mapping", 19, 16), ("ch4_r2w_dir_insert_mapping", 15, 12), ("ch4_acc_trigger_sel", 11, 11), ("ch4_acc_mode", 10, 10), ("ch4_acc_clr_mode", 9, 8), ("ch4_urg2_wr_brk_en", 7, 7), ("ch4_urg2_strong_en", 4, 4), ("ch4_oldest_timer_2_en", 3, 3), ("ch4_oldest_timer_en", 2, 2), ("ch4_oldest_cmd_select_en", 1, 1)],
    0x2ae4: [("ch4_quota_bw_ini", 31, 24), ("ch4_bw_quota_max", 15, 8)],
    0x2ae8: [("ch4_oldest_time_2", 31, 20), ("ch4_oldest_time", 19, 8), ("ch4_bw_acc_unit", 3, 0)],
    0x2aec: [("ch4_cmd_extend_num", 31, 28), ("ch4_extend_bl_max", 25, 20), ("ch4_ostd_bl_max", 19, 8), ("ch4_ostd_cmd_max", 7, 4), ("ch4_outstand_en", 0, 0)],
    0x2af0: [("ch4_wr_brk_time", 9, 0)],
    0x2af4: [("ch4_wms_bg_insert_mapping", 31, 28), ("ch4_wms_page_insert_mapping", 27, 24), ("ch4_wms_bank_free_mapping", 23, 20), ("ch4_wms_dir_insert_mapping", 19, 16), ("ch4_wms_r2w_dir_insert_mapping", 15, 12), ("ch4_wmask_insert_mapping", 11, 8)],
    0x2b00: [("ch5_bg_insert_mapping", 31, 28), ("ch5_page_insert_mapping", 27, 24), ("ch5_bank_free_mapping", 23, 20), ("ch5_dir_insert_mapping", 19, 16), ("ch5_r2w_dir_insert_mapping", 15, 12), ("ch5_acc_trigger_sel", 11, 11), ("ch5_acc_mode", 10, 10), ("ch5_acc_clr_mode", 9, 8), ("ch5_urg2_wr_brk_en", 7, 7), ("ch5_urg2_strong_en", 4, 4), ("ch5_oldest_timer_2_en", 3, 3), ("ch5_oldest_timer_en", 2, 2), ("ch5_oldest_cmd_select_en", 1, 1)],
    0x2b04: [("ch5_quota_bw_ini", 31, 24), ("ch5_bw_quota_max", 15, 8)],
    0x2b08: [("ch5_oldest_time_2", 31, 20), ("ch5_oldest_time", 19, 8), ("ch5_bw_acc_unit", 3, 0)],
    0x2b0c: [("ch5_cmd_extend_num", 31, 28), ("ch5_extend_bl_max", 25, 20), ("ch5_ostd_bl_max", 19, 8), ("ch5_ostd_cmd_max", 7, 4), ("ch5_outstand_en", 0, 0)],
    0x2b10: [("ch5_wr_brk_time", 9, 0)],
    0x2b14: [("ch5_wms_bg_insert_mapping", 31, 28), ("ch5_wms_page_insert_mapping", 27, 24), ("ch5_wms_bank_free_mapping", 23, 20), ("ch5_wms_dir_insert_mapping", 19, 16), ("ch5_wms_r2w_dir_insert_mapping", 15, 12), ("ch5_wmask_insert_mapping", 11, 8)],
    0x2b20: [("ch6_bg_insert_mapping", 31, 28), ("ch6_page_insert_mapping", 27, 24), ("ch6_bank_free_mapping", 23, 20), ("ch6_dir_insert_mapping", 19, 16), ("ch6_r2w_dir_insert_mapping", 15, 12), ("ch6_acc_trigger_sel", 11, 11), ("ch6_acc_mode", 10, 10), ("ch6_acc_clr_mode", 9, 8), ("ch6_urg2_wr_brk_en", 7, 7), ("ch6_urg2_strong_en", 4, 4), ("ch6_oldest_timer_2_en", 3, 3), ("ch6_oldest_timer_en", 2, 2), ("ch6_oldest_cmd_select_en", 1, 1)],
    0x2b24: [("ch6_quota_bw_ini", 31, 24), ("ch6_bw_quota_max", 15, 8)],
    0x2b28: [("ch6_oldest_time_2", 31, 20), ("ch6_oldest_time", 19, 8), ("ch6_bw_acc_unit", 3, 0)],
    0x2b2c: [("ch6_cmd_extend_num", 31, 28), ("ch6_extend_bl_max", 25, 20), ("ch6_ostd_bl_max", 19, 8), ("ch6_ostd_cmd_max", 7, 4), ("ch6_outstand_en", 0, 0)],
    0x2b30: [("ch6_wr_brk_time", 9, 0)],
    0x2b34: [("ch6_wms_bg_insert_mapping", 31, 28), ("ch6_wms_page_insert_mapping", 27, 24), ("ch6_wms_bank_free_mapping", 23, 20), ("ch6_wms_dir_insert_mapping", 19, 16), ("ch6_wms_r2w_dir_insert_mapping", 15, 12), ("ch6_wmask_insert_mapping", 11, 8)],
    0x2b40: [("ch7_bg_insert_mapping", 31, 28), ("ch7_page_insert_mapping", 27, 24), ("ch7_bank_free_mapping", 23, 20), ("ch7_dir_insert_mapping", 19, 16), ("ch7_r2w_dir_insert_mapping", 15, 12), ("ch7_acc_trigger_sel", 11, 11), ("ch7_acc_mode", 10, 10), ("ch7_acc_clr_mode", 9, 8), ("ch7_urg2_wr_brk_en", 7, 7), ("ch7_urg2_strong_en", 4, 4), ("ch7_oldest_timer_2_en", 3, 3), ("ch7_oldest_timer_en", 2, 2), ("ch7_oldest_cmd_select_en", 1, 1)],
    0x2b44: [("ch7_quota_bw_ini", 31, 24), ("ch7_bw_quota_max", 15, 8)],
    0x2b48: [("ch7_oldest_time_2", 31, 20), ("ch7_oldest_time", 19, 8), ("ch7_bw_acc_unit", 3, 0)],
    0x2b4c: [("ch7_cmd_extend_num", 31, 28), ("ch7_extend_bl_max", 25, 20), ("ch7_ostd_bl_max", 19, 8), ("ch7_ostd_cmd_max", 7, 4), ("ch7_outstand_en", 0, 0)],
    0x2b50: [("ch7_wr_brk_time", 9, 0)],
    0x2b54: [("ch7_wms_bg_insert_mapping", 31, 28), ("ch7_wms_page_insert_mapping", 27, 24), ("ch7_wms_bank_free_mapping", 23, 20), ("ch7_wms_dir_insert_mapping", 19, 16), ("ch7_wms_r2w_dir_insert_mapping", 15, 12), ("ch7_wmask_insert_mapping", 11, 8)],
    0x2b60: [("ch8_bg_insert_mapping", 31, 28), ("ch8_page_insert_mapping", 27, 24), ("ch8_bank_free_mapping", 23, 20), ("ch8_dir_insert_mapping", 19, 16), ("ch8_r2w_dir_insert_mapping", 15, 12), ("ch8_acc_trigger_sel", 11, 11), ("ch8_acc_mode", 10, 10), ("ch8_acc_clr_mode", 9, 8), ("ch8_urg2_wr_brk_en", 7, 7), ("ch8_urg2_strong_en", 4, 4), ("ch8_oldest_timer_2_en", 3, 3), ("ch8_oldest_timer_en", 2, 2), ("ch8_oldest_cmd_select_en", 1, 1)],
    0x2b64: [("ch8_quota_bw_ini", 31, 24), ("ch8_bw_quota_max", 15, 8)],
    0x2b68: [("ch8_oldest_time_2", 31, 20), ("ch8_oldest_time", 19, 8), ("ch8_bw_acc_unit", 3, 0)],
    0x2b6c: [("ch8_cmd_extend_num", 31, 28), ("ch8_extend_bl_max", 25, 20), ("ch8_ostd_bl_max", 19, 8), ("ch8_ostd_cmd_max", 7, 4), ("ch8_outstand_en", 0, 0)],
    0x2b70: [("ch8_wr_brk_time", 9, 0)],
    0x2b74: [("ch8_wms_bg_insert_mapping", 31, 28), ("ch8_wms_page_insert_mapping", 27, 24), ("ch8_wms_bank_free_mapping", 23, 20), ("ch8_wms_dir_insert_mapping", 19, 16), ("ch8_wms_r2w_dir_insert_mapping", 15, 12), ("ch8_wmask_insert_mapping", 11, 8)],
    0x2b80: [("ch9_bg_insert_mapping", 31, 28), ("ch9_page_insert_mapping", 27, 24), ("ch9_bank_free_mapping", 23, 20), ("ch9_dir_insert_mapping", 19, 16), ("ch9_r2w_dir_insert_mapping", 15, 12), ("ch9_acc_trigger_sel", 11, 11), ("ch9_acc_mode", 10, 10), ("ch9_acc_clr_mode", 9, 8), ("ch9_urg2_wr_brk_en", 7, 7), ("ch9_urg2_strong_en", 4, 4), ("ch9_oldest_timer_2_en", 3, 3), ("ch9_oldest_timer_en", 2, 2), ("ch9_oldest_cmd_select_en", 1, 1)],
    0x2b84: [("ch9_quota_bw_ini", 31, 24), ("ch9_bw_quota_max", 15, 8)],
    0x2b88: [("ch9_oldest_time_2", 31, 20), ("ch9_oldest_time", 19, 8), ("ch9_bw_acc_unit", 3, 0)],
    0x2b8c: [("ch9_cmd_extend_num", 31, 28), ("ch9_extend_bl_max", 25, 20), ("ch9_ostd_bl_max", 19, 8), ("ch9_ostd_cmd_max", 7, 4), ("ch9_outstand_en", 0, 0)],
    0x2b90: [("ch9_wr_brk_time", 9, 0)],
    0x2b94: [("ch9_wms_bg_insert_mapping", 31, 28), ("ch9_wms_page_insert_mapping", 27, 24), ("ch9_wms_bank_free_mapping", 23, 20), ("ch9_wms_dir_insert_mapping", 19, 16), ("ch9_wms_r2w_dir_insert_mapping", 15, 12), ("ch9_wmask_insert_mapping", 11, 8)],
    0x2ba0: [("ch10_bg_insert_mapping", 31, 28), ("ch10_page_insert_mapping", 27, 24), ("ch10_bank_free_mapping", 23, 20), ("ch10_dir_insert_mapping", 19, 16), ("ch10_r2w_dir_insert_mapping", 15, 12), ("ch10_acc_trigger_sel", 11, 11), ("ch10_acc_mode", 10, 10), ("ch10_acc_clr_mode", 9, 8), ("ch10_urg2_wr_brk_en", 7, 7), ("ch10_urg2_strong_en", 4, 4), ("ch10_oldest_timer_2_en", 3, 3), ("ch10_oldest_timer_en", 2, 2), ("ch10_oldest_cmd_select_en", 1, 1)],
    0x2ba4: [("ch10_quota_bw_ini", 31, 24), ("ch10_bw_quota_max", 15, 8)],
    0x2ba8: [("ch10_oldest_time_2", 31, 20), ("ch10_oldest_time", 19, 8), ("ch10_bw_acc_unit", 3, 0)],
    0x2bac: [("ch10_cmd_extend_num", 31, 28), ("ch10_extend_bl_max", 25, 20), ("ch10_ostd_bl_max", 19, 8), ("ch10_ostd_cmd_max", 7, 4), ("ch10_outstand_en", 0, 0)],
    0x2bb0: [("ch10_wr_brk_time", 9, 0)],
    0x2bb4: [("ch10_wms_bg_insert_mapping", 31, 28), ("ch10_wms_page_insert_mapping", 27, 24), ("ch10_wms_bank_free_mapping", 23, 20), ("ch10_wms_dir_insert_mapping", 19, 16), ("ch10_wms_r2w_dir_insert_mapping", 15, 12), ("ch10_wmask_insert_mapping", 11, 8)],
    0x2c00: [("meas_sram_last_w_num", 26, 16), ("meas_rk_ctrl_mc2", 9, 8), ("meas_rk_ctrl_mc1", 7, 6), ("meas_sram_w_addr_rst", 5, 5), ("meas_sram_one_time", 4, 4), ("meas_sram_mode_ctrl", 3, 0)],
    0x2c04: [("meas_sram_r_add_inc", 31, 31), ("meas_sram_r_addr_sync", 15, 15), ("meas_sram_r_addr", 10, 0)],
    0x2c08: [("meas_one_shot_mode_en", 31, 31), ("meas_cnt_mode_max_en", 30, 30), ("meas_cnt_mode_avg_en", 29, 29), ("meas_cnt_record_mode", 28, 28), ("meas_timer1_sync", 10, 9), ("meas_trig_sel", 8, 8), ("meas_serial_cont", 5, 5), ("meas_mode", 4, 4), ("meas_start", 0, 0)],
    0x2c0c: [("meas_timer1", 31, 0)],
    0x2c14: [("meas_cnt1_mask_en", 24, 24), ("meas_cnt1_id", 23, 16), ("meas_cnt1_mask_id", 15, 12), ("meas_cnt1_id_en", 10, 10), ("meas_cnt1_ddr_num", 9, 8)],
    0x2c18: [("meas_cnt2_mask_en", 24, 24), ("meas_cnt2_id", 23, 16), ("meas_cnt2_mask_id", 15, 12), ("meas_cnt2_id_en", 10, 10), ("meas_cnt2_ddr_num", 9, 8), ("meas_cnt2_mode", 0, 0)],
    0x2c1c: [("meas_cnt3_mask_en", 24, 24), ("meas_cnt3_id", 23, 16), ("meas_cnt3_mask_id", 15, 12), ("meas_cnt3_id_en", 10, 10), ("meas_cnt3_ddr_num", 9, 8), ("meas_cnt3_mode", 0, 0)],
    0x2c20: [("meas_cnt4_mask_en", 24, 24), ("meas_cnt4_id", 23, 16), ("meas_cnt4_mask_id", 15, 12), ("meas_cnt4_id_en", 10, 10), ("meas_cnt4_ddr_num", 9, 8), ("meas_cnt4_mode", 0, 0)],
    0x2c44: [("meas_en", 31, 31), ("meas_stop", 30, 30), ("meas_sram_clear_en", 29, 29), ("meas_page_addr_thr_en", 28, 28), ("meas_dram_num_sel", 27, 26), ("meas_timer_en", 25, 25), ("meas_counting_mode", 24, 24), ("addr_thr_cnt_mode_en", 23, 23), ("meas_mc_sel", 22, 21), ("meas_chop_cnt_en", 20, 20), ("meas_wmask_cnt_en", 19, 19)],
    0x2c50: [("meas_page_addr_thr2", 19, 12), ("meas_page_addr_thr1", 7, 0)],
    0x2c54: [("cnt_mode_irq_thershold", 31, 0)],
    0x2c58: [("cnt2_irq_en", 3, 3), ("cnt1_irq_en", 2, 2)],
    0x2c5c: [("mes_mem_tra_dc_sel", 31, 31), ("mes_mem_cmp_id", 23, 16), ("mes_mem_cmp_dir", 9, 8), ("mes_mem_tras_adr", 3, 3), ("mes_mem_tras_id", 1, 1), ("mes_mem_tras_en", 0, 0)],
    0x2c60: [("mes_cmp_addr", 31, 3)],
    0x2c64: [("mes_cmp_addr_mask", 31, 3)],
    0x2c68: [("eff_sram_testrwm_0", 20, 20), ("eff_sram_testrwm_1", 19, 19), ("eff_bist_mode", 18, 18), ("eff_sram_drf_mode", 17, 17), ("eff_sram_test1", 16, 16), ("eff_sram_drf_resume", 15, 15), ("eff_sram_ls", 13, 13), ("eff_sram_rme", 12, 12), ("eff_sram_rm", 11, 8), ("eff_sram_bc1_0", 7, 7), ("eff_sram_bc1_1", 6, 6), ("eff_sram_bc2_0", 5, 5), ("eff_sram_bc2_1", 4, 4), ("eff_sram_test_rnm_0", 3, 3), ("eff_sram_test_rnm_1", 2, 2), ("eff_sram_scan_shift_en", 1, 1), ("eff_mem_speed_mode", 0, 0)],
    0x2c6c: [("eff_meas_sram1_config_from_reg_en", 29, 29), ("eff_meas_sram0_config_from_reg_en", 28, 28), ("eff_meas_sram1_wtsel", 27, 26), ("eff_meas_sram1_rtsel", 25, 24), ("eff_meas_sram1_mtsel", 23, 22), ("eff_meas_sram0_wtsel", 21, 20), ("eff_meas_sram0_rtsel", 19, 18), ("eff_meas_sram0_mtsel", 17, 16), ("eff_meas_sram1_ls_7", 15, 15), ("eff_meas_sram1_ls_6", 14, 14), ("eff_meas_sram1_ls_5", 13, 13), ("eff_meas_sram1_ls_4", 12, 12), ("eff_meas_sram1_ls_3", 11, 11), ("eff_meas_sram1_ls_2", 10, 10), ("eff_meas_sram1_ls_1", 9, 9), ("eff_meas_sram1_ls_0", 8, 8), ("eff_meas_sram0_ls_7", 7, 7), ("eff_meas_sram0_ls_6", 6, 6), ("eff_meas_sram0_ls_5", 5, 5), ("eff_meas_sram0_ls_4", 4, 4), ("eff_meas_sram0_ls_3", 3, 3), ("eff_meas_sram0_ls_2", 2, 2), ("eff_meas_sram0_ls_1", 1, 1), ("eff_meas_sram0_ls_0", 0, 0)],
    0x2c70: [("eff_meas_sram1_drf_test_resume", 10, 10), ("eff_meas_sram1_drf_bist_mode", 9, 9), ("eff_meas_sram1_bist_mode", 8, 8), ("eff_meas_sram0_drf_test_resume", 2, 2), ("eff_meas_sram0_drf_bist_mode", 1, 1), ("eff_meas_sram0_bist_mode", 0, 0)],
    0x2c78: [("mes_cmp_addr_upper", 0, 0)],
    0x2c7c: [("mes_cmp_addr_mask_upper", 0, 0)],
    0x2f90: [("mc_fifo_err_int_en", 8, 8), ("int_err_active_en", 0, 0)],
}

# 是否已載入內建資料
_EMBEDDED_LOADED = False


def get_embedded_reg_map() -> Dict[int, RegisterInfo]:
    """
    取得內建的 Register Map

    Returns:
        Dict[int, RegisterInfo]: offset -> RegisterInfo 的對應表
        如果沒有內建資料，回傳空 dict
    """
    if not EMBEDDED_REGMAP_DATA:
        return {}

    reg_map = {}
    for offset, fields_data in EMBEDDED_REGMAP_DATA.items():
        reg_info = RegisterInfo(offset=offset)
        for name, high_bit, low_bit in fields_data:
            reg_info.fields.append(BitField(name=name, high_bit=high_bit, low_bit=low_bit))
        reg_map[offset] = reg_info

    return reg_map


def has_embedded_regmap() -> bool:
    """檢查是否有內建的 Register Map 資料"""
    return len(EMBEDDED_REGMAP_DATA) > 0
