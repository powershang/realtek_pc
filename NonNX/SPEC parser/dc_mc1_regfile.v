// File         :      dc_mc1_regfile.v
// Spec         :      MatriX_DesignSpec-DC_MC
// Description  :      Standard register file Read/Write Interface
// Date         :      2025-2-27
// SpecParser version: 10.6

//***************************************
//File Settings As Below:
//Length data : 32
//Length address : 12
//RTL_Naming:true
//PortNameLowercase:true
//Port_Naming_Rule : _BitName_
//Read_only(input) : No postfix
//Reg'Q out(output) : No postfix
//Full_Addr_ByteName : true
//Double buffered by F/F:true
//Sync'd and de-glitch hardware clear:false
//Hardware_async:false
//Support Latch scan_sen:false
//Support Latch Scan Clk:false
//Support Latch Scan Mode:false
//gate level mux for scan:false
//All Control Inputs Registered:false
//Rbus clk sample:false
//Read data mux for doubler buffer:false
//read_write_reg_gating_on:false
//RBUS Async I/F:false
//wclr_out without DFF output:false
//read only address comment(in read procedure):true
//write procedure when write_en and hw_clr, take hw_crl priority over write_en: false
//Input Address Filter:true
//	Filter:0 Start Address: 0x180c2020
//	Filter:0 End   Address: 0x180c28fc
//	Filter:1 Start Address: 0x180c2a00
//	Filter:1 End   Address: 0x180c2fff
//***************************************
/////////////////////////////////////////////////////
// Special Design & P&R concern
//
//
//
//



//DEFINEs 



module dc_mc1_regfile(
clk,           // input,  CLK source
rst_n,         // input,  async reset
new_rst_n,         // input,  async new reset
reg_addr,      // input,  address
write_reg,     // input,  write pulse
write_data,    // input,  data to write
read_reg,      // input,  read pulse
read_data,     // output, data requested
mem_num_cfg,			//output,register output
lpddr5_en,			//output,register output
lpddr4_en,			//output,register output
lpddr3_en,			//output,register output
ddr4_en,			//output,register output
ddr3_en,			//output,register output
mcx2_option,			//output,register output
mcx2_mc1_act_cnt,			//output,register output
mcx2_mc2_act_cnt,			//output,register output
mcx2_mc1_act_sel,			//output,register output
qos_cmd_mode,			//output,register output
mcx2_mode,			//output,register output
mcx1_2cke_en,			//output,register output
mcx2_en,			//output,register output
parser_int_en,			//output,register output
geardown_en,			//output,register output
geardown_pre_set_en,			//output,register output
ddr4_x8,			//output,register output
ddr4_x8_bg1_sel,			//output,register output
ddrx_rst,			//output,register output
ddrx_cke,			//output,register output
ref_cmd_rst_delay_num,			//output,register output
ddr_wck_en,			//output,register output
ddr_wck_toggle,			//output,register output
cfmt_security_en,			//output,register output
cs_mrs_out_mode,			//output,register output
ca_toggle_rate,			//output,register output
cs_swap,			//output,register output
lock_cs_1,			//output,register output
lock_cs_0,			//output,register output
pda_mode_dram_sel,			//output,register output
pda_mode_en,			//output,register output
rd_ecc_en,			//output,register output
wr_ecc_en,			//output,register output
rd_dbi_en,			//output,register output
wr_dbi_en,			//output,register output
wr_dbi_dq_byte_1,			//output,register output
wr_dbi_dq_byte_0,			//output,register output
odt_post_num,			//output,register output
odt_lock_high,			//output,register output
odt_en,			//output,register output
udq_msb_sel,			//output,register output
udq_lsb_sel,			//output,register output
ldq_msb_sel,			//output,register output
ldq_lsb_sel,			//output,register output
ch_stop_req,			//output,register output
max_conti_ref_num,			//output,register output
ref_regulate,			//output,register output
per_bank_ref_en,			//output,register output
all_bank_ref_en,			//output,register output
ref_pop_num,			//output,register output
ref_pul_num,			//output,register output
ref_2ref_d,			//output,register output
immd_ref_aft_calib,			//output,register output
ref_idle_mode,			//output,register output
ref_idle_en,			//output,register output
ref_idle_time,			//output,register output
ref_rx_rst_cnt,			//output,register output
ref_tx_rst_cnt,			//output,register output
parser_algo,			//output,register output
bank_full_option,			//output,register output
act_bl_remain_thr,			//output,register output
act_bl_calc,			//output,register output
mask_tmccd,			//output,register output
mask_tmccd_en,			//output,register output
dis_ap,			//output,register output
dis_preacc,			//output,register output
dis_acc,			//output,register output
dis_acc_interlave,			//output,register output
dis_cmd_grp_in_order,			//output,register output
en_cmd_bg_in_order,			//output,register output
hppr_mode,			//output,register output
sppr_mode,			//output,register output
ddr4_cmd_bg_in_order,			//output,register output
lpddr4_wmask_in_order,			//output,register output
bank_free_tmrp_rd,			//output,register output
bank_free_tmrp_wr,			//output,register output
bank_free_bl_adj,			//output,register output
bank_free_offset_updn,			//output,register output
bank_free_offset,			//output,register output
bank_free_tmrprcd_rd,			//output,register output
bank_free_tmrprcd_wr,			//output,register output
bg_balance_1,			//output,register output
bg_balance_0,			//output,register output
bg_balance_en,			//output,register output
no_scramble,			//output,register output
global_scramble_en,			//output,register output
emi_scramble_en,			//output,register output
cmd_start,			//output,register output
cmd_execute_posi,			//output,register output
cmd_num,			//output,register output
cmd_ctl_cmd_1,			//output,register output
cmd_ctl_cmd_2,			//output,register output
cmd_ctl_cmd_3,			//output,register output
cmd_ctl_cmd_4,			//output,register output
cmd_ctl_cmd_5,			//output,register output
cmd_ctl_t1,			//output,register output
cmd_ctl_t0,			//output,register output
cmd_ctl_t3,			//output,register output
cmd_ctl_t2,			//output,register output
cmd_ctl_t5,			//output,register output
cmd_ctl_t4,			//output,register output
tmras,			//output,register output
tmrcl,			//output,register output
tmcl,			//output,register output
tmrrd,			//output,register output
tmrp,			//output,register output
tmrcdrd,			//output,register output
tmrc,			//output,register output
tmccd,			//output,register output
tmrtp,			//output,register output
tmwtr,			//output,register output
tmwr,			//output,register output
tmfaw,			//output,register output
tmrp_a_sel,			//output,register output
tmrc_sel,			//output,register output
tmwrp_a,			//output,register output
tmrrp_a,			//output,register output
tmdqsck,			//output,register output
tmrp_ab,			//output,register output
tmwtr_l,			//output,register output
tmrrd_l,			//output,register output
tmccd_l,			//output,register output
tmodt_on,			//output,register output
tmodtl_on,			//output,register output
tmrpst,			//output,register output
tmccdmw,			//output,register output
tmaad,			//output,register output
tmccdmw_dbk_in_sbg,			//output,register output
tmccdmw_dbk_in_dbg,			//output,register output
tmccdmw_sbk_in_sbg,			//output,register output
tmrtw_dbg,			//output,register output
tmrtw_sbg,			//output,register output
tmrank0_w2r,			//output,register output
tmrank0_w2w,			//output,register output
tmrank0_r2w,			//output,register output
tmrank0_r2r,			//output,register output
reg_rk_wait_exit_bl_cnt,			//output,register output
reg_rk_wait_extend_self_bl_cnt,			//output,register output
pbkref_postpone,			//output,register output
dynamic_rank_acc,			//output,register output
tm_rank0_acc_time,			//output,register output
tmrank1_w2r,			//output,register output
tmrank1_w2w,			//output,register output
tmrank1_r2w,			//output,register output
tmrank1_r2r,			//output,register output
reg_rk_wait_extend_other_bl_cnt,			//output,register output
pbk_exec_period_en,			//output,register output
pbk_wait_bank_empty_en,			//output,register output
pbk_ref_lock_bk_ignore,			//output,register output
tm_rank1_acc_time,			//output,register output
lp5_tm_rank_arb_en,			//output,register output
lp4_tm_rank_arb_en,			//output,register output
tm_wckpre_toggle_fs_pre,			//output,register output
tm_wckenlfs,			//output,register output
tm_wckpre_static,			//output,register output
tm_wckpre_toggle_fs,			//output,register output
t_refi,			//output,register output
t_refc,			//output,register output
t_refi_max,			//output,register output
t_no_ref_max,			//output,register output
tmpbr2act,			//output,register output
tmrefi_pb,			//output,register output
tmrfc_pb,			//output,register output
tmrefi_pb_timeout,			//output,register output
tmpbr2pbr,			//output,register output
t_odt_dfi,			//output,register output
t_ca_dfi,			//output,register output
t_write_dfi_en,			//output,register output
t_read_dfi_en,			//output,register output
t_gck_enable,			//output,register output
t_gck_write_dfi_en,			//output,register output
t_gck_read_dfi_en,			//output,register output
qos_dbg_sel,			//output,register output
qos_dummy,			//output,register output
modr_dbg_en,			//output,register output
modr_dbg_sel,			//output,register output
mc_force_int,			//output,register output
mc_force_int_en,			//output,register output
parser_rbus_dbg_bg1_sel,			//output,register output
parser_rbus_dbg_bg0_sel,			//output,register output
parser_rbus_dbg_sel,			//output,register output
phy_dbg_sel,			//output,register output
fake_rd_id,			//output,register output
fake_rd_id_en,			//output,register output
dummy_wdg_rst_fw0,			//output,register output
dummy_wdg_rst_fw1,			//output,register output
dummy_wdg_rst_fw2,			//output,register output
dummy_wdg_rst_fw3,			//output,register output
dummy_fw0,			//output,register output
dummy_fw1,			//output,register output
dummy_fw2,			//output,register output
dummy_fw3,			//output,register output
dummy_fw4,			//output,register output
dummy_fw5,			//output,register output
dummy_fw6,			//output,register output
dummy_fw7,			//output,register output
dummy_fw8,			//output,register output
dummy_fw9,			//output,register output
dummy_fw10,			//output,register output
dummy_fw11,			//output,register output
dummy_fw12,			//output,register output
dummy_fw13,			//output,register output
dummy_fw14,			//output,register output
dummy_fw15,			//output,register output
limit_ostd_cmd_max_lv2_0,			//output,register output
limit_cmd_extend_num_lv2_0,			//output,register output
limit_ostd_cmd_max_0,			//output,register output
limit_cmd_extend_num_0,			//output,register output
limit_ref_list_0,			//output,register output
limit_en_0,			//output,register output
limit_ostd_cmd_max_lv2_1,			//output,register output
limit_cmd_extend_num_lv2_1,			//output,register output
limit_ostd_cmd_max_1,			//output,register output
limit_cmd_extend_num_1,			//output,register output
limit_ref_list_1,			//output,register output
limit_en_1,			//output,register output
limit_ostd_cmd_max_lv2_2,			//output,register output
limit_cmd_extend_num_lv2_2,			//output,register output
limit_ostd_cmd_max_2,			//output,register output
limit_cmd_extend_num_2,			//output,register output
limit_ref_list_2,			//output,register output
limit_en_2,			//output,register output
limit_ostd_cmd_max_lv2_3,			//output,register output
limit_cmd_extend_num_lv2_3,			//output,register output
limit_ostd_cmd_max_3,			//output,register output
limit_cmd_extend_num_3,			//output,register output
limit_ref_list_3,			//output,register output
limit_en_3,			//output,register output
limit_ostd_cmd_max_lv2_4,			//output,register output
limit_cmd_extend_num_lv2_4,			//output,register output
limit_ostd_cmd_max_4,			//output,register output
limit_cmd_extend_num_4,			//output,register output
limit_ref_list_4,			//output,register output
limit_en_4,			//output,register output
limit_ostd_cmd_max_lv2_5,			//output,register output
limit_cmd_extend_num_lv2_5,			//output,register output
limit_ostd_cmd_max_5,			//output,register output
limit_cmd_extend_num_5,			//output,register output
limit_ref_list_5,			//output,register output
limit_en_5,			//output,register output
limit_ostd_cmd_max_lv2_6,			//output,register output
limit_cmd_extend_num_lv2_6,			//output,register output
limit_ostd_cmd_max_6,			//output,register output
limit_cmd_extend_num_6,			//output,register output
limit_ref_list_6,			//output,register output
limit_en_6,			//output,register output
limit_ostd_cmd_max_lv2_7,			//output,register output
limit_cmd_extend_num_lv2_7,			//output,register output
limit_ostd_cmd_max_7,			//output,register output
limit_cmd_extend_num_7,			//output,register output
limit_ref_list_7,			//output,register output
limit_en_7,			//output,register output
limit_ostd_cmd_max_lv2_8,			//output,register output
limit_cmd_extend_num_lv2_8,			//output,register output
limit_ostd_cmd_max_8,			//output,register output
limit_cmd_extend_num_8,			//output,register output
limit_ref_list_8,			//output,register output
limit_en_8,			//output,register output
limit_ostd_cmd_max_lv2_9,			//output,register output
limit_cmd_extend_num_lv2_9,			//output,register output
limit_ostd_cmd_max_9,			//output,register output
limit_cmd_extend_num_9,			//output,register output
limit_ref_list_9,			//output,register output
limit_en_9,			//output,register output
limit_ostd_cmd_max_lv2_10,			//output,register output
limit_cmd_extend_num_lv2_10,			//output,register output
limit_ostd_cmd_max_10,			//output,register output
limit_cmd_extend_num_10,			//output,register output
limit_ref_list_10,			//output,register output
limit_en_10,			//output,register output
limit_data_num_lv2_0,			//output,register output
limit_data_num_0,			//output,register output
limit_data_num_lv2_1,			//output,register output
limit_data_num_1,			//output,register output
limit_data_num_lv2_2,			//output,register output
limit_data_num_2,			//output,register output
limit_data_num_lv2_3,			//output,register output
limit_data_num_3,			//output,register output
limit_data_num_lv2_4,			//output,register output
limit_data_num_4,			//output,register output
limit_data_num_lv2_5,			//output,register output
limit_data_num_5,			//output,register output
limit_data_num_lv2_6,			//output,register output
limit_data_num_6,			//output,register output
limit_data_num_lv2_7,			//output,register output
limit_data_num_7,			//output,register output
limit_data_num_lv2_8,			//output,register output
limit_data_num_8,			//output,register output
limit_data_num_lv2_9,			//output,register output
limit_data_num_9,			//output,register output
limit_data_num_lv2_10,			//output,register output
limit_data_num_10,			//output,register output
limit_timer_cycle_0,			//output,register output
limit_timer_cycle_1,			//output,register output
limit_timer_cycle_2,			//output,register output
limit_timer_cycle_3,			//output,register output
limit_timer_cycle_4,			//output,register output
limit_timer_cycle_5,			//output,register output
limit_timer_cycle_6,			//output,register output
limit_timer_cycle_7,			//output,register output
limit_timer_cycle_8,			//output,register output
limit_timer_cycle_9,			//output,register output
limit_timer_cycle_10,			//output,register output
hi_priority_id6_en,			//output,register output
hi_priority_id3_en,			//output,register output
hi_priority_id2_en,			//output,register output
hi_priority_id1_en,			//output,register output
hi_priority_id0_en,			//output,register output
dis_tracking_gp1_id_en,			//output,register output
dis_tracking_gp0_id_en,			//output,register output
dis_tracking_id0_en,			//output,register output
dis_tracking_id1_en,			//output,register output
ch_ref_bl_gt_sel,			//output,register output
ch_un_match_id_pg_wt,			//output,register output
ch_tag_tracking,			//output,register output
ch_dir_cont_chg_sel,			//output,register output
ch_parser_cmd_limt_sel,			//output,register output
ch_dir_short_dly_en,			//output,register output
ch_dir_cont_bl_mode,			//output,register output
tracking_sel,			//output,register output
bank_wr_sel,			//output,register output
channel_id_weight_en,			//output,register output
channel_rw_weight_en,			//output,register output
wms_bk_we_map,			//output,register output
wms_bf_bl_sel,			//output,register output
hi_priority_id3,			//output,register output
hi_priority_id2,			//output,register output
hi_priority_id1,			//output,register output
hi_priority_id0,			//output,register output
hi_priority_mask_id6,			//output,register output
hi_priority_id6,			//output,register output
ch_dir_max_bl,			//output,register output
reg_ch_rw_match_mask_cycel_sel,			//output,register output
reg_ch_wr_chg_wait_time,			//output,register output
reg_wr_chg_revert_en,			//output,register output
total_rw_bl_low_bound_2,			//output,register output
total_rw_bl_low_bound_w,			//output,register output
total_rw_bl_low_bound_r,			//output,register output
long_bl_thr,			//output,register output
short_rw_ps_bl_thr,			//output,register output
short_rw_bl_thr,			//output,register output
ref_mask_dir,			//output,register output
ddr4_cmd_inorder_en,			//output,register output
ref_mask_ch,			//output,register output
ref_mask_urg2_ch,			//output,register output
ref_mask_id3_en,			//output,register output
ref_mask_id2_en,			//output,register output
ref_mask_id1_en,			//output,register output
ref_mask_id0_en,			//output,register output
ch_ahead_en,			//output,register output
ch_parser_total_bl_max,			//output,register output
ch_ddr4_balance_cmd_max,			//output,register output
ch_parser_cmd_max,			//output,register output
ddr4_balance_bl_thr,			//output,register output
ddr4_db_tracking,			//output,register output
ddr4_fast_con,			//output,register output
ddr4_balance_con,			//output,register output
ch_max_id_bl_thr,			//output,register output
ch_max_id_bl_en,			//output,register output
dis_tracking_gp0_id,			//output,register output
dis_tracking_gp1_id,			//output,register output
dis_tracking_id1,			//output,register output
dis_tracking_id0,			//output,register output
ch0_bg_insert_mapping,			//output,register output
ch0_page_insert_mapping,			//output,register output
ch0_bank_free_mapping,			//output,register output
ch0_dir_insert_mapping,			//output,register output
ch0_r2w_dir_insert_mapping,			//output,register output
ch0_acc_trigger_sel,			//output,register output
ch0_acc_mode,			//output,register output
ch0_acc_clr_mode,			//output,register output
ch0_urg2_wr_brk_en,			//output,register output
ch0_urg2_strong_en,			//output,register output
ch0_oldest_timer_2_en,			//output,register output
ch0_oldest_timer_en,			//output,register output
ch0_oldest_cmd_select_en,			//output,register output
ch0_quota_bw_ini,			//output,register output
ch0_bw_quota_max,			//output,register output
ch0_oldest_time_2,			//output,register output
ch0_oldest_time,			//output,register output
ch0_bw_acc_unit,			//output,register output
ch0_cmd_extend_num,			//output,register output
ch0_extend_bl_max,			//output,register output
ch0_ostd_bl_max,			//output,register output
ch0_ostd_cmd_max,			//output,register output
ch0_outstand_en,			//output,register output
ch0_wr_brk_time,			//output,register output
ch0_wms_bg_insert_mapping,			//output,register output
ch0_wms_page_insert_mapping,			//output,register output
ch0_wms_bank_free_mapping,			//output,register output
ch0_wms_dir_insert_mapping,			//output,register output
ch0_wms_r2w_dir_insert_mapping,			//output,register output
ch0_wmask_insert_mapping,			//output,register output
ch1_bg_insert_mapping,			//output,register output
ch1_page_insert_mapping,			//output,register output
ch1_bank_free_mapping,			//output,register output
ch1_dir_insert_mapping,			//output,register output
ch1_r2w_dir_insert_mapping,			//output,register output
ch1_acc_trigger_sel,			//output,register output
ch1_acc_mode,			//output,register output
ch1_acc_clr_mode,			//output,register output
ch1_urg2_wr_brk_en,			//output,register output
ch1_urg2_strong_en,			//output,register output
ch1_oldest_timer_2_en,			//output,register output
ch1_oldest_timer_en,			//output,register output
ch1_oldest_cmd_select_en,			//output,register output
ch1_quota_bw_ini,			//output,register output
ch1_bw_quota_max,			//output,register output
ch1_oldest_time_2,			//output,register output
ch1_oldest_time,			//output,register output
ch1_bw_acc_unit,			//output,register output
ch1_cmd_extend_num,			//output,register output
ch1_extend_bl_max,			//output,register output
ch1_ostd_bl_max,			//output,register output
ch1_ostd_cmd_max,			//output,register output
ch1_outstand_en,			//output,register output
ch1_wr_brk_time,			//output,register output
ch1_wms_bg_insert_mapping,			//output,register output
ch1_wms_page_insert_mapping,			//output,register output
ch1_wms_bank_free_mapping,			//output,register output
ch1_wms_dir_insert_mapping,			//output,register output
ch1_wms_r2w_dir_insert_mapping,			//output,register output
ch1_wmask_insert_mapping,			//output,register output
ch2_bg_insert_mapping,			//output,register output
ch2_page_insert_mapping,			//output,register output
ch2_bank_free_mapping,			//output,register output
ch2_dir_insert_mapping,			//output,register output
ch2_r2w_dir_insert_mapping,			//output,register output
ch2_acc_trigger_sel,			//output,register output
ch2_acc_mode,			//output,register output
ch2_acc_clr_mode,			//output,register output
ch2_urg2_wr_brk_en,			//output,register output
ch2_urg2_strong_en,			//output,register output
ch2_oldest_timer_2_en,			//output,register output
ch2_oldest_timer_en,			//output,register output
ch2_oldest_cmd_select_en,			//output,register output
ch2_quota_bw_ini,			//output,register output
ch2_bw_quota_max,			//output,register output
ch2_oldest_time_2,			//output,register output
ch2_oldest_time,			//output,register output
ch2_bw_acc_unit,			//output,register output
ch2_cmd_extend_num,			//output,register output
ch2_extend_bl_max,			//output,register output
ch2_ostd_bl_max,			//output,register output
ch2_ostd_cmd_max,			//output,register output
ch2_outstand_en,			//output,register output
ch2_wr_brk_time,			//output,register output
ch2_wms_bg_insert_mapping,			//output,register output
ch2_wms_page_insert_mapping,			//output,register output
ch2_wms_bank_free_mapping,			//output,register output
ch2_wms_dir_insert_mapping,			//output,register output
ch2_wms_r2w_dir_insert_mapping,			//output,register output
ch2_wmask_insert_mapping,			//output,register output
ch3_bg_insert_mapping,			//output,register output
ch3_page_insert_mapping,			//output,register output
ch3_bank_free_mapping,			//output,register output
ch3_dir_insert_mapping,			//output,register output
ch3_r2w_dir_insert_mapping,			//output,register output
ch3_acc_trigger_sel,			//output,register output
ch3_acc_mode,			//output,register output
ch3_acc_clr_mode,			//output,register output
ch3_urg2_wr_brk_en,			//output,register output
ch3_urg2_strong_en,			//output,register output
ch3_oldest_timer_2_en,			//output,register output
ch3_oldest_timer_en,			//output,register output
ch3_oldest_cmd_select_en,			//output,register output
ch3_quota_bw_ini,			//output,register output
ch3_bw_quota_max,			//output,register output
ch3_oldest_time_2,			//output,register output
ch3_oldest_time,			//output,register output
ch3_bw_acc_unit,			//output,register output
ch3_cmd_extend_num,			//output,register output
ch3_extend_bl_max,			//output,register output
ch3_ostd_bl_max,			//output,register output
ch3_ostd_cmd_max,			//output,register output
ch3_outstand_en,			//output,register output
ch3_wr_brk_time,			//output,register output
ch3_wms_bg_insert_mapping,			//output,register output
ch3_wms_page_insert_mapping,			//output,register output
ch3_wms_bank_free_mapping,			//output,register output
ch3_wms_dir_insert_mapping,			//output,register output
ch3_wms_r2w_dir_insert_mapping,			//output,register output
ch3_wmask_insert_mapping,			//output,register output
ch4_bg_insert_mapping,			//output,register output
ch4_page_insert_mapping,			//output,register output
ch4_bank_free_mapping,			//output,register output
ch4_dir_insert_mapping,			//output,register output
ch4_r2w_dir_insert_mapping,			//output,register output
ch4_acc_trigger_sel,			//output,register output
ch4_acc_mode,			//output,register output
ch4_acc_clr_mode,			//output,register output
ch4_urg2_wr_brk_en,			//output,register output
ch4_urg2_strong_en,			//output,register output
ch4_oldest_timer_2_en,			//output,register output
ch4_oldest_timer_en,			//output,register output
ch4_oldest_cmd_select_en,			//output,register output
ch4_quota_bw_ini,			//output,register output
ch4_bw_quota_max,			//output,register output
ch4_oldest_time_2,			//output,register output
ch4_oldest_time,			//output,register output
ch4_bw_acc_unit,			//output,register output
ch4_cmd_extend_num,			//output,register output
ch4_extend_bl_max,			//output,register output
ch4_ostd_bl_max,			//output,register output
ch4_ostd_cmd_max,			//output,register output
ch4_outstand_en,			//output,register output
ch4_wr_brk_time,			//output,register output
ch4_wms_bg_insert_mapping,			//output,register output
ch4_wms_page_insert_mapping,			//output,register output
ch4_wms_bank_free_mapping,			//output,register output
ch4_wms_dir_insert_mapping,			//output,register output
ch4_wms_r2w_dir_insert_mapping,			//output,register output
ch4_wmask_insert_mapping,			//output,register output
ch5_bg_insert_mapping,			//output,register output
ch5_page_insert_mapping,			//output,register output
ch5_bank_free_mapping,			//output,register output
ch5_dir_insert_mapping,			//output,register output
ch5_r2w_dir_insert_mapping,			//output,register output
ch5_acc_trigger_sel,			//output,register output
ch5_acc_mode,			//output,register output
ch5_acc_clr_mode,			//output,register output
ch5_urg2_wr_brk_en,			//output,register output
ch5_urg2_strong_en,			//output,register output
ch5_oldest_timer_2_en,			//output,register output
ch5_oldest_timer_en,			//output,register output
ch5_oldest_cmd_select_en,			//output,register output
ch5_quota_bw_ini,			//output,register output
ch5_bw_quota_max,			//output,register output
ch5_oldest_time_2,			//output,register output
ch5_oldest_time,			//output,register output
ch5_bw_acc_unit,			//output,register output
ch5_cmd_extend_num,			//output,register output
ch5_extend_bl_max,			//output,register output
ch5_ostd_bl_max,			//output,register output
ch5_ostd_cmd_max,			//output,register output
ch5_outstand_en,			//output,register output
ch5_wr_brk_time,			//output,register output
ch5_wms_bg_insert_mapping,			//output,register output
ch5_wms_page_insert_mapping,			//output,register output
ch5_wms_bank_free_mapping,			//output,register output
ch5_wms_dir_insert_mapping,			//output,register output
ch5_wms_r2w_dir_insert_mapping,			//output,register output
ch5_wmask_insert_mapping,			//output,register output
ch6_bg_insert_mapping,			//output,register output
ch6_page_insert_mapping,			//output,register output
ch6_bank_free_mapping,			//output,register output
ch6_dir_insert_mapping,			//output,register output
ch6_r2w_dir_insert_mapping,			//output,register output
ch6_acc_trigger_sel,			//output,register output
ch6_acc_mode,			//output,register output
ch6_acc_clr_mode,			//output,register output
ch6_urg2_wr_brk_en,			//output,register output
ch6_urg2_strong_en,			//output,register output
ch6_oldest_timer_2_en,			//output,register output
ch6_oldest_timer_en,			//output,register output
ch6_oldest_cmd_select_en,			//output,register output
ch6_quota_bw_ini,			//output,register output
ch6_bw_quota_max,			//output,register output
ch6_oldest_time_2,			//output,register output
ch6_oldest_time,			//output,register output
ch6_bw_acc_unit,			//output,register output
ch6_cmd_extend_num,			//output,register output
ch6_extend_bl_max,			//output,register output
ch6_ostd_bl_max,			//output,register output
ch6_ostd_cmd_max,			//output,register output
ch6_outstand_en,			//output,register output
ch6_wr_brk_time,			//output,register output
ch6_wms_bg_insert_mapping,			//output,register output
ch6_wms_page_insert_mapping,			//output,register output
ch6_wms_bank_free_mapping,			//output,register output
ch6_wms_dir_insert_mapping,			//output,register output
ch6_wms_r2w_dir_insert_mapping,			//output,register output
ch6_wmask_insert_mapping,			//output,register output
ch7_bg_insert_mapping,			//output,register output
ch7_page_insert_mapping,			//output,register output
ch7_bank_free_mapping,			//output,register output
ch7_dir_insert_mapping,			//output,register output
ch7_r2w_dir_insert_mapping,			//output,register output
ch7_acc_trigger_sel,			//output,register output
ch7_acc_mode,			//output,register output
ch7_acc_clr_mode,			//output,register output
ch7_urg2_wr_brk_en,			//output,register output
ch7_urg2_strong_en,			//output,register output
ch7_oldest_timer_2_en,			//output,register output
ch7_oldest_timer_en,			//output,register output
ch7_oldest_cmd_select_en,			//output,register output
ch7_quota_bw_ini,			//output,register output
ch7_bw_quota_max,			//output,register output
ch7_oldest_time_2,			//output,register output
ch7_oldest_time,			//output,register output
ch7_bw_acc_unit,			//output,register output
ch7_cmd_extend_num,			//output,register output
ch7_extend_bl_max,			//output,register output
ch7_ostd_bl_max,			//output,register output
ch7_ostd_cmd_max,			//output,register output
ch7_outstand_en,			//output,register output
ch7_wr_brk_time,			//output,register output
ch7_wms_bg_insert_mapping,			//output,register output
ch7_wms_page_insert_mapping,			//output,register output
ch7_wms_bank_free_mapping,			//output,register output
ch7_wms_dir_insert_mapping,			//output,register output
ch7_wms_r2w_dir_insert_mapping,			//output,register output
ch7_wmask_insert_mapping,			//output,register output
ch8_bg_insert_mapping,			//output,register output
ch8_page_insert_mapping,			//output,register output
ch8_bank_free_mapping,			//output,register output
ch8_dir_insert_mapping,			//output,register output
ch8_r2w_dir_insert_mapping,			//output,register output
ch8_acc_trigger_sel,			//output,register output
ch8_acc_mode,			//output,register output
ch8_acc_clr_mode,			//output,register output
ch8_urg2_wr_brk_en,			//output,register output
ch8_urg2_strong_en,			//output,register output
ch8_oldest_timer_2_en,			//output,register output
ch8_oldest_timer_en,			//output,register output
ch8_oldest_cmd_select_en,			//output,register output
ch8_quota_bw_ini,			//output,register output
ch8_bw_quota_max,			//output,register output
ch8_oldest_time_2,			//output,register output
ch8_oldest_time,			//output,register output
ch8_bw_acc_unit,			//output,register output
ch8_cmd_extend_num,			//output,register output
ch8_extend_bl_max,			//output,register output
ch8_ostd_bl_max,			//output,register output
ch8_ostd_cmd_max,			//output,register output
ch8_outstand_en,			//output,register output
ch8_wr_brk_time,			//output,register output
ch8_wms_bg_insert_mapping,			//output,register output
ch8_wms_page_insert_mapping,			//output,register output
ch8_wms_bank_free_mapping,			//output,register output
ch8_wms_dir_insert_mapping,			//output,register output
ch8_wms_r2w_dir_insert_mapping,			//output,register output
ch8_wmask_insert_mapping,			//output,register output
ch9_bg_insert_mapping,			//output,register output
ch9_page_insert_mapping,			//output,register output
ch9_bank_free_mapping,			//output,register output
ch9_dir_insert_mapping,			//output,register output
ch9_r2w_dir_insert_mapping,			//output,register output
ch9_acc_trigger_sel,			//output,register output
ch9_acc_mode,			//output,register output
ch9_acc_clr_mode,			//output,register output
ch9_urg2_wr_brk_en,			//output,register output
ch9_urg2_strong_en,			//output,register output
ch9_oldest_timer_2_en,			//output,register output
ch9_oldest_timer_en,			//output,register output
ch9_oldest_cmd_select_en,			//output,register output
ch9_quota_bw_ini,			//output,register output
ch9_bw_quota_max,			//output,register output
ch9_oldest_time_2,			//output,register output
ch9_oldest_time,			//output,register output
ch9_bw_acc_unit,			//output,register output
ch9_cmd_extend_num,			//output,register output
ch9_extend_bl_max,			//output,register output
ch9_ostd_bl_max,			//output,register output
ch9_ostd_cmd_max,			//output,register output
ch9_outstand_en,			//output,register output
ch9_wr_brk_time,			//output,register output
ch9_wms_bg_insert_mapping,			//output,register output
ch9_wms_page_insert_mapping,			//output,register output
ch9_wms_bank_free_mapping,			//output,register output
ch9_wms_dir_insert_mapping,			//output,register output
ch9_wms_r2w_dir_insert_mapping,			//output,register output
ch9_wmask_insert_mapping,			//output,register output
ch10_bg_insert_mapping,			//output,register output
ch10_page_insert_mapping,			//output,register output
ch10_bank_free_mapping,			//output,register output
ch10_dir_insert_mapping,			//output,register output
ch10_r2w_dir_insert_mapping,			//output,register output
ch10_acc_trigger_sel,			//output,register output
ch10_acc_mode,			//output,register output
ch10_acc_clr_mode,			//output,register output
ch10_urg2_wr_brk_en,			//output,register output
ch10_urg2_strong_en,			//output,register output
ch10_oldest_timer_2_en,			//output,register output
ch10_oldest_timer_en,			//output,register output
ch10_oldest_cmd_select_en,			//output,register output
ch10_quota_bw_ini,			//output,register output
ch10_bw_quota_max,			//output,register output
ch10_oldest_time_2,			//output,register output
ch10_oldest_time,			//output,register output
ch10_bw_acc_unit,			//output,register output
ch10_cmd_extend_num,			//output,register output
ch10_extend_bl_max,			//output,register output
ch10_ostd_bl_max,			//output,register output
ch10_ostd_cmd_max,			//output,register output
ch10_outstand_en,			//output,register output
ch10_wr_brk_time,			//output,register output
ch10_wms_bg_insert_mapping,			//output,register output
ch10_wms_page_insert_mapping,			//output,register output
ch10_wms_bank_free_mapping,			//output,register output
ch10_wms_dir_insert_mapping,			//output,register output
ch10_wms_r2w_dir_insert_mapping,			//output,register output
ch10_wmask_insert_mapping,			//output,register output
meas_sram_last_w_num,			//output,register output
meas_rk_ctrl_mc2,			//output,register output
meas_rk_ctrl_mc1,			//output,register output
meas_sram_w_addr_rst,			//output,register output
meas_sram_one_time,			//output,register output
meas_sram_mode_ctrl,			//output,register output
meas_sram_r_add_inc,			//output,register output
meas_sram_r_addr_sync,			//output,register output
meas_sram_r_addr,			//output,register output
meas_one_shot_mode_en,			//output,register output
meas_cnt_mode_max_en,			//output,register output
meas_cnt_mode_avg_en,			//output,register output
meas_cnt_record_mode,			//output,register output
meas_timer1_sync,			//output,register output
meas_trig_sel,			//output,register output
meas_serial_cont,			//output,register output
meas_mode,			//output,register output
meas_start,			//output,register output
meas_timer1,			//output,register output
meas_cnt1_mask_en,			//output,register output
meas_cnt1_id,			//output,register output
meas_cnt1_mask_id,			//output,register output
meas_cnt1_id_en,			//output,register output
meas_cnt1_ddr_num,			//output,register output
meas_cnt2_mask_en,			//output,register output
meas_cnt2_id,			//output,register output
meas_cnt2_mask_id,			//output,register output
meas_cnt2_id_en,			//output,register output
meas_cnt2_ddr_num,			//output,register output
meas_cnt2_mode,			//output,register output
meas_cnt3_mask_en,			//output,register output
meas_cnt3_id,			//output,register output
meas_cnt3_mask_id,			//output,register output
meas_cnt3_id_en,			//output,register output
meas_cnt3_ddr_num,			//output,register output
meas_cnt3_mode,			//output,register output
meas_cnt4_mask_en,			//output,register output
meas_cnt4_id,			//output,register output
meas_cnt4_mask_id,			//output,register output
meas_cnt4_id_en,			//output,register output
meas_cnt4_ddr_num,			//output,register output
meas_cnt4_mode,			//output,register output
meas_en,			//output,register output
meas_stop,			//output,register output
meas_sram_clear_en,			//output,register output
meas_page_addr_thr_en,			//output,register output
meas_dram_num_sel,			//output,register output
meas_timer_en,			//output,register output
meas_counting_mode,			//output,register output
addr_thr_cnt_mode_en,			//output,register output
meas_mc_sel,			//output,register output
meas_chop_cnt_en,			//output,register output
meas_wmask_cnt_en,			//output,register output
meas_page_addr_thr2,			//output,register output
meas_page_addr_thr1,			//output,register output
cnt_mode_irq_thershold,			//output,register output
cnt2_irq_en,			//output,register output
cnt1_irq_en,			//output,register output
mes_mem_tra_dc_sel,			//output,register output
mes_mem_cmp_id,			//output,register output
mes_mem_cmp_dir,			//output,register output
mes_mem_tras_adr,			//output,register output
mes_mem_tras_id,			//output,register output
mes_mem_tras_en,			//output,register output
mes_cmp_addr,			//output,register output
mes_cmp_addr_mask,			//output,register output
eff_sram_testrwm_0,			//output,register output
eff_sram_testrwm_1,			//output,register output
eff_bist_mode,			//output,register output
eff_sram_drf_mode,			//output,register output
eff_sram_test1,			//output,register output
eff_sram_drf_resume,			//output,register output
eff_sram_ls,			//output,register output
eff_sram_rme,			//output,register output
eff_sram_rm,			//output,register output
eff_sram_bc1_0,			//output,register output
eff_sram_bc1_1,			//output,register output
eff_sram_bc2_0,			//output,register output
eff_sram_bc2_1,			//output,register output
eff_sram_test_rnm_0,			//output,register output
eff_sram_test_rnm_1,			//output,register output
eff_sram_scan_shift_en,			//output,register output
eff_mem_speed_mode,			//output,register output
eff_meas_sram1_config_from_reg_en,			//output,register output
eff_meas_sram0_config_from_reg_en,			//output,register output
eff_meas_sram1_wtsel,			//output,register output
eff_meas_sram1_rtsel,			//output,register output
eff_meas_sram1_mtsel,			//output,register output
eff_meas_sram0_wtsel,			//output,register output
eff_meas_sram0_rtsel,			//output,register output
eff_meas_sram0_mtsel,			//output,register output
eff_meas_sram1_ls_7,			//output,register output
eff_meas_sram1_ls_6,			//output,register output
eff_meas_sram1_ls_5,			//output,register output
eff_meas_sram1_ls_4,			//output,register output
eff_meas_sram1_ls_3,			//output,register output
eff_meas_sram1_ls_2,			//output,register output
eff_meas_sram1_ls_1,			//output,register output
eff_meas_sram1_ls_0,			//output,register output
eff_meas_sram0_ls_7,			//output,register output
eff_meas_sram0_ls_6,			//output,register output
eff_meas_sram0_ls_5,			//output,register output
eff_meas_sram0_ls_4,			//output,register output
eff_meas_sram0_ls_3,			//output,register output
eff_meas_sram0_ls_2,			//output,register output
eff_meas_sram0_ls_1,			//output,register output
eff_meas_sram0_ls_0,			//output,register output
eff_meas_sram1_drf_test_resume,			//output,register output
eff_meas_sram1_drf_bist_mode,			//output,register output
eff_meas_sram1_bist_mode,			//output,register output
eff_meas_sram0_drf_test_resume,			//output,register output
eff_meas_sram0_drf_bist_mode,			//output,register output
eff_meas_sram0_bist_mode,			//output,register output
mes_cmp_addr_upper,			//output,register output
mes_cmp_addr_mask_upper,			//output,register output
mc_fifo_err_int_en,			//output,register output
int_err_active_en,			//output,register output
dbe_err_flag1_wclr_out,			//output,write clr out
dbe_err_flag0_wclr_out,			//output,write clr out
fmtr_unknown_cmd_wclr_out,			//output,write clr out
rk1_wr_chop_no_mask_wclr_out,			//output,write clr out
rk1_active_ddr_num_mismatch_wclr_out,			//output,write clr out
rk0_wr_chop_no_mask_wclr_out,			//output,write clr out
rk0_active_ddr_num_mismatch_wclr_out,			//output,write clr out
cnt2_irq_status_wclr_out,			//output,write clr out
cnt1_irq_status_wclr_out,			//output,write clr out
rk1_err_pbk_wclr_out,			//output,write clr out
rk0_err_pbk_wclr_out,			//output,write clr out
rk1_err_active_wclr_out,			//output,write clr out
rk0_err_active_wclr_out,			//output,write clr out
///---------input new nor------------//
n_rk0_qos_debug,              //input, nor
n_rk1_qos_debug,              //input, nor
////----------------input new nor end------------------------//
///---------input new nor------------//
update_ddrx_rst,              //input, nor
update_ddrx_cke,              //input, nor
update_ref_idle_en,              //input, nor
update_cmd_start,              //input, nor
update_meas_sram_w_addr_rst,              //input, nor
update_meas_sram_r_addr_sync,              //input, nor
update_meas_start,              //input, nor
update_meas_sram_clear_en,              //input, nor
n_ddrx_rst,              //input, nor
n_ddrx_cke,              //input, nor
n_ref_idle_en,              //input, nor
n_cmd_start,              //input, nor
n_meas_sram_w_addr_rst,              //input, nor
n_meas_sram_r_addr_sync,              //input, nor
n_meas_start,              //input, nor
n_meas_sram_clear_en,              //input, nor
////----------------input new nor end------------------------//
meas_irq,			//input, R-only reg bypassing
ddr_reset_o_status,			//input, R-only reg bypassing
ddr_cke_o_status,			//input, R-only reg bypassing
zq_cal,			//input, R-only reg bypassing
self_refresh,			//input, R-only reg bypassing
power_down,			//input, R-only reg bypassing
modr_lpddr4_fps,			//input, R-only reg bypassing
modr_ca_training,			//input, R-only reg bypassing
modr_geardown_mode,			//input, R-only reg bypassing
modr_mpr_mode,			//input, R-only reg bypassing
modr_wl,			//input, R-only reg bypassing
modr_rl,			//input, R-only reg bypassing
modr_write_level,			//input, R-only reg bypassing
modr_write_preamble,			//input, R-only reg bypassing
modr_read_preamble,			//input, R-only reg bypassing
rk1_parser_rbus_dbg,			//input, R-only reg bypassing
modr_full_data,			//input, R-only reg bypassing
dbe_err_flag1,			//input, R-only reg bypassing
dbe_err_flag0,			//input, R-only reg bypassing
fmtr_unknown_cmd,			//input, R-only reg bypassing
rk0_parser_rbus_dbg,			//input, R-only reg bypassing
rk1_wr_chop_no_mask,			//input, R-only reg bypassing
rk1_active_ddr_num_mismatch,			//input, R-only reg bypassing
rk0_wr_chop_no_mask,			//input, R-only reg bypassing
rk0_active_ddr_num_mismatch,			//input, R-only reg bypassing
mc_write_ctrl_error_status,			//input, R-only reg bypassing
mc_read_ctrl_error_status,			//input, R-only reg bypassing
meas_sram_cur_w_addr,			//input, R-only reg bypassing
meas_serial_cnt,			//input, R-only reg bypassing
meas_timer1_cnt,			//input, R-only reg bypassing
meas_cnt1_r,			//input, R-only reg bypassing
meas_cnt1_w,			//input, R-only reg bypassing
meas_cnt2_r,			//input, R-only reg bypassing
meas_cnt2_w,			//input, R-only reg bypassing
meas_cnt3_r,			//input, R-only reg bypassing
meas_cnt3_w,			//input, R-only reg bypassing
meas_cnt4_r,			//input, R-only reg bypassing
meas_cnt4_w,			//input, R-only reg bypassing
meas_field_status,			//input, R-only reg bypassing
meas_sram_data_valid,			//input, R-only reg bypassing
cnt2_irq_status,			//input, R-only reg bypassing
cnt1_irq_status,			//input, R-only reg bypassing
eff_bist_done,			//input, R-only reg bypassing
eff_bist_fail_0,			//input, R-only reg bypassing
eff_bist_drf_done,			//input, R-only reg bypassing
eff_drf_bist_fail_0,			//input, R-only reg bypassing
eff_bist_drf_pause,			//input, R-only reg bypassing
eff_bist_fail_1,			//input, R-only reg bypassing
eff_bist_fail_all,			//input, R-only reg bypassing
eff_drf_bist_fail_1,			//input, R-only reg bypassing
eff_drf_bist_fail_all,			//input, R-only reg bypassing
eff_meas_sram1_drf_fail_all,			//input, R-only reg bypassing
eff_meas_sram1_fail_all,			//input, R-only reg bypassing
eff_meas_sram1_drf_start_pause,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_done,			//input, R-only reg bypassing
eff_meas_sram1_bist_done,			//input, R-only reg bypassing
eff_meas_sram0_drf_fail_all,			//input, R-only reg bypassing
eff_meas_sram0_fail_all,			//input, R-only reg bypassing
eff_meas_sram0_drf_start_pause,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_done,			//input, R-only reg bypassing
eff_meas_sram0_bist_done,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_7,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_6,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_5,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_4,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_3,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_2,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_1,			//input, R-only reg bypassing
eff_meas_sram1_drf_bist_fail_0,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_7,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_6,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_5,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_4,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_3,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_2,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_1,			//input, R-only reg bypassing
eff_meas_sram0_drf_bist_fail_0,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_7,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_6,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_5,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_4,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_3,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_2,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_1,			//input, R-only reg bypassing
eff_meas_sram1_bist_fail_0,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_7,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_6,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_5,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_4,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_3,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_2,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_1,			//input, R-only reg bypassing
eff_meas_sram0_bist_fail_0,			//input, R-only reg bypassing
rfu_cmd_lock_err,			//input, R-only reg bypassing
precharge_all_err,			//input, R-only reg bypassing
mc_fifo_err_int,			//input, R-only reg bypassing
rk1_err_pbk,			//input, R-only reg bypassing
rk0_err_pbk,			//input, R-only reg bypassing
rk1_err_active,			//input, R-only reg bypassing
rk0_err_active,			//input, R-only reg bypassing
mc_mes_client_1_rprt_en,			//output, Read port enable
meas_sram_data_0,			//input, Read port data to read_data
mc_mes_client_2_rprt_en,			//output, Read port enable
meas_sram_data_1			//input Read port data to read_data
);


// Parameter Declaration
parameter NAME = "DC_MC1";

// Input     Declaration  
input clk;			//Module clock
input rst_n;                            //Async, Active-0, module reset
input new_rst_n;                            //Async, Active-0, module new reset
input [11:0] reg_addr;			//user specified length addr
input read_reg;			//read pulse
input write_reg;			//write pulse
input [31:0] write_data;			//data input
input meas_irq;			//input,R-only reg bypassing
input ddr_reset_o_status;			//input,R-only reg bypassing
input ddr_cke_o_status;			//input,R-only reg bypassing
input zq_cal;			//input,R-only reg bypassing
input self_refresh;			//input,R-only reg bypassing
input power_down;			//input,R-only reg bypassing
input [1:0] modr_lpddr4_fps;			//input,R-only reg bypassing
input [7:0] modr_ca_training;			//input,R-only reg bypassing
input modr_geardown_mode;			//input,R-only reg bypassing
input modr_mpr_mode;			//input,R-only reg bypassing
input [2:0] modr_wl;			//input,R-only reg bypassing
input [4:0] modr_rl;			//input,R-only reg bypassing
input modr_write_level;			//input,R-only reg bypassing
input modr_write_preamble;			//input,R-only reg bypassing
input modr_read_preamble;			//input,R-only reg bypassing
input [31:0] rk1_parser_rbus_dbg;			//input,R-only reg bypassing
input [19:0] modr_full_data;			//input,R-only reg bypassing
input dbe_err_flag1;			//input,R-only reg bypassing
input dbe_err_flag0;			//input,R-only reg bypassing
input fmtr_unknown_cmd;			//input,R-only reg bypassing
input [31:0] rk0_parser_rbus_dbg;			//input,R-only reg bypassing
input rk1_wr_chop_no_mask;			//input,R-only reg bypassing
input rk1_active_ddr_num_mismatch;			//input,R-only reg bypassing
input rk0_wr_chop_no_mask;			//input,R-only reg bypassing
input rk0_active_ddr_num_mismatch;			//input,R-only reg bypassing
input [31:0] mc_write_ctrl_error_status;			//input,R-only reg bypassing
input [31:0] mc_read_ctrl_error_status;			//input,R-only reg bypassing
input [10:0] meas_sram_cur_w_addr;			//input,R-only reg bypassing
input [1:0] meas_serial_cnt;			//input,R-only reg bypassing
input [31:0] meas_timer1_cnt;			//input,R-only reg bypassing
input [31:0] meas_cnt1_r;			//input,R-only reg bypassing
input [31:0] meas_cnt1_w;			//input,R-only reg bypassing
input [31:0] meas_cnt2_r;			//input,R-only reg bypassing
input [31:0] meas_cnt2_w;			//input,R-only reg bypassing
input [31:0] meas_cnt3_r;			//input,R-only reg bypassing
input [31:0] meas_cnt3_w;			//input,R-only reg bypassing
input [31:0] meas_cnt4_r;			//input,R-only reg bypassing
input [31:0] meas_cnt4_w;			//input,R-only reg bypassing
input [7:0] meas_field_status;			//input,R-only reg bypassing
input meas_sram_data_valid;			//input,R-only reg bypassing
input cnt2_irq_status;			//input,R-only reg bypassing
input cnt1_irq_status;			//input,R-only reg bypassing
input eff_bist_done;			//input,R-only reg bypassing
input eff_bist_fail_0;			//input,R-only reg bypassing
input eff_bist_drf_done;			//input,R-only reg bypassing
input eff_drf_bist_fail_0;			//input,R-only reg bypassing
input eff_bist_drf_pause;			//input,R-only reg bypassing
input eff_bist_fail_1;			//input,R-only reg bypassing
input eff_bist_fail_all;			//input,R-only reg bypassing
input eff_drf_bist_fail_1;			//input,R-only reg bypassing
input eff_drf_bist_fail_all;			//input,R-only reg bypassing
input eff_meas_sram1_drf_fail_all;			//input,R-only reg bypassing
input eff_meas_sram1_fail_all;			//input,R-only reg bypassing
input eff_meas_sram1_drf_start_pause;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_done;			//input,R-only reg bypassing
input eff_meas_sram1_bist_done;			//input,R-only reg bypassing
input eff_meas_sram0_drf_fail_all;			//input,R-only reg bypassing
input eff_meas_sram0_fail_all;			//input,R-only reg bypassing
input eff_meas_sram0_drf_start_pause;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_done;			//input,R-only reg bypassing
input eff_meas_sram0_bist_done;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_7;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_6;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_5;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_4;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_3;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_2;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_1;			//input,R-only reg bypassing
input eff_meas_sram1_drf_bist_fail_0;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_7;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_6;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_5;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_4;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_3;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_2;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_1;			//input,R-only reg bypassing
input eff_meas_sram0_drf_bist_fail_0;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_7;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_6;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_5;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_4;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_3;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_2;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_1;			//input,R-only reg bypassing
input eff_meas_sram1_bist_fail_0;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_7;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_6;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_5;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_4;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_3;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_2;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_1;			//input,R-only reg bypassing
input eff_meas_sram0_bist_fail_0;			//input,R-only reg bypassing
input rfu_cmd_lock_err;			//input,R-only reg bypassing
input precharge_all_err;			//input,R-only reg bypassing
input mc_fifo_err_int;			//input,R-only reg bypassing
input rk1_err_pbk;			//input,R-only reg bypassing
input rk0_err_pbk;			//input,R-only reg bypassing
input rk1_err_active;			//input,R-only reg bypassing
input rk0_err_active;			//input,R-only reg bypassing
input [30:0] meas_sram_data_0;			//input, Read port data to read_data
input [31:0] meas_sram_data_1;			//input, Read port data to read_data


////========================== input new nor===============================//
input [31:0] n_rk0_qos_debug;
input [31:0] n_rk1_qos_debug;
////===========================input new nor end ============================//
////========================== input new nor===============================//
input n_ddrx_rst;
input n_ddrx_cke;
input n_ref_idle_en;
input n_cmd_start;
input n_meas_sram_w_addr_rst;
input n_meas_sram_r_addr_sync;
input n_meas_start;
input n_meas_sram_clear_en;
input update_ddrx_rst;
input update_ddrx_cke;
input update_ref_idle_en;
input update_cmd_start;
input update_meas_sram_w_addr_rst;
input update_meas_sram_r_addr_sync;
input update_meas_start;
input update_meas_sram_clear_en;
////===========================input new nor end ============================//
// Output    Decalaraion 
output [31:0] read_data;//data output


output dbe_err_flag1_wclr_out;		//output,write clr out
output dbe_err_flag0_wclr_out;		//output,write clr out
output fmtr_unknown_cmd_wclr_out;		//output,write clr out
output rk1_wr_chop_no_mask_wclr_out;		//output,write clr out
output rk1_active_ddr_num_mismatch_wclr_out;		//output,write clr out
output rk0_wr_chop_no_mask_wclr_out;		//output,write clr out
output rk0_active_ddr_num_mismatch_wclr_out;		//output,write clr out
output cnt2_irq_status_wclr_out;		//output,write clr out
output cnt1_irq_status_wclr_out;		//output,write clr out
output rk1_err_pbk_wclr_out;		//output,write clr out
output rk0_err_pbk_wclr_out;		//output,write clr out
output rk1_err_active_wclr_out;		//output,write clr out
output rk0_err_active_wclr_out;		//output,write clr out
output mem_num_cfg;			//register output
output lpddr5_en;			//register output
output lpddr4_en;			//register output
output lpddr3_en;			//register output
output ddr4_en;			//register output
output ddr3_en;			//register output
output [3:0] mcx2_option;			//register output
output [3:0] mcx2_mc1_act_cnt;			//register output
output [3:0] mcx2_mc2_act_cnt;			//register output
output mcx2_mc1_act_sel;			//register output
output qos_cmd_mode;			//register output
output [1:0] mcx2_mode;			//register output
output mcx1_2cke_en;			//register output
output mcx2_en;			//register output
output parser_int_en;			//register output
output geardown_en;			//register output
output geardown_pre_set_en;			//register output
output ddr4_x8;			//register output
output [1:0] ddr4_x8_bg1_sel;			//register output
output ddrx_rst;			//register output
output ddrx_cke;			//register output
output [3:0] ref_cmd_rst_delay_num;			//register output
output ddr_wck_en;			//register output
output [1:0] ddr_wck_toggle;			//register output
output cfmt_security_en;			//register output
output [1:0] cs_mrs_out_mode;			//register output
output [2:0] ca_toggle_rate;			//register output
output cs_swap;			//register output
output lock_cs_1;			//register output
output lock_cs_0;			//register output
output [3:0] pda_mode_dram_sel;			//register output
output pda_mode_en;			//register output
output rd_ecc_en;			//register output
output wr_ecc_en;			//register output
output rd_dbi_en;			//register output
output wr_dbi_en;			//register output
output [7:0] wr_dbi_dq_byte_1;			//register output
output [7:0] wr_dbi_dq_byte_0;			//register output
output [2:0] odt_post_num;			//register output
output odt_lock_high;			//register output
output odt_en;			//register output
output [1:0] udq_msb_sel;			//register output
output [1:0] udq_lsb_sel;			//register output
output [1:0] ldq_msb_sel;			//register output
output [1:0] ldq_lsb_sel;			//register output
output [10:0] ch_stop_req;			//register output
output [3:0] max_conti_ref_num;			//register output
output ref_regulate;			//register output
output per_bank_ref_en;			//register output
output all_bank_ref_en;			//register output
output [2:0] ref_pop_num;			//register output
output [2:0] ref_pul_num;			//register output
output [7:0] ref_2ref_d;			//register output
output immd_ref_aft_calib;			//register output
output ref_idle_mode;			//register output
output ref_idle_en;			//register output
output [11:0] ref_idle_time;			//register output
output [5:0] ref_rx_rst_cnt;			//register output
output [5:0] ref_tx_rst_cnt;			//register output
output [3:0] parser_algo;			//register output
output bank_full_option;			//register output
output [11:0] act_bl_remain_thr;			//register output
output act_bl_calc;			//register output
output [1:0] mask_tmccd;			//register output
output mask_tmccd_en;			//register output
output dis_ap;			//register output
output dis_preacc;			//register output
output dis_acc;			//register output
output dis_acc_interlave;			//register output
output dis_cmd_grp_in_order;			//register output
output en_cmd_bg_in_order;			//register output
output hppr_mode;			//register output
output sppr_mode;			//register output
output ddr4_cmd_bg_in_order;			//register output
output lpddr4_wmask_in_order;			//register output
output [7:0] bank_free_tmrp_rd;			//register output
output [7:0] bank_free_tmrp_wr;			//register output
output bank_free_bl_adj;			//register output
output bank_free_offset_updn;			//register output
output [5:0] bank_free_offset;			//register output
output [7:0] bank_free_tmrprcd_rd;			//register output
output [7:0] bank_free_tmrprcd_wr;			//register output
output [5:0] bg_balance_1;			//register output
output [5:0] bg_balance_0;			//register output
output bg_balance_en;			//register output
output no_scramble;			//register output
output global_scramble_en;			//register output
output emi_scramble_en;			//register output
output cmd_start;			//register output
output [1:0] cmd_execute_posi;			//register output
output [2:0] cmd_num;			//register output
output [31:0] cmd_ctl_cmd_1;			//register output
output [31:0] cmd_ctl_cmd_2;			//register output
output [31:0] cmd_ctl_cmd_3;			//register output
output [31:0] cmd_ctl_cmd_4;			//register output
output [31:0] cmd_ctl_cmd_5;			//register output
output [15:0] cmd_ctl_t1;			//register output
output [15:0] cmd_ctl_t0;			//register output
output [15:0] cmd_ctl_t3;			//register output
output [15:0] cmd_ctl_t2;			//register output
output [15:0] cmd_ctl_t5;			//register output
output [15:0] cmd_ctl_t4;			//register output
output [7:0] tmras;			//register output
output [5:0] tmrcl;			//register output
output [5:0] tmcl;			//register output
output [4:0] tmrrd;			//register output
output [5:0] tmrp;			//register output
output [5:0] tmrcdrd;			//register output
output [7:0] tmrc;			//register output
output [3:0] tmccd;			//register output
output [6:0] tmrtp;			//register output
output [4:0] tmwtr;			//register output
output [5:0] tmwr;			//register output
output [7:0] tmfaw;			//register output
output tmrp_a_sel;			//register output
output tmrc_sel;			//register output
output [7:0] tmwrp_a;			//register output
output [7:0] tmrrp_a;			//register output
output [3:0] tmdqsck;			//register output
output [5:0] tmrp_ab;			//register output
output [4:0] tmwtr_l;			//register output
output [4:0] tmrrd_l;			//register output
output [3:0] tmccd_l;			//register output
output [3:0] tmodt_on;			//register output
output [4:0] tmodtl_on;			//register output
output [1:0] tmrpst;			//register output
output [5:0] tmccdmw;			//register output
output [3:0] tmaad;			//register output
output [3:0] tmccdmw_dbk_in_sbg;			//register output
output [3:0] tmccdmw_dbk_in_dbg;			//register output
output [4:0] tmccdmw_sbk_in_sbg;			//register output
output [5:0] tmrtw_dbg;			//register output
output [5:0] tmrtw_sbg;			//register output
output [5:0] tmrank0_w2r;			//register output
output [5:0] tmrank0_w2w;			//register output
output [5:0] tmrank0_r2w;			//register output
output [5:0] tmrank0_r2r;			//register output
output [9:0] reg_rk_wait_exit_bl_cnt;			//register output
output [9:0] reg_rk_wait_extend_self_bl_cnt;			//register output
output pbkref_postpone;			//register output
output dynamic_rank_acc;			//register output
output [9:0] tm_rank0_acc_time;			//register output
output [5:0] tmrank1_w2r;			//register output
output [5:0] tmrank1_w2w;			//register output
output [5:0] tmrank1_r2w;			//register output
output [5:0] tmrank1_r2r;			//register output
output [9:0] reg_rk_wait_extend_other_bl_cnt;			//register output
output pbk_exec_period_en;			//register output
output pbk_wait_bank_empty_en;			//register output
output pbk_ref_lock_bk_ignore;			//register output
output [9:0] tm_rank1_acc_time;			//register output
output lp5_tm_rank_arb_en;			//register output
output lp4_tm_rank_arb_en;			//register output
output [4:0] tm_wckpre_toggle_fs_pre;			//register output
output [4:0] tm_wckenlfs;			//register output
output [4:0] tm_wckpre_static;			//register output
output [4:0] tm_wckpre_toggle_fs;			//register output
output [15:0] t_refi;			//register output
output [10:0] t_refc;			//register output
output [15:0] t_refi_max;			//register output
output [15:0] t_no_ref_max;			//register output
output [7:0] tmpbr2act;			//register output
output [10:0] tmrefi_pb;			//register output
output [8:0] tmrfc_pb;			//register output
output [10:0] tmrefi_pb_timeout;			//register output
output [8:0] tmpbr2pbr;			//register output
output [4:0] t_odt_dfi;			//register output
output [4:0] t_ca_dfi;			//register output
output [4:0] t_write_dfi_en;			//register output
output [4:0] t_read_dfi_en;			//register output
output t_gck_enable;			//register output
output [4:0] t_gck_write_dfi_en;			//register output
output [4:0] t_gck_read_dfi_en;			//register output
output [3:0] qos_dbg_sel;			//register output
output [7:0] qos_dummy;			//register output
output modr_dbg_en;			//register output
output [5:0] modr_dbg_sel;			//register output
output [1:0] mc_force_int;			//register output
output [1:0] mc_force_int_en;			//register output
output [2:0] parser_rbus_dbg_bg1_sel;			//register output
output [2:0] parser_rbus_dbg_bg0_sel;			//register output
output [4:0] parser_rbus_dbg_sel;			//register output
output [5:0] phy_dbg_sel;			//register output
output [7:0] fake_rd_id;			//register output
output fake_rd_id_en;			//register output
output [31:0] dummy_wdg_rst_fw0;			//register output
output [31:0] dummy_wdg_rst_fw1;			//register output
output [31:0] dummy_wdg_rst_fw2;			//register output
output [31:0] dummy_wdg_rst_fw3;			//register output
output [31:0] dummy_fw0;			//register output
output [31:0] dummy_fw1;			//register output
output [31:0] dummy_fw2;			//register output
output [31:0] dummy_fw3;			//register output
output [31:0] dummy_fw4;			//register output
output [31:0] dummy_fw5;			//register output
output [31:0] dummy_fw6;			//register output
output [31:0] dummy_fw7;			//register output
output [31:0] dummy_fw8;			//register output
output [31:0] dummy_fw9;			//register output
output [31:0] dummy_fw10;			//register output
output [31:0] dummy_fw11;			//register output
output [31:0] dummy_fw12;			//register output
output [31:0] dummy_fw13;			//register output
output [31:0] dummy_fw14;			//register output
output [31:0] dummy_fw15;			//register output
output [3:0] limit_ostd_cmd_max_lv2_0;			//register output
output [3:0] limit_cmd_extend_num_lv2_0;			//register output
output [3:0] limit_ostd_cmd_max_0;			//register output
output [3:0] limit_cmd_extend_num_0;			//register output
output [13:0] limit_ref_list_0;			//register output
output [1:0] limit_en_0;			//register output
output [3:0] limit_ostd_cmd_max_lv2_1;			//register output
output [3:0] limit_cmd_extend_num_lv2_1;			//register output
output [3:0] limit_ostd_cmd_max_1;			//register output
output [3:0] limit_cmd_extend_num_1;			//register output
output [13:0] limit_ref_list_1;			//register output
output [1:0] limit_en_1;			//register output
output [3:0] limit_ostd_cmd_max_lv2_2;			//register output
output [3:0] limit_cmd_extend_num_lv2_2;			//register output
output [3:0] limit_ostd_cmd_max_2;			//register output
output [3:0] limit_cmd_extend_num_2;			//register output
output [13:0] limit_ref_list_2;			//register output
output [1:0] limit_en_2;			//register output
output [3:0] limit_ostd_cmd_max_lv2_3;			//register output
output [3:0] limit_cmd_extend_num_lv2_3;			//register output
output [3:0] limit_ostd_cmd_max_3;			//register output
output [3:0] limit_cmd_extend_num_3;			//register output
output [13:0] limit_ref_list_3;			//register output
output [1:0] limit_en_3;			//register output
output [3:0] limit_ostd_cmd_max_lv2_4;			//register output
output [3:0] limit_cmd_extend_num_lv2_4;			//register output
output [3:0] limit_ostd_cmd_max_4;			//register output
output [3:0] limit_cmd_extend_num_4;			//register output
output [13:0] limit_ref_list_4;			//register output
output [1:0] limit_en_4;			//register output
output [3:0] limit_ostd_cmd_max_lv2_5;			//register output
output [3:0] limit_cmd_extend_num_lv2_5;			//register output
output [3:0] limit_ostd_cmd_max_5;			//register output
output [3:0] limit_cmd_extend_num_5;			//register output
output [13:0] limit_ref_list_5;			//register output
output [1:0] limit_en_5;			//register output
output [3:0] limit_ostd_cmd_max_lv2_6;			//register output
output [3:0] limit_cmd_extend_num_lv2_6;			//register output
output [3:0] limit_ostd_cmd_max_6;			//register output
output [3:0] limit_cmd_extend_num_6;			//register output
output [13:0] limit_ref_list_6;			//register output
output [1:0] limit_en_6;			//register output
output [3:0] limit_ostd_cmd_max_lv2_7;			//register output
output [3:0] limit_cmd_extend_num_lv2_7;			//register output
output [3:0] limit_ostd_cmd_max_7;			//register output
output [3:0] limit_cmd_extend_num_7;			//register output
output [13:0] limit_ref_list_7;			//register output
output [1:0] limit_en_7;			//register output
output [3:0] limit_ostd_cmd_max_lv2_8;			//register output
output [3:0] limit_cmd_extend_num_lv2_8;			//register output
output [3:0] limit_ostd_cmd_max_8;			//register output
output [3:0] limit_cmd_extend_num_8;			//register output
output [13:0] limit_ref_list_8;			//register output
output [1:0] limit_en_8;			//register output
output [3:0] limit_ostd_cmd_max_lv2_9;			//register output
output [3:0] limit_cmd_extend_num_lv2_9;			//register output
output [3:0] limit_ostd_cmd_max_9;			//register output
output [3:0] limit_cmd_extend_num_9;			//register output
output [13:0] limit_ref_list_9;			//register output
output [1:0] limit_en_9;			//register output
output [3:0] limit_ostd_cmd_max_lv2_10;			//register output
output [3:0] limit_cmd_extend_num_lv2_10;			//register output
output [3:0] limit_ostd_cmd_max_10;			//register output
output [3:0] limit_cmd_extend_num_10;			//register output
output [13:0] limit_ref_list_10;			//register output
output [1:0] limit_en_10;			//register output
output [15:0] limit_data_num_lv2_0;			//register output
output [15:0] limit_data_num_0;			//register output
output [15:0] limit_data_num_lv2_1;			//register output
output [15:0] limit_data_num_1;			//register output
output [15:0] limit_data_num_lv2_2;			//register output
output [15:0] limit_data_num_2;			//register output
output [15:0] limit_data_num_lv2_3;			//register output
output [15:0] limit_data_num_3;			//register output
output [15:0] limit_data_num_lv2_4;			//register output
output [15:0] limit_data_num_4;			//register output
output [15:0] limit_data_num_lv2_5;			//register output
output [15:0] limit_data_num_5;			//register output
output [15:0] limit_data_num_lv2_6;			//register output
output [15:0] limit_data_num_6;			//register output
output [15:0] limit_data_num_lv2_7;			//register output
output [15:0] limit_data_num_7;			//register output
output [15:0] limit_data_num_lv2_8;			//register output
output [15:0] limit_data_num_8;			//register output
output [15:0] limit_data_num_lv2_9;			//register output
output [15:0] limit_data_num_9;			//register output
output [15:0] limit_data_num_lv2_10;			//register output
output [15:0] limit_data_num_10;			//register output
output [15:0] limit_timer_cycle_0;			//register output
output [15:0] limit_timer_cycle_1;			//register output
output [15:0] limit_timer_cycle_2;			//register output
output [15:0] limit_timer_cycle_3;			//register output
output [15:0] limit_timer_cycle_4;			//register output
output [15:0] limit_timer_cycle_5;			//register output
output [15:0] limit_timer_cycle_6;			//register output
output [15:0] limit_timer_cycle_7;			//register output
output [15:0] limit_timer_cycle_8;			//register output
output [15:0] limit_timer_cycle_9;			//register output
output [15:0] limit_timer_cycle_10;			//register output
output hi_priority_id6_en;			//register output
output hi_priority_id3_en;			//register output
output hi_priority_id2_en;			//register output
output hi_priority_id1_en;			//register output
output hi_priority_id0_en;			//register output
output dis_tracking_gp1_id_en;			//register output
output dis_tracking_gp0_id_en;			//register output
output dis_tracking_id0_en;			//register output
output dis_tracking_id1_en;			//register output
output ch_ref_bl_gt_sel;			//register output
output ch_un_match_id_pg_wt;			//register output
output ch_tag_tracking;			//register output
output ch_dir_cont_chg_sel;			//register output
output ch_parser_cmd_limt_sel;			//register output
output ch_dir_short_dly_en;			//register output
output [1:0] ch_dir_cont_bl_mode;			//register output
output tracking_sel;			//register output
output bank_wr_sel;			//register output
output channel_id_weight_en;			//register output
output channel_rw_weight_en;			//register output
output wms_bk_we_map;			//register output
output wms_bf_bl_sel;			//register output
output [7:0] hi_priority_id3;			//register output
output [7:0] hi_priority_id2;			//register output
output [7:0] hi_priority_id1;			//register output
output [7:0] hi_priority_id0;			//register output
output [7:0] hi_priority_mask_id6;			//register output
output [7:0] hi_priority_id6;			//register output
output [11:0] ch_dir_max_bl;			//register output
output [2:0] reg_ch_rw_match_mask_cycel_sel;			//register output
output [4:0] reg_ch_wr_chg_wait_time;			//register output
output reg_wr_chg_revert_en;			//register output
output [12:0] total_rw_bl_low_bound_2;			//register output
output [12:0] total_rw_bl_low_bound_w;			//register output
output [12:0] total_rw_bl_low_bound_r;			//register output
output [5:0] long_bl_thr;			//register output
output [4:0] short_rw_ps_bl_thr;			//register output
output [7:0] short_rw_bl_thr;			//register output
output [1:0] ref_mask_dir;			//register output
output ddr4_cmd_inorder_en;			//register output
output [3:0] ref_mask_ch;			//register output
output [8:0] ref_mask_urg2_ch;			//register output
output ref_mask_id3_en;			//register output
output ref_mask_id2_en;			//register output
output ref_mask_id1_en;			//register output
output ref_mask_id0_en;			//register output
output ch_ahead_en;			//register output
output [9:0] ch_parser_total_bl_max;			//register output
output [3:0] ch_ddr4_balance_cmd_max;			//register output
output [3:0] ch_parser_cmd_max;			//register output
output [5:0] ddr4_balance_bl_thr;			//register output
output ddr4_db_tracking;			//register output
output ddr4_fast_con;			//register output
output ddr4_balance_con;			//register output
output [9:0] ch_max_id_bl_thr;			//register output
output ch_max_id_bl_en;			//register output
output [3:0] dis_tracking_gp0_id;			//register output
output [3:0] dis_tracking_gp1_id;			//register output
output [7:0] dis_tracking_id1;			//register output
output [7:0] dis_tracking_id0;			//register output
output [3:0] ch0_bg_insert_mapping;			//register output
output [3:0] ch0_page_insert_mapping;			//register output
output [3:0] ch0_bank_free_mapping;			//register output
output [3:0] ch0_dir_insert_mapping;			//register output
output [3:0] ch0_r2w_dir_insert_mapping;			//register output
output ch0_acc_trigger_sel;			//register output
output ch0_acc_mode;			//register output
output [1:0] ch0_acc_clr_mode;			//register output
output ch0_urg2_wr_brk_en;			//register output
output ch0_urg2_strong_en;			//register output
output ch0_oldest_timer_2_en;			//register output
output ch0_oldest_timer_en;			//register output
output ch0_oldest_cmd_select_en;			//register output
output [7:0] ch0_quota_bw_ini;			//register output
output [7:0] ch0_bw_quota_max;			//register output
output [11:0] ch0_oldest_time_2;			//register output
output [11:0] ch0_oldest_time;			//register output
output [3:0] ch0_bw_acc_unit;			//register output
output [3:0] ch0_cmd_extend_num;			//register output
output [5:0] ch0_extend_bl_max;			//register output
output [11:0] ch0_ostd_bl_max;			//register output
output [3:0] ch0_ostd_cmd_max;			//register output
output ch0_outstand_en;			//register output
output [9:0] ch0_wr_brk_time;			//register output
output [3:0] ch0_wms_bg_insert_mapping;			//register output
output [3:0] ch0_wms_page_insert_mapping;			//register output
output [3:0] ch0_wms_bank_free_mapping;			//register output
output [3:0] ch0_wms_dir_insert_mapping;			//register output
output [3:0] ch0_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch0_wmask_insert_mapping;			//register output
output [3:0] ch1_bg_insert_mapping;			//register output
output [3:0] ch1_page_insert_mapping;			//register output
output [3:0] ch1_bank_free_mapping;			//register output
output [3:0] ch1_dir_insert_mapping;			//register output
output [3:0] ch1_r2w_dir_insert_mapping;			//register output
output ch1_acc_trigger_sel;			//register output
output ch1_acc_mode;			//register output
output [1:0] ch1_acc_clr_mode;			//register output
output ch1_urg2_wr_brk_en;			//register output
output ch1_urg2_strong_en;			//register output
output ch1_oldest_timer_2_en;			//register output
output ch1_oldest_timer_en;			//register output
output ch1_oldest_cmd_select_en;			//register output
output [7:0] ch1_quota_bw_ini;			//register output
output [7:0] ch1_bw_quota_max;			//register output
output [11:0] ch1_oldest_time_2;			//register output
output [11:0] ch1_oldest_time;			//register output
output [3:0] ch1_bw_acc_unit;			//register output
output [3:0] ch1_cmd_extend_num;			//register output
output [5:0] ch1_extend_bl_max;			//register output
output [11:0] ch1_ostd_bl_max;			//register output
output [3:0] ch1_ostd_cmd_max;			//register output
output ch1_outstand_en;			//register output
output [9:0] ch1_wr_brk_time;			//register output
output [3:0] ch1_wms_bg_insert_mapping;			//register output
output [3:0] ch1_wms_page_insert_mapping;			//register output
output [3:0] ch1_wms_bank_free_mapping;			//register output
output [3:0] ch1_wms_dir_insert_mapping;			//register output
output [3:0] ch1_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch1_wmask_insert_mapping;			//register output
output [3:0] ch2_bg_insert_mapping;			//register output
output [3:0] ch2_page_insert_mapping;			//register output
output [3:0] ch2_bank_free_mapping;			//register output
output [3:0] ch2_dir_insert_mapping;			//register output
output [3:0] ch2_r2w_dir_insert_mapping;			//register output
output ch2_acc_trigger_sel;			//register output
output ch2_acc_mode;			//register output
output [1:0] ch2_acc_clr_mode;			//register output
output ch2_urg2_wr_brk_en;			//register output
output ch2_urg2_strong_en;			//register output
output ch2_oldest_timer_2_en;			//register output
output ch2_oldest_timer_en;			//register output
output ch2_oldest_cmd_select_en;			//register output
output [7:0] ch2_quota_bw_ini;			//register output
output [7:0] ch2_bw_quota_max;			//register output
output [11:0] ch2_oldest_time_2;			//register output
output [11:0] ch2_oldest_time;			//register output
output [3:0] ch2_bw_acc_unit;			//register output
output [3:0] ch2_cmd_extend_num;			//register output
output [5:0] ch2_extend_bl_max;			//register output
output [11:0] ch2_ostd_bl_max;			//register output
output [3:0] ch2_ostd_cmd_max;			//register output
output ch2_outstand_en;			//register output
output [9:0] ch2_wr_brk_time;			//register output
output [3:0] ch2_wms_bg_insert_mapping;			//register output
output [3:0] ch2_wms_page_insert_mapping;			//register output
output [3:0] ch2_wms_bank_free_mapping;			//register output
output [3:0] ch2_wms_dir_insert_mapping;			//register output
output [3:0] ch2_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch2_wmask_insert_mapping;			//register output
output [3:0] ch3_bg_insert_mapping;			//register output
output [3:0] ch3_page_insert_mapping;			//register output
output [3:0] ch3_bank_free_mapping;			//register output
output [3:0] ch3_dir_insert_mapping;			//register output
output [3:0] ch3_r2w_dir_insert_mapping;			//register output
output ch3_acc_trigger_sel;			//register output
output ch3_acc_mode;			//register output
output [1:0] ch3_acc_clr_mode;			//register output
output ch3_urg2_wr_brk_en;			//register output
output ch3_urg2_strong_en;			//register output
output ch3_oldest_timer_2_en;			//register output
output ch3_oldest_timer_en;			//register output
output ch3_oldest_cmd_select_en;			//register output
output [7:0] ch3_quota_bw_ini;			//register output
output [7:0] ch3_bw_quota_max;			//register output
output [11:0] ch3_oldest_time_2;			//register output
output [11:0] ch3_oldest_time;			//register output
output [3:0] ch3_bw_acc_unit;			//register output
output [3:0] ch3_cmd_extend_num;			//register output
output [5:0] ch3_extend_bl_max;			//register output
output [11:0] ch3_ostd_bl_max;			//register output
output [3:0] ch3_ostd_cmd_max;			//register output
output ch3_outstand_en;			//register output
output [9:0] ch3_wr_brk_time;			//register output
output [3:0] ch3_wms_bg_insert_mapping;			//register output
output [3:0] ch3_wms_page_insert_mapping;			//register output
output [3:0] ch3_wms_bank_free_mapping;			//register output
output [3:0] ch3_wms_dir_insert_mapping;			//register output
output [3:0] ch3_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch3_wmask_insert_mapping;			//register output
output [3:0] ch4_bg_insert_mapping;			//register output
output [3:0] ch4_page_insert_mapping;			//register output
output [3:0] ch4_bank_free_mapping;			//register output
output [3:0] ch4_dir_insert_mapping;			//register output
output [3:0] ch4_r2w_dir_insert_mapping;			//register output
output ch4_acc_trigger_sel;			//register output
output ch4_acc_mode;			//register output
output [1:0] ch4_acc_clr_mode;			//register output
output ch4_urg2_wr_brk_en;			//register output
output ch4_urg2_strong_en;			//register output
output ch4_oldest_timer_2_en;			//register output
output ch4_oldest_timer_en;			//register output
output ch4_oldest_cmd_select_en;			//register output
output [7:0] ch4_quota_bw_ini;			//register output
output [7:0] ch4_bw_quota_max;			//register output
output [11:0] ch4_oldest_time_2;			//register output
output [11:0] ch4_oldest_time;			//register output
output [3:0] ch4_bw_acc_unit;			//register output
output [3:0] ch4_cmd_extend_num;			//register output
output [5:0] ch4_extend_bl_max;			//register output
output [11:0] ch4_ostd_bl_max;			//register output
output [3:0] ch4_ostd_cmd_max;			//register output
output ch4_outstand_en;			//register output
output [9:0] ch4_wr_brk_time;			//register output
output [3:0] ch4_wms_bg_insert_mapping;			//register output
output [3:0] ch4_wms_page_insert_mapping;			//register output
output [3:0] ch4_wms_bank_free_mapping;			//register output
output [3:0] ch4_wms_dir_insert_mapping;			//register output
output [3:0] ch4_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch4_wmask_insert_mapping;			//register output
output [3:0] ch5_bg_insert_mapping;			//register output
output [3:0] ch5_page_insert_mapping;			//register output
output [3:0] ch5_bank_free_mapping;			//register output
output [3:0] ch5_dir_insert_mapping;			//register output
output [3:0] ch5_r2w_dir_insert_mapping;			//register output
output ch5_acc_trigger_sel;			//register output
output ch5_acc_mode;			//register output
output [1:0] ch5_acc_clr_mode;			//register output
output ch5_urg2_wr_brk_en;			//register output
output ch5_urg2_strong_en;			//register output
output ch5_oldest_timer_2_en;			//register output
output ch5_oldest_timer_en;			//register output
output ch5_oldest_cmd_select_en;			//register output
output [7:0] ch5_quota_bw_ini;			//register output
output [7:0] ch5_bw_quota_max;			//register output
output [11:0] ch5_oldest_time_2;			//register output
output [11:0] ch5_oldest_time;			//register output
output [3:0] ch5_bw_acc_unit;			//register output
output [3:0] ch5_cmd_extend_num;			//register output
output [5:0] ch5_extend_bl_max;			//register output
output [11:0] ch5_ostd_bl_max;			//register output
output [3:0] ch5_ostd_cmd_max;			//register output
output ch5_outstand_en;			//register output
output [9:0] ch5_wr_brk_time;			//register output
output [3:0] ch5_wms_bg_insert_mapping;			//register output
output [3:0] ch5_wms_page_insert_mapping;			//register output
output [3:0] ch5_wms_bank_free_mapping;			//register output
output [3:0] ch5_wms_dir_insert_mapping;			//register output
output [3:0] ch5_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch5_wmask_insert_mapping;			//register output
output [3:0] ch6_bg_insert_mapping;			//register output
output [3:0] ch6_page_insert_mapping;			//register output
output [3:0] ch6_bank_free_mapping;			//register output
output [3:0] ch6_dir_insert_mapping;			//register output
output [3:0] ch6_r2w_dir_insert_mapping;			//register output
output ch6_acc_trigger_sel;			//register output
output ch6_acc_mode;			//register output
output [1:0] ch6_acc_clr_mode;			//register output
output ch6_urg2_wr_brk_en;			//register output
output ch6_urg2_strong_en;			//register output
output ch6_oldest_timer_2_en;			//register output
output ch6_oldest_timer_en;			//register output
output ch6_oldest_cmd_select_en;			//register output
output [7:0] ch6_quota_bw_ini;			//register output
output [7:0] ch6_bw_quota_max;			//register output
output [11:0] ch6_oldest_time_2;			//register output
output [11:0] ch6_oldest_time;			//register output
output [3:0] ch6_bw_acc_unit;			//register output
output [3:0] ch6_cmd_extend_num;			//register output
output [5:0] ch6_extend_bl_max;			//register output
output [11:0] ch6_ostd_bl_max;			//register output
output [3:0] ch6_ostd_cmd_max;			//register output
output ch6_outstand_en;			//register output
output [9:0] ch6_wr_brk_time;			//register output
output [3:0] ch6_wms_bg_insert_mapping;			//register output
output [3:0] ch6_wms_page_insert_mapping;			//register output
output [3:0] ch6_wms_bank_free_mapping;			//register output
output [3:0] ch6_wms_dir_insert_mapping;			//register output
output [3:0] ch6_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch6_wmask_insert_mapping;			//register output
output [3:0] ch7_bg_insert_mapping;			//register output
output [3:0] ch7_page_insert_mapping;			//register output
output [3:0] ch7_bank_free_mapping;			//register output
output [3:0] ch7_dir_insert_mapping;			//register output
output [3:0] ch7_r2w_dir_insert_mapping;			//register output
output ch7_acc_trigger_sel;			//register output
output ch7_acc_mode;			//register output
output [1:0] ch7_acc_clr_mode;			//register output
output ch7_urg2_wr_brk_en;			//register output
output ch7_urg2_strong_en;			//register output
output ch7_oldest_timer_2_en;			//register output
output ch7_oldest_timer_en;			//register output
output ch7_oldest_cmd_select_en;			//register output
output [7:0] ch7_quota_bw_ini;			//register output
output [7:0] ch7_bw_quota_max;			//register output
output [11:0] ch7_oldest_time_2;			//register output
output [11:0] ch7_oldest_time;			//register output
output [3:0] ch7_bw_acc_unit;			//register output
output [3:0] ch7_cmd_extend_num;			//register output
output [5:0] ch7_extend_bl_max;			//register output
output [11:0] ch7_ostd_bl_max;			//register output
output [3:0] ch7_ostd_cmd_max;			//register output
output ch7_outstand_en;			//register output
output [9:0] ch7_wr_brk_time;			//register output
output [3:0] ch7_wms_bg_insert_mapping;			//register output
output [3:0] ch7_wms_page_insert_mapping;			//register output
output [3:0] ch7_wms_bank_free_mapping;			//register output
output [3:0] ch7_wms_dir_insert_mapping;			//register output
output [3:0] ch7_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch7_wmask_insert_mapping;			//register output
output [3:0] ch8_bg_insert_mapping;			//register output
output [3:0] ch8_page_insert_mapping;			//register output
output [3:0] ch8_bank_free_mapping;			//register output
output [3:0] ch8_dir_insert_mapping;			//register output
output [3:0] ch8_r2w_dir_insert_mapping;			//register output
output ch8_acc_trigger_sel;			//register output
output ch8_acc_mode;			//register output
output [1:0] ch8_acc_clr_mode;			//register output
output ch8_urg2_wr_brk_en;			//register output
output ch8_urg2_strong_en;			//register output
output ch8_oldest_timer_2_en;			//register output
output ch8_oldest_timer_en;			//register output
output ch8_oldest_cmd_select_en;			//register output
output [7:0] ch8_quota_bw_ini;			//register output
output [7:0] ch8_bw_quota_max;			//register output
output [11:0] ch8_oldest_time_2;			//register output
output [11:0] ch8_oldest_time;			//register output
output [3:0] ch8_bw_acc_unit;			//register output
output [3:0] ch8_cmd_extend_num;			//register output
output [5:0] ch8_extend_bl_max;			//register output
output [11:0] ch8_ostd_bl_max;			//register output
output [3:0] ch8_ostd_cmd_max;			//register output
output ch8_outstand_en;			//register output
output [9:0] ch8_wr_brk_time;			//register output
output [3:0] ch8_wms_bg_insert_mapping;			//register output
output [3:0] ch8_wms_page_insert_mapping;			//register output
output [3:0] ch8_wms_bank_free_mapping;			//register output
output [3:0] ch8_wms_dir_insert_mapping;			//register output
output [3:0] ch8_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch8_wmask_insert_mapping;			//register output
output [3:0] ch9_bg_insert_mapping;			//register output
output [3:0] ch9_page_insert_mapping;			//register output
output [3:0] ch9_bank_free_mapping;			//register output
output [3:0] ch9_dir_insert_mapping;			//register output
output [3:0] ch9_r2w_dir_insert_mapping;			//register output
output ch9_acc_trigger_sel;			//register output
output ch9_acc_mode;			//register output
output [1:0] ch9_acc_clr_mode;			//register output
output ch9_urg2_wr_brk_en;			//register output
output ch9_urg2_strong_en;			//register output
output ch9_oldest_timer_2_en;			//register output
output ch9_oldest_timer_en;			//register output
output ch9_oldest_cmd_select_en;			//register output
output [7:0] ch9_quota_bw_ini;			//register output
output [7:0] ch9_bw_quota_max;			//register output
output [11:0] ch9_oldest_time_2;			//register output
output [11:0] ch9_oldest_time;			//register output
output [3:0] ch9_bw_acc_unit;			//register output
output [3:0] ch9_cmd_extend_num;			//register output
output [5:0] ch9_extend_bl_max;			//register output
output [11:0] ch9_ostd_bl_max;			//register output
output [3:0] ch9_ostd_cmd_max;			//register output
output ch9_outstand_en;			//register output
output [9:0] ch9_wr_brk_time;			//register output
output [3:0] ch9_wms_bg_insert_mapping;			//register output
output [3:0] ch9_wms_page_insert_mapping;			//register output
output [3:0] ch9_wms_bank_free_mapping;			//register output
output [3:0] ch9_wms_dir_insert_mapping;			//register output
output [3:0] ch9_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch9_wmask_insert_mapping;			//register output
output [3:0] ch10_bg_insert_mapping;			//register output
output [3:0] ch10_page_insert_mapping;			//register output
output [3:0] ch10_bank_free_mapping;			//register output
output [3:0] ch10_dir_insert_mapping;			//register output
output [3:0] ch10_r2w_dir_insert_mapping;			//register output
output ch10_acc_trigger_sel;			//register output
output ch10_acc_mode;			//register output
output [1:0] ch10_acc_clr_mode;			//register output
output ch10_urg2_wr_brk_en;			//register output
output ch10_urg2_strong_en;			//register output
output ch10_oldest_timer_2_en;			//register output
output ch10_oldest_timer_en;			//register output
output ch10_oldest_cmd_select_en;			//register output
output [7:0] ch10_quota_bw_ini;			//register output
output [7:0] ch10_bw_quota_max;			//register output
output [11:0] ch10_oldest_time_2;			//register output
output [11:0] ch10_oldest_time;			//register output
output [3:0] ch10_bw_acc_unit;			//register output
output [3:0] ch10_cmd_extend_num;			//register output
output [5:0] ch10_extend_bl_max;			//register output
output [11:0] ch10_ostd_bl_max;			//register output
output [3:0] ch10_ostd_cmd_max;			//register output
output ch10_outstand_en;			//register output
output [9:0] ch10_wr_brk_time;			//register output
output [3:0] ch10_wms_bg_insert_mapping;			//register output
output [3:0] ch10_wms_page_insert_mapping;			//register output
output [3:0] ch10_wms_bank_free_mapping;			//register output
output [3:0] ch10_wms_dir_insert_mapping;			//register output
output [3:0] ch10_wms_r2w_dir_insert_mapping;			//register output
output [3:0] ch10_wmask_insert_mapping;			//register output
output [10:0] meas_sram_last_w_num;			//register output
output [1:0] meas_rk_ctrl_mc2;			//register output
output [1:0] meas_rk_ctrl_mc1;			//register output
output meas_sram_w_addr_rst;			//register output
output meas_sram_one_time;			//register output
output [3:0] meas_sram_mode_ctrl;			//register output
output meas_sram_r_add_inc;			//register output
output meas_sram_r_addr_sync;			//register output
output [10:0] meas_sram_r_addr;			//register output
output meas_one_shot_mode_en;			//register output
output meas_cnt_mode_max_en;			//register output
output meas_cnt_mode_avg_en;			//register output
output meas_cnt_record_mode;			//register output
output [1:0] meas_timer1_sync;			//register output
output meas_trig_sel;			//register output
output meas_serial_cont;			//register output
output meas_mode;			//register output
output meas_start;			//register output
output [31:0] meas_timer1;			//register output
output meas_cnt1_mask_en;			//register output
output [7:0] meas_cnt1_id;			//register output
output [3:0] meas_cnt1_mask_id;			//register output
output meas_cnt1_id_en;			//register output
output [1:0] meas_cnt1_ddr_num;			//register output
output meas_cnt2_mask_en;			//register output
output [7:0] meas_cnt2_id;			//register output
output [3:0] meas_cnt2_mask_id;			//register output
output meas_cnt2_id_en;			//register output
output [1:0] meas_cnt2_ddr_num;			//register output
output meas_cnt2_mode;			//register output
output meas_cnt3_mask_en;			//register output
output [7:0] meas_cnt3_id;			//register output
output [3:0] meas_cnt3_mask_id;			//register output
output meas_cnt3_id_en;			//register output
output [1:0] meas_cnt3_ddr_num;			//register output
output meas_cnt3_mode;			//register output
output meas_cnt4_mask_en;			//register output
output [7:0] meas_cnt4_id;			//register output
output [3:0] meas_cnt4_mask_id;			//register output
output meas_cnt4_id_en;			//register output
output [1:0] meas_cnt4_ddr_num;			//register output
output meas_cnt4_mode;			//register output
output meas_en;			//register output
output meas_stop;			//register output
output meas_sram_clear_en;			//register output
output meas_page_addr_thr_en;			//register output
output [1:0] meas_dram_num_sel;			//register output
output meas_timer_en;			//register output
output meas_counting_mode;			//register output
output addr_thr_cnt_mode_en;			//register output
output [1:0] meas_mc_sel;			//register output
output meas_chop_cnt_en;			//register output
output meas_wmask_cnt_en;			//register output
output [7:0] meas_page_addr_thr2;			//register output
output [7:0] meas_page_addr_thr1;			//register output
output [31:0] cnt_mode_irq_thershold;			//register output
output cnt2_irq_en;			//register output
output cnt1_irq_en;			//register output
output mes_mem_tra_dc_sel;			//register output
output [7:0] mes_mem_cmp_id;			//register output
output [1:0] mes_mem_cmp_dir;			//register output
output mes_mem_tras_adr;			//register output
output mes_mem_tras_id;			//register output
output mes_mem_tras_en;			//register output
output [28:0] mes_cmp_addr;			//register output
output [28:0] mes_cmp_addr_mask;			//register output
output eff_sram_testrwm_0;			//register output
output eff_sram_testrwm_1;			//register output
output eff_bist_mode;			//register output
output eff_sram_drf_mode;			//register output
output eff_sram_test1;			//register output
output eff_sram_drf_resume;			//register output
output eff_sram_ls;			//register output
output eff_sram_rme;			//register output
output [3:0] eff_sram_rm;			//register output
output eff_sram_bc1_0;			//register output
output eff_sram_bc1_1;			//register output
output eff_sram_bc2_0;			//register output
output eff_sram_bc2_1;			//register output
output eff_sram_test_rnm_0;			//register output
output eff_sram_test_rnm_1;			//register output
output eff_sram_scan_shift_en;			//register output
output eff_mem_speed_mode;			//register output
output eff_meas_sram1_config_from_reg_en;			//register output
output eff_meas_sram0_config_from_reg_en;			//register output
output [1:0] eff_meas_sram1_wtsel;			//register output
output [1:0] eff_meas_sram1_rtsel;			//register output
output [1:0] eff_meas_sram1_mtsel;			//register output
output [1:0] eff_meas_sram0_wtsel;			//register output
output [1:0] eff_meas_sram0_rtsel;			//register output
output [1:0] eff_meas_sram0_mtsel;			//register output
output eff_meas_sram1_ls_7;			//register output
output eff_meas_sram1_ls_6;			//register output
output eff_meas_sram1_ls_5;			//register output
output eff_meas_sram1_ls_4;			//register output
output eff_meas_sram1_ls_3;			//register output
output eff_meas_sram1_ls_2;			//register output
output eff_meas_sram1_ls_1;			//register output
output eff_meas_sram1_ls_0;			//register output
output eff_meas_sram0_ls_7;			//register output
output eff_meas_sram0_ls_6;			//register output
output eff_meas_sram0_ls_5;			//register output
output eff_meas_sram0_ls_4;			//register output
output eff_meas_sram0_ls_3;			//register output
output eff_meas_sram0_ls_2;			//register output
output eff_meas_sram0_ls_1;			//register output
output eff_meas_sram0_ls_0;			//register output
output eff_meas_sram1_drf_test_resume;			//register output
output eff_meas_sram1_drf_bist_mode;			//register output
output eff_meas_sram1_bist_mode;			//register output
output eff_meas_sram0_drf_test_resume;			//register output
output eff_meas_sram0_drf_bist_mode;			//register output
output eff_meas_sram0_bist_mode;			//register output
output mes_cmp_addr_upper;			//register output
output mes_cmp_addr_mask_upper;			//register output
output mc_fifo_err_int_en;			//register output
output int_err_active_en;			//register output
output mc_mes_client_1_rprt_en;			//output, Read port enable
output mc_mes_client_2_rprt_en;			//output, Read port enable

//Register      Declaration
reg  [31:0] reg180c2718_wclr_out;	//wclr_out registered
assign  dbe_err_flag1_wclr_out = reg180c2718_wclr_out[2];
assign  dbe_err_flag0_wclr_out = reg180c2718_wclr_out[1];
assign  fmtr_unknown_cmd_wclr_out = reg180c2718_wclr_out[0];
reg  [31:0] reg180c2728_wclr_out;	//wclr_out registered
assign  rk1_wr_chop_no_mask_wclr_out = reg180c2728_wclr_out[3];
assign  rk1_active_ddr_num_mismatch_wclr_out = reg180c2728_wclr_out[2];
assign  rk0_wr_chop_no_mask_wclr_out = reg180c2728_wclr_out[1];
assign  rk0_active_ddr_num_mismatch_wclr_out = reg180c2728_wclr_out[0];
reg  [31:0] reg180c2c58_wclr_out;	//wclr_out registered
assign  cnt2_irq_status_wclr_out = reg180c2c58_wclr_out[1];
assign  cnt1_irq_status_wclr_out = reg180c2c58_wclr_out[0];
reg  [31:0] reg180c2f94_wclr_out;	//wclr_out registered
assign  rk1_err_pbk_wclr_out = reg180c2f94_wclr_out[3];
assign  rk0_err_pbk_wclr_out = reg180c2f94_wclr_out[2];
assign  rk1_err_active_wclr_out = reg180c2f94_wclr_out[1];
assign  rk0_err_active_wclr_out = reg180c2f94_wclr_out[0];

//Wire      Declaration
wire [ 11:0]  reg_addr;
wire [ 31:0]  write_data;
reg [ 31:0]  read_data;
wire [228:0]    write_en ;
wire addr_hit;




//============== register anounce ==============//
reg     [31:0] reg180c2020;
reg     [31:0] reg180c2028;
reg     [31:0] reg180c202c;
reg     [31:0] reg180c2030;
reg     [31:0] reg180c2034;
reg     [31:0] reg180c2038;
reg     [31:0] reg180c203c;
reg     [31:0] reg180c2040;
reg     [31:0] reg180c2044;
reg     [31:0] reg180c2050;
reg     [31:0] reg180c2060;
reg     [31:0] reg180c2064;
reg     [31:0] reg180c2068;
reg     [31:0] reg180c2080;
reg     [31:0] reg180c2088;
reg     [31:0] reg180c2090;
reg     [31:0] reg180c2098;
reg     [31:0] reg180c20a0;
reg     [31:0] reg180c20f0;
reg     [31:0] reg180c2100;
reg     [31:0] reg180c2110;
reg     [31:0] reg180c2114;
reg     [31:0] reg180c2118;
reg     [31:0] reg180c211c;
reg     [31:0] reg180c2120;
reg     [31:0] reg180c2130;
reg     [31:0] reg180c2138;
reg     [31:0] reg180c2140;
reg     [31:0] reg180c2200;
reg     [31:0] reg180c2208;
reg     [31:0] reg180c2210;
reg     [31:0] reg180c2218;
reg     [31:0] reg180c2220;
reg     [31:0] reg180c2228;
reg     [31:0] reg180c222c;
reg     [31:0] reg180c2230;
reg     [31:0] reg180c2234;
reg     [31:0] reg180c2238;
reg     [31:0] reg180c2240;
reg     [31:0] reg180c2244;
reg     [31:0] reg180c2248;
reg     [31:0] reg180c22a0;
reg     [31:0] reg180c22a4;
reg     [31:0] reg180c22a8;
reg     [31:0] reg180c22ac;
reg     [31:0] reg180c2300;
reg     [31:0] reg180c2304;
reg     [31:0] reg180c2710;
reg     [31:0] reg180c2718;
reg     [31:0] reg180c271c;
reg     [31:0] reg180c2720;
reg     [31:0] reg180c2734;
reg     [31:0] reg180c273c;
reg     [31:0] reg180c2740;
reg     [31:0] reg180c2744;
reg     [31:0] reg180c2748;
reg     [31:0] reg180c274c;
reg     [31:0] reg180c2750;
reg     [31:0] reg180c2754;
reg     [31:0] reg180c2758;
reg     [31:0] reg180c275c;
reg     [31:0] reg180c2760;
reg     [31:0] reg180c2764;
reg     [31:0] reg180c2768;
reg     [31:0] reg180c276c;
reg     [31:0] reg180c2770;
reg     [31:0] reg180c2774;
reg     [31:0] reg180c2778;
reg     [31:0] reg180c277c;
reg     [31:0] reg180c2780;
reg     [31:0] reg180c2784;
reg     [31:0] reg180c2788;
reg     [31:0] reg180c278c;
reg     [31:0] reg180c2800;
reg     [31:0] reg180c2804;
reg     [31:0] reg180c2808;
reg     [31:0] reg180c280c;
reg     [31:0] reg180c2810;
reg     [31:0] reg180c2814;
reg     [31:0] reg180c2818;
reg     [31:0] reg180c281c;
reg     [31:0] reg180c2820;
reg     [31:0] reg180c2824;
reg     [31:0] reg180c2828;
reg     [31:0] reg180c2840;
reg     [31:0] reg180c2844;
reg     [31:0] reg180c2848;
reg     [31:0] reg180c284c;
reg     [31:0] reg180c2850;
reg     [31:0] reg180c2854;
reg     [31:0] reg180c2858;
reg     [31:0] reg180c285c;
reg     [31:0] reg180c2860;
reg     [31:0] reg180c2864;
reg     [31:0] reg180c2868;
reg     [31:0] reg180c2880;
reg     [31:0] reg180c2884;
reg     [31:0] reg180c2888;
reg     [31:0] reg180c288c;
reg     [31:0] reg180c2890;
reg     [31:0] reg180c2894;
reg     [31:0] reg180c2898;
reg     [31:0] reg180c289c;
reg     [31:0] reg180c28a0;
reg     [31:0] reg180c28a4;
reg     [31:0] reg180c28a8;
reg     [31:0] reg180c2a00;
reg     [31:0] reg180c2a04;
reg     [31:0] reg180c2a10;
reg     [31:0] reg180c2a14;
reg     [31:0] reg180c2a18;
reg     [31:0] reg180c2a1c;
reg     [31:0] reg180c2a20;
reg     [31:0] reg180c2a24;
reg     [31:0] reg180c2a28;
reg     [31:0] reg180c2a2c;
reg     [31:0] reg180c2a30;
reg     [31:0] reg180c2a34;
reg     [31:0] reg180c2a3c;
reg     [31:0] reg180c2a60;
reg     [31:0] reg180c2a64;
reg     [31:0] reg180c2a68;
reg     [31:0] reg180c2a6c;
reg     [31:0] reg180c2a70;
reg     [31:0] reg180c2a74;
reg     [31:0] reg180c2a80;
reg     [31:0] reg180c2a84;
reg     [31:0] reg180c2a88;
reg     [31:0] reg180c2a8c;
reg     [31:0] reg180c2a90;
reg     [31:0] reg180c2a94;
reg     [31:0] reg180c2aa0;
reg     [31:0] reg180c2aa4;
reg     [31:0] reg180c2aa8;
reg     [31:0] reg180c2aac;
reg     [31:0] reg180c2ab0;
reg     [31:0] reg180c2ab4;
reg     [31:0] reg180c2ac0;
reg     [31:0] reg180c2ac4;
reg     [31:0] reg180c2ac8;
reg     [31:0] reg180c2acc;
reg     [31:0] reg180c2ad0;
reg     [31:0] reg180c2ad4;
reg     [31:0] reg180c2ae0;
reg     [31:0] reg180c2ae4;
reg     [31:0] reg180c2ae8;
reg     [31:0] reg180c2aec;
reg     [31:0] reg180c2af0;
reg     [31:0] reg180c2af4;
reg     [31:0] reg180c2b00;
reg     [31:0] reg180c2b04;
reg     [31:0] reg180c2b08;
reg     [31:0] reg180c2b0c;
reg     [31:0] reg180c2b10;
reg     [31:0] reg180c2b14;
reg     [31:0] reg180c2b20;
reg     [31:0] reg180c2b24;
reg     [31:0] reg180c2b28;
reg     [31:0] reg180c2b2c;
reg     [31:0] reg180c2b30;
reg     [31:0] reg180c2b34;
reg     [31:0] reg180c2b40;
reg     [31:0] reg180c2b44;
reg     [31:0] reg180c2b48;
reg     [31:0] reg180c2b4c;
reg     [31:0] reg180c2b50;
reg     [31:0] reg180c2b54;
reg     [31:0] reg180c2b60;
reg     [31:0] reg180c2b64;
reg     [31:0] reg180c2b68;
reg     [31:0] reg180c2b6c;
reg     [31:0] reg180c2b70;
reg     [31:0] reg180c2b74;
reg     [31:0] reg180c2b80;
reg     [31:0] reg180c2b84;
reg     [31:0] reg180c2b88;
reg     [31:0] reg180c2b8c;
reg     [31:0] reg180c2b90;
reg     [31:0] reg180c2b94;
reg     [31:0] reg180c2ba0;
reg     [31:0] reg180c2ba4;
reg     [31:0] reg180c2ba8;
reg     [31:0] reg180c2bac;
reg     [31:0] reg180c2bb0;
reg     [31:0] reg180c2bb4;
reg     [31:0] reg180c2c00;
reg     [31:0] reg180c2c04;
reg     [31:0] reg180c2c08;
reg     [31:0] reg180c2c0c;
reg     [31:0] reg180c2c14;
reg     [31:0] reg180c2c18;
reg     [31:0] reg180c2c1c;
reg     [31:0] reg180c2c20;
reg     [31:0] reg180c2c44;
reg     [31:0] reg180c2c50;
reg     [31:0] reg180c2c54;
reg     [31:0] reg180c2c58;
reg     [31:0] reg180c2c5c;
reg     [31:0] reg180c2c60;
reg     [31:0] reg180c2c64;
reg     [31:0] reg180c2c68;
reg     [31:0] reg180c2c6c;
reg     [31:0] reg180c2c70;
reg     [31:0] reg180c2c78;
reg     [31:0] reg180c2c7c;
reg     [31:0] reg180c2f90;
reg     [ 228  : 0] addr_dec; //select signal from decoding address


//============== combinational logics ==============//




//assign memory unit's Q to outports
assign mem_num_cfg		= reg180c2020[24];
assign lpddr5_en		= reg180c2020[6];
assign lpddr4_en		= reg180c2020[5];
assign lpddr3_en		= reg180c2020[4];
assign ddr4_en		= reg180c2020[1];
assign ddr3_en		= reg180c2020[0];
assign mcx2_option		= reg180c2028[31:28];
assign mcx2_mc1_act_cnt		= reg180c2028[27:24];
assign mcx2_mc2_act_cnt		= reg180c2028[23:20];
assign mcx2_mc1_act_sel		= reg180c2028[19];
assign qos_cmd_mode		= reg180c2028[16];
assign mcx2_mode		= reg180c2028[9:8];
assign mcx1_2cke_en		= reg180c2028[1];
assign mcx2_en		= reg180c2028[0];
assign parser_int_en		= reg180c202c[0];
assign geardown_en		= reg180c2030[28];
assign geardown_pre_set_en		= reg180c2030[27];
assign ddr4_x8		= reg180c2030[2];
assign ddr4_x8_bg1_sel		= reg180c2030[1:0];
assign ddrx_rst		= reg180c2034[17];
assign ddrx_cke		= reg180c2034[16];
assign ref_cmd_rst_delay_num		= reg180c2034[15:12];
assign ddr_wck_en		= reg180c2034[2];
assign ddr_wck_toggle		= reg180c2034[1:0];
assign cfmt_security_en		= reg180c2038[0];
assign cs_mrs_out_mode		= reg180c203c[9:8];
assign ca_toggle_rate		= reg180c203c[7:5];
assign cs_swap		= reg180c203c[4];
assign lock_cs_1		= reg180c203c[1];
assign lock_cs_0		= reg180c203c[0];
assign pda_mode_dram_sel		= reg180c2040[27:24];
assign pda_mode_en		= reg180c2040[20];
assign rd_ecc_en		= reg180c2040[19];
assign wr_ecc_en		= reg180c2040[18];
assign rd_dbi_en		= reg180c2040[17];
assign wr_dbi_en		= reg180c2040[16];
assign wr_dbi_dq_byte_1		= reg180c2040[15:8];
assign wr_dbi_dq_byte_0		= reg180c2040[7:0];
assign odt_post_num		= reg180c2044[26:24];
assign odt_lock_high		= reg180c2044[17];
assign odt_en		= reg180c2044[16];
assign udq_msb_sel		= reg180c2044[13:12];
assign udq_lsb_sel		= reg180c2044[9:8];
assign ldq_msb_sel		= reg180c2044[5:4];
assign ldq_lsb_sel		= reg180c2044[1:0];
assign ch_stop_req		= reg180c2050[10:0];
assign max_conti_ref_num		= reg180c2060[31:28];
assign ref_regulate		= reg180c2060[23];
assign per_bank_ref_en		= reg180c2060[17];
assign all_bank_ref_en		= reg180c2060[16];
assign ref_pop_num		= reg180c2060[10:8];
assign ref_pul_num		= reg180c2060[2:0];
assign ref_2ref_d		= reg180c2064[31:24];
assign immd_ref_aft_calib		= reg180c2064[23];
assign ref_idle_mode		= reg180c2064[21];
assign ref_idle_en		= reg180c2064[20];
assign ref_idle_time		= reg180c2064[11:0];
assign ref_rx_rst_cnt		= reg180c2068[13:8];
assign ref_tx_rst_cnt		= reg180c2068[5:0];
assign parser_algo		= reg180c2080[31:28];
assign bank_full_option		= reg180c2080[24];
assign act_bl_remain_thr		= reg180c2080[23:12];
assign act_bl_calc		= reg180c2080[10];
assign mask_tmccd		= reg180c2080[9:8];
assign mask_tmccd_en		= reg180c2080[7];
assign dis_ap		= reg180c2080[5];
assign dis_preacc		= reg180c2080[4];
assign dis_acc		= reg180c2080[3];
assign dis_acc_interlave		= reg180c2080[2];
assign dis_cmd_grp_in_order		= reg180c2080[1];
assign en_cmd_bg_in_order		= reg180c2080[0];
assign hppr_mode		= reg180c2088[25];
assign sppr_mode		= reg180c2088[24];
assign ddr4_cmd_bg_in_order		= reg180c2088[1];
assign lpddr4_wmask_in_order		= reg180c2088[0];
assign bank_free_tmrp_rd		= reg180c2090[15:8];
assign bank_free_tmrp_wr		= reg180c2090[7:0];
assign bank_free_bl_adj		= reg180c2098[23];
assign bank_free_offset_updn		= reg180c2098[22];
assign bank_free_offset		= reg180c2098[21:16];
assign bank_free_tmrprcd_rd		= reg180c2098[15:8];
assign bank_free_tmrprcd_wr		= reg180c2098[7:0];
assign bg_balance_1		= reg180c20a0[21:16];
assign bg_balance_0		= reg180c20a0[13:8];
assign bg_balance_en		= reg180c20a0[0];
assign no_scramble		= reg180c20f0[8];
assign global_scramble_en		= reg180c20f0[4];
assign emi_scramble_en		= reg180c20f0[0];
assign cmd_start		= reg180c2100[31];
assign cmd_execute_posi		= reg180c2100[9:8];
assign cmd_num		= reg180c2100[2:0];
assign cmd_ctl_cmd_1		= reg180c2110[31:0];
assign cmd_ctl_cmd_2		= reg180c2114[31:0];
assign cmd_ctl_cmd_3		= reg180c2118[31:0];
assign cmd_ctl_cmd_4		= reg180c211c[31:0];
assign cmd_ctl_cmd_5		= reg180c2120[31:0];
assign cmd_ctl_t1		= reg180c2130[31:16];
assign cmd_ctl_t0		= reg180c2130[15:0];
assign cmd_ctl_t3		= reg180c2138[31:16];
assign cmd_ctl_t2		= reg180c2138[15:0];
assign cmd_ctl_t5		= reg180c2140[31:16];
assign cmd_ctl_t4		= reg180c2140[15:0];
assign tmras		= reg180c2200[23:16];
assign tmrcl		= reg180c2200[13:8];
assign tmcl		= reg180c2200[5:0];
assign tmrrd		= reg180c2208[28:24];
assign tmrp		= reg180c2208[21:16];
assign tmrcdrd		= reg180c2208[13:8];
assign tmrc		= reg180c2208[7:0];
assign tmccd		= reg180c2210[27:24];
assign tmrtp		= reg180c2210[22:16];
assign tmwtr		= reg180c2210[12:8];
assign tmwr		= reg180c2210[5:0];
assign tmfaw		= reg180c2218[31:24];
assign tmrp_a_sel		= reg180c2218[17];
assign tmrc_sel		= reg180c2218[16];
assign tmwrp_a		= reg180c2218[15:8];
assign tmrrp_a		= reg180c2218[7:0];
assign tmdqsck		= reg180c2220[31:28];
assign tmrp_ab		= reg180c2220[25:20];
assign tmwtr_l		= reg180c2220[16:12];
assign tmrrd_l		= reg180c2220[8:4];
assign tmccd_l		= reg180c2220[3:0];
assign tmodt_on		= reg180c2228[23:20];
assign tmodtl_on		= reg180c2228[16:12];
assign tmrpst		= reg180c2228[9:8];
assign tmccdmw		= reg180c2228[5:0];
assign tmaad		= reg180c222c[31:28];
assign tmccdmw_dbk_in_sbg		= reg180c222c[27:24];
assign tmccdmw_dbk_in_dbg		= reg180c222c[23:20];
assign tmccdmw_sbk_in_sbg		= reg180c222c[19:15];
assign tmrtw_dbg		= reg180c222c[13:8];
assign tmrtw_sbg		= reg180c222c[5:0];
assign tmrank0_w2r		= reg180c2230[29:24];
assign tmrank0_w2w		= reg180c2230[21:16];
assign tmrank0_r2w		= reg180c2230[13:8];
assign tmrank0_r2r		= reg180c2230[5:0];
assign reg_rk_wait_exit_bl_cnt		= reg180c2234[31:22];
assign reg_rk_wait_extend_self_bl_cnt		= reg180c2234[21:12];
assign pbkref_postpone		= reg180c2234[11];
assign dynamic_rank_acc		= reg180c2234[10];
assign tm_rank0_acc_time		= reg180c2234[9:0];
assign tmrank1_w2r		= reg180c2238[29:24];
assign tmrank1_w2w		= reg180c2238[21:16];
assign tmrank1_r2w		= reg180c2238[13:8];
assign tmrank1_r2r		= reg180c2238[5:0];
assign reg_rk_wait_extend_other_bl_cnt		= reg180c2240[25:16];
assign pbk_exec_period_en		= reg180c2240[14];
assign pbk_wait_bank_empty_en		= reg180c2240[13];
assign pbk_ref_lock_bk_ignore		= reg180c2240[12];
assign tm_rank1_acc_time		= reg180c2240[9:0];
assign lp5_tm_rank_arb_en		= reg180c2244[1];
assign lp4_tm_rank_arb_en		= reg180c2244[0];
assign tm_wckpre_toggle_fs_pre		= reg180c2248[28:24];
assign tm_wckenlfs		= reg180c2248[20:16];
assign tm_wckpre_static		= reg180c2248[12:8];
assign tm_wckpre_toggle_fs		= reg180c2248[4:0];
assign t_refi		= reg180c22a0[31:16];
assign t_refc		= reg180c22a0[10:0];
assign t_refi_max		= reg180c22a4[31:16];
assign t_no_ref_max		= reg180c22a4[15:0];
assign tmpbr2act		= reg180c22a8[31:24];
assign tmrefi_pb		= reg180c22a8[22:12];
assign tmrfc_pb		= reg180c22a8[8:0];
assign tmrefi_pb_timeout		= reg180c22ac[22:12];
assign tmpbr2pbr		= reg180c22ac[8:0];
assign t_odt_dfi		= reg180c2300[28:24];
assign t_ca_dfi		= reg180c2300[20:16];
assign t_write_dfi_en		= reg180c2300[12:8];
assign t_read_dfi_en		= reg180c2300[4:0];
assign t_gck_enable		= reg180c2304[13];
assign t_gck_write_dfi_en		= reg180c2304[12:8];
assign t_gck_read_dfi_en		= reg180c2304[4:0];
assign qos_dbg_sel		= reg180c2710[27:24];
assign qos_dummy		= reg180c2710[23:16];
assign modr_dbg_en		= reg180c2718[31];
assign modr_dbg_sel		= reg180c2718[29:24];
assign mc_force_int		= reg180c271c[9:8];
assign mc_force_int_en		= reg180c271c[1:0];
assign parser_rbus_dbg_bg1_sel		= reg180c2720[14:12];
assign parser_rbus_dbg_bg0_sel		= reg180c2720[10:8];
assign parser_rbus_dbg_sel		= reg180c2720[4:0];
assign phy_dbg_sel		= reg180c2734[5:0];
assign fake_rd_id		= reg180c273c[23:16];
assign fake_rd_id_en		= reg180c273c[0];
assign dummy_wdg_rst_fw0		= reg180c2740[31:0];
assign dummy_wdg_rst_fw1		= reg180c2744[31:0];
assign dummy_wdg_rst_fw2		= reg180c2748[31:0];
assign dummy_wdg_rst_fw3		= reg180c274c[31:0];
assign dummy_fw0		= reg180c2750[31:0];
assign dummy_fw1		= reg180c2754[31:0];
assign dummy_fw2		= reg180c2758[31:0];
assign dummy_fw3		= reg180c275c[31:0];
assign dummy_fw4		= reg180c2760[31:0];
assign dummy_fw5		= reg180c2764[31:0];
assign dummy_fw6		= reg180c2768[31:0];
assign dummy_fw7		= reg180c276c[31:0];
assign dummy_fw8		= reg180c2770[31:0];
assign dummy_fw9		= reg180c2774[31:0];
assign dummy_fw10		= reg180c2778[31:0];
assign dummy_fw11		= reg180c277c[31:0];
assign dummy_fw12		= reg180c2780[31:0];
assign dummy_fw13		= reg180c2784[31:0];
assign dummy_fw14		= reg180c2788[31:0];
assign dummy_fw15		= reg180c278c[31:0];
assign limit_ostd_cmd_max_lv2_0		= reg180c2800[31:28];
assign limit_cmd_extend_num_lv2_0		= reg180c2800[27:24];
assign limit_ostd_cmd_max_0		= reg180c2800[23:20];
assign limit_cmd_extend_num_0		= reg180c2800[19:16];
assign limit_ref_list_0		= reg180c2800[15:2];
assign limit_en_0		= reg180c2800[1:0];
assign limit_ostd_cmd_max_lv2_1		= reg180c2804[31:28];
assign limit_cmd_extend_num_lv2_1		= reg180c2804[27:24];
assign limit_ostd_cmd_max_1		= reg180c2804[23:20];
assign limit_cmd_extend_num_1		= reg180c2804[19:16];
assign limit_ref_list_1		= reg180c2804[15:2];
assign limit_en_1		= reg180c2804[1:0];
assign limit_ostd_cmd_max_lv2_2		= reg180c2808[31:28];
assign limit_cmd_extend_num_lv2_2		= reg180c2808[27:24];
assign limit_ostd_cmd_max_2		= reg180c2808[23:20];
assign limit_cmd_extend_num_2		= reg180c2808[19:16];
assign limit_ref_list_2		= reg180c2808[15:2];
assign limit_en_2		= reg180c2808[1:0];
assign limit_ostd_cmd_max_lv2_3		= reg180c280c[31:28];
assign limit_cmd_extend_num_lv2_3		= reg180c280c[27:24];
assign limit_ostd_cmd_max_3		= reg180c280c[23:20];
assign limit_cmd_extend_num_3		= reg180c280c[19:16];
assign limit_ref_list_3		= reg180c280c[15:2];
assign limit_en_3		= reg180c280c[1:0];
assign limit_ostd_cmd_max_lv2_4		= reg180c2810[31:28];
assign limit_cmd_extend_num_lv2_4		= reg180c2810[27:24];
assign limit_ostd_cmd_max_4		= reg180c2810[23:20];
assign limit_cmd_extend_num_4		= reg180c2810[19:16];
assign limit_ref_list_4		= reg180c2810[15:2];
assign limit_en_4		= reg180c2810[1:0];
assign limit_ostd_cmd_max_lv2_5		= reg180c2814[31:28];
assign limit_cmd_extend_num_lv2_5		= reg180c2814[27:24];
assign limit_ostd_cmd_max_5		= reg180c2814[23:20];
assign limit_cmd_extend_num_5		= reg180c2814[19:16];
assign limit_ref_list_5		= reg180c2814[15:2];
assign limit_en_5		= reg180c2814[1:0];
assign limit_ostd_cmd_max_lv2_6		= reg180c2818[31:28];
assign limit_cmd_extend_num_lv2_6		= reg180c2818[27:24];
assign limit_ostd_cmd_max_6		= reg180c2818[23:20];
assign limit_cmd_extend_num_6		= reg180c2818[19:16];
assign limit_ref_list_6		= reg180c2818[15:2];
assign limit_en_6		= reg180c2818[1:0];
assign limit_ostd_cmd_max_lv2_7		= reg180c281c[31:28];
assign limit_cmd_extend_num_lv2_7		= reg180c281c[27:24];
assign limit_ostd_cmd_max_7		= reg180c281c[23:20];
assign limit_cmd_extend_num_7		= reg180c281c[19:16];
assign limit_ref_list_7		= reg180c281c[15:2];
assign limit_en_7		= reg180c281c[1:0];
assign limit_ostd_cmd_max_lv2_8		= reg180c2820[31:28];
assign limit_cmd_extend_num_lv2_8		= reg180c2820[27:24];
assign limit_ostd_cmd_max_8		= reg180c2820[23:20];
assign limit_cmd_extend_num_8		= reg180c2820[19:16];
assign limit_ref_list_8		= reg180c2820[15:2];
assign limit_en_8		= reg180c2820[1:0];
assign limit_ostd_cmd_max_lv2_9		= reg180c2824[31:28];
assign limit_cmd_extend_num_lv2_9		= reg180c2824[27:24];
assign limit_ostd_cmd_max_9		= reg180c2824[23:20];
assign limit_cmd_extend_num_9		= reg180c2824[19:16];
assign limit_ref_list_9		= reg180c2824[15:2];
assign limit_en_9		= reg180c2824[1:0];
assign limit_ostd_cmd_max_lv2_10		= reg180c2828[31:28];
assign limit_cmd_extend_num_lv2_10		= reg180c2828[27:24];
assign limit_ostd_cmd_max_10		= reg180c2828[23:20];
assign limit_cmd_extend_num_10		= reg180c2828[19:16];
assign limit_ref_list_10		= reg180c2828[15:2];
assign limit_en_10		= reg180c2828[1:0];
assign limit_data_num_lv2_0		= reg180c2840[31:16];
assign limit_data_num_0		= reg180c2840[15:0];
assign limit_data_num_lv2_1		= reg180c2844[31:16];
assign limit_data_num_1		= reg180c2844[15:0];
assign limit_data_num_lv2_2		= reg180c2848[31:16];
assign limit_data_num_2		= reg180c2848[15:0];
assign limit_data_num_lv2_3		= reg180c284c[31:16];
assign limit_data_num_3		= reg180c284c[15:0];
assign limit_data_num_lv2_4		= reg180c2850[31:16];
assign limit_data_num_4		= reg180c2850[15:0];
assign limit_data_num_lv2_5		= reg180c2854[31:16];
assign limit_data_num_5		= reg180c2854[15:0];
assign limit_data_num_lv2_6		= reg180c2858[31:16];
assign limit_data_num_6		= reg180c2858[15:0];
assign limit_data_num_lv2_7		= reg180c285c[31:16];
assign limit_data_num_7		= reg180c285c[15:0];
assign limit_data_num_lv2_8		= reg180c2860[31:16];
assign limit_data_num_8		= reg180c2860[15:0];
assign limit_data_num_lv2_9		= reg180c2864[31:16];
assign limit_data_num_9		= reg180c2864[15:0];
assign limit_data_num_lv2_10		= reg180c2868[31:16];
assign limit_data_num_10		= reg180c2868[15:0];
assign limit_timer_cycle_0		= reg180c2880[15:0];
assign limit_timer_cycle_1		= reg180c2884[15:0];
assign limit_timer_cycle_2		= reg180c2888[15:0];
assign limit_timer_cycle_3		= reg180c288c[15:0];
assign limit_timer_cycle_4		= reg180c2890[15:0];
assign limit_timer_cycle_5		= reg180c2894[15:0];
assign limit_timer_cycle_6		= reg180c2898[15:0];
assign limit_timer_cycle_7		= reg180c289c[15:0];
assign limit_timer_cycle_8		= reg180c28a0[15:0];
assign limit_timer_cycle_9		= reg180c28a4[15:0];
assign limit_timer_cycle_10		= reg180c28a8[15:0];
assign hi_priority_id6_en		= reg180c2a00[22];
assign hi_priority_id3_en		= reg180c2a00[19];
assign hi_priority_id2_en		= reg180c2a00[18];
assign hi_priority_id1_en		= reg180c2a00[17];
assign hi_priority_id0_en		= reg180c2a00[16];
assign dis_tracking_gp1_id_en		= reg180c2a00[15];
assign dis_tracking_gp0_id_en		= reg180c2a00[14];
assign dis_tracking_id0_en		= reg180c2a00[13];
assign dis_tracking_id1_en		= reg180c2a00[12];
assign ch_ref_bl_gt_sel		= reg180c2a00[11];
assign ch_un_match_id_pg_wt		= reg180c2a00[10];
assign ch_tag_tracking		= reg180c2a00[9];
assign ch_dir_cont_chg_sel		= reg180c2a00[8];
assign ch_parser_cmd_limt_sel		= reg180c2a00[7];
assign ch_dir_short_dly_en		= reg180c2a00[6];
assign ch_dir_cont_bl_mode		= reg180c2a00[5:4];
assign tracking_sel		= reg180c2a00[3];
assign bank_wr_sel		= reg180c2a00[2];
assign channel_id_weight_en		= reg180c2a00[1];
assign channel_rw_weight_en		= reg180c2a00[0];
assign wms_bk_we_map		= reg180c2a04[1];
assign wms_bf_bl_sel		= reg180c2a04[0];
assign hi_priority_id3		= reg180c2a10[31:24];
assign hi_priority_id2		= reg180c2a10[23:16];
assign hi_priority_id1		= reg180c2a10[15:8];
assign hi_priority_id0		= reg180c2a10[7:0];
assign hi_priority_mask_id6		= reg180c2a14[31:24];
assign hi_priority_id6		= reg180c2a14[23:16];
assign ch_dir_max_bl		= reg180c2a18[31:20];
assign reg_ch_rw_match_mask_cycel_sel		= reg180c2a18[18:16];
assign reg_ch_wr_chg_wait_time		= reg180c2a18[12:8];
assign reg_wr_chg_revert_en		= reg180c2a18[4];
assign total_rw_bl_low_bound_2		= reg180c2a1c[28:16];
assign total_rw_bl_low_bound_w		= reg180c2a20[28:16];
assign total_rw_bl_low_bound_r		= reg180c2a20[12:0];
assign long_bl_thr		= reg180c2a24[21:16];
assign short_rw_ps_bl_thr		= reg180c2a24[12:8];
assign short_rw_bl_thr		= reg180c2a24[7:0];
assign ref_mask_dir		= reg180c2a28[31:30];
assign ddr4_cmd_inorder_en		= reg180c2a28[24];
assign ref_mask_ch		= reg180c2a28[23:20];
assign ref_mask_urg2_ch		= reg180c2a28[16:8];
assign ref_mask_id3_en		= reg180c2a28[7];
assign ref_mask_id2_en		= reg180c2a28[6];
assign ref_mask_id1_en		= reg180c2a28[5];
assign ref_mask_id0_en		= reg180c2a28[4];
assign ch_ahead_en		= reg180c2a28[0];
assign ch_parser_total_bl_max		= reg180c2a2c[25:16];
assign ch_ddr4_balance_cmd_max		= reg180c2a2c[7:4];
assign ch_parser_cmd_max		= reg180c2a2c[3:0];
assign ddr4_balance_bl_thr		= reg180c2a30[21:16];
assign ddr4_db_tracking		= reg180c2a30[2];
assign ddr4_fast_con		= reg180c2a30[1];
assign ddr4_balance_con		= reg180c2a30[0];
assign ch_max_id_bl_thr		= reg180c2a34[25:16];
assign ch_max_id_bl_en		= reg180c2a34[0];
assign dis_tracking_gp0_id		= reg180c2a3c[23:20];
assign dis_tracking_gp1_id		= reg180c2a3c[19:16];
assign dis_tracking_id1		= reg180c2a3c[15:8];
assign dis_tracking_id0		= reg180c2a3c[7:0];
assign ch0_bg_insert_mapping		= reg180c2a60[31:28];
assign ch0_page_insert_mapping		= reg180c2a60[27:24];
assign ch0_bank_free_mapping		= reg180c2a60[23:20];
assign ch0_dir_insert_mapping		= reg180c2a60[19:16];
assign ch0_r2w_dir_insert_mapping		= reg180c2a60[15:12];
assign ch0_acc_trigger_sel		= reg180c2a60[11];
assign ch0_acc_mode		= reg180c2a60[10];
assign ch0_acc_clr_mode		= reg180c2a60[9:8];
assign ch0_urg2_wr_brk_en		= reg180c2a60[7];
assign ch0_urg2_strong_en		= reg180c2a60[4];
assign ch0_oldest_timer_2_en		= reg180c2a60[3];
assign ch0_oldest_timer_en		= reg180c2a60[2];
assign ch0_oldest_cmd_select_en		= reg180c2a60[1];
assign ch0_quota_bw_ini		= reg180c2a64[31:24];
assign ch0_bw_quota_max		= reg180c2a64[15:8];
assign ch0_oldest_time_2		= reg180c2a68[31:20];
assign ch0_oldest_time		= reg180c2a68[19:8];
assign ch0_bw_acc_unit		= reg180c2a68[3:0];
assign ch0_cmd_extend_num		= reg180c2a6c[31:28];
assign ch0_extend_bl_max		= reg180c2a6c[25:20];
assign ch0_ostd_bl_max		= reg180c2a6c[19:8];
assign ch0_ostd_cmd_max		= reg180c2a6c[7:4];
assign ch0_outstand_en		= reg180c2a6c[0];
assign ch0_wr_brk_time		= reg180c2a70[9:0];
assign ch0_wms_bg_insert_mapping		= reg180c2a74[31:28];
assign ch0_wms_page_insert_mapping		= reg180c2a74[27:24];
assign ch0_wms_bank_free_mapping		= reg180c2a74[23:20];
assign ch0_wms_dir_insert_mapping		= reg180c2a74[19:16];
assign ch0_wms_r2w_dir_insert_mapping		= reg180c2a74[15:12];
assign ch0_wmask_insert_mapping		= reg180c2a74[11:8];
assign ch1_bg_insert_mapping		= reg180c2a80[31:28];
assign ch1_page_insert_mapping		= reg180c2a80[27:24];
assign ch1_bank_free_mapping		= reg180c2a80[23:20];
assign ch1_dir_insert_mapping		= reg180c2a80[19:16];
assign ch1_r2w_dir_insert_mapping		= reg180c2a80[15:12];
assign ch1_acc_trigger_sel		= reg180c2a80[11];
assign ch1_acc_mode		= reg180c2a80[10];
assign ch1_acc_clr_mode		= reg180c2a80[9:8];
assign ch1_urg2_wr_brk_en		= reg180c2a80[7];
assign ch1_urg2_strong_en		= reg180c2a80[4];
assign ch1_oldest_timer_2_en		= reg180c2a80[3];
assign ch1_oldest_timer_en		= reg180c2a80[2];
assign ch1_oldest_cmd_select_en		= reg180c2a80[1];
assign ch1_quota_bw_ini		= reg180c2a84[31:24];
assign ch1_bw_quota_max		= reg180c2a84[15:8];
assign ch1_oldest_time_2		= reg180c2a88[31:20];
assign ch1_oldest_time		= reg180c2a88[19:8];
assign ch1_bw_acc_unit		= reg180c2a88[3:0];
assign ch1_cmd_extend_num		= reg180c2a8c[31:28];
assign ch1_extend_bl_max		= reg180c2a8c[25:20];
assign ch1_ostd_bl_max		= reg180c2a8c[19:8];
assign ch1_ostd_cmd_max		= reg180c2a8c[7:4];
assign ch1_outstand_en		= reg180c2a8c[0];
assign ch1_wr_brk_time		= reg180c2a90[9:0];
assign ch1_wms_bg_insert_mapping		= reg180c2a94[31:28];
assign ch1_wms_page_insert_mapping		= reg180c2a94[27:24];
assign ch1_wms_bank_free_mapping		= reg180c2a94[23:20];
assign ch1_wms_dir_insert_mapping		= reg180c2a94[19:16];
assign ch1_wms_r2w_dir_insert_mapping		= reg180c2a94[15:12];
assign ch1_wmask_insert_mapping		= reg180c2a94[11:8];
assign ch2_bg_insert_mapping		= reg180c2aa0[31:28];
assign ch2_page_insert_mapping		= reg180c2aa0[27:24];
assign ch2_bank_free_mapping		= reg180c2aa0[23:20];
assign ch2_dir_insert_mapping		= reg180c2aa0[19:16];
assign ch2_r2w_dir_insert_mapping		= reg180c2aa0[15:12];
assign ch2_acc_trigger_sel		= reg180c2aa0[11];
assign ch2_acc_mode		= reg180c2aa0[10];
assign ch2_acc_clr_mode		= reg180c2aa0[9:8];
assign ch2_urg2_wr_brk_en		= reg180c2aa0[7];
assign ch2_urg2_strong_en		= reg180c2aa0[4];
assign ch2_oldest_timer_2_en		= reg180c2aa0[3];
assign ch2_oldest_timer_en		= reg180c2aa0[2];
assign ch2_oldest_cmd_select_en		= reg180c2aa0[1];
assign ch2_quota_bw_ini		= reg180c2aa4[31:24];
assign ch2_bw_quota_max		= reg180c2aa4[15:8];
assign ch2_oldest_time_2		= reg180c2aa8[31:20];
assign ch2_oldest_time		= reg180c2aa8[19:8];
assign ch2_bw_acc_unit		= reg180c2aa8[3:0];
assign ch2_cmd_extend_num		= reg180c2aac[31:28];
assign ch2_extend_bl_max		= reg180c2aac[25:20];
assign ch2_ostd_bl_max		= reg180c2aac[19:8];
assign ch2_ostd_cmd_max		= reg180c2aac[7:4];
assign ch2_outstand_en		= reg180c2aac[0];
assign ch2_wr_brk_time		= reg180c2ab0[9:0];
assign ch2_wms_bg_insert_mapping		= reg180c2ab4[31:28];
assign ch2_wms_page_insert_mapping		= reg180c2ab4[27:24];
assign ch2_wms_bank_free_mapping		= reg180c2ab4[23:20];
assign ch2_wms_dir_insert_mapping		= reg180c2ab4[19:16];
assign ch2_wms_r2w_dir_insert_mapping		= reg180c2ab4[15:12];
assign ch2_wmask_insert_mapping		= reg180c2ab4[11:8];
assign ch3_bg_insert_mapping		= reg180c2ac0[31:28];
assign ch3_page_insert_mapping		= reg180c2ac0[27:24];
assign ch3_bank_free_mapping		= reg180c2ac0[23:20];
assign ch3_dir_insert_mapping		= reg180c2ac0[19:16];
assign ch3_r2w_dir_insert_mapping		= reg180c2ac0[15:12];
assign ch3_acc_trigger_sel		= reg180c2ac0[11];
assign ch3_acc_mode		= reg180c2ac0[10];
assign ch3_acc_clr_mode		= reg180c2ac0[9:8];
assign ch3_urg2_wr_brk_en		= reg180c2ac0[7];
assign ch3_urg2_strong_en		= reg180c2ac0[4];
assign ch3_oldest_timer_2_en		= reg180c2ac0[3];
assign ch3_oldest_timer_en		= reg180c2ac0[2];
assign ch3_oldest_cmd_select_en		= reg180c2ac0[1];
assign ch3_quota_bw_ini		= reg180c2ac4[31:24];
assign ch3_bw_quota_max		= reg180c2ac4[15:8];
assign ch3_oldest_time_2		= reg180c2ac8[31:20];
assign ch3_oldest_time		= reg180c2ac8[19:8];
assign ch3_bw_acc_unit		= reg180c2ac8[3:0];
assign ch3_cmd_extend_num		= reg180c2acc[31:28];
assign ch3_extend_bl_max		= reg180c2acc[25:20];
assign ch3_ostd_bl_max		= reg180c2acc[19:8];
assign ch3_ostd_cmd_max		= reg180c2acc[7:4];
assign ch3_outstand_en		= reg180c2acc[0];
assign ch3_wr_brk_time		= reg180c2ad0[9:0];
assign ch3_wms_bg_insert_mapping		= reg180c2ad4[31:28];
assign ch3_wms_page_insert_mapping		= reg180c2ad4[27:24];
assign ch3_wms_bank_free_mapping		= reg180c2ad4[23:20];
assign ch3_wms_dir_insert_mapping		= reg180c2ad4[19:16];
assign ch3_wms_r2w_dir_insert_mapping		= reg180c2ad4[15:12];
assign ch3_wmask_insert_mapping		= reg180c2ad4[11:8];
assign ch4_bg_insert_mapping		= reg180c2ae0[31:28];
assign ch4_page_insert_mapping		= reg180c2ae0[27:24];
assign ch4_bank_free_mapping		= reg180c2ae0[23:20];
assign ch4_dir_insert_mapping		= reg180c2ae0[19:16];
assign ch4_r2w_dir_insert_mapping		= reg180c2ae0[15:12];
assign ch4_acc_trigger_sel		= reg180c2ae0[11];
assign ch4_acc_mode		= reg180c2ae0[10];
assign ch4_acc_clr_mode		= reg180c2ae0[9:8];
assign ch4_urg2_wr_brk_en		= reg180c2ae0[7];
assign ch4_urg2_strong_en		= reg180c2ae0[4];
assign ch4_oldest_timer_2_en		= reg180c2ae0[3];
assign ch4_oldest_timer_en		= reg180c2ae0[2];
assign ch4_oldest_cmd_select_en		= reg180c2ae0[1];
assign ch4_quota_bw_ini		= reg180c2ae4[31:24];
assign ch4_bw_quota_max		= reg180c2ae4[15:8];
assign ch4_oldest_time_2		= reg180c2ae8[31:20];
assign ch4_oldest_time		= reg180c2ae8[19:8];
assign ch4_bw_acc_unit		= reg180c2ae8[3:0];
assign ch4_cmd_extend_num		= reg180c2aec[31:28];
assign ch4_extend_bl_max		= reg180c2aec[25:20];
assign ch4_ostd_bl_max		= reg180c2aec[19:8];
assign ch4_ostd_cmd_max		= reg180c2aec[7:4];
assign ch4_outstand_en		= reg180c2aec[0];
assign ch4_wr_brk_time		= reg180c2af0[9:0];
assign ch4_wms_bg_insert_mapping		= reg180c2af4[31:28];
assign ch4_wms_page_insert_mapping		= reg180c2af4[27:24];
assign ch4_wms_bank_free_mapping		= reg180c2af4[23:20];
assign ch4_wms_dir_insert_mapping		= reg180c2af4[19:16];
assign ch4_wms_r2w_dir_insert_mapping		= reg180c2af4[15:12];
assign ch4_wmask_insert_mapping		= reg180c2af4[11:8];
assign ch5_bg_insert_mapping		= reg180c2b00[31:28];
assign ch5_page_insert_mapping		= reg180c2b00[27:24];
assign ch5_bank_free_mapping		= reg180c2b00[23:20];
assign ch5_dir_insert_mapping		= reg180c2b00[19:16];
assign ch5_r2w_dir_insert_mapping		= reg180c2b00[15:12];
assign ch5_acc_trigger_sel		= reg180c2b00[11];
assign ch5_acc_mode		= reg180c2b00[10];
assign ch5_acc_clr_mode		= reg180c2b00[9:8];
assign ch5_urg2_wr_brk_en		= reg180c2b00[7];
assign ch5_urg2_strong_en		= reg180c2b00[4];
assign ch5_oldest_timer_2_en		= reg180c2b00[3];
assign ch5_oldest_timer_en		= reg180c2b00[2];
assign ch5_oldest_cmd_select_en		= reg180c2b00[1];
assign ch5_quota_bw_ini		= reg180c2b04[31:24];
assign ch5_bw_quota_max		= reg180c2b04[15:8];
assign ch5_oldest_time_2		= reg180c2b08[31:20];
assign ch5_oldest_time		= reg180c2b08[19:8];
assign ch5_bw_acc_unit		= reg180c2b08[3:0];
assign ch5_cmd_extend_num		= reg180c2b0c[31:28];
assign ch5_extend_bl_max		= reg180c2b0c[25:20];
assign ch5_ostd_bl_max		= reg180c2b0c[19:8];
assign ch5_ostd_cmd_max		= reg180c2b0c[7:4];
assign ch5_outstand_en		= reg180c2b0c[0];
assign ch5_wr_brk_time		= reg180c2b10[9:0];
assign ch5_wms_bg_insert_mapping		= reg180c2b14[31:28];
assign ch5_wms_page_insert_mapping		= reg180c2b14[27:24];
assign ch5_wms_bank_free_mapping		= reg180c2b14[23:20];
assign ch5_wms_dir_insert_mapping		= reg180c2b14[19:16];
assign ch5_wms_r2w_dir_insert_mapping		= reg180c2b14[15:12];
assign ch5_wmask_insert_mapping		= reg180c2b14[11:8];
assign ch6_bg_insert_mapping		= reg180c2b20[31:28];
assign ch6_page_insert_mapping		= reg180c2b20[27:24];
assign ch6_bank_free_mapping		= reg180c2b20[23:20];
assign ch6_dir_insert_mapping		= reg180c2b20[19:16];
assign ch6_r2w_dir_insert_mapping		= reg180c2b20[15:12];
assign ch6_acc_trigger_sel		= reg180c2b20[11];
assign ch6_acc_mode		= reg180c2b20[10];
assign ch6_acc_clr_mode		= reg180c2b20[9:8];
assign ch6_urg2_wr_brk_en		= reg180c2b20[7];
assign ch6_urg2_strong_en		= reg180c2b20[4];
assign ch6_oldest_timer_2_en		= reg180c2b20[3];
assign ch6_oldest_timer_en		= reg180c2b20[2];
assign ch6_oldest_cmd_select_en		= reg180c2b20[1];
assign ch6_quota_bw_ini		= reg180c2b24[31:24];
assign ch6_bw_quota_max		= reg180c2b24[15:8];
assign ch6_oldest_time_2		= reg180c2b28[31:20];
assign ch6_oldest_time		= reg180c2b28[19:8];
assign ch6_bw_acc_unit		= reg180c2b28[3:0];
assign ch6_cmd_extend_num		= reg180c2b2c[31:28];
assign ch6_extend_bl_max		= reg180c2b2c[25:20];
assign ch6_ostd_bl_max		= reg180c2b2c[19:8];
assign ch6_ostd_cmd_max		= reg180c2b2c[7:4];
assign ch6_outstand_en		= reg180c2b2c[0];
assign ch6_wr_brk_time		= reg180c2b30[9:0];
assign ch6_wms_bg_insert_mapping		= reg180c2b34[31:28];
assign ch6_wms_page_insert_mapping		= reg180c2b34[27:24];
assign ch6_wms_bank_free_mapping		= reg180c2b34[23:20];
assign ch6_wms_dir_insert_mapping		= reg180c2b34[19:16];
assign ch6_wms_r2w_dir_insert_mapping		= reg180c2b34[15:12];
assign ch6_wmask_insert_mapping		= reg180c2b34[11:8];
assign ch7_bg_insert_mapping		= reg180c2b40[31:28];
assign ch7_page_insert_mapping		= reg180c2b40[27:24];
assign ch7_bank_free_mapping		= reg180c2b40[23:20];
assign ch7_dir_insert_mapping		= reg180c2b40[19:16];
assign ch7_r2w_dir_insert_mapping		= reg180c2b40[15:12];
assign ch7_acc_trigger_sel		= reg180c2b40[11];
assign ch7_acc_mode		= reg180c2b40[10];
assign ch7_acc_clr_mode		= reg180c2b40[9:8];
assign ch7_urg2_wr_brk_en		= reg180c2b40[7];
assign ch7_urg2_strong_en		= reg180c2b40[4];
assign ch7_oldest_timer_2_en		= reg180c2b40[3];
assign ch7_oldest_timer_en		= reg180c2b40[2];
assign ch7_oldest_cmd_select_en		= reg180c2b40[1];
assign ch7_quota_bw_ini		= reg180c2b44[31:24];
assign ch7_bw_quota_max		= reg180c2b44[15:8];
assign ch7_oldest_time_2		= reg180c2b48[31:20];
assign ch7_oldest_time		= reg180c2b48[19:8];
assign ch7_bw_acc_unit		= reg180c2b48[3:0];
assign ch7_cmd_extend_num		= reg180c2b4c[31:28];
assign ch7_extend_bl_max		= reg180c2b4c[25:20];
assign ch7_ostd_bl_max		= reg180c2b4c[19:8];
assign ch7_ostd_cmd_max		= reg180c2b4c[7:4];
assign ch7_outstand_en		= reg180c2b4c[0];
assign ch7_wr_brk_time		= reg180c2b50[9:0];
assign ch7_wms_bg_insert_mapping		= reg180c2b54[31:28];
assign ch7_wms_page_insert_mapping		= reg180c2b54[27:24];
assign ch7_wms_bank_free_mapping		= reg180c2b54[23:20];
assign ch7_wms_dir_insert_mapping		= reg180c2b54[19:16];
assign ch7_wms_r2w_dir_insert_mapping		= reg180c2b54[15:12];
assign ch7_wmask_insert_mapping		= reg180c2b54[11:8];
assign ch8_bg_insert_mapping		= reg180c2b60[31:28];
assign ch8_page_insert_mapping		= reg180c2b60[27:24];
assign ch8_bank_free_mapping		= reg180c2b60[23:20];
assign ch8_dir_insert_mapping		= reg180c2b60[19:16];
assign ch8_r2w_dir_insert_mapping		= reg180c2b60[15:12];
assign ch8_acc_trigger_sel		= reg180c2b60[11];
assign ch8_acc_mode		= reg180c2b60[10];
assign ch8_acc_clr_mode		= reg180c2b60[9:8];
assign ch8_urg2_wr_brk_en		= reg180c2b60[7];
assign ch8_urg2_strong_en		= reg180c2b60[4];
assign ch8_oldest_timer_2_en		= reg180c2b60[3];
assign ch8_oldest_timer_en		= reg180c2b60[2];
assign ch8_oldest_cmd_select_en		= reg180c2b60[1];
assign ch8_quota_bw_ini		= reg180c2b64[31:24];
assign ch8_bw_quota_max		= reg180c2b64[15:8];
assign ch8_oldest_time_2		= reg180c2b68[31:20];
assign ch8_oldest_time		= reg180c2b68[19:8];
assign ch8_bw_acc_unit		= reg180c2b68[3:0];
assign ch8_cmd_extend_num		= reg180c2b6c[31:28];
assign ch8_extend_bl_max		= reg180c2b6c[25:20];
assign ch8_ostd_bl_max		= reg180c2b6c[19:8];
assign ch8_ostd_cmd_max		= reg180c2b6c[7:4];
assign ch8_outstand_en		= reg180c2b6c[0];
assign ch8_wr_brk_time		= reg180c2b70[9:0];
assign ch8_wms_bg_insert_mapping		= reg180c2b74[31:28];
assign ch8_wms_page_insert_mapping		= reg180c2b74[27:24];
assign ch8_wms_bank_free_mapping		= reg180c2b74[23:20];
assign ch8_wms_dir_insert_mapping		= reg180c2b74[19:16];
assign ch8_wms_r2w_dir_insert_mapping		= reg180c2b74[15:12];
assign ch8_wmask_insert_mapping		= reg180c2b74[11:8];
assign ch9_bg_insert_mapping		= reg180c2b80[31:28];
assign ch9_page_insert_mapping		= reg180c2b80[27:24];
assign ch9_bank_free_mapping		= reg180c2b80[23:20];
assign ch9_dir_insert_mapping		= reg180c2b80[19:16];
assign ch9_r2w_dir_insert_mapping		= reg180c2b80[15:12];
assign ch9_acc_trigger_sel		= reg180c2b80[11];
assign ch9_acc_mode		= reg180c2b80[10];
assign ch9_acc_clr_mode		= reg180c2b80[9:8];
assign ch9_urg2_wr_brk_en		= reg180c2b80[7];
assign ch9_urg2_strong_en		= reg180c2b80[4];
assign ch9_oldest_timer_2_en		= reg180c2b80[3];
assign ch9_oldest_timer_en		= reg180c2b80[2];
assign ch9_oldest_cmd_select_en		= reg180c2b80[1];
assign ch9_quota_bw_ini		= reg180c2b84[31:24];
assign ch9_bw_quota_max		= reg180c2b84[15:8];
assign ch9_oldest_time_2		= reg180c2b88[31:20];
assign ch9_oldest_time		= reg180c2b88[19:8];
assign ch9_bw_acc_unit		= reg180c2b88[3:0];
assign ch9_cmd_extend_num		= reg180c2b8c[31:28];
assign ch9_extend_bl_max		= reg180c2b8c[25:20];
assign ch9_ostd_bl_max		= reg180c2b8c[19:8];
assign ch9_ostd_cmd_max		= reg180c2b8c[7:4];
assign ch9_outstand_en		= reg180c2b8c[0];
assign ch9_wr_brk_time		= reg180c2b90[9:0];
assign ch9_wms_bg_insert_mapping		= reg180c2b94[31:28];
assign ch9_wms_page_insert_mapping		= reg180c2b94[27:24];
assign ch9_wms_bank_free_mapping		= reg180c2b94[23:20];
assign ch9_wms_dir_insert_mapping		= reg180c2b94[19:16];
assign ch9_wms_r2w_dir_insert_mapping		= reg180c2b94[15:12];
assign ch9_wmask_insert_mapping		= reg180c2b94[11:8];
assign ch10_bg_insert_mapping		= reg180c2ba0[31:28];
assign ch10_page_insert_mapping		= reg180c2ba0[27:24];
assign ch10_bank_free_mapping		= reg180c2ba0[23:20];
assign ch10_dir_insert_mapping		= reg180c2ba0[19:16];
assign ch10_r2w_dir_insert_mapping		= reg180c2ba0[15:12];
assign ch10_acc_trigger_sel		= reg180c2ba0[11];
assign ch10_acc_mode		= reg180c2ba0[10];
assign ch10_acc_clr_mode		= reg180c2ba0[9:8];
assign ch10_urg2_wr_brk_en		= reg180c2ba0[7];
assign ch10_urg2_strong_en		= reg180c2ba0[4];
assign ch10_oldest_timer_2_en		= reg180c2ba0[3];
assign ch10_oldest_timer_en		= reg180c2ba0[2];
assign ch10_oldest_cmd_select_en		= reg180c2ba0[1];
assign ch10_quota_bw_ini		= reg180c2ba4[31:24];
assign ch10_bw_quota_max		= reg180c2ba4[15:8];
assign ch10_oldest_time_2		= reg180c2ba8[31:20];
assign ch10_oldest_time		= reg180c2ba8[19:8];
assign ch10_bw_acc_unit		= reg180c2ba8[3:0];
assign ch10_cmd_extend_num		= reg180c2bac[31:28];
assign ch10_extend_bl_max		= reg180c2bac[25:20];
assign ch10_ostd_bl_max		= reg180c2bac[19:8];
assign ch10_ostd_cmd_max		= reg180c2bac[7:4];
assign ch10_outstand_en		= reg180c2bac[0];
assign ch10_wr_brk_time		= reg180c2bb0[9:0];
assign ch10_wms_bg_insert_mapping		= reg180c2bb4[31:28];
assign ch10_wms_page_insert_mapping		= reg180c2bb4[27:24];
assign ch10_wms_bank_free_mapping		= reg180c2bb4[23:20];
assign ch10_wms_dir_insert_mapping		= reg180c2bb4[19:16];
assign ch10_wms_r2w_dir_insert_mapping		= reg180c2bb4[15:12];
assign ch10_wmask_insert_mapping		= reg180c2bb4[11:8];
assign meas_sram_last_w_num		= reg180c2c00[26:16];
assign meas_rk_ctrl_mc2		= reg180c2c00[9:8];
assign meas_rk_ctrl_mc1		= reg180c2c00[7:6];
assign meas_sram_w_addr_rst		= reg180c2c00[5];
assign meas_sram_one_time		= reg180c2c00[4];
assign meas_sram_mode_ctrl		= reg180c2c00[3:0];
assign meas_sram_r_add_inc		= reg180c2c04[31];
assign meas_sram_r_addr_sync		= reg180c2c04[15];
assign meas_sram_r_addr		= reg180c2c04[10:0];
assign meas_one_shot_mode_en		= reg180c2c08[31];
assign meas_cnt_mode_max_en		= reg180c2c08[30];
assign meas_cnt_mode_avg_en		= reg180c2c08[29];
assign meas_cnt_record_mode		= reg180c2c08[28];
assign meas_timer1_sync		= reg180c2c08[10:9];
assign meas_trig_sel		= reg180c2c08[8];
assign meas_serial_cont		= reg180c2c08[5];
assign meas_mode		= reg180c2c08[4];
assign meas_start		= reg180c2c08[0];
assign meas_timer1		= reg180c2c0c[31:0];
assign meas_cnt1_mask_en		= reg180c2c14[24];
assign meas_cnt1_id		= reg180c2c14[23:16];
assign meas_cnt1_mask_id		= reg180c2c14[15:12];
assign meas_cnt1_id_en		= reg180c2c14[10];
assign meas_cnt1_ddr_num		= reg180c2c14[9:8];
assign meas_cnt2_mask_en		= reg180c2c18[24];
assign meas_cnt2_id		= reg180c2c18[23:16];
assign meas_cnt2_mask_id		= reg180c2c18[15:12];
assign meas_cnt2_id_en		= reg180c2c18[10];
assign meas_cnt2_ddr_num		= reg180c2c18[9:8];
assign meas_cnt2_mode		= reg180c2c18[0];
assign meas_cnt3_mask_en		= reg180c2c1c[24];
assign meas_cnt3_id		= reg180c2c1c[23:16];
assign meas_cnt3_mask_id		= reg180c2c1c[15:12];
assign meas_cnt3_id_en		= reg180c2c1c[10];
assign meas_cnt3_ddr_num		= reg180c2c1c[9:8];
assign meas_cnt3_mode		= reg180c2c1c[0];
assign meas_cnt4_mask_en		= reg180c2c20[24];
assign meas_cnt4_id		= reg180c2c20[23:16];
assign meas_cnt4_mask_id		= reg180c2c20[15:12];
assign meas_cnt4_id_en		= reg180c2c20[10];
assign meas_cnt4_ddr_num		= reg180c2c20[9:8];
assign meas_cnt4_mode		= reg180c2c20[0];
assign meas_en		= reg180c2c44[31];
assign meas_stop		= reg180c2c44[30];
assign meas_sram_clear_en		= reg180c2c44[29];
assign meas_page_addr_thr_en		= reg180c2c44[28];
assign meas_dram_num_sel		= reg180c2c44[27:26];
assign meas_timer_en		= reg180c2c44[25];
assign meas_counting_mode		= reg180c2c44[24];
assign addr_thr_cnt_mode_en		= reg180c2c44[23];
assign meas_mc_sel		= reg180c2c44[22:21];
assign meas_chop_cnt_en		= reg180c2c44[20];
assign meas_wmask_cnt_en		= reg180c2c44[19];
assign meas_page_addr_thr2		= reg180c2c50[19:12];
assign meas_page_addr_thr1		= reg180c2c50[7:0];
assign cnt_mode_irq_thershold		= reg180c2c54[31:0];
assign cnt2_irq_en		= reg180c2c58[3];
assign cnt1_irq_en		= reg180c2c58[2];
assign mes_mem_tra_dc_sel		= reg180c2c5c[31];
assign mes_mem_cmp_id		= reg180c2c5c[23:16];
assign mes_mem_cmp_dir		= reg180c2c5c[9:8];
assign mes_mem_tras_adr		= reg180c2c5c[3];
assign mes_mem_tras_id		= reg180c2c5c[1];
assign mes_mem_tras_en		= reg180c2c5c[0];
assign mes_cmp_addr		= reg180c2c60[31:3];
assign mes_cmp_addr_mask		= reg180c2c64[31:3];
assign eff_sram_testrwm_0		= reg180c2c68[20];
assign eff_sram_testrwm_1		= reg180c2c68[19];
assign eff_bist_mode		= reg180c2c68[18];
assign eff_sram_drf_mode		= reg180c2c68[17];
assign eff_sram_test1		= reg180c2c68[16];
assign eff_sram_drf_resume		= reg180c2c68[15];
assign eff_sram_ls		= reg180c2c68[13];
assign eff_sram_rme		= reg180c2c68[12];
assign eff_sram_rm		= reg180c2c68[11:8];
assign eff_sram_bc1_0		= reg180c2c68[7];
assign eff_sram_bc1_1		= reg180c2c68[6];
assign eff_sram_bc2_0		= reg180c2c68[5];
assign eff_sram_bc2_1		= reg180c2c68[4];
assign eff_sram_test_rnm_0		= reg180c2c68[3];
assign eff_sram_test_rnm_1		= reg180c2c68[2];
assign eff_sram_scan_shift_en		= reg180c2c68[1];
assign eff_mem_speed_mode		= reg180c2c68[0];
assign eff_meas_sram1_config_from_reg_en		= reg180c2c6c[29];
assign eff_meas_sram0_config_from_reg_en		= reg180c2c6c[28];
assign eff_meas_sram1_wtsel		= reg180c2c6c[27:26];
assign eff_meas_sram1_rtsel		= reg180c2c6c[25:24];
assign eff_meas_sram1_mtsel		= reg180c2c6c[23:22];
assign eff_meas_sram0_wtsel		= reg180c2c6c[21:20];
assign eff_meas_sram0_rtsel		= reg180c2c6c[19:18];
assign eff_meas_sram0_mtsel		= reg180c2c6c[17:16];
assign eff_meas_sram1_ls_7		= reg180c2c6c[15];
assign eff_meas_sram1_ls_6		= reg180c2c6c[14];
assign eff_meas_sram1_ls_5		= reg180c2c6c[13];
assign eff_meas_sram1_ls_4		= reg180c2c6c[12];
assign eff_meas_sram1_ls_3		= reg180c2c6c[11];
assign eff_meas_sram1_ls_2		= reg180c2c6c[10];
assign eff_meas_sram1_ls_1		= reg180c2c6c[9];
assign eff_meas_sram1_ls_0		= reg180c2c6c[8];
assign eff_meas_sram0_ls_7		= reg180c2c6c[7];
assign eff_meas_sram0_ls_6		= reg180c2c6c[6];
assign eff_meas_sram0_ls_5		= reg180c2c6c[5];
assign eff_meas_sram0_ls_4		= reg180c2c6c[4];
assign eff_meas_sram0_ls_3		= reg180c2c6c[3];
assign eff_meas_sram0_ls_2		= reg180c2c6c[2];
assign eff_meas_sram0_ls_1		= reg180c2c6c[1];
assign eff_meas_sram0_ls_0		= reg180c2c6c[0];
assign eff_meas_sram1_drf_test_resume		= reg180c2c70[10];
assign eff_meas_sram1_drf_bist_mode		= reg180c2c70[9];
assign eff_meas_sram1_bist_mode		= reg180c2c70[8];
assign eff_meas_sram0_drf_test_resume		= reg180c2c70[2];
assign eff_meas_sram0_drf_bist_mode		= reg180c2c70[1];
assign eff_meas_sram0_bist_mode		= reg180c2c70[0];
assign mes_cmp_addr_upper		= reg180c2c78[0];
assign mes_cmp_addr_mask_upper		= reg180c2c7c[0];
assign mc_fifo_err_int_en		= reg180c2f90[8];
assign int_err_active_en		= reg180c2f90[0];


//Address decode
always@(reg_addr) begin
	case (reg_addr[11:0])
		12'h020: addr_dec =229'h0000000000000000000000000000000000000000000000000000000001;  //==addr_dec[  0]
		12'h028: addr_dec =229'h0000000000000000000000000000000000000000000000000000000002;  //==addr_dec[  1]
		12'h02c: addr_dec =229'h0000000000000000000000000000000000000000000000000000000004;  //==addr_dec[  2]
		12'h030: addr_dec =229'h0000000000000000000000000000000000000000000000000000000008;  //==addr_dec[  3]
		12'h034: addr_dec =229'h0000000000000000000000000000000000000000000000000000000010;  //==addr_dec[  4]
		12'h038: addr_dec =229'h0000000000000000000000000000000000000000000000000000000020;  //==addr_dec[  5]
		12'h03c: addr_dec =229'h0000000000000000000000000000000000000000000000000000000040;  //==addr_dec[  6]
		12'h040: addr_dec =229'h0000000000000000000000000000000000000000000000000000000080;  //==addr_dec[  7]
		12'h044: addr_dec =229'h0000000000000000000000000000000000000000000000000000000100;  //==addr_dec[  8]
		12'h050: addr_dec =229'h0000000000000000000000000000000000000000000000000000000200;  //==addr_dec[  9]
		12'h060: addr_dec =229'h0000000000000000000000000000000000000000000000000000000400;  //==addr_dec[  10]
		12'h064: addr_dec =229'h0000000000000000000000000000000000000000000000000000000800;  //==addr_dec[  11]
		12'h068: addr_dec =229'h0000000000000000000000000000000000000000000000000000001000;  //==addr_dec[  12]
		12'h080: addr_dec =229'h0000000000000000000000000000000000000000000000000000002000;  //==addr_dec[  13]
		12'h088: addr_dec =229'h0000000000000000000000000000000000000000000000000000004000;  //==addr_dec[  14]
		12'h090: addr_dec =229'h0000000000000000000000000000000000000000000000000000008000;  //==addr_dec[  15]
		12'h098: addr_dec =229'h0000000000000000000000000000000000000000000000000000010000;  //==addr_dec[  16]
		12'h0a0: addr_dec =229'h0000000000000000000000000000000000000000000000000000020000;  //==addr_dec[  17]
		12'h0f0: addr_dec =229'h0000000000000000000000000000000000000000000000000000040000;  //==addr_dec[  18]
		12'h100: addr_dec =229'h0000000000000000000000000000000000000000000000000000080000;  //==addr_dec[  19]
		12'h110: addr_dec =229'h0000000000000000000000000000000000000000000000000000100000;  //==addr_dec[  20]
		12'h114: addr_dec =229'h0000000000000000000000000000000000000000000000000000200000;  //==addr_dec[  21]
		12'h118: addr_dec =229'h0000000000000000000000000000000000000000000000000000400000;  //==addr_dec[  22]
		12'h11c: addr_dec =229'h0000000000000000000000000000000000000000000000000000800000;  //==addr_dec[  23]
		12'h120: addr_dec =229'h0000000000000000000000000000000000000000000000000001000000;  //==addr_dec[  24]
		12'h130: addr_dec =229'h0000000000000000000000000000000000000000000000000002000000;  //==addr_dec[  25]
		12'h138: addr_dec =229'h0000000000000000000000000000000000000000000000000004000000;  //==addr_dec[  26]
		12'h140: addr_dec =229'h0000000000000000000000000000000000000000000000000008000000;  //==addr_dec[  27]
		12'h200: addr_dec =229'h0000000000000000000000000000000000000000000000000010000000;  //==addr_dec[  28]
		12'h208: addr_dec =229'h0000000000000000000000000000000000000000000000000020000000;  //==addr_dec[  29]
		12'h210: addr_dec =229'h0000000000000000000000000000000000000000000000000040000000;  //==addr_dec[  30]
		12'h218: addr_dec =229'h0000000000000000000000000000000000000000000000000080000000;  //==addr_dec[  31]
		12'h220: addr_dec =229'h0000000000000000000000000000000000000000000000000100000000;  //==addr_dec[  32]
		12'h228: addr_dec =229'h0000000000000000000000000000000000000000000000000200000000;  //==addr_dec[  33]
		12'h22c: addr_dec =229'h0000000000000000000000000000000000000000000000000400000000;  //==addr_dec[  34]
		12'h230: addr_dec =229'h0000000000000000000000000000000000000000000000000800000000;  //==addr_dec[  35]
		12'h234: addr_dec =229'h0000000000000000000000000000000000000000000000001000000000;  //==addr_dec[  36]
		12'h238: addr_dec =229'h0000000000000000000000000000000000000000000000002000000000;  //==addr_dec[  37]
		12'h240: addr_dec =229'h0000000000000000000000000000000000000000000000004000000000;  //==addr_dec[  38]
		12'h244: addr_dec =229'h0000000000000000000000000000000000000000000000008000000000;  //==addr_dec[  39]
		12'h248: addr_dec =229'h0000000000000000000000000000000000000000000000010000000000;  //==addr_dec[  40]
		12'h2a0: addr_dec =229'h0000000000000000000000000000000000000000000000020000000000;  //==addr_dec[  41]
		12'h2a4: addr_dec =229'h0000000000000000000000000000000000000000000000040000000000;  //==addr_dec[  42]
		12'h2a8: addr_dec =229'h0000000000000000000000000000000000000000000000080000000000;  //==addr_dec[  43]
		12'h2ac: addr_dec =229'h0000000000000000000000000000000000000000000000100000000000;  //==addr_dec[  44]
		12'h300: addr_dec =229'h0000000000000000000000000000000000000000000000200000000000;  //==addr_dec[  45]
		12'h304: addr_dec =229'h0000000000000000000000000000000000000000000000400000000000;  //==addr_dec[  46]
		12'h600: addr_dec =229'h0000000000000000000000000000000000000000000000800000000000;  //==addr_dec[  47]
		12'h608: addr_dec =229'h0000000000000000000000000000000000000000000001000000000000;  //==addr_dec[  48]
		12'h70c: addr_dec =229'h0000000000000000000000000000000000000000000002000000000000;  //==addr_dec[  49]
		12'h710: addr_dec =229'h0000000000000000000000000000000000000000000004000000000000;  //==addr_dec[  50]
		12'h714: addr_dec =229'h0000000000000000000000000000000000000000000008000000000000;  //==addr_dec[  51]
		12'h718: addr_dec =229'h0000000000000000000000000000000000000000000010000000000000;  //==addr_dec[  52]
		12'h71c: addr_dec =229'h0000000000000000000000000000000000000000000020000000000000;  //==addr_dec[  53]
		12'h720: addr_dec =229'h0000000000000000000000000000000000000000000040000000000000;  //==addr_dec[  54]
		12'h724: addr_dec =229'h0000000000000000000000000000000000000000000080000000000000;  //==addr_dec[  55]
		12'h728: addr_dec =229'h0000000000000000000000000000000000000000000100000000000000;  //==addr_dec[  56]
		12'h72c: addr_dec =229'h0000000000000000000000000000000000000000000200000000000000;  //==addr_dec[  57]
		12'h730: addr_dec =229'h0000000000000000000000000000000000000000000400000000000000;  //==addr_dec[  58]
		12'h734: addr_dec =229'h0000000000000000000000000000000000000000000800000000000000;  //==addr_dec[  59]
		12'h738: addr_dec =229'h0000000000000000000000000000000000000000001000000000000000;  //==addr_dec[  60]
		12'h73c: addr_dec =229'h0000000000000000000000000000000000000000002000000000000000;  //==addr_dec[  61]
		12'h740: addr_dec =229'h0000000000000000000000000000000000000000004000000000000000;  //==addr_dec[  62]
		12'h744: addr_dec =229'h0000000000000000000000000000000000000000008000000000000000;  //==addr_dec[  63]
		12'h748: addr_dec =229'h0000000000000000000000000000000000000000010000000000000000;  //==addr_dec[  64]
		12'h74c: addr_dec =229'h0000000000000000000000000000000000000000020000000000000000;  //==addr_dec[  65]
		12'h750: addr_dec =229'h0000000000000000000000000000000000000000040000000000000000;  //==addr_dec[  66]
		12'h754: addr_dec =229'h0000000000000000000000000000000000000000080000000000000000;  //==addr_dec[  67]
		12'h758: addr_dec =229'h0000000000000000000000000000000000000000100000000000000000;  //==addr_dec[  68]
		12'h75c: addr_dec =229'h0000000000000000000000000000000000000000200000000000000000;  //==addr_dec[  69]
		12'h760: addr_dec =229'h0000000000000000000000000000000000000000400000000000000000;  //==addr_dec[  70]
		12'h764: addr_dec =229'h0000000000000000000000000000000000000000800000000000000000;  //==addr_dec[  71]
		12'h768: addr_dec =229'h0000000000000000000000000000000000000001000000000000000000;  //==addr_dec[  72]
		12'h76c: addr_dec =229'h0000000000000000000000000000000000000002000000000000000000;  //==addr_dec[  73]
		12'h770: addr_dec =229'h0000000000000000000000000000000000000004000000000000000000;  //==addr_dec[  74]
		12'h774: addr_dec =229'h0000000000000000000000000000000000000008000000000000000000;  //==addr_dec[  75]
		12'h778: addr_dec =229'h0000000000000000000000000000000000000010000000000000000000;  //==addr_dec[  76]
		12'h77c: addr_dec =229'h0000000000000000000000000000000000000020000000000000000000;  //==addr_dec[  77]
		12'h780: addr_dec =229'h0000000000000000000000000000000000000040000000000000000000;  //==addr_dec[  78]
		12'h784: addr_dec =229'h0000000000000000000000000000000000000080000000000000000000;  //==addr_dec[  79]
		12'h788: addr_dec =229'h0000000000000000000000000000000000000100000000000000000000;  //==addr_dec[  80]
		12'h78c: addr_dec =229'h0000000000000000000000000000000000000200000000000000000000;  //==addr_dec[  81]
		12'h800: addr_dec =229'h0000000000000000000000000000000000000400000000000000000000;  //==addr_dec[  82]
		12'h804: addr_dec =229'h0000000000000000000000000000000000000800000000000000000000;  //==addr_dec[  83]
		12'h808: addr_dec =229'h0000000000000000000000000000000000001000000000000000000000;  //==addr_dec[  84]
		12'h80c: addr_dec =229'h0000000000000000000000000000000000002000000000000000000000;  //==addr_dec[  85]
		12'h810: addr_dec =229'h0000000000000000000000000000000000004000000000000000000000;  //==addr_dec[  86]
		12'h814: addr_dec =229'h0000000000000000000000000000000000008000000000000000000000;  //==addr_dec[  87]
		12'h818: addr_dec =229'h0000000000000000000000000000000000010000000000000000000000;  //==addr_dec[  88]
		12'h81c: addr_dec =229'h0000000000000000000000000000000000020000000000000000000000;  //==addr_dec[  89]
		12'h820: addr_dec =229'h0000000000000000000000000000000000040000000000000000000000;  //==addr_dec[  90]
		12'h824: addr_dec =229'h0000000000000000000000000000000000080000000000000000000000;  //==addr_dec[  91]
		12'h828: addr_dec =229'h0000000000000000000000000000000000100000000000000000000000;  //==addr_dec[  92]
		12'h840: addr_dec =229'h0000000000000000000000000000000000200000000000000000000000;  //==addr_dec[  93]
		12'h844: addr_dec =229'h0000000000000000000000000000000000400000000000000000000000;  //==addr_dec[  94]
		12'h848: addr_dec =229'h0000000000000000000000000000000000800000000000000000000000;  //==addr_dec[  95]
		12'h84c: addr_dec =229'h0000000000000000000000000000000001000000000000000000000000;  //==addr_dec[  96]
		12'h850: addr_dec =229'h0000000000000000000000000000000002000000000000000000000000;  //==addr_dec[  97]
		12'h854: addr_dec =229'h0000000000000000000000000000000004000000000000000000000000;  //==addr_dec[  98]
		12'h858: addr_dec =229'h0000000000000000000000000000000008000000000000000000000000;  //==addr_dec[  99]
		12'h85c: addr_dec =229'h0000000000000000000000000000000010000000000000000000000000;  //==addr_dec[  100]
		12'h860: addr_dec =229'h0000000000000000000000000000000020000000000000000000000000;  //==addr_dec[  101]
		12'h864: addr_dec =229'h0000000000000000000000000000000040000000000000000000000000;  //==addr_dec[  102]
		12'h868: addr_dec =229'h0000000000000000000000000000000080000000000000000000000000;  //==addr_dec[  103]
		12'h880: addr_dec =229'h0000000000000000000000000000000100000000000000000000000000;  //==addr_dec[  104]
		12'h884: addr_dec =229'h0000000000000000000000000000000200000000000000000000000000;  //==addr_dec[  105]
		12'h888: addr_dec =229'h0000000000000000000000000000000400000000000000000000000000;  //==addr_dec[  106]
		12'h88c: addr_dec =229'h0000000000000000000000000000000800000000000000000000000000;  //==addr_dec[  107]
		12'h890: addr_dec =229'h0000000000000000000000000000001000000000000000000000000000;  //==addr_dec[  108]
		12'h894: addr_dec =229'h0000000000000000000000000000002000000000000000000000000000;  //==addr_dec[  109]
		12'h898: addr_dec =229'h0000000000000000000000000000004000000000000000000000000000;  //==addr_dec[  110]
		12'h89c: addr_dec =229'h0000000000000000000000000000008000000000000000000000000000;  //==addr_dec[  111]
		12'h8a0: addr_dec =229'h0000000000000000000000000000010000000000000000000000000000;  //==addr_dec[  112]
		12'h8a4: addr_dec =229'h0000000000000000000000000000020000000000000000000000000000;  //==addr_dec[  113]
		12'h8a8: addr_dec =229'h0000000000000000000000000000040000000000000000000000000000;  //==addr_dec[  114]
		12'ha00: addr_dec =229'h0000000000000000000000000000080000000000000000000000000000;  //==addr_dec[  115]
		12'ha04: addr_dec =229'h0000000000000000000000000000100000000000000000000000000000;  //==addr_dec[  116]
		12'ha10: addr_dec =229'h0000000000000000000000000000200000000000000000000000000000;  //==addr_dec[  117]
		12'ha14: addr_dec =229'h0000000000000000000000000000400000000000000000000000000000;  //==addr_dec[  118]
		12'ha18: addr_dec =229'h0000000000000000000000000000800000000000000000000000000000;  //==addr_dec[  119]
		12'ha1c: addr_dec =229'h0000000000000000000000000001000000000000000000000000000000;  //==addr_dec[  120]
		12'ha20: addr_dec =229'h0000000000000000000000000002000000000000000000000000000000;  //==addr_dec[  121]
		12'ha24: addr_dec =229'h0000000000000000000000000004000000000000000000000000000000;  //==addr_dec[  122]
		12'ha28: addr_dec =229'h0000000000000000000000000008000000000000000000000000000000;  //==addr_dec[  123]
		12'ha2c: addr_dec =229'h0000000000000000000000000010000000000000000000000000000000;  //==addr_dec[  124]
		12'ha30: addr_dec =229'h0000000000000000000000000020000000000000000000000000000000;  //==addr_dec[  125]
		12'ha34: addr_dec =229'h0000000000000000000000000040000000000000000000000000000000;  //==addr_dec[  126]
		12'ha3c: addr_dec =229'h0000000000000000000000000080000000000000000000000000000000;  //==addr_dec[  127]
		12'ha60: addr_dec =229'h0000000000000000000000000100000000000000000000000000000000;  //==addr_dec[  128]
		12'ha64: addr_dec =229'h0000000000000000000000000200000000000000000000000000000000;  //==addr_dec[  129]
		12'ha68: addr_dec =229'h0000000000000000000000000400000000000000000000000000000000;  //==addr_dec[  130]
		12'ha6c: addr_dec =229'h0000000000000000000000000800000000000000000000000000000000;  //==addr_dec[  131]
		12'ha70: addr_dec =229'h0000000000000000000000001000000000000000000000000000000000;  //==addr_dec[  132]
		12'ha74: addr_dec =229'h0000000000000000000000002000000000000000000000000000000000;  //==addr_dec[  133]
		12'ha80: addr_dec =229'h0000000000000000000000004000000000000000000000000000000000;  //==addr_dec[  134]
		12'ha84: addr_dec =229'h0000000000000000000000008000000000000000000000000000000000;  //==addr_dec[  135]
		12'ha88: addr_dec =229'h0000000000000000000000010000000000000000000000000000000000;  //==addr_dec[  136]
		12'ha8c: addr_dec =229'h0000000000000000000000020000000000000000000000000000000000;  //==addr_dec[  137]
		12'ha90: addr_dec =229'h0000000000000000000000040000000000000000000000000000000000;  //==addr_dec[  138]
		12'ha94: addr_dec =229'h0000000000000000000000080000000000000000000000000000000000;  //==addr_dec[  139]
		12'haa0: addr_dec =229'h0000000000000000000000100000000000000000000000000000000000;  //==addr_dec[  140]
		12'haa4: addr_dec =229'h0000000000000000000000200000000000000000000000000000000000;  //==addr_dec[  141]
		12'haa8: addr_dec =229'h0000000000000000000000400000000000000000000000000000000000;  //==addr_dec[  142]
		12'haac: addr_dec =229'h0000000000000000000000800000000000000000000000000000000000;  //==addr_dec[  143]
		12'hab0: addr_dec =229'h0000000000000000000001000000000000000000000000000000000000;  //==addr_dec[  144]
		12'hab4: addr_dec =229'h0000000000000000000002000000000000000000000000000000000000;  //==addr_dec[  145]
		12'hac0: addr_dec =229'h0000000000000000000004000000000000000000000000000000000000;  //==addr_dec[  146]
		12'hac4: addr_dec =229'h0000000000000000000008000000000000000000000000000000000000;  //==addr_dec[  147]
		12'hac8: addr_dec =229'h0000000000000000000010000000000000000000000000000000000000;  //==addr_dec[  148]
		12'hacc: addr_dec =229'h0000000000000000000020000000000000000000000000000000000000;  //==addr_dec[  149]
		12'had0: addr_dec =229'h0000000000000000000040000000000000000000000000000000000000;  //==addr_dec[  150]
		12'had4: addr_dec =229'h0000000000000000000080000000000000000000000000000000000000;  //==addr_dec[  151]
		12'hae0: addr_dec =229'h0000000000000000000100000000000000000000000000000000000000;  //==addr_dec[  152]
		12'hae4: addr_dec =229'h0000000000000000000200000000000000000000000000000000000000;  //==addr_dec[  153]
		12'hae8: addr_dec =229'h0000000000000000000400000000000000000000000000000000000000;  //==addr_dec[  154]
		12'haec: addr_dec =229'h0000000000000000000800000000000000000000000000000000000000;  //==addr_dec[  155]
		12'haf0: addr_dec =229'h0000000000000000001000000000000000000000000000000000000000;  //==addr_dec[  156]
		12'haf4: addr_dec =229'h0000000000000000002000000000000000000000000000000000000000;  //==addr_dec[  157]
		12'hb00: addr_dec =229'h0000000000000000004000000000000000000000000000000000000000;  //==addr_dec[  158]
		12'hb04: addr_dec =229'h0000000000000000008000000000000000000000000000000000000000;  //==addr_dec[  159]
		12'hb08: addr_dec =229'h0000000000000000010000000000000000000000000000000000000000;  //==addr_dec[  160]
		12'hb0c: addr_dec =229'h0000000000000000020000000000000000000000000000000000000000;  //==addr_dec[  161]
		12'hb10: addr_dec =229'h0000000000000000040000000000000000000000000000000000000000;  //==addr_dec[  162]
		12'hb14: addr_dec =229'h0000000000000000080000000000000000000000000000000000000000;  //==addr_dec[  163]
		12'hb20: addr_dec =229'h0000000000000000100000000000000000000000000000000000000000;  //==addr_dec[  164]
		12'hb24: addr_dec =229'h0000000000000000200000000000000000000000000000000000000000;  //==addr_dec[  165]
		12'hb28: addr_dec =229'h0000000000000000400000000000000000000000000000000000000000;  //==addr_dec[  166]
		12'hb2c: addr_dec =229'h0000000000000000800000000000000000000000000000000000000000;  //==addr_dec[  167]
		12'hb30: addr_dec =229'h0000000000000001000000000000000000000000000000000000000000;  //==addr_dec[  168]
		12'hb34: addr_dec =229'h0000000000000002000000000000000000000000000000000000000000;  //==addr_dec[  169]
		12'hb40: addr_dec =229'h0000000000000004000000000000000000000000000000000000000000;  //==addr_dec[  170]
		12'hb44: addr_dec =229'h0000000000000008000000000000000000000000000000000000000000;  //==addr_dec[  171]
		12'hb48: addr_dec =229'h0000000000000010000000000000000000000000000000000000000000;  //==addr_dec[  172]
		12'hb4c: addr_dec =229'h0000000000000020000000000000000000000000000000000000000000;  //==addr_dec[  173]
		12'hb50: addr_dec =229'h0000000000000040000000000000000000000000000000000000000000;  //==addr_dec[  174]
		12'hb54: addr_dec =229'h0000000000000080000000000000000000000000000000000000000000;  //==addr_dec[  175]
		12'hb60: addr_dec =229'h0000000000000100000000000000000000000000000000000000000000;  //==addr_dec[  176]
		12'hb64: addr_dec =229'h0000000000000200000000000000000000000000000000000000000000;  //==addr_dec[  177]
		12'hb68: addr_dec =229'h0000000000000400000000000000000000000000000000000000000000;  //==addr_dec[  178]
		12'hb6c: addr_dec =229'h0000000000000800000000000000000000000000000000000000000000;  //==addr_dec[  179]
		12'hb70: addr_dec =229'h0000000000001000000000000000000000000000000000000000000000;  //==addr_dec[  180]
		12'hb74: addr_dec =229'h0000000000002000000000000000000000000000000000000000000000;  //==addr_dec[  181]
		12'hb80: addr_dec =229'h0000000000004000000000000000000000000000000000000000000000;  //==addr_dec[  182]
		12'hb84: addr_dec =229'h0000000000008000000000000000000000000000000000000000000000;  //==addr_dec[  183]
		12'hb88: addr_dec =229'h0000000000010000000000000000000000000000000000000000000000;  //==addr_dec[  184]
		12'hb8c: addr_dec =229'h0000000000020000000000000000000000000000000000000000000000;  //==addr_dec[  185]
		12'hb90: addr_dec =229'h0000000000040000000000000000000000000000000000000000000000;  //==addr_dec[  186]
		12'hb94: addr_dec =229'h0000000000080000000000000000000000000000000000000000000000;  //==addr_dec[  187]
		12'hba0: addr_dec =229'h0000000000100000000000000000000000000000000000000000000000;  //==addr_dec[  188]
		12'hba4: addr_dec =229'h0000000000200000000000000000000000000000000000000000000000;  //==addr_dec[  189]
		12'hba8: addr_dec =229'h0000000000400000000000000000000000000000000000000000000000;  //==addr_dec[  190]
		12'hbac: addr_dec =229'h0000000000800000000000000000000000000000000000000000000000;  //==addr_dec[  191]
		12'hbb0: addr_dec =229'h0000000001000000000000000000000000000000000000000000000000;  //==addr_dec[  192]
		12'hbb4: addr_dec =229'h0000000002000000000000000000000000000000000000000000000000;  //==addr_dec[  193]
		12'hc00: addr_dec =229'h0000000004000000000000000000000000000000000000000000000000;  //==addr_dec[  194]
		12'hc04: addr_dec =229'h0000000008000000000000000000000000000000000000000000000000;  //==addr_dec[  195]
		12'hc08: addr_dec =229'h0000000010000000000000000000000000000000000000000000000000;  //==addr_dec[  196]
		12'hc0c: addr_dec =229'h0000000020000000000000000000000000000000000000000000000000;  //==addr_dec[  197]
		12'hc10: addr_dec =229'h0000000040000000000000000000000000000000000000000000000000;  //==addr_dec[  198]
		12'hc14: addr_dec =229'h0000000080000000000000000000000000000000000000000000000000;  //==addr_dec[  199]
		12'hc18: addr_dec =229'h0000000100000000000000000000000000000000000000000000000000;  //==addr_dec[  200]
		12'hc1c: addr_dec =229'h0000000200000000000000000000000000000000000000000000000000;  //==addr_dec[  201]
		12'hc20: addr_dec =229'h0000000400000000000000000000000000000000000000000000000000;  //==addr_dec[  202]
		12'hc24: addr_dec =229'h0000000800000000000000000000000000000000000000000000000000;  //==addr_dec[  203]
		12'hc28: addr_dec =229'h0000001000000000000000000000000000000000000000000000000000;  //==addr_dec[  204]
		12'hc2c: addr_dec =229'h0000002000000000000000000000000000000000000000000000000000;  //==addr_dec[  205]
		12'hc30: addr_dec =229'h0000004000000000000000000000000000000000000000000000000000;  //==addr_dec[  206]
		12'hc34: addr_dec =229'h0000008000000000000000000000000000000000000000000000000000;  //==addr_dec[  207]
		12'hc38: addr_dec =229'h0000010000000000000000000000000000000000000000000000000000;  //==addr_dec[  208]
		12'hc3c: addr_dec =229'h0000020000000000000000000000000000000000000000000000000000;  //==addr_dec[  209]
		12'hc40: addr_dec =229'h0000040000000000000000000000000000000000000000000000000000;  //==addr_dec[  210]
		12'hc44: addr_dec =229'h0000080000000000000000000000000000000000000000000000000000;  //==addr_dec[  211]
		12'hc48: addr_dec =229'h0000100000000000000000000000000000000000000000000000000000;  //==addr_dec[  212]
		12'hc4c: addr_dec =229'h0000200000000000000000000000000000000000000000000000000000;  //==addr_dec[  213]
		12'hc50: addr_dec =229'h0000400000000000000000000000000000000000000000000000000000;  //==addr_dec[  214]
		12'hc54: addr_dec =229'h0000800000000000000000000000000000000000000000000000000000;  //==addr_dec[  215]
		12'hc58: addr_dec =229'h0001000000000000000000000000000000000000000000000000000000;  //==addr_dec[  216]
		12'hc5c: addr_dec =229'h0002000000000000000000000000000000000000000000000000000000;  //==addr_dec[  217]
		12'hc60: addr_dec =229'h0004000000000000000000000000000000000000000000000000000000;  //==addr_dec[  218]
		12'hc64: addr_dec =229'h0008000000000000000000000000000000000000000000000000000000;  //==addr_dec[  219]
		12'hc68: addr_dec =229'h0010000000000000000000000000000000000000000000000000000000;  //==addr_dec[  220]
		12'hc6c: addr_dec =229'h0020000000000000000000000000000000000000000000000000000000;  //==addr_dec[  221]
		12'hc70: addr_dec =229'h0040000000000000000000000000000000000000000000000000000000;  //==addr_dec[  222]
		12'hc74: addr_dec =229'h0080000000000000000000000000000000000000000000000000000000;  //==addr_dec[  223]
		12'hc78: addr_dec =229'h0100000000000000000000000000000000000000000000000000000000;  //==addr_dec[  224]
		12'hc7c: addr_dec =229'h0200000000000000000000000000000000000000000000000000000000;  //==addr_dec[  225]
		12'hf80: addr_dec =229'h0400000000000000000000000000000000000000000000000000000000;  //==addr_dec[  226]
		12'hf90: addr_dec =229'h0800000000000000000000000000000000000000000000000000000000;  //==addr_dec[  227]
		12'hf94: addr_dec =229'h1000000000000000000000000000000000000000000000000000000000;  //==addr_dec[  228]
         default  :  addr_dec =229'h0000000000000000000000000000000000000000000000000000000000;
    endcase
end

assign write_en =  addr_dec & {229{write_reg}};
assign addr_hit =  (| addr_dec);





//============== Sequential  procedure ==============//
//============== Rport, Wport ==============//
assign mc_mes_client_1_rprt_en = addr_dec[212] & read_reg;
assign mc_mes_client_2_rprt_en = addr_dec[213] & read_reg;
//------------Wclr_out registered---------------------
wire dbe_err_flag1_wclr_out_pre;
wire dbe_err_flag0_wclr_out_pre;
wire fmtr_unknown_cmd_wclr_out_pre;
wire rk1_wr_chop_no_mask_wclr_out_pre;
wire rk1_active_ddr_num_mismatch_wclr_out_pre;
wire rk0_wr_chop_no_mask_wclr_out_pre;
wire rk0_active_ddr_num_mismatch_wclr_out_pre;
wire cnt2_irq_status_wclr_out_pre;
wire cnt1_irq_status_wclr_out_pre;
wire rk1_err_pbk_wclr_out_pre;
wire rk0_err_pbk_wclr_out_pre;
wire rk1_err_active_wclr_out_pre;
wire rk0_err_active_wclr_out_pre;
assign dbe_err_flag1_wclr_out_pre = write_en[52] &  write_data[2];
assign dbe_err_flag0_wclr_out_pre = write_en[52] &  write_data[1];
assign fmtr_unknown_cmd_wclr_out_pre = write_en[52] &  write_data[0];
assign rk1_wr_chop_no_mask_wclr_out_pre = write_en[56] &  write_data[3];
assign rk1_active_ddr_num_mismatch_wclr_out_pre = write_en[56] &  write_data[2];
assign rk0_wr_chop_no_mask_wclr_out_pre = write_en[56] &  write_data[1];
assign rk0_active_ddr_num_mismatch_wclr_out_pre = write_en[56] &  write_data[0];
assign cnt2_irq_status_wclr_out_pre = write_en[216] &  write_data[1];
assign cnt1_irq_status_wclr_out_pre = write_en[216] &  write_data[0];
assign rk1_err_pbk_wclr_out_pre = write_en[228] &  write_data[3];
assign rk0_err_pbk_wclr_out_pre = write_en[228] &  write_data[2];
assign rk1_err_active_wclr_out_pre = write_en[228] &  write_data[1];
assign rk0_err_active_wclr_out_pre = write_en[228] &  write_data[0];
//delay 1 cycle for register 
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        begin
	reg180c2718_wclr_out[2] <= 1'h0;
	reg180c2718_wclr_out[1] <= 1'h0;
	reg180c2718_wclr_out[0] <= 1'h0;
        end
    else
        begin
	reg180c2718_wclr_out[2] <= dbe_err_flag1_wclr_out_pre;
	reg180c2718_wclr_out[1] <= dbe_err_flag0_wclr_out_pre;
	reg180c2718_wclr_out[0] <= fmtr_unknown_cmd_wclr_out_pre;
        end
end
//delay 1 cycle for register 
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        begin
	reg180c2728_wclr_out[3] <= 1'h0;
	reg180c2728_wclr_out[2] <= 1'h0;
	reg180c2728_wclr_out[1] <= 1'h0;
	reg180c2728_wclr_out[0] <= 1'h0;
        end
    else
        begin
	reg180c2728_wclr_out[3] <= rk1_wr_chop_no_mask_wclr_out_pre;
	reg180c2728_wclr_out[2] <= rk1_active_ddr_num_mismatch_wclr_out_pre;
	reg180c2728_wclr_out[1] <= rk0_wr_chop_no_mask_wclr_out_pre;
	reg180c2728_wclr_out[0] <= rk0_active_ddr_num_mismatch_wclr_out_pre;
        end
end
//delay 1 cycle for register 
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        begin
	reg180c2c58_wclr_out[1] <= 1'h0;
	reg180c2c58_wclr_out[0] <= 1'h0;
        end
    else
        begin
	reg180c2c58_wclr_out[1] <= cnt2_irq_status_wclr_out_pre;
	reg180c2c58_wclr_out[0] <= cnt1_irq_status_wclr_out_pre;
        end
end
//delay 1 cycle for register 
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        begin
	reg180c2f94_wclr_out[3] <= 1'h0;
	reg180c2f94_wclr_out[2] <= 1'h0;
	reg180c2f94_wclr_out[1] <= 1'h0;
	reg180c2f94_wclr_out[0] <= 1'h0;
        end
    else
        begin
	reg180c2f94_wclr_out[3] <= rk1_err_pbk_wclr_out_pre;
	reg180c2f94_wclr_out[2] <= rk0_err_pbk_wclr_out_pre;
	reg180c2f94_wclr_out[1] <= rk1_err_active_wclr_out_pre;
	reg180c2f94_wclr_out[0] <= rk0_err_active_wclr_out_pre;
        end
end

//========================================================//
//==================== write procedure ===================//
//========================================================//
//addr = 0x180c2020
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2020[24] <= 1'h0;
         reg180c2020[6] <= 1'h1;
         reg180c2020[5] <= 1'h0;
         reg180c2020[4] <= 1'h0;
         reg180c2020[1] <= 1'h0;
         reg180c2020[0] <= 1'h0;
       end
     else begin
       if (write_en[0])
         begin
           reg180c2020[24] <= write_data[24];
           reg180c2020[6] <= write_data[6];
           reg180c2020[5] <= write_data[5];
           reg180c2020[4] <= write_data[4];
           reg180c2020[1] <= write_data[1];
           reg180c2020[0] <= write_data[0];
         end
       else
         begin
           reg180c2020[24] <= reg180c2020[24];
           reg180c2020[6] <= reg180c2020[6];
           reg180c2020[5] <= reg180c2020[5];
           reg180c2020[4] <= reg180c2020[4];
           reg180c2020[1] <= reg180c2020[1];
           reg180c2020[0] <= reg180c2020[0];
         end
     end
  end

//addr = 0x180c2028
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2028[31:28] <= 4'h0;
         reg180c2028[27:24] <= 4'h0;
         reg180c2028[23:20] <= 4'h0;
         reg180c2028[19] <= 1'h0;
         reg180c2028[16] <= 1'h0;
         reg180c2028[9:8] <= 2'h0;
         reg180c2028[1] <= 1'h0;
         reg180c2028[0] <= 1'h0;
       end
     else begin
       if (write_en[1])
         begin
           reg180c2028[31:28] <= write_data[31:28];
           reg180c2028[27:24] <= write_data[27:24];
           reg180c2028[23:20] <= write_data[23:20];
           reg180c2028[19] <= write_data[19];
           reg180c2028[16] <= write_data[16];
           reg180c2028[9:8] <= write_data[9:8];
           reg180c2028[1] <= write_data[1];
           reg180c2028[0] <= write_data[0];
         end
       else
         begin
           reg180c2028[31:28] <= reg180c2028[31:28];
           reg180c2028[27:24] <= reg180c2028[27:24];
           reg180c2028[23:20] <= reg180c2028[23:20];
           reg180c2028[19] <= reg180c2028[19];
           reg180c2028[16] <= reg180c2028[16];
           reg180c2028[9:8] <= reg180c2028[9:8];
           reg180c2028[1] <= reg180c2028[1];
           reg180c2028[0] <= reg180c2028[0];
         end
     end
  end

//addr = 0x180c202c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c202c[0] <= 1'h0;
       end
     else begin
       if (write_en[2])
         begin
           reg180c202c[0] <= write_data[0];
         end
       else
         begin
           reg180c202c[0] <= reg180c202c[0];
         end
     end
  end

//addr = 0x180c2030
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2030[28] <= 1'h0;
         reg180c2030[27] <= 1'h0;
         reg180c2030[2] <= 1'h0;
         reg180c2030[1:0] <= 2'h0;
       end
     else begin
       if (write_en[3])
         begin
           reg180c2030[28] <= write_data[28];
           reg180c2030[27] <= write_data[27];
           reg180c2030[2] <= write_data[2];
           reg180c2030[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2030[28] <= reg180c2030[28];
           reg180c2030[27] <= reg180c2030[27];
           reg180c2030[2] <= reg180c2030[2];
           reg180c2030[1:0] <= reg180c2030[1:0];
         end
     end
  end

//addr = 0x180c2034
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2034[15:12] <= 4'h0;
         reg180c2034[2] <= 1'h0;
         reg180c2034[1:0] <= 2'h0;
       end
     else begin
       if (write_en[4])
         begin
           reg180c2034[15:12] <= write_data[15:12];
           reg180c2034[2] <= write_data[2];
           reg180c2034[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2034[15:12] <= reg180c2034[15:12];
           reg180c2034[2] <= reg180c2034[2];
           reg180c2034[1:0] <= reg180c2034[1:0];
         end
     end
  end

always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2034[17] <= 1'h0;
         reg180c2034[16] <= 1'h0;
       end
     else begin
       if (write_en[4])
         begin
           reg180c2034[17] <= write_data[17];
           reg180c2034[16] <= write_data[16];
         end
       else
         begin
             reg180c2034[17] <= update_ddrx_rst ? n_ddrx_rst : reg180c2034[17];
             reg180c2034[16] <= update_ddrx_cke ? n_ddrx_cke : reg180c2034[16];
         end
     end
  end

//addr = 0x180c2038
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2038[0] <= 1'h0;
       end
     else begin
       if (write_en[5])
         begin
           reg180c2038[0] <= write_data[0];
         end
       else
         begin
           reg180c2038[0] <= reg180c2038[0];
         end
     end
  end

//addr = 0x180c203c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c203c[9:8] <= 2'h0;
         reg180c203c[7:5] <= 3'h0;
         reg180c203c[4] <= 1'h0;
         reg180c203c[1] <= 1'h0;
         reg180c203c[0] <= 1'h0;
       end
     else begin
       if (write_en[6])
         begin
           reg180c203c[9:8] <= write_data[9:8];
           reg180c203c[7:5] <= write_data[7:5];
           reg180c203c[4] <= write_data[4];
           reg180c203c[1] <= write_data[1];
           reg180c203c[0] <= write_data[0];
         end
       else
         begin
           reg180c203c[9:8] <= reg180c203c[9:8];
           reg180c203c[7:5] <= reg180c203c[7:5];
           reg180c203c[4] <= reg180c203c[4];
           reg180c203c[1] <= reg180c203c[1];
           reg180c203c[0] <= reg180c203c[0];
         end
     end
  end

//addr = 0x180c2040
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2040[27:24] <= 4'h0;
         reg180c2040[20] <= 1'h0;
         reg180c2040[19] <= 1'h0;
         reg180c2040[18] <= 1'h0;
         reg180c2040[17] <= 1'h0;
         reg180c2040[16] <= 1'h0;
         reg180c2040[15:8] <= 8'h0;
         reg180c2040[7:0] <= 8'h0;
       end
     else begin
       if (write_en[7])
         begin
           reg180c2040[27:24] <= write_data[27:24];
           reg180c2040[20] <= write_data[20];
           reg180c2040[19] <= write_data[19];
           reg180c2040[18] <= write_data[18];
           reg180c2040[17] <= write_data[17];
           reg180c2040[16] <= write_data[16];
           reg180c2040[15:8] <= write_data[15:8];
           reg180c2040[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2040[27:24] <= reg180c2040[27:24];
           reg180c2040[20] <= reg180c2040[20];
           reg180c2040[19] <= reg180c2040[19];
           reg180c2040[18] <= reg180c2040[18];
           reg180c2040[17] <= reg180c2040[17];
           reg180c2040[16] <= reg180c2040[16];
           reg180c2040[15:8] <= reg180c2040[15:8];
           reg180c2040[7:0] <= reg180c2040[7:0];
         end
     end
  end

//addr = 0x180c2044
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2044[26:24] <= 3'h0;
         reg180c2044[17] <= 1'h0;
         reg180c2044[16] <= 1'h0;
         reg180c2044[13:12] <= 2'h3;
         reg180c2044[9:8] <= 2'h2;
         reg180c2044[5:4] <= 2'h1;
         reg180c2044[1:0] <= 2'h0;
       end
     else begin
       if (write_en[8])
         begin
           reg180c2044[26:24] <= write_data[26:24];
           reg180c2044[17] <= write_data[17];
           reg180c2044[16] <= write_data[16];
           reg180c2044[13:12] <= write_data[13:12];
           reg180c2044[9:8] <= write_data[9:8];
           reg180c2044[5:4] <= write_data[5:4];
           reg180c2044[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2044[26:24] <= reg180c2044[26:24];
           reg180c2044[17] <= reg180c2044[17];
           reg180c2044[16] <= reg180c2044[16];
           reg180c2044[13:12] <= reg180c2044[13:12];
           reg180c2044[9:8] <= reg180c2044[9:8];
           reg180c2044[5:4] <= reg180c2044[5:4];
           reg180c2044[1:0] <= reg180c2044[1:0];
         end
     end
  end

//addr = 0x180c2050
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2050[10:0] <= 11'h0;
       end
     else begin
       if (write_en[9])
         begin
           reg180c2050[10:0] <= write_data[10:0];
         end
       else
         begin
           reg180c2050[10:0] <= reg180c2050[10:0];
         end
     end
  end

//addr = 0x180c2060
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2060[31:28] <= 4'h7;
         reg180c2060[23] <= 1'h0;
         reg180c2060[17] <= 1'h0;
         reg180c2060[16] <= 1'h0;
         reg180c2060[10:8] <= 3'h0;
         reg180c2060[2:0] <= 3'h0;
       end
     else begin
       if (write_en[10])
         begin
           reg180c2060[31:28] <= write_data[31:28];
           reg180c2060[23] <= write_data[23];
           reg180c2060[17] <= write_data[17];
           reg180c2060[16] <= write_data[16];
           reg180c2060[10:8] <= write_data[10:8];
           reg180c2060[2:0] <= write_data[2:0];
         end
       else
         begin
           reg180c2060[31:28] <= reg180c2060[31:28];
           reg180c2060[23] <= reg180c2060[23];
           reg180c2060[17] <= reg180c2060[17];
           reg180c2060[16] <= reg180c2060[16];
           reg180c2060[10:8] <= reg180c2060[10:8];
           reg180c2060[2:0] <= reg180c2060[2:0];
         end
     end
  end

//addr = 0x180c2064
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2064[31:24] <= 8'h0;
         reg180c2064[23] <= 1'h0;
         reg180c2064[21] <= 1'h0;
         reg180c2064[11:0] <= 12'h0;
       end
     else begin
       if (write_en[11])
         begin
           reg180c2064[31:24] <= write_data[31:24];
           reg180c2064[23] <= write_data[23];
           reg180c2064[21] <= write_data[21];
           reg180c2064[11:0] <= write_data[11:0];
         end
       else
         begin
           reg180c2064[31:24] <= reg180c2064[31:24];
           reg180c2064[23] <= reg180c2064[23];
           reg180c2064[21] <= reg180c2064[21];
           reg180c2064[11:0] <= reg180c2064[11:0];
         end
     end
  end

always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2064[20] <= 1'h0;
       end
     else begin
       if (write_en[11])
         begin
           reg180c2064[20] <= write_data[20];
         end
       else
         begin
             reg180c2064[20] <= update_ref_idle_en ? n_ref_idle_en : reg180c2064[20];
         end
     end
  end

//addr = 0x180c2068
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2068[13:8] <= 6'h0;
         reg180c2068[5:0] <= 6'h0;
       end
     else begin
       if (write_en[12])
         begin
           reg180c2068[13:8] <= write_data[13:8];
           reg180c2068[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c2068[13:8] <= reg180c2068[13:8];
           reg180c2068[5:0] <= reg180c2068[5:0];
         end
     end
  end

//addr = 0x180c2080
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2080[31:28] <= 4'hf;
         reg180c2080[24] <= 1'h1;
         reg180c2080[23:12] <= 12'h0;
         reg180c2080[10] <= 1'h0;
         reg180c2080[9:8] <= 2'h0;
         reg180c2080[7] <= 1'h0;
         reg180c2080[5] <= 1'h0;
         reg180c2080[4] <= 1'h0;
         reg180c2080[3] <= 1'h0;
         reg180c2080[2] <= 1'h0;
         reg180c2080[1] <= 1'h0;
         reg180c2080[0] <= 1'h0;
       end
     else begin
       if (write_en[13])
         begin
           reg180c2080[31:28] <= write_data[31:28];
           reg180c2080[24] <= write_data[24];
           reg180c2080[23:12] <= write_data[23:12];
           reg180c2080[10] <= write_data[10];
           reg180c2080[9:8] <= write_data[9:8];
           reg180c2080[7] <= write_data[7];
           reg180c2080[5] <= write_data[5];
           reg180c2080[4] <= write_data[4];
           reg180c2080[3] <= write_data[3];
           reg180c2080[2] <= write_data[2];
           reg180c2080[1] <= write_data[1];
           reg180c2080[0] <= write_data[0];
         end
       else
         begin
           reg180c2080[31:28] <= reg180c2080[31:28];
           reg180c2080[24] <= reg180c2080[24];
           reg180c2080[23:12] <= reg180c2080[23:12];
           reg180c2080[10] <= reg180c2080[10];
           reg180c2080[9:8] <= reg180c2080[9:8];
           reg180c2080[7] <= reg180c2080[7];
           reg180c2080[5] <= reg180c2080[5];
           reg180c2080[4] <= reg180c2080[4];
           reg180c2080[3] <= reg180c2080[3];
           reg180c2080[2] <= reg180c2080[2];
           reg180c2080[1] <= reg180c2080[1];
           reg180c2080[0] <= reg180c2080[0];
         end
     end
  end

//addr = 0x180c2088
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2088[25] <= 1'h0;
         reg180c2088[24] <= 1'h0;
         reg180c2088[1] <= 1'h0;
         reg180c2088[0] <= 1'h0;
       end
     else begin
       if (write_en[14])
         begin
           reg180c2088[25] <= write_data[25];
           reg180c2088[24] <= write_data[24];
           reg180c2088[1] <= write_data[1];
           reg180c2088[0] <= write_data[0];
         end
       else
         begin
           reg180c2088[25] <= reg180c2088[25];
           reg180c2088[24] <= reg180c2088[24];
           reg180c2088[1] <= reg180c2088[1];
           reg180c2088[0] <= reg180c2088[0];
         end
     end
  end

//addr = 0x180c2090
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2090[15:8] <= 8'h15;
         reg180c2090[7:0] <= 8'h2e;
       end
     else begin
       if (write_en[15])
         begin
           reg180c2090[15:8] <= write_data[15:8];
           reg180c2090[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2090[15:8] <= reg180c2090[15:8];
           reg180c2090[7:0] <= reg180c2090[7:0];
         end
     end
  end

//addr = 0x180c2098
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2098[23] <= 1'h0;
         reg180c2098[22] <= 1'h0;
         reg180c2098[21:16] <= 6'h0;
         reg180c2098[15:8] <= 8'h22;
         reg180c2098[7:0] <= 8'h3b;
       end
     else begin
       if (write_en[16])
         begin
           reg180c2098[23] <= write_data[23];
           reg180c2098[22] <= write_data[22];
           reg180c2098[21:16] <= write_data[21:16];
           reg180c2098[15:8] <= write_data[15:8];
           reg180c2098[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2098[23] <= reg180c2098[23];
           reg180c2098[22] <= reg180c2098[22];
           reg180c2098[21:16] <= reg180c2098[21:16];
           reg180c2098[15:8] <= reg180c2098[15:8];
           reg180c2098[7:0] <= reg180c2098[7:0];
         end
     end
  end

//addr = 0x180c20a0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c20a0[21:16] <= 6'h0;
         reg180c20a0[13:8] <= 6'h0;
         reg180c20a0[0] <= 1'h0;
       end
     else begin
       if (write_en[17])
         begin
           reg180c20a0[21:16] <= write_data[21:16];
           reg180c20a0[13:8] <= write_data[13:8];
           reg180c20a0[0] <= write_data[0];
         end
       else
         begin
           reg180c20a0[21:16] <= reg180c20a0[21:16];
           reg180c20a0[13:8] <= reg180c20a0[13:8];
           reg180c20a0[0] <= reg180c20a0[0];
         end
     end
  end

//addr = 0x180c20f0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c20f0[8] <= 1'h0;
         reg180c20f0[4] <= 1'h0;
         reg180c20f0[0] <= 1'h0;
       end
     else begin
       if (write_en[18])
         begin
           reg180c20f0[8] <= write_data[8];
           reg180c20f0[4] <= write_data[4];
           reg180c20f0[0] <= write_data[0];
         end
       else
         begin
           reg180c20f0[8] <= reg180c20f0[8];
           reg180c20f0[4] <= reg180c20f0[4];
           reg180c20f0[0] <= reg180c20f0[0];
         end
     end
  end

//addr = 0x180c2100
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2100[9:8] <= 2'h0;
         reg180c2100[2:0] <= 3'h0;
       end
     else begin
       if (write_en[19])
         begin
           reg180c2100[9:8] <= write_data[9:8];
           reg180c2100[2:0] <= write_data[2:0];
         end
       else
         begin
           reg180c2100[9:8] <= reg180c2100[9:8];
           reg180c2100[2:0] <= reg180c2100[2:0];
         end
     end
  end

always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2100[31] <= 1'h0;
       end
     else begin
       if (write_en[19])
         begin
           reg180c2100[31] <= write_data[31];
         end
       else
         begin
             reg180c2100[31] <= update_cmd_start ? n_cmd_start : reg180c2100[31];
         end
     end
  end

//addr = 0x180c2110
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2110[31:0] <= 32'h0;
       end
     else begin
       if (write_en[20])
         begin
           reg180c2110[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2110[31:0] <= reg180c2110[31:0];
         end
     end
  end

//addr = 0x180c2114
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2114[31:0] <= 32'h0;
       end
     else begin
       if (write_en[21])
         begin
           reg180c2114[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2114[31:0] <= reg180c2114[31:0];
         end
     end
  end

//addr = 0x180c2118
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2118[31:0] <= 32'h0;
       end
     else begin
       if (write_en[22])
         begin
           reg180c2118[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2118[31:0] <= reg180c2118[31:0];
         end
     end
  end

//addr = 0x180c211c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c211c[31:0] <= 32'h0;
       end
     else begin
       if (write_en[23])
         begin
           reg180c211c[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c211c[31:0] <= reg180c211c[31:0];
         end
     end
  end

//addr = 0x180c2120
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2120[31:0] <= 32'h0;
       end
     else begin
       if (write_en[24])
         begin
           reg180c2120[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2120[31:0] <= reg180c2120[31:0];
         end
     end
  end

//addr = 0x180c2130
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2130[31:16] <= 16'h0;
         reg180c2130[15:0] <= 16'h0;
       end
     else begin
       if (write_en[25])
         begin
           reg180c2130[31:16] <= write_data[31:16];
           reg180c2130[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2130[31:16] <= reg180c2130[31:16];
           reg180c2130[15:0] <= reg180c2130[15:0];
         end
     end
  end

//addr = 0x180c2138
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2138[31:16] <= 16'h0;
         reg180c2138[15:0] <= 16'h0;
       end
     else begin
       if (write_en[26])
         begin
           reg180c2138[31:16] <= write_data[31:16];
           reg180c2138[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2138[31:16] <= reg180c2138[31:16];
           reg180c2138[15:0] <= reg180c2138[15:0];
         end
     end
  end

//addr = 0x180c2140
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2140[31:16] <= 16'h0;
         reg180c2140[15:0] <= 16'h0;
       end
     else begin
       if (write_en[27])
         begin
           reg180c2140[31:16] <= write_data[31:16];
           reg180c2140[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2140[31:16] <= reg180c2140[31:16];
           reg180c2140[15:0] <= reg180c2140[15:0];
         end
     end
  end

//addr = 0x180c2200
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2200[23:16] <= 8'h0;
         reg180c2200[13:8] <= 6'h0;
         reg180c2200[5:0] <= 6'h6;
       end
     else begin
       if (write_en[28])
         begin
           reg180c2200[23:16] <= write_data[23:16];
           reg180c2200[13:8] <= write_data[13:8];
           reg180c2200[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c2200[23:16] <= reg180c2200[23:16];
           reg180c2200[13:8] <= reg180c2200[13:8];
           reg180c2200[5:0] <= reg180c2200[5:0];
         end
     end
  end

//addr = 0x180c2208
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2208[28:24] <= 5'h0;
         reg180c2208[21:16] <= 6'h0;
         reg180c2208[13:8] <= 6'hd;
         reg180c2208[7:0] <= 8'h0;
       end
     else begin
       if (write_en[29])
         begin
           reg180c2208[28:24] <= write_data[28:24];
           reg180c2208[21:16] <= write_data[21:16];
           reg180c2208[13:8] <= write_data[13:8];
           reg180c2208[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2208[28:24] <= reg180c2208[28:24];
           reg180c2208[21:16] <= reg180c2208[21:16];
           reg180c2208[13:8] <= reg180c2208[13:8];
           reg180c2208[7:0] <= reg180c2208[7:0];
         end
     end
  end

//addr = 0x180c2210
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2210[27:24] <= 4'h0;
         reg180c2210[22:16] <= 7'h0;
         reg180c2210[12:8] <= 5'h0;
         reg180c2210[5:0] <= 6'h0;
       end
     else begin
       if (write_en[30])
         begin
           reg180c2210[27:24] <= write_data[27:24];
           reg180c2210[22:16] <= write_data[22:16];
           reg180c2210[12:8] <= write_data[12:8];
           reg180c2210[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c2210[27:24] <= reg180c2210[27:24];
           reg180c2210[22:16] <= reg180c2210[22:16];
           reg180c2210[12:8] <= reg180c2210[12:8];
           reg180c2210[5:0] <= reg180c2210[5:0];
         end
     end
  end

//addr = 0x180c2218
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2218[31:24] <= 8'h0;
         reg180c2218[17] <= 1'h0;
         reg180c2218[16] <= 1'h0;
         reg180c2218[15:8] <= 8'h0;
         reg180c2218[7:0] <= 8'h0;
       end
     else begin
       if (write_en[31])
         begin
           reg180c2218[31:24] <= write_data[31:24];
           reg180c2218[17] <= write_data[17];
           reg180c2218[16] <= write_data[16];
           reg180c2218[15:8] <= write_data[15:8];
           reg180c2218[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2218[31:24] <= reg180c2218[31:24];
           reg180c2218[17] <= reg180c2218[17];
           reg180c2218[16] <= reg180c2218[16];
           reg180c2218[15:8] <= reg180c2218[15:8];
           reg180c2218[7:0] <= reg180c2218[7:0];
         end
     end
  end

//addr = 0x180c2220
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2220[31:28] <= 4'h0;
         reg180c2220[25:20] <= 6'h0;
         reg180c2220[16:12] <= 5'h0;
         reg180c2220[8:4] <= 5'h0;
         reg180c2220[3:0] <= 4'h0;
       end
     else begin
       if (write_en[32])
         begin
           reg180c2220[31:28] <= write_data[31:28];
           reg180c2220[25:20] <= write_data[25:20];
           reg180c2220[16:12] <= write_data[16:12];
           reg180c2220[8:4] <= write_data[8:4];
           reg180c2220[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2220[31:28] <= reg180c2220[31:28];
           reg180c2220[25:20] <= reg180c2220[25:20];
           reg180c2220[16:12] <= reg180c2220[16:12];
           reg180c2220[8:4] <= reg180c2220[8:4];
           reg180c2220[3:0] <= reg180c2220[3:0];
         end
     end
  end

//addr = 0x180c2228
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2228[23:20] <= 4'h0;
         reg180c2228[16:12] <= 5'h0;
         reg180c2228[9:8] <= 2'h0;
         reg180c2228[5:0] <= 6'h0;
       end
     else begin
       if (write_en[33])
         begin
           reg180c2228[23:20] <= write_data[23:20];
           reg180c2228[16:12] <= write_data[16:12];
           reg180c2228[9:8] <= write_data[9:8];
           reg180c2228[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c2228[23:20] <= reg180c2228[23:20];
           reg180c2228[16:12] <= reg180c2228[16:12];
           reg180c2228[9:8] <= reg180c2228[9:8];
           reg180c2228[5:0] <= reg180c2228[5:0];
         end
     end
  end

//addr = 0x180c222c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c222c[31:28] <= 4'h0;
         reg180c222c[27:24] <= 4'h0;
         reg180c222c[23:20] <= 4'h0;
         reg180c222c[19:15] <= 5'h0;
         reg180c222c[13:8] <= 6'h0;
         reg180c222c[5:0] <= 6'h0;
       end
     else begin
       if (write_en[34])
         begin
           reg180c222c[31:28] <= write_data[31:28];
           reg180c222c[27:24] <= write_data[27:24];
           reg180c222c[23:20] <= write_data[23:20];
           reg180c222c[19:15] <= write_data[19:15];
           reg180c222c[13:8] <= write_data[13:8];
           reg180c222c[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c222c[31:28] <= reg180c222c[31:28];
           reg180c222c[27:24] <= reg180c222c[27:24];
           reg180c222c[23:20] <= reg180c222c[23:20];
           reg180c222c[19:15] <= reg180c222c[19:15];
           reg180c222c[13:8] <= reg180c222c[13:8];
           reg180c222c[5:0] <= reg180c222c[5:0];
         end
     end
  end

//addr = 0x180c2230
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2230[29:24] <= 6'h0;
         reg180c2230[21:16] <= 6'h0;
         reg180c2230[13:8] <= 6'h0;
         reg180c2230[5:0] <= 6'h0;
       end
     else begin
       if (write_en[35])
         begin
           reg180c2230[29:24] <= write_data[29:24];
           reg180c2230[21:16] <= write_data[21:16];
           reg180c2230[13:8] <= write_data[13:8];
           reg180c2230[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c2230[29:24] <= reg180c2230[29:24];
           reg180c2230[21:16] <= reg180c2230[21:16];
           reg180c2230[13:8] <= reg180c2230[13:8];
           reg180c2230[5:0] <= reg180c2230[5:0];
         end
     end
  end

//addr = 0x180c2234
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2234[31:22] <= 10'h20;
         reg180c2234[21:12] <= 10'h30;
         reg180c2234[11] <= 1'h0;
         reg180c2234[10] <= 1'h1;
         reg180c2234[9:0] <= 10'h0;
       end
     else begin
       if (write_en[36])
         begin
           reg180c2234[31:22] <= write_data[31:22];
           reg180c2234[21:12] <= write_data[21:12];
           reg180c2234[11] <= write_data[11];
           reg180c2234[10] <= write_data[10];
           reg180c2234[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2234[31:22] <= reg180c2234[31:22];
           reg180c2234[21:12] <= reg180c2234[21:12];
           reg180c2234[11] <= reg180c2234[11];
           reg180c2234[10] <= reg180c2234[10];
           reg180c2234[9:0] <= reg180c2234[9:0];
         end
     end
  end

//addr = 0x180c2238
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2238[29:24] <= 6'h0;
         reg180c2238[21:16] <= 6'h0;
         reg180c2238[13:8] <= 6'h0;
         reg180c2238[5:0] <= 6'h0;
       end
     else begin
       if (write_en[37])
         begin
           reg180c2238[29:24] <= write_data[29:24];
           reg180c2238[21:16] <= write_data[21:16];
           reg180c2238[13:8] <= write_data[13:8];
           reg180c2238[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c2238[29:24] <= reg180c2238[29:24];
           reg180c2238[21:16] <= reg180c2238[21:16];
           reg180c2238[13:8] <= reg180c2238[13:8];
           reg180c2238[5:0] <= reg180c2238[5:0];
         end
     end
  end

//addr = 0x180c2240
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2240[25:16] <= 10'h30;
         reg180c2240[14] <= 1'h0;
         reg180c2240[13] <= 1'h1;
         reg180c2240[12] <= 1'h0;
         reg180c2240[9:0] <= 10'h0;
       end
     else begin
       if (write_en[38])
         begin
           reg180c2240[25:16] <= write_data[25:16];
           reg180c2240[14] <= write_data[14];
           reg180c2240[13] <= write_data[13];
           reg180c2240[12] <= write_data[12];
           reg180c2240[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2240[25:16] <= reg180c2240[25:16];
           reg180c2240[14] <= reg180c2240[14];
           reg180c2240[13] <= reg180c2240[13];
           reg180c2240[12] <= reg180c2240[12];
           reg180c2240[9:0] <= reg180c2240[9:0];
         end
     end
  end

//addr = 0x180c2244
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2244[1] <= 1'h0;
         reg180c2244[0] <= 1'h0;
       end
     else begin
       if (write_en[39])
         begin
           reg180c2244[1] <= write_data[1];
           reg180c2244[0] <= write_data[0];
         end
       else
         begin
           reg180c2244[1] <= reg180c2244[1];
           reg180c2244[0] <= reg180c2244[0];
         end
     end
  end

//addr = 0x180c2248
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2248[28:24] <= 5'h0;
         reg180c2248[20:16] <= 5'h0;
         reg180c2248[12:8] <= 5'h0;
         reg180c2248[4:0] <= 5'h0;
       end
     else begin
       if (write_en[40])
         begin
           reg180c2248[28:24] <= write_data[28:24];
           reg180c2248[20:16] <= write_data[20:16];
           reg180c2248[12:8] <= write_data[12:8];
           reg180c2248[4:0] <= write_data[4:0];
         end
       else
         begin
           reg180c2248[28:24] <= reg180c2248[28:24];
           reg180c2248[20:16] <= reg180c2248[20:16];
           reg180c2248[12:8] <= reg180c2248[12:8];
           reg180c2248[4:0] <= reg180c2248[4:0];
         end
     end
  end

//addr = 0x180c22a0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c22a0[31:16] <= 16'h0;
         reg180c22a0[10:0] <= 11'h0;
       end
     else begin
       if (write_en[41])
         begin
           reg180c22a0[31:16] <= write_data[31:16];
           reg180c22a0[10:0] <= write_data[10:0];
         end
       else
         begin
           reg180c22a0[31:16] <= reg180c22a0[31:16];
           reg180c22a0[10:0] <= reg180c22a0[10:0];
         end
     end
  end

//addr = 0x180c22a4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c22a4[31:16] <= 16'h1000;
         reg180c22a4[15:0] <= 16'h4000;
       end
     else begin
       if (write_en[42])
         begin
           reg180c22a4[31:16] <= write_data[31:16];
           reg180c22a4[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c22a4[31:16] <= reg180c22a4[31:16];
           reg180c22a4[15:0] <= reg180c22a4[15:0];
         end
     end
  end

//addr = 0x180c22a8
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c22a8[31:24] <= 8'h0;
         reg180c22a8[22:12] <= 11'h0;
         reg180c22a8[8:0] <= 9'h0;
       end
     else begin
       if (write_en[43])
         begin
           reg180c22a8[31:24] <= write_data[31:24];
           reg180c22a8[22:12] <= write_data[22:12];
           reg180c22a8[8:0] <= write_data[8:0];
         end
       else
         begin
           reg180c22a8[31:24] <= reg180c22a8[31:24];
           reg180c22a8[22:12] <= reg180c22a8[22:12];
           reg180c22a8[8:0] <= reg180c22a8[8:0];
         end
     end
  end

//addr = 0x180c22ac
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c22ac[22:12] <= 11'h0;
         reg180c22ac[8:0] <= 9'h0;
       end
     else begin
       if (write_en[44])
         begin
           reg180c22ac[22:12] <= write_data[22:12];
           reg180c22ac[8:0] <= write_data[8:0];
         end
       else
         begin
           reg180c22ac[22:12] <= reg180c22ac[22:12];
           reg180c22ac[8:0] <= reg180c22ac[8:0];
         end
     end
  end

//addr = 0x180c2300
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2300[28:24] <= 5'h0;
         reg180c2300[20:16] <= 5'h0;
         reg180c2300[12:8] <= 5'h0;
         reg180c2300[4:0] <= 5'h0;
       end
     else begin
       if (write_en[45])
         begin
           reg180c2300[28:24] <= write_data[28:24];
           reg180c2300[20:16] <= write_data[20:16];
           reg180c2300[12:8] <= write_data[12:8];
           reg180c2300[4:0] <= write_data[4:0];
         end
       else
         begin
           reg180c2300[28:24] <= reg180c2300[28:24];
           reg180c2300[20:16] <= reg180c2300[20:16];
           reg180c2300[12:8] <= reg180c2300[12:8];
           reg180c2300[4:0] <= reg180c2300[4:0];
         end
     end
  end

//addr = 0x180c2304
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2304[13] <= 1'h0;
         reg180c2304[12:8] <= 5'h0;
         reg180c2304[4:0] <= 5'h0;
       end
     else begin
       if (write_en[46])
         begin
           reg180c2304[13] <= write_data[13];
           reg180c2304[12:8] <= write_data[12:8];
           reg180c2304[4:0] <= write_data[4:0];
         end
       else
         begin
           reg180c2304[13] <= reg180c2304[13];
           reg180c2304[12:8] <= reg180c2304[12:8];
           reg180c2304[4:0] <= reg180c2304[4:0];
         end
     end
  end

//addr = 0x180c2710
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2710[27:24] <= 4'h0;
         reg180c2710[23:16] <= 8'h0;
       end
     else begin
       if (write_en[50])
         begin
           reg180c2710[27:24] <= write_data[27:24];
           reg180c2710[23:16] <= write_data[23:16];
         end
       else
         begin
           reg180c2710[27:24] <= reg180c2710[27:24];
           reg180c2710[23:16] <= reg180c2710[23:16];
         end
     end
  end

//addr = 0x180c2718
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2718[31] <= 1'h0;
         reg180c2718[29:24] <= 6'h0;
       end
     else begin
       if (write_en[52])
         begin
           reg180c2718[31] <= write_data[31];
           reg180c2718[29:24] <= write_data[29:24];
         end
       else
         begin
           reg180c2718[31] <= reg180c2718[31];
           reg180c2718[29:24] <= reg180c2718[29:24];
         end
     end
  end

//addr = 0x180c271c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c271c[9:8] <= 2'h0;
         reg180c271c[1:0] <= 2'h0;
       end
     else begin
       if (write_en[53])
         begin
           reg180c271c[9:8] <= write_data[9:8];
           reg180c271c[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c271c[9:8] <= reg180c271c[9:8];
           reg180c271c[1:0] <= reg180c271c[1:0];
         end
     end
  end

//addr = 0x180c2720
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2720[14:12] <= 3'h0;
         reg180c2720[10:8] <= 3'h0;
         reg180c2720[4:0] <= 5'h0;
       end
     else begin
       if (write_en[54])
         begin
           reg180c2720[14:12] <= write_data[14:12];
           reg180c2720[10:8] <= write_data[10:8];
           reg180c2720[4:0] <= write_data[4:0];
         end
       else
         begin
           reg180c2720[14:12] <= reg180c2720[14:12];
           reg180c2720[10:8] <= reg180c2720[10:8];
           reg180c2720[4:0] <= reg180c2720[4:0];
         end
     end
  end

//addr = 0x180c2734
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2734[5:0] <= 6'h0;
       end
     else begin
       if (write_en[59])
         begin
           reg180c2734[5:0] <= write_data[5:0];
         end
       else
         begin
           reg180c2734[5:0] <= reg180c2734[5:0];
         end
     end
  end

//addr = 0x180c273c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c273c[23:16] <= 8'h0;
         reg180c273c[0] <= 1'h0;
       end
     else begin
       if (write_en[61])
         begin
           reg180c273c[23:16] <= write_data[23:16];
           reg180c273c[0] <= write_data[0];
         end
       else
         begin
           reg180c273c[23:16] <= reg180c273c[23:16];
           reg180c273c[0] <= reg180c273c[0];
         end
     end
  end

//addr = 0x180c2740
always @(posedge clk or negedge new_rst_n)
  begin 
     if(!new_rst_n)
       begin
         reg180c2740[31:0] <= 32'h0;
       end
     else begin
       if (write_en[62])
         begin
           reg180c2740[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2740[31:0] <= reg180c2740[31:0];
         end
     end
  end

//addr = 0x180c2744
always @(posedge clk or negedge new_rst_n)
  begin 
     if(!new_rst_n)
       begin
         reg180c2744[31:0] <= 32'h0;
       end
     else begin
       if (write_en[63])
         begin
           reg180c2744[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2744[31:0] <= reg180c2744[31:0];
         end
     end
  end

//addr = 0x180c2748
always @(posedge clk or negedge new_rst_n)
  begin 
     if(!new_rst_n)
       begin
         reg180c2748[31:0] <= 32'h0;
       end
     else begin
       if (write_en[64])
         begin
           reg180c2748[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2748[31:0] <= reg180c2748[31:0];
         end
     end
  end

//addr = 0x180c274c
always @(posedge clk or negedge new_rst_n)
  begin 
     if(!new_rst_n)
       begin
         reg180c274c[31:0] <= 32'h0;
       end
     else begin
       if (write_en[65])
         begin
           reg180c274c[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c274c[31:0] <= reg180c274c[31:0];
         end
     end
  end

//addr = 0x180c2750
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2750[31:0] <= 32'h0;
       end
     else begin
       if (write_en[66])
         begin
           reg180c2750[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2750[31:0] <= reg180c2750[31:0];
         end
     end
  end

//addr = 0x180c2754
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2754[31:0] <= 32'h0;
       end
     else begin
       if (write_en[67])
         begin
           reg180c2754[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2754[31:0] <= reg180c2754[31:0];
         end
     end
  end

//addr = 0x180c2758
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2758[31:0] <= 32'h0;
       end
     else begin
       if (write_en[68])
         begin
           reg180c2758[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2758[31:0] <= reg180c2758[31:0];
         end
     end
  end

//addr = 0x180c275c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c275c[31:0] <= 32'h0;
       end
     else begin
       if (write_en[69])
         begin
           reg180c275c[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c275c[31:0] <= reg180c275c[31:0];
         end
     end
  end

//addr = 0x180c2760
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2760[31:0] <= 32'h0;
       end
     else begin
       if (write_en[70])
         begin
           reg180c2760[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2760[31:0] <= reg180c2760[31:0];
         end
     end
  end

//addr = 0x180c2764
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2764[31:0] <= 32'h0;
       end
     else begin
       if (write_en[71])
         begin
           reg180c2764[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2764[31:0] <= reg180c2764[31:0];
         end
     end
  end

//addr = 0x180c2768
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2768[31:0] <= 32'h0;
       end
     else begin
       if (write_en[72])
         begin
           reg180c2768[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2768[31:0] <= reg180c2768[31:0];
         end
     end
  end

//addr = 0x180c276c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c276c[31:0] <= 32'h0;
       end
     else begin
       if (write_en[73])
         begin
           reg180c276c[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c276c[31:0] <= reg180c276c[31:0];
         end
     end
  end

//addr = 0x180c2770
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2770[31:0] <= 32'h0;
       end
     else begin
       if (write_en[74])
         begin
           reg180c2770[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2770[31:0] <= reg180c2770[31:0];
         end
     end
  end

//addr = 0x180c2774
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2774[31:0] <= 32'h0;
       end
     else begin
       if (write_en[75])
         begin
           reg180c2774[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2774[31:0] <= reg180c2774[31:0];
         end
     end
  end

//addr = 0x180c2778
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2778[31:0] <= 32'h0;
       end
     else begin
       if (write_en[76])
         begin
           reg180c2778[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2778[31:0] <= reg180c2778[31:0];
         end
     end
  end

//addr = 0x180c277c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c277c[31:0] <= 32'h0;
       end
     else begin
       if (write_en[77])
         begin
           reg180c277c[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c277c[31:0] <= reg180c277c[31:0];
         end
     end
  end

//addr = 0x180c2780
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2780[31:0] <= 32'h0;
       end
     else begin
       if (write_en[78])
         begin
           reg180c2780[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2780[31:0] <= reg180c2780[31:0];
         end
     end
  end

//addr = 0x180c2784
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2784[31:0] <= 32'h0;
       end
     else begin
       if (write_en[79])
         begin
           reg180c2784[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2784[31:0] <= reg180c2784[31:0];
         end
     end
  end

//addr = 0x180c2788
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2788[31:0] <= 32'h0;
       end
     else begin
       if (write_en[80])
         begin
           reg180c2788[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2788[31:0] <= reg180c2788[31:0];
         end
     end
  end

//addr = 0x180c278c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c278c[31:0] <= 32'h0;
       end
     else begin
       if (write_en[81])
         begin
           reg180c278c[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c278c[31:0] <= reg180c278c[31:0];
         end
     end
  end

//addr = 0x180c2800
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2800[31:28] <= 4'h0;
         reg180c2800[27:24] <= 4'h0;
         reg180c2800[23:20] <= 4'h0;
         reg180c2800[19:16] <= 4'h0;
         reg180c2800[15:2] <= 14'h0;
         reg180c2800[1:0] <= 2'h0;
       end
     else begin
       if (write_en[82])
         begin
           reg180c2800[31:28] <= write_data[31:28];
           reg180c2800[27:24] <= write_data[27:24];
           reg180c2800[23:20] <= write_data[23:20];
           reg180c2800[19:16] <= write_data[19:16];
           reg180c2800[15:2] <= write_data[15:2];
           reg180c2800[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2800[31:28] <= reg180c2800[31:28];
           reg180c2800[27:24] <= reg180c2800[27:24];
           reg180c2800[23:20] <= reg180c2800[23:20];
           reg180c2800[19:16] <= reg180c2800[19:16];
           reg180c2800[15:2] <= reg180c2800[15:2];
           reg180c2800[1:0] <= reg180c2800[1:0];
         end
     end
  end

//addr = 0x180c2804
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2804[31:28] <= 4'h0;
         reg180c2804[27:24] <= 4'h0;
         reg180c2804[23:20] <= 4'h0;
         reg180c2804[19:16] <= 4'h0;
         reg180c2804[15:2] <= 14'h0;
         reg180c2804[1:0] <= 2'h0;
       end
     else begin
       if (write_en[83])
         begin
           reg180c2804[31:28] <= write_data[31:28];
           reg180c2804[27:24] <= write_data[27:24];
           reg180c2804[23:20] <= write_data[23:20];
           reg180c2804[19:16] <= write_data[19:16];
           reg180c2804[15:2] <= write_data[15:2];
           reg180c2804[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2804[31:28] <= reg180c2804[31:28];
           reg180c2804[27:24] <= reg180c2804[27:24];
           reg180c2804[23:20] <= reg180c2804[23:20];
           reg180c2804[19:16] <= reg180c2804[19:16];
           reg180c2804[15:2] <= reg180c2804[15:2];
           reg180c2804[1:0] <= reg180c2804[1:0];
         end
     end
  end

//addr = 0x180c2808
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2808[31:28] <= 4'h0;
         reg180c2808[27:24] <= 4'h0;
         reg180c2808[23:20] <= 4'h0;
         reg180c2808[19:16] <= 4'h0;
         reg180c2808[15:2] <= 14'h0;
         reg180c2808[1:0] <= 2'h0;
       end
     else begin
       if (write_en[84])
         begin
           reg180c2808[31:28] <= write_data[31:28];
           reg180c2808[27:24] <= write_data[27:24];
           reg180c2808[23:20] <= write_data[23:20];
           reg180c2808[19:16] <= write_data[19:16];
           reg180c2808[15:2] <= write_data[15:2];
           reg180c2808[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2808[31:28] <= reg180c2808[31:28];
           reg180c2808[27:24] <= reg180c2808[27:24];
           reg180c2808[23:20] <= reg180c2808[23:20];
           reg180c2808[19:16] <= reg180c2808[19:16];
           reg180c2808[15:2] <= reg180c2808[15:2];
           reg180c2808[1:0] <= reg180c2808[1:0];
         end
     end
  end

//addr = 0x180c280c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c280c[31:28] <= 4'h0;
         reg180c280c[27:24] <= 4'h0;
         reg180c280c[23:20] <= 4'h0;
         reg180c280c[19:16] <= 4'h0;
         reg180c280c[15:2] <= 14'h0;
         reg180c280c[1:0] <= 2'h0;
       end
     else begin
       if (write_en[85])
         begin
           reg180c280c[31:28] <= write_data[31:28];
           reg180c280c[27:24] <= write_data[27:24];
           reg180c280c[23:20] <= write_data[23:20];
           reg180c280c[19:16] <= write_data[19:16];
           reg180c280c[15:2] <= write_data[15:2];
           reg180c280c[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c280c[31:28] <= reg180c280c[31:28];
           reg180c280c[27:24] <= reg180c280c[27:24];
           reg180c280c[23:20] <= reg180c280c[23:20];
           reg180c280c[19:16] <= reg180c280c[19:16];
           reg180c280c[15:2] <= reg180c280c[15:2];
           reg180c280c[1:0] <= reg180c280c[1:0];
         end
     end
  end

//addr = 0x180c2810
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2810[31:28] <= 4'h0;
         reg180c2810[27:24] <= 4'h0;
         reg180c2810[23:20] <= 4'h0;
         reg180c2810[19:16] <= 4'h0;
         reg180c2810[15:2] <= 14'h0;
         reg180c2810[1:0] <= 2'h0;
       end
     else begin
       if (write_en[86])
         begin
           reg180c2810[31:28] <= write_data[31:28];
           reg180c2810[27:24] <= write_data[27:24];
           reg180c2810[23:20] <= write_data[23:20];
           reg180c2810[19:16] <= write_data[19:16];
           reg180c2810[15:2] <= write_data[15:2];
           reg180c2810[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2810[31:28] <= reg180c2810[31:28];
           reg180c2810[27:24] <= reg180c2810[27:24];
           reg180c2810[23:20] <= reg180c2810[23:20];
           reg180c2810[19:16] <= reg180c2810[19:16];
           reg180c2810[15:2] <= reg180c2810[15:2];
           reg180c2810[1:0] <= reg180c2810[1:0];
         end
     end
  end

//addr = 0x180c2814
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2814[31:28] <= 4'h0;
         reg180c2814[27:24] <= 4'h0;
         reg180c2814[23:20] <= 4'h0;
         reg180c2814[19:16] <= 4'h0;
         reg180c2814[15:2] <= 14'h0;
         reg180c2814[1:0] <= 2'h0;
       end
     else begin
       if (write_en[87])
         begin
           reg180c2814[31:28] <= write_data[31:28];
           reg180c2814[27:24] <= write_data[27:24];
           reg180c2814[23:20] <= write_data[23:20];
           reg180c2814[19:16] <= write_data[19:16];
           reg180c2814[15:2] <= write_data[15:2];
           reg180c2814[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2814[31:28] <= reg180c2814[31:28];
           reg180c2814[27:24] <= reg180c2814[27:24];
           reg180c2814[23:20] <= reg180c2814[23:20];
           reg180c2814[19:16] <= reg180c2814[19:16];
           reg180c2814[15:2] <= reg180c2814[15:2];
           reg180c2814[1:0] <= reg180c2814[1:0];
         end
     end
  end

//addr = 0x180c2818
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2818[31:28] <= 4'h0;
         reg180c2818[27:24] <= 4'h0;
         reg180c2818[23:20] <= 4'h0;
         reg180c2818[19:16] <= 4'h0;
         reg180c2818[15:2] <= 14'h0;
         reg180c2818[1:0] <= 2'h0;
       end
     else begin
       if (write_en[88])
         begin
           reg180c2818[31:28] <= write_data[31:28];
           reg180c2818[27:24] <= write_data[27:24];
           reg180c2818[23:20] <= write_data[23:20];
           reg180c2818[19:16] <= write_data[19:16];
           reg180c2818[15:2] <= write_data[15:2];
           reg180c2818[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2818[31:28] <= reg180c2818[31:28];
           reg180c2818[27:24] <= reg180c2818[27:24];
           reg180c2818[23:20] <= reg180c2818[23:20];
           reg180c2818[19:16] <= reg180c2818[19:16];
           reg180c2818[15:2] <= reg180c2818[15:2];
           reg180c2818[1:0] <= reg180c2818[1:0];
         end
     end
  end

//addr = 0x180c281c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c281c[31:28] <= 4'h0;
         reg180c281c[27:24] <= 4'h0;
         reg180c281c[23:20] <= 4'h0;
         reg180c281c[19:16] <= 4'h0;
         reg180c281c[15:2] <= 14'h0;
         reg180c281c[1:0] <= 2'h0;
       end
     else begin
       if (write_en[89])
         begin
           reg180c281c[31:28] <= write_data[31:28];
           reg180c281c[27:24] <= write_data[27:24];
           reg180c281c[23:20] <= write_data[23:20];
           reg180c281c[19:16] <= write_data[19:16];
           reg180c281c[15:2] <= write_data[15:2];
           reg180c281c[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c281c[31:28] <= reg180c281c[31:28];
           reg180c281c[27:24] <= reg180c281c[27:24];
           reg180c281c[23:20] <= reg180c281c[23:20];
           reg180c281c[19:16] <= reg180c281c[19:16];
           reg180c281c[15:2] <= reg180c281c[15:2];
           reg180c281c[1:0] <= reg180c281c[1:0];
         end
     end
  end

//addr = 0x180c2820
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2820[31:28] <= 4'h0;
         reg180c2820[27:24] <= 4'h0;
         reg180c2820[23:20] <= 4'h0;
         reg180c2820[19:16] <= 4'h0;
         reg180c2820[15:2] <= 14'h0;
         reg180c2820[1:0] <= 2'h0;
       end
     else begin
       if (write_en[90])
         begin
           reg180c2820[31:28] <= write_data[31:28];
           reg180c2820[27:24] <= write_data[27:24];
           reg180c2820[23:20] <= write_data[23:20];
           reg180c2820[19:16] <= write_data[19:16];
           reg180c2820[15:2] <= write_data[15:2];
           reg180c2820[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2820[31:28] <= reg180c2820[31:28];
           reg180c2820[27:24] <= reg180c2820[27:24];
           reg180c2820[23:20] <= reg180c2820[23:20];
           reg180c2820[19:16] <= reg180c2820[19:16];
           reg180c2820[15:2] <= reg180c2820[15:2];
           reg180c2820[1:0] <= reg180c2820[1:0];
         end
     end
  end

//addr = 0x180c2824
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2824[31:28] <= 4'h0;
         reg180c2824[27:24] <= 4'h0;
         reg180c2824[23:20] <= 4'h0;
         reg180c2824[19:16] <= 4'h0;
         reg180c2824[15:2] <= 14'h0;
         reg180c2824[1:0] <= 2'h0;
       end
     else begin
       if (write_en[91])
         begin
           reg180c2824[31:28] <= write_data[31:28];
           reg180c2824[27:24] <= write_data[27:24];
           reg180c2824[23:20] <= write_data[23:20];
           reg180c2824[19:16] <= write_data[19:16];
           reg180c2824[15:2] <= write_data[15:2];
           reg180c2824[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2824[31:28] <= reg180c2824[31:28];
           reg180c2824[27:24] <= reg180c2824[27:24];
           reg180c2824[23:20] <= reg180c2824[23:20];
           reg180c2824[19:16] <= reg180c2824[19:16];
           reg180c2824[15:2] <= reg180c2824[15:2];
           reg180c2824[1:0] <= reg180c2824[1:0];
         end
     end
  end

//addr = 0x180c2828
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2828[31:28] <= 4'h0;
         reg180c2828[27:24] <= 4'h0;
         reg180c2828[23:20] <= 4'h0;
         reg180c2828[19:16] <= 4'h0;
         reg180c2828[15:2] <= 14'h0;
         reg180c2828[1:0] <= 2'h0;
       end
     else begin
       if (write_en[92])
         begin
           reg180c2828[31:28] <= write_data[31:28];
           reg180c2828[27:24] <= write_data[27:24];
           reg180c2828[23:20] <= write_data[23:20];
           reg180c2828[19:16] <= write_data[19:16];
           reg180c2828[15:2] <= write_data[15:2];
           reg180c2828[1:0] <= write_data[1:0];
         end
       else
         begin
           reg180c2828[31:28] <= reg180c2828[31:28];
           reg180c2828[27:24] <= reg180c2828[27:24];
           reg180c2828[23:20] <= reg180c2828[23:20];
           reg180c2828[19:16] <= reg180c2828[19:16];
           reg180c2828[15:2] <= reg180c2828[15:2];
           reg180c2828[1:0] <= reg180c2828[1:0];
         end
     end
  end

//addr = 0x180c2840
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2840[31:16] <= 16'h0;
         reg180c2840[15:0] <= 16'h0;
       end
     else begin
       if (write_en[93])
         begin
           reg180c2840[31:16] <= write_data[31:16];
           reg180c2840[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2840[31:16] <= reg180c2840[31:16];
           reg180c2840[15:0] <= reg180c2840[15:0];
         end
     end
  end

//addr = 0x180c2844
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2844[31:16] <= 16'h0;
         reg180c2844[15:0] <= 16'h0;
       end
     else begin
       if (write_en[94])
         begin
           reg180c2844[31:16] <= write_data[31:16];
           reg180c2844[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2844[31:16] <= reg180c2844[31:16];
           reg180c2844[15:0] <= reg180c2844[15:0];
         end
     end
  end

//addr = 0x180c2848
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2848[31:16] <= 16'h0;
         reg180c2848[15:0] <= 16'h0;
       end
     else begin
       if (write_en[95])
         begin
           reg180c2848[31:16] <= write_data[31:16];
           reg180c2848[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2848[31:16] <= reg180c2848[31:16];
           reg180c2848[15:0] <= reg180c2848[15:0];
         end
     end
  end

//addr = 0x180c284c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c284c[31:16] <= 16'h0;
         reg180c284c[15:0] <= 16'h0;
       end
     else begin
       if (write_en[96])
         begin
           reg180c284c[31:16] <= write_data[31:16];
           reg180c284c[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c284c[31:16] <= reg180c284c[31:16];
           reg180c284c[15:0] <= reg180c284c[15:0];
         end
     end
  end

//addr = 0x180c2850
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2850[31:16] <= 16'h0;
         reg180c2850[15:0] <= 16'h0;
       end
     else begin
       if (write_en[97])
         begin
           reg180c2850[31:16] <= write_data[31:16];
           reg180c2850[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2850[31:16] <= reg180c2850[31:16];
           reg180c2850[15:0] <= reg180c2850[15:0];
         end
     end
  end

//addr = 0x180c2854
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2854[31:16] <= 16'h0;
         reg180c2854[15:0] <= 16'h0;
       end
     else begin
       if (write_en[98])
         begin
           reg180c2854[31:16] <= write_data[31:16];
           reg180c2854[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2854[31:16] <= reg180c2854[31:16];
           reg180c2854[15:0] <= reg180c2854[15:0];
         end
     end
  end

//addr = 0x180c2858
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2858[31:16] <= 16'h0;
         reg180c2858[15:0] <= 16'h0;
       end
     else begin
       if (write_en[99])
         begin
           reg180c2858[31:16] <= write_data[31:16];
           reg180c2858[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2858[31:16] <= reg180c2858[31:16];
           reg180c2858[15:0] <= reg180c2858[15:0];
         end
     end
  end

//addr = 0x180c285c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c285c[31:16] <= 16'h0;
         reg180c285c[15:0] <= 16'h0;
       end
     else begin
       if (write_en[100])
         begin
           reg180c285c[31:16] <= write_data[31:16];
           reg180c285c[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c285c[31:16] <= reg180c285c[31:16];
           reg180c285c[15:0] <= reg180c285c[15:0];
         end
     end
  end

//addr = 0x180c2860
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2860[31:16] <= 16'h0;
         reg180c2860[15:0] <= 16'h0;
       end
     else begin
       if (write_en[101])
         begin
           reg180c2860[31:16] <= write_data[31:16];
           reg180c2860[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2860[31:16] <= reg180c2860[31:16];
           reg180c2860[15:0] <= reg180c2860[15:0];
         end
     end
  end

//addr = 0x180c2864
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2864[31:16] <= 16'h0;
         reg180c2864[15:0] <= 16'h0;
       end
     else begin
       if (write_en[102])
         begin
           reg180c2864[31:16] <= write_data[31:16];
           reg180c2864[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2864[31:16] <= reg180c2864[31:16];
           reg180c2864[15:0] <= reg180c2864[15:0];
         end
     end
  end

//addr = 0x180c2868
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2868[31:16] <= 16'h0;
         reg180c2868[15:0] <= 16'h0;
       end
     else begin
       if (write_en[103])
         begin
           reg180c2868[31:16] <= write_data[31:16];
           reg180c2868[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2868[31:16] <= reg180c2868[31:16];
           reg180c2868[15:0] <= reg180c2868[15:0];
         end
     end
  end

//addr = 0x180c2880
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2880[15:0] <= 16'h0;
       end
     else begin
       if (write_en[104])
         begin
           reg180c2880[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2880[15:0] <= reg180c2880[15:0];
         end
     end
  end

//addr = 0x180c2884
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2884[15:0] <= 16'h0;
       end
     else begin
       if (write_en[105])
         begin
           reg180c2884[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2884[15:0] <= reg180c2884[15:0];
         end
     end
  end

//addr = 0x180c2888
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2888[15:0] <= 16'h0;
       end
     else begin
       if (write_en[106])
         begin
           reg180c2888[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2888[15:0] <= reg180c2888[15:0];
         end
     end
  end

//addr = 0x180c288c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c288c[15:0] <= 16'h0;
       end
     else begin
       if (write_en[107])
         begin
           reg180c288c[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c288c[15:0] <= reg180c288c[15:0];
         end
     end
  end

//addr = 0x180c2890
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2890[15:0] <= 16'h0;
       end
     else begin
       if (write_en[108])
         begin
           reg180c2890[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2890[15:0] <= reg180c2890[15:0];
         end
     end
  end

//addr = 0x180c2894
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2894[15:0] <= 16'h0;
       end
     else begin
       if (write_en[109])
         begin
           reg180c2894[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2894[15:0] <= reg180c2894[15:0];
         end
     end
  end

//addr = 0x180c2898
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2898[15:0] <= 16'h0;
       end
     else begin
       if (write_en[110])
         begin
           reg180c2898[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c2898[15:0] <= reg180c2898[15:0];
         end
     end
  end

//addr = 0x180c289c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c289c[15:0] <= 16'h0;
       end
     else begin
       if (write_en[111])
         begin
           reg180c289c[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c289c[15:0] <= reg180c289c[15:0];
         end
     end
  end

//addr = 0x180c28a0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c28a0[15:0] <= 16'h0;
       end
     else begin
       if (write_en[112])
         begin
           reg180c28a0[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c28a0[15:0] <= reg180c28a0[15:0];
         end
     end
  end

//addr = 0x180c28a4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c28a4[15:0] <= 16'h0;
       end
     else begin
       if (write_en[113])
         begin
           reg180c28a4[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c28a4[15:0] <= reg180c28a4[15:0];
         end
     end
  end

//addr = 0x180c28a8
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c28a8[15:0] <= 16'h0;
       end
     else begin
       if (write_en[114])
         begin
           reg180c28a8[15:0] <= write_data[15:0];
         end
       else
         begin
           reg180c28a8[15:0] <= reg180c28a8[15:0];
         end
     end
  end

//addr = 0x180c2a00
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a00[22] <= 1'h0;
         reg180c2a00[19] <= 1'h0;
         reg180c2a00[18] <= 1'h0;
         reg180c2a00[17] <= 1'h0;
         reg180c2a00[16] <= 1'h0;
         reg180c2a00[15] <= 1'h0;
         reg180c2a00[14] <= 1'h0;
         reg180c2a00[13] <= 1'h0;
         reg180c2a00[12] <= 1'h0;
         reg180c2a00[11] <= 1'h0;
         reg180c2a00[10] <= 1'h0;
         reg180c2a00[9] <= 1'h0;
         reg180c2a00[8] <= 1'h0;
         reg180c2a00[7] <= 1'h0;
         reg180c2a00[6] <= 1'h1;
         reg180c2a00[5:4] <= 2'h0;
         reg180c2a00[3] <= 1'h0;
         reg180c2a00[2] <= 1'h0;
         reg180c2a00[1] <= 1'h1;
         reg180c2a00[0] <= 1'h1;
       end
     else begin
       if (write_en[115])
         begin
           reg180c2a00[22] <= write_data[22];
           reg180c2a00[19] <= write_data[19];
           reg180c2a00[18] <= write_data[18];
           reg180c2a00[17] <= write_data[17];
           reg180c2a00[16] <= write_data[16];
           reg180c2a00[15] <= write_data[15];
           reg180c2a00[14] <= write_data[14];
           reg180c2a00[13] <= write_data[13];
           reg180c2a00[12] <= write_data[12];
           reg180c2a00[11] <= write_data[11];
           reg180c2a00[10] <= write_data[10];
           reg180c2a00[9] <= write_data[9];
           reg180c2a00[8] <= write_data[8];
           reg180c2a00[7] <= write_data[7];
           reg180c2a00[6] <= write_data[6];
           reg180c2a00[5:4] <= write_data[5:4];
           reg180c2a00[3] <= write_data[3];
           reg180c2a00[2] <= write_data[2];
           reg180c2a00[1] <= write_data[1];
           reg180c2a00[0] <= write_data[0];
         end
       else
         begin
           reg180c2a00[22] <= reg180c2a00[22];
           reg180c2a00[19] <= reg180c2a00[19];
           reg180c2a00[18] <= reg180c2a00[18];
           reg180c2a00[17] <= reg180c2a00[17];
           reg180c2a00[16] <= reg180c2a00[16];
           reg180c2a00[15] <= reg180c2a00[15];
           reg180c2a00[14] <= reg180c2a00[14];
           reg180c2a00[13] <= reg180c2a00[13];
           reg180c2a00[12] <= reg180c2a00[12];
           reg180c2a00[11] <= reg180c2a00[11];
           reg180c2a00[10] <= reg180c2a00[10];
           reg180c2a00[9] <= reg180c2a00[9];
           reg180c2a00[8] <= reg180c2a00[8];
           reg180c2a00[7] <= reg180c2a00[7];
           reg180c2a00[6] <= reg180c2a00[6];
           reg180c2a00[5:4] <= reg180c2a00[5:4];
           reg180c2a00[3] <= reg180c2a00[3];
           reg180c2a00[2] <= reg180c2a00[2];
           reg180c2a00[1] <= reg180c2a00[1];
           reg180c2a00[0] <= reg180c2a00[0];
         end
     end
  end

//addr = 0x180c2a04
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a04[1] <= 1'h0;
         reg180c2a04[0] <= 1'h0;
       end
     else begin
       if (write_en[116])
         begin
           reg180c2a04[1] <= write_data[1];
           reg180c2a04[0] <= write_data[0];
         end
       else
         begin
           reg180c2a04[1] <= reg180c2a04[1];
           reg180c2a04[0] <= reg180c2a04[0];
         end
     end
  end

//addr = 0x180c2a10
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a10[31:24] <= 8'h0;
         reg180c2a10[23:16] <= 8'h0;
         reg180c2a10[15:8] <= 8'h0;
         reg180c2a10[7:0] <= 8'h0;
       end
     else begin
       if (write_en[117])
         begin
           reg180c2a10[31:24] <= write_data[31:24];
           reg180c2a10[23:16] <= write_data[23:16];
           reg180c2a10[15:8] <= write_data[15:8];
           reg180c2a10[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2a10[31:24] <= reg180c2a10[31:24];
           reg180c2a10[23:16] <= reg180c2a10[23:16];
           reg180c2a10[15:8] <= reg180c2a10[15:8];
           reg180c2a10[7:0] <= reg180c2a10[7:0];
         end
     end
  end

//addr = 0x180c2a14
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a14[31:24] <= 8'h0;
         reg180c2a14[23:16] <= 8'h0;
       end
     else begin
       if (write_en[118])
         begin
           reg180c2a14[31:24] <= write_data[31:24];
           reg180c2a14[23:16] <= write_data[23:16];
         end
       else
         begin
           reg180c2a14[31:24] <= reg180c2a14[31:24];
           reg180c2a14[23:16] <= reg180c2a14[23:16];
         end
     end
  end

//addr = 0x180c2a18
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a18[31:20] <= 12'h400;
         reg180c2a18[18:16] <= 3'h1;
         reg180c2a18[12:8] <= 5'h8;
         reg180c2a18[4] <= 1'h0;
       end
     else begin
       if (write_en[119])
         begin
           reg180c2a18[31:20] <= write_data[31:20];
           reg180c2a18[18:16] <= write_data[18:16];
           reg180c2a18[12:8] <= write_data[12:8];
           reg180c2a18[4] <= write_data[4];
         end
       else
         begin
           reg180c2a18[31:20] <= reg180c2a18[31:20];
           reg180c2a18[18:16] <= reg180c2a18[18:16];
           reg180c2a18[12:8] <= reg180c2a18[12:8];
           reg180c2a18[4] <= reg180c2a18[4];
         end
     end
  end

//addr = 0x180c2a1c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a1c[28:16] <= 13'h12c;
       end
     else begin
       if (write_en[120])
         begin
           reg180c2a1c[28:16] <= write_data[28:16];
         end
       else
         begin
           reg180c2a1c[28:16] <= reg180c2a1c[28:16];
         end
     end
  end

//addr = 0x180c2a20
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a20[28:16] <= 13'hfa;
         reg180c2a20[12:0] <= 13'hfa;
       end
     else begin
       if (write_en[121])
         begin
           reg180c2a20[28:16] <= write_data[28:16];
           reg180c2a20[12:0] <= write_data[12:0];
         end
       else
         begin
           reg180c2a20[28:16] <= reg180c2a20[28:16];
           reg180c2a20[12:0] <= reg180c2a20[12:0];
         end
     end
  end

//addr = 0x180c2a24
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a24[21:16] <= 6'h18;
         reg180c2a24[12:8] <= 5'h6;
         reg180c2a24[7:0] <= 8'h30;
       end
     else begin
       if (write_en[122])
         begin
           reg180c2a24[21:16] <= write_data[21:16];
           reg180c2a24[12:8] <= write_data[12:8];
           reg180c2a24[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2a24[21:16] <= reg180c2a24[21:16];
           reg180c2a24[12:8] <= reg180c2a24[12:8];
           reg180c2a24[7:0] <= reg180c2a24[7:0];
         end
     end
  end

//addr = 0x180c2a28
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a28[31:30] <= 2'h0;
         reg180c2a28[24] <= 1'h0;
         reg180c2a28[23:20] <= 4'hf;
         reg180c2a28[16:8] <= 9'h0;
         reg180c2a28[7] <= 1'h0;
         reg180c2a28[6] <= 1'h0;
         reg180c2a28[5] <= 1'h0;
         reg180c2a28[4] <= 1'h0;
         reg180c2a28[0] <= 1'h1;
       end
     else begin
       if (write_en[123])
         begin
           reg180c2a28[31:30] <= write_data[31:30];
           reg180c2a28[24] <= write_data[24];
           reg180c2a28[23:20] <= write_data[23:20];
           reg180c2a28[16:8] <= write_data[16:8];
           reg180c2a28[7] <= write_data[7];
           reg180c2a28[6] <= write_data[6];
           reg180c2a28[5] <= write_data[5];
           reg180c2a28[4] <= write_data[4];
           reg180c2a28[0] <= write_data[0];
         end
       else
         begin
           reg180c2a28[31:30] <= reg180c2a28[31:30];
           reg180c2a28[24] <= reg180c2a28[24];
           reg180c2a28[23:20] <= reg180c2a28[23:20];
           reg180c2a28[16:8] <= reg180c2a28[16:8];
           reg180c2a28[7] <= reg180c2a28[7];
           reg180c2a28[6] <= reg180c2a28[6];
           reg180c2a28[5] <= reg180c2a28[5];
           reg180c2a28[4] <= reg180c2a28[4];
           reg180c2a28[0] <= reg180c2a28[0];
         end
     end
  end

//addr = 0x180c2a2c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a2c[25:16] <= 10'h3af;
         reg180c2a2c[7:4] <= 4'h7;
         reg180c2a2c[3:0] <= 4'ha;
       end
     else begin
       if (write_en[124])
         begin
           reg180c2a2c[25:16] <= write_data[25:16];
           reg180c2a2c[7:4] <= write_data[7:4];
           reg180c2a2c[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2a2c[25:16] <= reg180c2a2c[25:16];
           reg180c2a2c[7:4] <= reg180c2a2c[7:4];
           reg180c2a2c[3:0] <= reg180c2a2c[3:0];
         end
     end
  end

//addr = 0x180c2a30
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a30[21:16] <= 6'hf;
         reg180c2a30[2] <= 1'h0;
         reg180c2a30[1] <= 1'h0;
         reg180c2a30[0] <= 1'h1;
       end
     else begin
       if (write_en[125])
         begin
           reg180c2a30[21:16] <= write_data[21:16];
           reg180c2a30[2] <= write_data[2];
           reg180c2a30[1] <= write_data[1];
           reg180c2a30[0] <= write_data[0];
         end
       else
         begin
           reg180c2a30[21:16] <= reg180c2a30[21:16];
           reg180c2a30[2] <= reg180c2a30[2];
           reg180c2a30[1] <= reg180c2a30[1];
           reg180c2a30[0] <= reg180c2a30[0];
         end
     end
  end

//addr = 0x180c2a34
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a34[25:16] <= 10'h3ff;
         reg180c2a34[0] <= 1'h0;
       end
     else begin
       if (write_en[126])
         begin
           reg180c2a34[25:16] <= write_data[25:16];
           reg180c2a34[0] <= write_data[0];
         end
       else
         begin
           reg180c2a34[25:16] <= reg180c2a34[25:16];
           reg180c2a34[0] <= reg180c2a34[0];
         end
     end
  end

//addr = 0x180c2a3c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a3c[23:20] <= 4'hf;
         reg180c2a3c[19:16] <= 4'hf;
         reg180c2a3c[15:8] <= 8'hff;
         reg180c2a3c[7:0] <= 8'hff;
       end
     else begin
       if (write_en[127])
         begin
           reg180c2a3c[23:20] <= write_data[23:20];
           reg180c2a3c[19:16] <= write_data[19:16];
           reg180c2a3c[15:8] <= write_data[15:8];
           reg180c2a3c[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2a3c[23:20] <= reg180c2a3c[23:20];
           reg180c2a3c[19:16] <= reg180c2a3c[19:16];
           reg180c2a3c[15:8] <= reg180c2a3c[15:8];
           reg180c2a3c[7:0] <= reg180c2a3c[7:0];
         end
     end
  end

//addr = 0x180c2a60
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a60[31:28] <= 4'h2;
         reg180c2a60[27:24] <= 4'h9;
         reg180c2a60[23:20] <= 4'h8;
         reg180c2a60[19:16] <= 4'h4;
         reg180c2a60[15:12] <= 4'h0;
         reg180c2a60[11] <= 1'h1;
         reg180c2a60[10] <= 1'h0;
         reg180c2a60[9:8] <= 2'h0;
         reg180c2a60[7] <= 1'h0;
         reg180c2a60[4] <= 1'h0;
         reg180c2a60[3] <= 1'h0;
         reg180c2a60[2] <= 1'h1;
         reg180c2a60[1] <= 1'h1;
       end
     else begin
       if (write_en[128])
         begin
           reg180c2a60[31:28] <= write_data[31:28];
           reg180c2a60[27:24] <= write_data[27:24];
           reg180c2a60[23:20] <= write_data[23:20];
           reg180c2a60[19:16] <= write_data[19:16];
           reg180c2a60[15:12] <= write_data[15:12];
           reg180c2a60[11] <= write_data[11];
           reg180c2a60[10] <= write_data[10];
           reg180c2a60[9:8] <= write_data[9:8];
           reg180c2a60[7] <= write_data[7];
           reg180c2a60[4] <= write_data[4];
           reg180c2a60[3] <= write_data[3];
           reg180c2a60[2] <= write_data[2];
           reg180c2a60[1] <= write_data[1];
         end
       else
         begin
           reg180c2a60[31:28] <= reg180c2a60[31:28];
           reg180c2a60[27:24] <= reg180c2a60[27:24];
           reg180c2a60[23:20] <= reg180c2a60[23:20];
           reg180c2a60[19:16] <= reg180c2a60[19:16];
           reg180c2a60[15:12] <= reg180c2a60[15:12];
           reg180c2a60[11] <= reg180c2a60[11];
           reg180c2a60[10] <= reg180c2a60[10];
           reg180c2a60[9:8] <= reg180c2a60[9:8];
           reg180c2a60[7] <= reg180c2a60[7];
           reg180c2a60[4] <= reg180c2a60[4];
           reg180c2a60[3] <= reg180c2a60[3];
           reg180c2a60[2] <= reg180c2a60[2];
           reg180c2a60[1] <= reg180c2a60[1];
         end
     end
  end

//addr = 0x180c2a64
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a64[31:24] <= 8'h30;
         reg180c2a64[15:8] <= 8'h6f;
       end
     else begin
       if (write_en[129])
         begin
           reg180c2a64[31:24] <= write_data[31:24];
           reg180c2a64[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2a64[31:24] <= reg180c2a64[31:24];
           reg180c2a64[15:8] <= reg180c2a64[15:8];
         end
     end
  end

//addr = 0x180c2a68
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a68[31:20] <= 12'h300;
         reg180c2a68[19:8] <= 12'h180;
         reg180c2a68[3:0] <= 4'h8;
       end
     else begin
       if (write_en[130])
         begin
           reg180c2a68[31:20] <= write_data[31:20];
           reg180c2a68[19:8] <= write_data[19:8];
           reg180c2a68[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2a68[31:20] <= reg180c2a68[31:20];
           reg180c2a68[19:8] <= reg180c2a68[19:8];
           reg180c2a68[3:0] <= reg180c2a68[3:0];
         end
     end
  end

//addr = 0x180c2a6c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a6c[31:28] <= 4'h6;
         reg180c2a6c[25:20] <= 6'ha;
         reg180c2a6c[19:8] <= 12'h100;
         reg180c2a6c[7:4] <= 4'h4;
         reg180c2a6c[0] <= 1'h1;
       end
     else begin
       if (write_en[131])
         begin
           reg180c2a6c[31:28] <= write_data[31:28];
           reg180c2a6c[25:20] <= write_data[25:20];
           reg180c2a6c[19:8] <= write_data[19:8];
           reg180c2a6c[7:4] <= write_data[7:4];
           reg180c2a6c[0] <= write_data[0];
         end
       else
         begin
           reg180c2a6c[31:28] <= reg180c2a6c[31:28];
           reg180c2a6c[25:20] <= reg180c2a6c[25:20];
           reg180c2a6c[19:8] <= reg180c2a6c[19:8];
           reg180c2a6c[7:4] <= reg180c2a6c[7:4];
           reg180c2a6c[0] <= reg180c2a6c[0];
         end
     end
  end

//addr = 0x180c2a70
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a70[9:0] <= 10'h0;
       end
     else begin
       if (write_en[132])
         begin
           reg180c2a70[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2a70[9:0] <= reg180c2a70[9:0];
         end
     end
  end

//addr = 0x180c2a74
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a74[31:28] <= 4'h2;
         reg180c2a74[27:24] <= 4'h4;
         reg180c2a74[23:20] <= 4'hc;
         reg180c2a74[19:16] <= 4'h4;
         reg180c2a74[15:12] <= 4'h0;
         reg180c2a74[11:8] <= 4'h2;
       end
     else begin
       if (write_en[133])
         begin
           reg180c2a74[31:28] <= write_data[31:28];
           reg180c2a74[27:24] <= write_data[27:24];
           reg180c2a74[23:20] <= write_data[23:20];
           reg180c2a74[19:16] <= write_data[19:16];
           reg180c2a74[15:12] <= write_data[15:12];
           reg180c2a74[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2a74[31:28] <= reg180c2a74[31:28];
           reg180c2a74[27:24] <= reg180c2a74[27:24];
           reg180c2a74[23:20] <= reg180c2a74[23:20];
           reg180c2a74[19:16] <= reg180c2a74[19:16];
           reg180c2a74[15:12] <= reg180c2a74[15:12];
           reg180c2a74[11:8] <= reg180c2a74[11:8];
         end
     end
  end

//addr = 0x180c2a80
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a80[31:28] <= 4'h2;
         reg180c2a80[27:24] <= 4'h9;
         reg180c2a80[23:20] <= 4'h8;
         reg180c2a80[19:16] <= 4'h4;
         reg180c2a80[15:12] <= 4'h0;
         reg180c2a80[11] <= 1'h1;
         reg180c2a80[10] <= 1'h0;
         reg180c2a80[9:8] <= 2'h0;
         reg180c2a80[7] <= 1'h0;
         reg180c2a80[4] <= 1'h0;
         reg180c2a80[3] <= 1'h1;
         reg180c2a80[2] <= 1'h1;
         reg180c2a80[1] <= 1'h1;
       end
     else begin
       if (write_en[134])
         begin
           reg180c2a80[31:28] <= write_data[31:28];
           reg180c2a80[27:24] <= write_data[27:24];
           reg180c2a80[23:20] <= write_data[23:20];
           reg180c2a80[19:16] <= write_data[19:16];
           reg180c2a80[15:12] <= write_data[15:12];
           reg180c2a80[11] <= write_data[11];
           reg180c2a80[10] <= write_data[10];
           reg180c2a80[9:8] <= write_data[9:8];
           reg180c2a80[7] <= write_data[7];
           reg180c2a80[4] <= write_data[4];
           reg180c2a80[3] <= write_data[3];
           reg180c2a80[2] <= write_data[2];
           reg180c2a80[1] <= write_data[1];
         end
       else
         begin
           reg180c2a80[31:28] <= reg180c2a80[31:28];
           reg180c2a80[27:24] <= reg180c2a80[27:24];
           reg180c2a80[23:20] <= reg180c2a80[23:20];
           reg180c2a80[19:16] <= reg180c2a80[19:16];
           reg180c2a80[15:12] <= reg180c2a80[15:12];
           reg180c2a80[11] <= reg180c2a80[11];
           reg180c2a80[10] <= reg180c2a80[10];
           reg180c2a80[9:8] <= reg180c2a80[9:8];
           reg180c2a80[7] <= reg180c2a80[7];
           reg180c2a80[4] <= reg180c2a80[4];
           reg180c2a80[3] <= reg180c2a80[3];
           reg180c2a80[2] <= reg180c2a80[2];
           reg180c2a80[1] <= reg180c2a80[1];
         end
     end
  end

//addr = 0x180c2a84
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a84[31:24] <= 8'h0;
         reg180c2a84[15:8] <= 8'h60;
       end
     else begin
       if (write_en[135])
         begin
           reg180c2a84[31:24] <= write_data[31:24];
           reg180c2a84[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2a84[31:24] <= reg180c2a84[31:24];
           reg180c2a84[15:8] <= reg180c2a84[15:8];
         end
     end
  end

//addr = 0x180c2a88
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a88[31:20] <= 12'hfff;
         reg180c2a88[19:8] <= 12'h200;
         reg180c2a88[3:0] <= 4'h4;
       end
     else begin
       if (write_en[136])
         begin
           reg180c2a88[31:20] <= write_data[31:20];
           reg180c2a88[19:8] <= write_data[19:8];
           reg180c2a88[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2a88[31:20] <= reg180c2a88[31:20];
           reg180c2a88[19:8] <= reg180c2a88[19:8];
           reg180c2a88[3:0] <= reg180c2a88[3:0];
         end
     end
  end

//addr = 0x180c2a8c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a8c[31:28] <= 4'h4;
         reg180c2a8c[25:20] <= 6'h10;
         reg180c2a8c[19:8] <= 12'h100;
         reg180c2a8c[7:4] <= 4'h3;
         reg180c2a8c[0] <= 1'h1;
       end
     else begin
       if (write_en[137])
         begin
           reg180c2a8c[31:28] <= write_data[31:28];
           reg180c2a8c[25:20] <= write_data[25:20];
           reg180c2a8c[19:8] <= write_data[19:8];
           reg180c2a8c[7:4] <= write_data[7:4];
           reg180c2a8c[0] <= write_data[0];
         end
       else
         begin
           reg180c2a8c[31:28] <= reg180c2a8c[31:28];
           reg180c2a8c[25:20] <= reg180c2a8c[25:20];
           reg180c2a8c[19:8] <= reg180c2a8c[19:8];
           reg180c2a8c[7:4] <= reg180c2a8c[7:4];
           reg180c2a8c[0] <= reg180c2a8c[0];
         end
     end
  end

//addr = 0x180c2a90
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a90[9:0] <= 10'h0;
       end
     else begin
       if (write_en[138])
         begin
           reg180c2a90[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2a90[9:0] <= reg180c2a90[9:0];
         end
     end
  end

//addr = 0x180c2a94
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2a94[31:28] <= 4'h2;
         reg180c2a94[27:24] <= 4'h4;
         reg180c2a94[23:20] <= 4'hc;
         reg180c2a94[19:16] <= 4'h4;
         reg180c2a94[15:12] <= 4'h0;
         reg180c2a94[11:8] <= 4'h2;
       end
     else begin
       if (write_en[139])
         begin
           reg180c2a94[31:28] <= write_data[31:28];
           reg180c2a94[27:24] <= write_data[27:24];
           reg180c2a94[23:20] <= write_data[23:20];
           reg180c2a94[19:16] <= write_data[19:16];
           reg180c2a94[15:12] <= write_data[15:12];
           reg180c2a94[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2a94[31:28] <= reg180c2a94[31:28];
           reg180c2a94[27:24] <= reg180c2a94[27:24];
           reg180c2a94[23:20] <= reg180c2a94[23:20];
           reg180c2a94[19:16] <= reg180c2a94[19:16];
           reg180c2a94[15:12] <= reg180c2a94[15:12];
           reg180c2a94[11:8] <= reg180c2a94[11:8];
         end
     end
  end

//addr = 0x180c2aa0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2aa0[31:28] <= 4'h2;
         reg180c2aa0[27:24] <= 4'h9;
         reg180c2aa0[23:20] <= 4'h8;
         reg180c2aa0[19:16] <= 4'h4;
         reg180c2aa0[15:12] <= 4'h0;
         reg180c2aa0[11] <= 1'h1;
         reg180c2aa0[10] <= 1'h0;
         reg180c2aa0[9:8] <= 2'h0;
         reg180c2aa0[7] <= 1'h0;
         reg180c2aa0[4] <= 1'h0;
         reg180c2aa0[3] <= 1'h1;
         reg180c2aa0[2] <= 1'h1;
         reg180c2aa0[1] <= 1'h1;
       end
     else begin
       if (write_en[140])
         begin
           reg180c2aa0[31:28] <= write_data[31:28];
           reg180c2aa0[27:24] <= write_data[27:24];
           reg180c2aa0[23:20] <= write_data[23:20];
           reg180c2aa0[19:16] <= write_data[19:16];
           reg180c2aa0[15:12] <= write_data[15:12];
           reg180c2aa0[11] <= write_data[11];
           reg180c2aa0[10] <= write_data[10];
           reg180c2aa0[9:8] <= write_data[9:8];
           reg180c2aa0[7] <= write_data[7];
           reg180c2aa0[4] <= write_data[4];
           reg180c2aa0[3] <= write_data[3];
           reg180c2aa0[2] <= write_data[2];
           reg180c2aa0[1] <= write_data[1];
         end
       else
         begin
           reg180c2aa0[31:28] <= reg180c2aa0[31:28];
           reg180c2aa0[27:24] <= reg180c2aa0[27:24];
           reg180c2aa0[23:20] <= reg180c2aa0[23:20];
           reg180c2aa0[19:16] <= reg180c2aa0[19:16];
           reg180c2aa0[15:12] <= reg180c2aa0[15:12];
           reg180c2aa0[11] <= reg180c2aa0[11];
           reg180c2aa0[10] <= reg180c2aa0[10];
           reg180c2aa0[9:8] <= reg180c2aa0[9:8];
           reg180c2aa0[7] <= reg180c2aa0[7];
           reg180c2aa0[4] <= reg180c2aa0[4];
           reg180c2aa0[3] <= reg180c2aa0[3];
           reg180c2aa0[2] <= reg180c2aa0[2];
           reg180c2aa0[1] <= reg180c2aa0[1];
         end
     end
  end

//addr = 0x180c2aa4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2aa4[31:24] <= 8'h40;
         reg180c2aa4[15:8] <= 8'h7f;
       end
     else begin
       if (write_en[141])
         begin
           reg180c2aa4[31:24] <= write_data[31:24];
           reg180c2aa4[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2aa4[31:24] <= reg180c2aa4[31:24];
           reg180c2aa4[15:8] <= reg180c2aa4[15:8];
         end
     end
  end

//addr = 0x180c2aa8
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2aa8[31:20] <= 12'hfff;
         reg180c2aa8[19:8] <= 12'h96;
         reg180c2aa8[3:0] <= 4'h8;
       end
     else begin
       if (write_en[142])
         begin
           reg180c2aa8[31:20] <= write_data[31:20];
           reg180c2aa8[19:8] <= write_data[19:8];
           reg180c2aa8[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2aa8[31:20] <= reg180c2aa8[31:20];
           reg180c2aa8[19:8] <= reg180c2aa8[19:8];
           reg180c2aa8[3:0] <= reg180c2aa8[3:0];
         end
     end
  end

//addr = 0x180c2aac
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2aac[31:28] <= 4'h5;
         reg180c2aac[25:20] <= 6'h30;
         reg180c2aac[19:8] <= 12'h150;
         reg180c2aac[7:4] <= 4'h7;
         reg180c2aac[0] <= 1'h1;
       end
     else begin
       if (write_en[143])
         begin
           reg180c2aac[31:28] <= write_data[31:28];
           reg180c2aac[25:20] <= write_data[25:20];
           reg180c2aac[19:8] <= write_data[19:8];
           reg180c2aac[7:4] <= write_data[7:4];
           reg180c2aac[0] <= write_data[0];
         end
       else
         begin
           reg180c2aac[31:28] <= reg180c2aac[31:28];
           reg180c2aac[25:20] <= reg180c2aac[25:20];
           reg180c2aac[19:8] <= reg180c2aac[19:8];
           reg180c2aac[7:4] <= reg180c2aac[7:4];
           reg180c2aac[0] <= reg180c2aac[0];
         end
     end
  end

//addr = 0x180c2ab0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ab0[9:0] <= 10'h0;
       end
     else begin
       if (write_en[144])
         begin
           reg180c2ab0[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2ab0[9:0] <= reg180c2ab0[9:0];
         end
     end
  end

//addr = 0x180c2ab4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ab4[31:28] <= 4'h2;
         reg180c2ab4[27:24] <= 4'h4;
         reg180c2ab4[23:20] <= 4'hc;
         reg180c2ab4[19:16] <= 4'h4;
         reg180c2ab4[15:12] <= 4'h0;
         reg180c2ab4[11:8] <= 4'h2;
       end
     else begin
       if (write_en[145])
         begin
           reg180c2ab4[31:28] <= write_data[31:28];
           reg180c2ab4[27:24] <= write_data[27:24];
           reg180c2ab4[23:20] <= write_data[23:20];
           reg180c2ab4[19:16] <= write_data[19:16];
           reg180c2ab4[15:12] <= write_data[15:12];
           reg180c2ab4[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2ab4[31:28] <= reg180c2ab4[31:28];
           reg180c2ab4[27:24] <= reg180c2ab4[27:24];
           reg180c2ab4[23:20] <= reg180c2ab4[23:20];
           reg180c2ab4[19:16] <= reg180c2ab4[19:16];
           reg180c2ab4[15:12] <= reg180c2ab4[15:12];
           reg180c2ab4[11:8] <= reg180c2ab4[11:8];
         end
     end
  end

//addr = 0x180c2ac0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ac0[31:28] <= 4'h2;
         reg180c2ac0[27:24] <= 4'h9;
         reg180c2ac0[23:20] <= 4'h8;
         reg180c2ac0[19:16] <= 4'h4;
         reg180c2ac0[15:12] <= 4'h0;
         reg180c2ac0[11] <= 1'h1;
         reg180c2ac0[10] <= 1'h0;
         reg180c2ac0[9:8] <= 2'h0;
         reg180c2ac0[7] <= 1'h0;
         reg180c2ac0[4] <= 1'h0;
         reg180c2ac0[3] <= 1'h1;
         reg180c2ac0[2] <= 1'h1;
         reg180c2ac0[1] <= 1'h1;
       end
     else begin
       if (write_en[146])
         begin
           reg180c2ac0[31:28] <= write_data[31:28];
           reg180c2ac0[27:24] <= write_data[27:24];
           reg180c2ac0[23:20] <= write_data[23:20];
           reg180c2ac0[19:16] <= write_data[19:16];
           reg180c2ac0[15:12] <= write_data[15:12];
           reg180c2ac0[11] <= write_data[11];
           reg180c2ac0[10] <= write_data[10];
           reg180c2ac0[9:8] <= write_data[9:8];
           reg180c2ac0[7] <= write_data[7];
           reg180c2ac0[4] <= write_data[4];
           reg180c2ac0[3] <= write_data[3];
           reg180c2ac0[2] <= write_data[2];
           reg180c2ac0[1] <= write_data[1];
         end
       else
         begin
           reg180c2ac0[31:28] <= reg180c2ac0[31:28];
           reg180c2ac0[27:24] <= reg180c2ac0[27:24];
           reg180c2ac0[23:20] <= reg180c2ac0[23:20];
           reg180c2ac0[19:16] <= reg180c2ac0[19:16];
           reg180c2ac0[15:12] <= reg180c2ac0[15:12];
           reg180c2ac0[11] <= reg180c2ac0[11];
           reg180c2ac0[10] <= reg180c2ac0[10];
           reg180c2ac0[9:8] <= reg180c2ac0[9:8];
           reg180c2ac0[7] <= reg180c2ac0[7];
           reg180c2ac0[4] <= reg180c2ac0[4];
           reg180c2ac0[3] <= reg180c2ac0[3];
           reg180c2ac0[2] <= reg180c2ac0[2];
           reg180c2ac0[1] <= reg180c2ac0[1];
         end
     end
  end

//addr = 0x180c2ac4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ac4[31:24] <= 8'h30;
         reg180c2ac4[15:8] <= 8'h75;
       end
     else begin
       if (write_en[147])
         begin
           reg180c2ac4[31:24] <= write_data[31:24];
           reg180c2ac4[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2ac4[31:24] <= reg180c2ac4[31:24];
           reg180c2ac4[15:8] <= reg180c2ac4[15:8];
         end
     end
  end

//addr = 0x180c2ac8
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ac8[31:20] <= 12'hfff;
         reg180c2ac8[19:8] <= 12'h100;
         reg180c2ac8[3:0] <= 4'h8;
       end
     else begin
       if (write_en[148])
         begin
           reg180c2ac8[31:20] <= write_data[31:20];
           reg180c2ac8[19:8] <= write_data[19:8];
           reg180c2ac8[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2ac8[31:20] <= reg180c2ac8[31:20];
           reg180c2ac8[19:8] <= reg180c2ac8[19:8];
           reg180c2ac8[3:0] <= reg180c2ac8[3:0];
         end
     end
  end

//addr = 0x180c2acc
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2acc[31:28] <= 4'h5;
         reg180c2acc[25:20] <= 6'h30;
         reg180c2acc[19:8] <= 12'h130;
         reg180c2acc[7:4] <= 4'h6;
         reg180c2acc[0] <= 1'h1;
       end
     else begin
       if (write_en[149])
         begin
           reg180c2acc[31:28] <= write_data[31:28];
           reg180c2acc[25:20] <= write_data[25:20];
           reg180c2acc[19:8] <= write_data[19:8];
           reg180c2acc[7:4] <= write_data[7:4];
           reg180c2acc[0] <= write_data[0];
         end
       else
         begin
           reg180c2acc[31:28] <= reg180c2acc[31:28];
           reg180c2acc[25:20] <= reg180c2acc[25:20];
           reg180c2acc[19:8] <= reg180c2acc[19:8];
           reg180c2acc[7:4] <= reg180c2acc[7:4];
           reg180c2acc[0] <= reg180c2acc[0];
         end
     end
  end

//addr = 0x180c2ad0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ad0[9:0] <= 10'h0;
       end
     else begin
       if (write_en[150])
         begin
           reg180c2ad0[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2ad0[9:0] <= reg180c2ad0[9:0];
         end
     end
  end

//addr = 0x180c2ad4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ad4[31:28] <= 4'h2;
         reg180c2ad4[27:24] <= 4'h4;
         reg180c2ad4[23:20] <= 4'hc;
         reg180c2ad4[19:16] <= 4'h4;
         reg180c2ad4[15:12] <= 4'h0;
         reg180c2ad4[11:8] <= 4'h2;
       end
     else begin
       if (write_en[151])
         begin
           reg180c2ad4[31:28] <= write_data[31:28];
           reg180c2ad4[27:24] <= write_data[27:24];
           reg180c2ad4[23:20] <= write_data[23:20];
           reg180c2ad4[19:16] <= write_data[19:16];
           reg180c2ad4[15:12] <= write_data[15:12];
           reg180c2ad4[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2ad4[31:28] <= reg180c2ad4[31:28];
           reg180c2ad4[27:24] <= reg180c2ad4[27:24];
           reg180c2ad4[23:20] <= reg180c2ad4[23:20];
           reg180c2ad4[19:16] <= reg180c2ad4[19:16];
           reg180c2ad4[15:12] <= reg180c2ad4[15:12];
           reg180c2ad4[11:8] <= reg180c2ad4[11:8];
         end
     end
  end

//addr = 0x180c2ae0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ae0[31:28] <= 4'h2;
         reg180c2ae0[27:24] <= 4'h9;
         reg180c2ae0[23:20] <= 4'h8;
         reg180c2ae0[19:16] <= 4'h4;
         reg180c2ae0[15:12] <= 4'h0;
         reg180c2ae0[11] <= 1'h1;
         reg180c2ae0[10] <= 1'h0;
         reg180c2ae0[9:8] <= 2'h0;
         reg180c2ae0[7] <= 1'h0;
         reg180c2ae0[4] <= 1'h0;
         reg180c2ae0[3] <= 1'h1;
         reg180c2ae0[2] <= 1'h1;
         reg180c2ae0[1] <= 1'h1;
       end
     else begin
       if (write_en[152])
         begin
           reg180c2ae0[31:28] <= write_data[31:28];
           reg180c2ae0[27:24] <= write_data[27:24];
           reg180c2ae0[23:20] <= write_data[23:20];
           reg180c2ae0[19:16] <= write_data[19:16];
           reg180c2ae0[15:12] <= write_data[15:12];
           reg180c2ae0[11] <= write_data[11];
           reg180c2ae0[10] <= write_data[10];
           reg180c2ae0[9:8] <= write_data[9:8];
           reg180c2ae0[7] <= write_data[7];
           reg180c2ae0[4] <= write_data[4];
           reg180c2ae0[3] <= write_data[3];
           reg180c2ae0[2] <= write_data[2];
           reg180c2ae0[1] <= write_data[1];
         end
       else
         begin
           reg180c2ae0[31:28] <= reg180c2ae0[31:28];
           reg180c2ae0[27:24] <= reg180c2ae0[27:24];
           reg180c2ae0[23:20] <= reg180c2ae0[23:20];
           reg180c2ae0[19:16] <= reg180c2ae0[19:16];
           reg180c2ae0[15:12] <= reg180c2ae0[15:12];
           reg180c2ae0[11] <= reg180c2ae0[11];
           reg180c2ae0[10] <= reg180c2ae0[10];
           reg180c2ae0[9:8] <= reg180c2ae0[9:8];
           reg180c2ae0[7] <= reg180c2ae0[7];
           reg180c2ae0[4] <= reg180c2ae0[4];
           reg180c2ae0[3] <= reg180c2ae0[3];
           reg180c2ae0[2] <= reg180c2ae0[2];
           reg180c2ae0[1] <= reg180c2ae0[1];
         end
     end
  end

//addr = 0x180c2ae4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ae4[31:24] <= 8'h20;
         reg180c2ae4[15:8] <= 8'h60;
       end
     else begin
       if (write_en[153])
         begin
           reg180c2ae4[31:24] <= write_data[31:24];
           reg180c2ae4[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2ae4[31:24] <= reg180c2ae4[31:24];
           reg180c2ae4[15:8] <= reg180c2ae4[15:8];
         end
     end
  end

//addr = 0x180c2ae8
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ae8[31:20] <= 12'hfff;
         reg180c2ae8[19:8] <= 12'h100;
         reg180c2ae8[3:0] <= 4'h8;
       end
     else begin
       if (write_en[154])
         begin
           reg180c2ae8[31:20] <= write_data[31:20];
           reg180c2ae8[19:8] <= write_data[19:8];
           reg180c2ae8[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2ae8[31:20] <= reg180c2ae8[31:20];
           reg180c2ae8[19:8] <= reg180c2ae8[19:8];
           reg180c2ae8[3:0] <= reg180c2ae8[3:0];
         end
     end
  end

//addr = 0x180c2aec
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2aec[31:28] <= 4'h8;
         reg180c2aec[25:20] <= 6'h30;
         reg180c2aec[19:8] <= 12'ha0;
         reg180c2aec[7:4] <= 4'h5;
         reg180c2aec[0] <= 1'h1;
       end
     else begin
       if (write_en[155])
         begin
           reg180c2aec[31:28] <= write_data[31:28];
           reg180c2aec[25:20] <= write_data[25:20];
           reg180c2aec[19:8] <= write_data[19:8];
           reg180c2aec[7:4] <= write_data[7:4];
           reg180c2aec[0] <= write_data[0];
         end
       else
         begin
           reg180c2aec[31:28] <= reg180c2aec[31:28];
           reg180c2aec[25:20] <= reg180c2aec[25:20];
           reg180c2aec[19:8] <= reg180c2aec[19:8];
           reg180c2aec[7:4] <= reg180c2aec[7:4];
           reg180c2aec[0] <= reg180c2aec[0];
         end
     end
  end

//addr = 0x180c2af0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2af0[9:0] <= 10'h0;
       end
     else begin
       if (write_en[156])
         begin
           reg180c2af0[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2af0[9:0] <= reg180c2af0[9:0];
         end
     end
  end

//addr = 0x180c2af4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2af4[31:28] <= 4'h2;
         reg180c2af4[27:24] <= 4'h4;
         reg180c2af4[23:20] <= 4'hc;
         reg180c2af4[19:16] <= 4'h4;
         reg180c2af4[15:12] <= 4'h0;
         reg180c2af4[11:8] <= 4'h2;
       end
     else begin
       if (write_en[157])
         begin
           reg180c2af4[31:28] <= write_data[31:28];
           reg180c2af4[27:24] <= write_data[27:24];
           reg180c2af4[23:20] <= write_data[23:20];
           reg180c2af4[19:16] <= write_data[19:16];
           reg180c2af4[15:12] <= write_data[15:12];
           reg180c2af4[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2af4[31:28] <= reg180c2af4[31:28];
           reg180c2af4[27:24] <= reg180c2af4[27:24];
           reg180c2af4[23:20] <= reg180c2af4[23:20];
           reg180c2af4[19:16] <= reg180c2af4[19:16];
           reg180c2af4[15:12] <= reg180c2af4[15:12];
           reg180c2af4[11:8] <= reg180c2af4[11:8];
         end
     end
  end

//addr = 0x180c2b00
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b00[31:28] <= 4'h2;
         reg180c2b00[27:24] <= 4'h9;
         reg180c2b00[23:20] <= 4'h8;
         reg180c2b00[19:16] <= 4'h4;
         reg180c2b00[15:12] <= 4'h0;
         reg180c2b00[11] <= 1'h1;
         reg180c2b00[10] <= 1'h0;
         reg180c2b00[9:8] <= 2'h0;
         reg180c2b00[7] <= 1'h0;
         reg180c2b00[4] <= 1'h0;
         reg180c2b00[3] <= 1'h1;
         reg180c2b00[2] <= 1'h1;
         reg180c2b00[1] <= 1'h1;
       end
     else begin
       if (write_en[158])
         begin
           reg180c2b00[31:28] <= write_data[31:28];
           reg180c2b00[27:24] <= write_data[27:24];
           reg180c2b00[23:20] <= write_data[23:20];
           reg180c2b00[19:16] <= write_data[19:16];
           reg180c2b00[15:12] <= write_data[15:12];
           reg180c2b00[11] <= write_data[11];
           reg180c2b00[10] <= write_data[10];
           reg180c2b00[9:8] <= write_data[9:8];
           reg180c2b00[7] <= write_data[7];
           reg180c2b00[4] <= write_data[4];
           reg180c2b00[3] <= write_data[3];
           reg180c2b00[2] <= write_data[2];
           reg180c2b00[1] <= write_data[1];
         end
       else
         begin
           reg180c2b00[31:28] <= reg180c2b00[31:28];
           reg180c2b00[27:24] <= reg180c2b00[27:24];
           reg180c2b00[23:20] <= reg180c2b00[23:20];
           reg180c2b00[19:16] <= reg180c2b00[19:16];
           reg180c2b00[15:12] <= reg180c2b00[15:12];
           reg180c2b00[11] <= reg180c2b00[11];
           reg180c2b00[10] <= reg180c2b00[10];
           reg180c2b00[9:8] <= reg180c2b00[9:8];
           reg180c2b00[7] <= reg180c2b00[7];
           reg180c2b00[4] <= reg180c2b00[4];
           reg180c2b00[3] <= reg180c2b00[3];
           reg180c2b00[2] <= reg180c2b00[2];
           reg180c2b00[1] <= reg180c2b00[1];
         end
     end
  end

//addr = 0x180c2b04
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b04[31:24] <= 8'h0;
         reg180c2b04[15:8] <= 8'h50;
       end
     else begin
       if (write_en[159])
         begin
           reg180c2b04[31:24] <= write_data[31:24];
           reg180c2b04[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2b04[31:24] <= reg180c2b04[31:24];
           reg180c2b04[15:8] <= reg180c2b04[15:8];
         end
     end
  end

//addr = 0x180c2b08
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b08[31:20] <= 12'hfff;
         reg180c2b08[19:8] <= 12'h100;
         reg180c2b08[3:0] <= 4'h8;
       end
     else begin
       if (write_en[160])
         begin
           reg180c2b08[31:20] <= write_data[31:20];
           reg180c2b08[19:8] <= write_data[19:8];
           reg180c2b08[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2b08[31:20] <= reg180c2b08[31:20];
           reg180c2b08[19:8] <= reg180c2b08[19:8];
           reg180c2b08[3:0] <= reg180c2b08[3:0];
         end
     end
  end

//addr = 0x180c2b0c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b0c[31:28] <= 4'h5;
         reg180c2b0c[25:20] <= 6'h30;
         reg180c2b0c[19:8] <= 12'h100;
         reg180c2b0c[7:4] <= 4'h4;
         reg180c2b0c[0] <= 1'h1;
       end
     else begin
       if (write_en[161])
         begin
           reg180c2b0c[31:28] <= write_data[31:28];
           reg180c2b0c[25:20] <= write_data[25:20];
           reg180c2b0c[19:8] <= write_data[19:8];
           reg180c2b0c[7:4] <= write_data[7:4];
           reg180c2b0c[0] <= write_data[0];
         end
       else
         begin
           reg180c2b0c[31:28] <= reg180c2b0c[31:28];
           reg180c2b0c[25:20] <= reg180c2b0c[25:20];
           reg180c2b0c[19:8] <= reg180c2b0c[19:8];
           reg180c2b0c[7:4] <= reg180c2b0c[7:4];
           reg180c2b0c[0] <= reg180c2b0c[0];
         end
     end
  end

//addr = 0x180c2b10
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b10[9:0] <= 10'h0;
       end
     else begin
       if (write_en[162])
         begin
           reg180c2b10[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2b10[9:0] <= reg180c2b10[9:0];
         end
     end
  end

//addr = 0x180c2b14
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b14[31:28] <= 4'h2;
         reg180c2b14[27:24] <= 4'h4;
         reg180c2b14[23:20] <= 4'hc;
         reg180c2b14[19:16] <= 4'h4;
         reg180c2b14[15:12] <= 4'h0;
         reg180c2b14[11:8] <= 4'h2;
       end
     else begin
       if (write_en[163])
         begin
           reg180c2b14[31:28] <= write_data[31:28];
           reg180c2b14[27:24] <= write_data[27:24];
           reg180c2b14[23:20] <= write_data[23:20];
           reg180c2b14[19:16] <= write_data[19:16];
           reg180c2b14[15:12] <= write_data[15:12];
           reg180c2b14[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2b14[31:28] <= reg180c2b14[31:28];
           reg180c2b14[27:24] <= reg180c2b14[27:24];
           reg180c2b14[23:20] <= reg180c2b14[23:20];
           reg180c2b14[19:16] <= reg180c2b14[19:16];
           reg180c2b14[15:12] <= reg180c2b14[15:12];
           reg180c2b14[11:8] <= reg180c2b14[11:8];
         end
     end
  end

//addr = 0x180c2b20
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b20[31:28] <= 4'h2;
         reg180c2b20[27:24] <= 4'h9;
         reg180c2b20[23:20] <= 4'h8;
         reg180c2b20[19:16] <= 4'h4;
         reg180c2b20[15:12] <= 4'h0;
         reg180c2b20[11] <= 1'h1;
         reg180c2b20[10] <= 1'h0;
         reg180c2b20[9:8] <= 2'h0;
         reg180c2b20[7] <= 1'h0;
         reg180c2b20[4] <= 1'h0;
         reg180c2b20[3] <= 1'h0;
         reg180c2b20[2] <= 1'h1;
         reg180c2b20[1] <= 1'h1;
       end
     else begin
       if (write_en[164])
         begin
           reg180c2b20[31:28] <= write_data[31:28];
           reg180c2b20[27:24] <= write_data[27:24];
           reg180c2b20[23:20] <= write_data[23:20];
           reg180c2b20[19:16] <= write_data[19:16];
           reg180c2b20[15:12] <= write_data[15:12];
           reg180c2b20[11] <= write_data[11];
           reg180c2b20[10] <= write_data[10];
           reg180c2b20[9:8] <= write_data[9:8];
           reg180c2b20[7] <= write_data[7];
           reg180c2b20[4] <= write_data[4];
           reg180c2b20[3] <= write_data[3];
           reg180c2b20[2] <= write_data[2];
           reg180c2b20[1] <= write_data[1];
         end
       else
         begin
           reg180c2b20[31:28] <= reg180c2b20[31:28];
           reg180c2b20[27:24] <= reg180c2b20[27:24];
           reg180c2b20[23:20] <= reg180c2b20[23:20];
           reg180c2b20[19:16] <= reg180c2b20[19:16];
           reg180c2b20[15:12] <= reg180c2b20[15:12];
           reg180c2b20[11] <= reg180c2b20[11];
           reg180c2b20[10] <= reg180c2b20[10];
           reg180c2b20[9:8] <= reg180c2b20[9:8];
           reg180c2b20[7] <= reg180c2b20[7];
           reg180c2b20[4] <= reg180c2b20[4];
           reg180c2b20[3] <= reg180c2b20[3];
           reg180c2b20[2] <= reg180c2b20[2];
           reg180c2b20[1] <= reg180c2b20[1];
         end
     end
  end

//addr = 0x180c2b24
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b24[31:24] <= 8'h0;
         reg180c2b24[15:8] <= 8'h50;
       end
     else begin
       if (write_en[165])
         begin
           reg180c2b24[31:24] <= write_data[31:24];
           reg180c2b24[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2b24[31:24] <= reg180c2b24[31:24];
           reg180c2b24[15:8] <= reg180c2b24[15:8];
         end
     end
  end

//addr = 0x180c2b28
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b28[31:20] <= 12'h800;
         reg180c2b28[19:8] <= 12'h100;
         reg180c2b28[3:0] <= 4'h8;
       end
     else begin
       if (write_en[166])
         begin
           reg180c2b28[31:20] <= write_data[31:20];
           reg180c2b28[19:8] <= write_data[19:8];
           reg180c2b28[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2b28[31:20] <= reg180c2b28[31:20];
           reg180c2b28[19:8] <= reg180c2b28[19:8];
           reg180c2b28[3:0] <= reg180c2b28[3:0];
         end
     end
  end

//addr = 0x180c2b2c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b2c[31:28] <= 4'h5;
         reg180c2b2c[25:20] <= 6'h30;
         reg180c2b2c[19:8] <= 12'h100;
         reg180c2b2c[7:4] <= 4'h4;
         reg180c2b2c[0] <= 1'h1;
       end
     else begin
       if (write_en[167])
         begin
           reg180c2b2c[31:28] <= write_data[31:28];
           reg180c2b2c[25:20] <= write_data[25:20];
           reg180c2b2c[19:8] <= write_data[19:8];
           reg180c2b2c[7:4] <= write_data[7:4];
           reg180c2b2c[0] <= write_data[0];
         end
       else
         begin
           reg180c2b2c[31:28] <= reg180c2b2c[31:28];
           reg180c2b2c[25:20] <= reg180c2b2c[25:20];
           reg180c2b2c[19:8] <= reg180c2b2c[19:8];
           reg180c2b2c[7:4] <= reg180c2b2c[7:4];
           reg180c2b2c[0] <= reg180c2b2c[0];
         end
     end
  end

//addr = 0x180c2b30
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b30[9:0] <= 10'h0;
       end
     else begin
       if (write_en[168])
         begin
           reg180c2b30[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2b30[9:0] <= reg180c2b30[9:0];
         end
     end
  end

//addr = 0x180c2b34
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b34[31:28] <= 4'h2;
         reg180c2b34[27:24] <= 4'h4;
         reg180c2b34[23:20] <= 4'hc;
         reg180c2b34[19:16] <= 4'h4;
         reg180c2b34[15:12] <= 4'h0;
         reg180c2b34[11:8] <= 4'h2;
       end
     else begin
       if (write_en[169])
         begin
           reg180c2b34[31:28] <= write_data[31:28];
           reg180c2b34[27:24] <= write_data[27:24];
           reg180c2b34[23:20] <= write_data[23:20];
           reg180c2b34[19:16] <= write_data[19:16];
           reg180c2b34[15:12] <= write_data[15:12];
           reg180c2b34[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2b34[31:28] <= reg180c2b34[31:28];
           reg180c2b34[27:24] <= reg180c2b34[27:24];
           reg180c2b34[23:20] <= reg180c2b34[23:20];
           reg180c2b34[19:16] <= reg180c2b34[19:16];
           reg180c2b34[15:12] <= reg180c2b34[15:12];
           reg180c2b34[11:8] <= reg180c2b34[11:8];
         end
     end
  end

//addr = 0x180c2b40
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b40[31:28] <= 4'h2;
         reg180c2b40[27:24] <= 4'h9;
         reg180c2b40[23:20] <= 4'h8;
         reg180c2b40[19:16] <= 4'h4;
         reg180c2b40[15:12] <= 4'h0;
         reg180c2b40[11] <= 1'h1;
         reg180c2b40[10] <= 1'h0;
         reg180c2b40[9:8] <= 2'h0;
         reg180c2b40[7] <= 1'h0;
         reg180c2b40[4] <= 1'h0;
         reg180c2b40[3] <= 1'h0;
         reg180c2b40[2] <= 1'h1;
         reg180c2b40[1] <= 1'h1;
       end
     else begin
       if (write_en[170])
         begin
           reg180c2b40[31:28] <= write_data[31:28];
           reg180c2b40[27:24] <= write_data[27:24];
           reg180c2b40[23:20] <= write_data[23:20];
           reg180c2b40[19:16] <= write_data[19:16];
           reg180c2b40[15:12] <= write_data[15:12];
           reg180c2b40[11] <= write_data[11];
           reg180c2b40[10] <= write_data[10];
           reg180c2b40[9:8] <= write_data[9:8];
           reg180c2b40[7] <= write_data[7];
           reg180c2b40[4] <= write_data[4];
           reg180c2b40[3] <= write_data[3];
           reg180c2b40[2] <= write_data[2];
           reg180c2b40[1] <= write_data[1];
         end
       else
         begin
           reg180c2b40[31:28] <= reg180c2b40[31:28];
           reg180c2b40[27:24] <= reg180c2b40[27:24];
           reg180c2b40[23:20] <= reg180c2b40[23:20];
           reg180c2b40[19:16] <= reg180c2b40[19:16];
           reg180c2b40[15:12] <= reg180c2b40[15:12];
           reg180c2b40[11] <= reg180c2b40[11];
           reg180c2b40[10] <= reg180c2b40[10];
           reg180c2b40[9:8] <= reg180c2b40[9:8];
           reg180c2b40[7] <= reg180c2b40[7];
           reg180c2b40[4] <= reg180c2b40[4];
           reg180c2b40[3] <= reg180c2b40[3];
           reg180c2b40[2] <= reg180c2b40[2];
           reg180c2b40[1] <= reg180c2b40[1];
         end
     end
  end

//addr = 0x180c2b44
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b44[31:24] <= 8'h0;
         reg180c2b44[15:8] <= 8'h50;
       end
     else begin
       if (write_en[171])
         begin
           reg180c2b44[31:24] <= write_data[31:24];
           reg180c2b44[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2b44[31:24] <= reg180c2b44[31:24];
           reg180c2b44[15:8] <= reg180c2b44[15:8];
         end
     end
  end

//addr = 0x180c2b48
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b48[31:20] <= 12'h800;
         reg180c2b48[19:8] <= 12'h100;
         reg180c2b48[3:0] <= 4'h8;
       end
     else begin
       if (write_en[172])
         begin
           reg180c2b48[31:20] <= write_data[31:20];
           reg180c2b48[19:8] <= write_data[19:8];
           reg180c2b48[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2b48[31:20] <= reg180c2b48[31:20];
           reg180c2b48[19:8] <= reg180c2b48[19:8];
           reg180c2b48[3:0] <= reg180c2b48[3:0];
         end
     end
  end

//addr = 0x180c2b4c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b4c[31:28] <= 4'h5;
         reg180c2b4c[25:20] <= 6'h30;
         reg180c2b4c[19:8] <= 12'h100;
         reg180c2b4c[7:4] <= 4'h4;
         reg180c2b4c[0] <= 1'h1;
       end
     else begin
       if (write_en[173])
         begin
           reg180c2b4c[31:28] <= write_data[31:28];
           reg180c2b4c[25:20] <= write_data[25:20];
           reg180c2b4c[19:8] <= write_data[19:8];
           reg180c2b4c[7:4] <= write_data[7:4];
           reg180c2b4c[0] <= write_data[0];
         end
       else
         begin
           reg180c2b4c[31:28] <= reg180c2b4c[31:28];
           reg180c2b4c[25:20] <= reg180c2b4c[25:20];
           reg180c2b4c[19:8] <= reg180c2b4c[19:8];
           reg180c2b4c[7:4] <= reg180c2b4c[7:4];
           reg180c2b4c[0] <= reg180c2b4c[0];
         end
     end
  end

//addr = 0x180c2b50
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b50[9:0] <= 10'h0;
       end
     else begin
       if (write_en[174])
         begin
           reg180c2b50[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2b50[9:0] <= reg180c2b50[9:0];
         end
     end
  end

//addr = 0x180c2b54
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b54[31:28] <= 4'h2;
         reg180c2b54[27:24] <= 4'h4;
         reg180c2b54[23:20] <= 4'hc;
         reg180c2b54[19:16] <= 4'h4;
         reg180c2b54[15:12] <= 4'h0;
         reg180c2b54[11:8] <= 4'h2;
       end
     else begin
       if (write_en[175])
         begin
           reg180c2b54[31:28] <= write_data[31:28];
           reg180c2b54[27:24] <= write_data[27:24];
           reg180c2b54[23:20] <= write_data[23:20];
           reg180c2b54[19:16] <= write_data[19:16];
           reg180c2b54[15:12] <= write_data[15:12];
           reg180c2b54[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2b54[31:28] <= reg180c2b54[31:28];
           reg180c2b54[27:24] <= reg180c2b54[27:24];
           reg180c2b54[23:20] <= reg180c2b54[23:20];
           reg180c2b54[19:16] <= reg180c2b54[19:16];
           reg180c2b54[15:12] <= reg180c2b54[15:12];
           reg180c2b54[11:8] <= reg180c2b54[11:8];
         end
     end
  end

//addr = 0x180c2b60
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b60[31:28] <= 4'h2;
         reg180c2b60[27:24] <= 4'h9;
         reg180c2b60[23:20] <= 4'h8;
         reg180c2b60[19:16] <= 4'h4;
         reg180c2b60[15:12] <= 4'h0;
         reg180c2b60[11] <= 1'h1;
         reg180c2b60[10] <= 1'h0;
         reg180c2b60[9:8] <= 2'h0;
         reg180c2b60[7] <= 1'h0;
         reg180c2b60[4] <= 1'h0;
         reg180c2b60[3] <= 1'h0;
         reg180c2b60[2] <= 1'h1;
         reg180c2b60[1] <= 1'h1;
       end
     else begin
       if (write_en[176])
         begin
           reg180c2b60[31:28] <= write_data[31:28];
           reg180c2b60[27:24] <= write_data[27:24];
           reg180c2b60[23:20] <= write_data[23:20];
           reg180c2b60[19:16] <= write_data[19:16];
           reg180c2b60[15:12] <= write_data[15:12];
           reg180c2b60[11] <= write_data[11];
           reg180c2b60[10] <= write_data[10];
           reg180c2b60[9:8] <= write_data[9:8];
           reg180c2b60[7] <= write_data[7];
           reg180c2b60[4] <= write_data[4];
           reg180c2b60[3] <= write_data[3];
           reg180c2b60[2] <= write_data[2];
           reg180c2b60[1] <= write_data[1];
         end
       else
         begin
           reg180c2b60[31:28] <= reg180c2b60[31:28];
           reg180c2b60[27:24] <= reg180c2b60[27:24];
           reg180c2b60[23:20] <= reg180c2b60[23:20];
           reg180c2b60[19:16] <= reg180c2b60[19:16];
           reg180c2b60[15:12] <= reg180c2b60[15:12];
           reg180c2b60[11] <= reg180c2b60[11];
           reg180c2b60[10] <= reg180c2b60[10];
           reg180c2b60[9:8] <= reg180c2b60[9:8];
           reg180c2b60[7] <= reg180c2b60[7];
           reg180c2b60[4] <= reg180c2b60[4];
           reg180c2b60[3] <= reg180c2b60[3];
           reg180c2b60[2] <= reg180c2b60[2];
           reg180c2b60[1] <= reg180c2b60[1];
         end
     end
  end

//addr = 0x180c2b64
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b64[31:24] <= 8'h0;
         reg180c2b64[15:8] <= 8'h50;
       end
     else begin
       if (write_en[177])
         begin
           reg180c2b64[31:24] <= write_data[31:24];
           reg180c2b64[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2b64[31:24] <= reg180c2b64[31:24];
           reg180c2b64[15:8] <= reg180c2b64[15:8];
         end
     end
  end

//addr = 0x180c2b68
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b68[31:20] <= 12'h800;
         reg180c2b68[19:8] <= 12'h100;
         reg180c2b68[3:0] <= 4'h8;
       end
     else begin
       if (write_en[178])
         begin
           reg180c2b68[31:20] <= write_data[31:20];
           reg180c2b68[19:8] <= write_data[19:8];
           reg180c2b68[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2b68[31:20] <= reg180c2b68[31:20];
           reg180c2b68[19:8] <= reg180c2b68[19:8];
           reg180c2b68[3:0] <= reg180c2b68[3:0];
         end
     end
  end

//addr = 0x180c2b6c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b6c[31:28] <= 4'h5;
         reg180c2b6c[25:20] <= 6'h30;
         reg180c2b6c[19:8] <= 12'h100;
         reg180c2b6c[7:4] <= 4'h4;
         reg180c2b6c[0] <= 1'h1;
       end
     else begin
       if (write_en[179])
         begin
           reg180c2b6c[31:28] <= write_data[31:28];
           reg180c2b6c[25:20] <= write_data[25:20];
           reg180c2b6c[19:8] <= write_data[19:8];
           reg180c2b6c[7:4] <= write_data[7:4];
           reg180c2b6c[0] <= write_data[0];
         end
       else
         begin
           reg180c2b6c[31:28] <= reg180c2b6c[31:28];
           reg180c2b6c[25:20] <= reg180c2b6c[25:20];
           reg180c2b6c[19:8] <= reg180c2b6c[19:8];
           reg180c2b6c[7:4] <= reg180c2b6c[7:4];
           reg180c2b6c[0] <= reg180c2b6c[0];
         end
     end
  end

//addr = 0x180c2b70
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b70[9:0] <= 10'h0;
       end
     else begin
       if (write_en[180])
         begin
           reg180c2b70[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2b70[9:0] <= reg180c2b70[9:0];
         end
     end
  end

//addr = 0x180c2b74
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b74[31:28] <= 4'h2;
         reg180c2b74[27:24] <= 4'h4;
         reg180c2b74[23:20] <= 4'hc;
         reg180c2b74[19:16] <= 4'h4;
         reg180c2b74[15:12] <= 4'h0;
         reg180c2b74[11:8] <= 4'h2;
       end
     else begin
       if (write_en[181])
         begin
           reg180c2b74[31:28] <= write_data[31:28];
           reg180c2b74[27:24] <= write_data[27:24];
           reg180c2b74[23:20] <= write_data[23:20];
           reg180c2b74[19:16] <= write_data[19:16];
           reg180c2b74[15:12] <= write_data[15:12];
           reg180c2b74[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2b74[31:28] <= reg180c2b74[31:28];
           reg180c2b74[27:24] <= reg180c2b74[27:24];
           reg180c2b74[23:20] <= reg180c2b74[23:20];
           reg180c2b74[19:16] <= reg180c2b74[19:16];
           reg180c2b74[15:12] <= reg180c2b74[15:12];
           reg180c2b74[11:8] <= reg180c2b74[11:8];
         end
     end
  end

//addr = 0x180c2b80
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b80[31:28] <= 4'h2;
         reg180c2b80[27:24] <= 4'h9;
         reg180c2b80[23:20] <= 4'h8;
         reg180c2b80[19:16] <= 4'h4;
         reg180c2b80[15:12] <= 4'h0;
         reg180c2b80[11] <= 1'h1;
         reg180c2b80[10] <= 1'h0;
         reg180c2b80[9:8] <= 2'h0;
         reg180c2b80[7] <= 1'h0;
         reg180c2b80[4] <= 1'h0;
         reg180c2b80[3] <= 1'h0;
         reg180c2b80[2] <= 1'h1;
         reg180c2b80[1] <= 1'h1;
       end
     else begin
       if (write_en[182])
         begin
           reg180c2b80[31:28] <= write_data[31:28];
           reg180c2b80[27:24] <= write_data[27:24];
           reg180c2b80[23:20] <= write_data[23:20];
           reg180c2b80[19:16] <= write_data[19:16];
           reg180c2b80[15:12] <= write_data[15:12];
           reg180c2b80[11] <= write_data[11];
           reg180c2b80[10] <= write_data[10];
           reg180c2b80[9:8] <= write_data[9:8];
           reg180c2b80[7] <= write_data[7];
           reg180c2b80[4] <= write_data[4];
           reg180c2b80[3] <= write_data[3];
           reg180c2b80[2] <= write_data[2];
           reg180c2b80[1] <= write_data[1];
         end
       else
         begin
           reg180c2b80[31:28] <= reg180c2b80[31:28];
           reg180c2b80[27:24] <= reg180c2b80[27:24];
           reg180c2b80[23:20] <= reg180c2b80[23:20];
           reg180c2b80[19:16] <= reg180c2b80[19:16];
           reg180c2b80[15:12] <= reg180c2b80[15:12];
           reg180c2b80[11] <= reg180c2b80[11];
           reg180c2b80[10] <= reg180c2b80[10];
           reg180c2b80[9:8] <= reg180c2b80[9:8];
           reg180c2b80[7] <= reg180c2b80[7];
           reg180c2b80[4] <= reg180c2b80[4];
           reg180c2b80[3] <= reg180c2b80[3];
           reg180c2b80[2] <= reg180c2b80[2];
           reg180c2b80[1] <= reg180c2b80[1];
         end
     end
  end

//addr = 0x180c2b84
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b84[31:24] <= 8'h30;
         reg180c2b84[15:8] <= 8'h6f;
       end
     else begin
       if (write_en[183])
         begin
           reg180c2b84[31:24] <= write_data[31:24];
           reg180c2b84[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2b84[31:24] <= reg180c2b84[31:24];
           reg180c2b84[15:8] <= reg180c2b84[15:8];
         end
     end
  end

//addr = 0x180c2b88
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b88[31:20] <= 12'h300;
         reg180c2b88[19:8] <= 12'h180;
         reg180c2b88[3:0] <= 4'h8;
       end
     else begin
       if (write_en[184])
         begin
           reg180c2b88[31:20] <= write_data[31:20];
           reg180c2b88[19:8] <= write_data[19:8];
           reg180c2b88[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2b88[31:20] <= reg180c2b88[31:20];
           reg180c2b88[19:8] <= reg180c2b88[19:8];
           reg180c2b88[3:0] <= reg180c2b88[3:0];
         end
     end
  end

//addr = 0x180c2b8c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b8c[31:28] <= 4'h6;
         reg180c2b8c[25:20] <= 6'ha;
         reg180c2b8c[19:8] <= 12'h100;
         reg180c2b8c[7:4] <= 4'h4;
         reg180c2b8c[0] <= 1'h1;
       end
     else begin
       if (write_en[185])
         begin
           reg180c2b8c[31:28] <= write_data[31:28];
           reg180c2b8c[25:20] <= write_data[25:20];
           reg180c2b8c[19:8] <= write_data[19:8];
           reg180c2b8c[7:4] <= write_data[7:4];
           reg180c2b8c[0] <= write_data[0];
         end
       else
         begin
           reg180c2b8c[31:28] <= reg180c2b8c[31:28];
           reg180c2b8c[25:20] <= reg180c2b8c[25:20];
           reg180c2b8c[19:8] <= reg180c2b8c[19:8];
           reg180c2b8c[7:4] <= reg180c2b8c[7:4];
           reg180c2b8c[0] <= reg180c2b8c[0];
         end
     end
  end

//addr = 0x180c2b90
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b90[9:0] <= 10'h0;
       end
     else begin
       if (write_en[186])
         begin
           reg180c2b90[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2b90[9:0] <= reg180c2b90[9:0];
         end
     end
  end

//addr = 0x180c2b94
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2b94[31:28] <= 4'h2;
         reg180c2b94[27:24] <= 4'h4;
         reg180c2b94[23:20] <= 4'hc;
         reg180c2b94[19:16] <= 4'h4;
         reg180c2b94[15:12] <= 4'h0;
         reg180c2b94[11:8] <= 4'h2;
       end
     else begin
       if (write_en[187])
         begin
           reg180c2b94[31:28] <= write_data[31:28];
           reg180c2b94[27:24] <= write_data[27:24];
           reg180c2b94[23:20] <= write_data[23:20];
           reg180c2b94[19:16] <= write_data[19:16];
           reg180c2b94[15:12] <= write_data[15:12];
           reg180c2b94[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2b94[31:28] <= reg180c2b94[31:28];
           reg180c2b94[27:24] <= reg180c2b94[27:24];
           reg180c2b94[23:20] <= reg180c2b94[23:20];
           reg180c2b94[19:16] <= reg180c2b94[19:16];
           reg180c2b94[15:12] <= reg180c2b94[15:12];
           reg180c2b94[11:8] <= reg180c2b94[11:8];
         end
     end
  end

//addr = 0x180c2ba0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ba0[31:28] <= 4'h2;
         reg180c2ba0[27:24] <= 4'h9;
         reg180c2ba0[23:20] <= 4'h8;
         reg180c2ba0[19:16] <= 4'h4;
         reg180c2ba0[15:12] <= 4'h0;
         reg180c2ba0[11] <= 1'h1;
         reg180c2ba0[10] <= 1'h0;
         reg180c2ba0[9:8] <= 2'h0;
         reg180c2ba0[7] <= 1'h0;
         reg180c2ba0[4] <= 1'h0;
         reg180c2ba0[3] <= 1'h0;
         reg180c2ba0[2] <= 1'h1;
         reg180c2ba0[1] <= 1'h1;
       end
     else begin
       if (write_en[188])
         begin
           reg180c2ba0[31:28] <= write_data[31:28];
           reg180c2ba0[27:24] <= write_data[27:24];
           reg180c2ba0[23:20] <= write_data[23:20];
           reg180c2ba0[19:16] <= write_data[19:16];
           reg180c2ba0[15:12] <= write_data[15:12];
           reg180c2ba0[11] <= write_data[11];
           reg180c2ba0[10] <= write_data[10];
           reg180c2ba0[9:8] <= write_data[9:8];
           reg180c2ba0[7] <= write_data[7];
           reg180c2ba0[4] <= write_data[4];
           reg180c2ba0[3] <= write_data[3];
           reg180c2ba0[2] <= write_data[2];
           reg180c2ba0[1] <= write_data[1];
         end
       else
         begin
           reg180c2ba0[31:28] <= reg180c2ba0[31:28];
           reg180c2ba0[27:24] <= reg180c2ba0[27:24];
           reg180c2ba0[23:20] <= reg180c2ba0[23:20];
           reg180c2ba0[19:16] <= reg180c2ba0[19:16];
           reg180c2ba0[15:12] <= reg180c2ba0[15:12];
           reg180c2ba0[11] <= reg180c2ba0[11];
           reg180c2ba0[10] <= reg180c2ba0[10];
           reg180c2ba0[9:8] <= reg180c2ba0[9:8];
           reg180c2ba0[7] <= reg180c2ba0[7];
           reg180c2ba0[4] <= reg180c2ba0[4];
           reg180c2ba0[3] <= reg180c2ba0[3];
           reg180c2ba0[2] <= reg180c2ba0[2];
           reg180c2ba0[1] <= reg180c2ba0[1];
         end
     end
  end

//addr = 0x180c2ba4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ba4[31:24] <= 8'h30;
         reg180c2ba4[15:8] <= 8'h6f;
       end
     else begin
       if (write_en[189])
         begin
           reg180c2ba4[31:24] <= write_data[31:24];
           reg180c2ba4[15:8] <= write_data[15:8];
         end
       else
         begin
           reg180c2ba4[31:24] <= reg180c2ba4[31:24];
           reg180c2ba4[15:8] <= reg180c2ba4[15:8];
         end
     end
  end

//addr = 0x180c2ba8
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2ba8[31:20] <= 12'h300;
         reg180c2ba8[19:8] <= 12'h180;
         reg180c2ba8[3:0] <= 4'h8;
       end
     else begin
       if (write_en[190])
         begin
           reg180c2ba8[31:20] <= write_data[31:20];
           reg180c2ba8[19:8] <= write_data[19:8];
           reg180c2ba8[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2ba8[31:20] <= reg180c2ba8[31:20];
           reg180c2ba8[19:8] <= reg180c2ba8[19:8];
           reg180c2ba8[3:0] <= reg180c2ba8[3:0];
         end
     end
  end

//addr = 0x180c2bac
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2bac[31:28] <= 4'h6;
         reg180c2bac[25:20] <= 6'ha;
         reg180c2bac[19:8] <= 12'h100;
         reg180c2bac[7:4] <= 4'h4;
         reg180c2bac[0] <= 1'h1;
       end
     else begin
       if (write_en[191])
         begin
           reg180c2bac[31:28] <= write_data[31:28];
           reg180c2bac[25:20] <= write_data[25:20];
           reg180c2bac[19:8] <= write_data[19:8];
           reg180c2bac[7:4] <= write_data[7:4];
           reg180c2bac[0] <= write_data[0];
         end
       else
         begin
           reg180c2bac[31:28] <= reg180c2bac[31:28];
           reg180c2bac[25:20] <= reg180c2bac[25:20];
           reg180c2bac[19:8] <= reg180c2bac[19:8];
           reg180c2bac[7:4] <= reg180c2bac[7:4];
           reg180c2bac[0] <= reg180c2bac[0];
         end
     end
  end

//addr = 0x180c2bb0
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2bb0[9:0] <= 10'h0;
       end
     else begin
       if (write_en[192])
         begin
           reg180c2bb0[9:0] <= write_data[9:0];
         end
       else
         begin
           reg180c2bb0[9:0] <= reg180c2bb0[9:0];
         end
     end
  end

//addr = 0x180c2bb4
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2bb4[31:28] <= 4'h2;
         reg180c2bb4[27:24] <= 4'h4;
         reg180c2bb4[23:20] <= 4'hc;
         reg180c2bb4[19:16] <= 4'h4;
         reg180c2bb4[15:12] <= 4'h0;
         reg180c2bb4[11:8] <= 4'h2;
       end
     else begin
       if (write_en[193])
         begin
           reg180c2bb4[31:28] <= write_data[31:28];
           reg180c2bb4[27:24] <= write_data[27:24];
           reg180c2bb4[23:20] <= write_data[23:20];
           reg180c2bb4[19:16] <= write_data[19:16];
           reg180c2bb4[15:12] <= write_data[15:12];
           reg180c2bb4[11:8] <= write_data[11:8];
         end
       else
         begin
           reg180c2bb4[31:28] <= reg180c2bb4[31:28];
           reg180c2bb4[27:24] <= reg180c2bb4[27:24];
           reg180c2bb4[23:20] <= reg180c2bb4[23:20];
           reg180c2bb4[19:16] <= reg180c2bb4[19:16];
           reg180c2bb4[15:12] <= reg180c2bb4[15:12];
           reg180c2bb4[11:8] <= reg180c2bb4[11:8];
         end
     end
  end

//addr = 0x180c2c00
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c00[26:16] <= 11'h0;
         reg180c2c00[9:8] <= 2'h3;
         reg180c2c00[7:6] <= 2'h3;
         reg180c2c00[4] <= 1'h0;
         reg180c2c00[3:0] <= 4'hf;
       end
     else begin
       if (write_en[194])
         begin
           reg180c2c00[26:16] <= write_data[26:16];
           reg180c2c00[9:8] <= write_data[9:8];
           reg180c2c00[7:6] <= write_data[7:6];
           reg180c2c00[4] <= write_data[4];
           reg180c2c00[3:0] <= write_data[3:0];
         end
       else
         begin
           reg180c2c00[26:16] <= reg180c2c00[26:16];
           reg180c2c00[9:8] <= reg180c2c00[9:8];
           reg180c2c00[7:6] <= reg180c2c00[7:6];
           reg180c2c00[4] <= reg180c2c00[4];
           reg180c2c00[3:0] <= reg180c2c00[3:0];
         end
     end
  end

always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c00[5] <= 1'h0;
       end
     else begin
       if (write_en[194])
         begin
           reg180c2c00[5] <= write_data[5];
         end
       else
         begin
             reg180c2c00[5] <= update_meas_sram_w_addr_rst ? n_meas_sram_w_addr_rst : reg180c2c00[5];
         end
     end
  end

//addr = 0x180c2c04
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c04[31] <= 1'h0;
         reg180c2c04[10:0] <= 11'h0;
       end
     else begin
       if (write_en[195])
         begin
           reg180c2c04[31] <= write_data[31];
           reg180c2c04[10:0] <= write_data[10:0];
         end
       else
         begin
           reg180c2c04[31] <= reg180c2c04[31];
           reg180c2c04[10:0] <= reg180c2c04[10:0];
         end
     end
  end

always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c04[15] <= 1'h0;
       end
     else begin
       if (write_en[195])
         begin
           reg180c2c04[15] <= write_data[15];
         end
       else
         begin
             reg180c2c04[15] <= update_meas_sram_r_addr_sync ? n_meas_sram_r_addr_sync : reg180c2c04[15];
         end
     end
  end

//addr = 0x180c2c08
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c08[31] <= 1'h0;
         reg180c2c08[30] <= 1'h0;
         reg180c2c08[29] <= 1'h0;
         reg180c2c08[28] <= 1'h0;
         reg180c2c08[10:9] <= 2'h0;
         reg180c2c08[8] <= 1'h0;
         reg180c2c08[5] <= 1'h0;
         reg180c2c08[4] <= 1'h0;
       end
     else begin
       if (write_en[196])
         begin
           reg180c2c08[31] <= write_data[31];
           reg180c2c08[30] <= write_data[30];
           reg180c2c08[29] <= write_data[29];
           reg180c2c08[28] <= write_data[28];
           reg180c2c08[10:9] <= write_data[10:9];
           reg180c2c08[8] <= write_data[8];
           reg180c2c08[5] <= write_data[5];
           reg180c2c08[4] <= write_data[4];
         end
       else
         begin
           reg180c2c08[31] <= reg180c2c08[31];
           reg180c2c08[30] <= reg180c2c08[30];
           reg180c2c08[29] <= reg180c2c08[29];
           reg180c2c08[28] <= reg180c2c08[28];
           reg180c2c08[10:9] <= reg180c2c08[10:9];
           reg180c2c08[8] <= reg180c2c08[8];
           reg180c2c08[5] <= reg180c2c08[5];
           reg180c2c08[4] <= reg180c2c08[4];
         end
     end
  end

always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c08[0] <= 1'h0;
       end
     else begin
       if (write_en[196])
         begin
           reg180c2c08[0] <= write_data[0];
         end
       else
         begin
             reg180c2c08[0] <= update_meas_start ? n_meas_start : reg180c2c08[0];
         end
     end
  end

//addr = 0x180c2c0c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c0c[31:0] <= 32'h0;
       end
     else begin
       if (write_en[197])
         begin
           reg180c2c0c[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2c0c[31:0] <= reg180c2c0c[31:0];
         end
     end
  end

//addr = 0x180c2c14
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c14[24] <= 1'h0;
         reg180c2c14[23:16] <= 8'h0;
         reg180c2c14[15:12] <= 4'h0;
         reg180c2c14[10] <= 1'h0;
         reg180c2c14[9:8] <= 2'h3;
       end
     else begin
       if (write_en[199])
         begin
           reg180c2c14[24] <= write_data[24];
           reg180c2c14[23:16] <= write_data[23:16];
           reg180c2c14[15:12] <= write_data[15:12];
           reg180c2c14[10] <= write_data[10];
           reg180c2c14[9:8] <= write_data[9:8];
         end
       else
         begin
           reg180c2c14[24] <= reg180c2c14[24];
           reg180c2c14[23:16] <= reg180c2c14[23:16];
           reg180c2c14[15:12] <= reg180c2c14[15:12];
           reg180c2c14[10] <= reg180c2c14[10];
           reg180c2c14[9:8] <= reg180c2c14[9:8];
         end
     end
  end

//addr = 0x180c2c18
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c18[24] <= 1'h0;
         reg180c2c18[23:16] <= 8'h0;
         reg180c2c18[15:12] <= 4'h0;
         reg180c2c18[10] <= 1'h0;
         reg180c2c18[9:8] <= 2'h3;
         reg180c2c18[0] <= 1'h0;
       end
     else begin
       if (write_en[200])
         begin
           reg180c2c18[24] <= write_data[24];
           reg180c2c18[23:16] <= write_data[23:16];
           reg180c2c18[15:12] <= write_data[15:12];
           reg180c2c18[10] <= write_data[10];
           reg180c2c18[9:8] <= write_data[9:8];
           reg180c2c18[0] <= write_data[0];
         end
       else
         begin
           reg180c2c18[24] <= reg180c2c18[24];
           reg180c2c18[23:16] <= reg180c2c18[23:16];
           reg180c2c18[15:12] <= reg180c2c18[15:12];
           reg180c2c18[10] <= reg180c2c18[10];
           reg180c2c18[9:8] <= reg180c2c18[9:8];
           reg180c2c18[0] <= reg180c2c18[0];
         end
     end
  end

//addr = 0x180c2c1c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c1c[24] <= 1'h0;
         reg180c2c1c[23:16] <= 8'h0;
         reg180c2c1c[15:12] <= 4'h0;
         reg180c2c1c[10] <= 1'h0;
         reg180c2c1c[9:8] <= 2'h3;
         reg180c2c1c[0] <= 1'h0;
       end
     else begin
       if (write_en[201])
         begin
           reg180c2c1c[24] <= write_data[24];
           reg180c2c1c[23:16] <= write_data[23:16];
           reg180c2c1c[15:12] <= write_data[15:12];
           reg180c2c1c[10] <= write_data[10];
           reg180c2c1c[9:8] <= write_data[9:8];
           reg180c2c1c[0] <= write_data[0];
         end
       else
         begin
           reg180c2c1c[24] <= reg180c2c1c[24];
           reg180c2c1c[23:16] <= reg180c2c1c[23:16];
           reg180c2c1c[15:12] <= reg180c2c1c[15:12];
           reg180c2c1c[10] <= reg180c2c1c[10];
           reg180c2c1c[9:8] <= reg180c2c1c[9:8];
           reg180c2c1c[0] <= reg180c2c1c[0];
         end
     end
  end

//addr = 0x180c2c20
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c20[24] <= 1'h0;
         reg180c2c20[23:16] <= 8'h0;
         reg180c2c20[15:12] <= 4'h0;
         reg180c2c20[10] <= 1'h0;
         reg180c2c20[9:8] <= 2'h3;
         reg180c2c20[0] <= 1'h0;
       end
     else begin
       if (write_en[202])
         begin
           reg180c2c20[24] <= write_data[24];
           reg180c2c20[23:16] <= write_data[23:16];
           reg180c2c20[15:12] <= write_data[15:12];
           reg180c2c20[10] <= write_data[10];
           reg180c2c20[9:8] <= write_data[9:8];
           reg180c2c20[0] <= write_data[0];
         end
       else
         begin
           reg180c2c20[24] <= reg180c2c20[24];
           reg180c2c20[23:16] <= reg180c2c20[23:16];
           reg180c2c20[15:12] <= reg180c2c20[15:12];
           reg180c2c20[10] <= reg180c2c20[10];
           reg180c2c20[9:8] <= reg180c2c20[9:8];
           reg180c2c20[0] <= reg180c2c20[0];
         end
     end
  end

//addr = 0x180c2c44
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c44[31] <= 1'h0;
         reg180c2c44[30] <= 1'h1;
         reg180c2c44[28] <= 1'h0;
         reg180c2c44[27:26] <= 2'h3;
         reg180c2c44[25] <= 1'h0;
         reg180c2c44[24] <= 1'h0;
         reg180c2c44[23] <= 1'h0;
         reg180c2c44[22:21] <= 2'h3;
         reg180c2c44[20] <= 1'h0;
         reg180c2c44[19] <= 1'h0;
       end
     else begin
       if (write_en[211])
         begin
           reg180c2c44[31] <= write_data[31];
           reg180c2c44[30] <= write_data[30];
           reg180c2c44[28] <= write_data[28];
           reg180c2c44[27:26] <= write_data[27:26];
           reg180c2c44[25] <= write_data[25];
           reg180c2c44[24] <= write_data[24];
           reg180c2c44[23] <= write_data[23];
           reg180c2c44[22:21] <= write_data[22:21];
           reg180c2c44[20] <= write_data[20];
           reg180c2c44[19] <= write_data[19];
         end
       else
         begin
           reg180c2c44[31] <= reg180c2c44[31];
           reg180c2c44[30] <= reg180c2c44[30];
           reg180c2c44[28] <= reg180c2c44[28];
           reg180c2c44[27:26] <= reg180c2c44[27:26];
           reg180c2c44[25] <= reg180c2c44[25];
           reg180c2c44[24] <= reg180c2c44[24];
           reg180c2c44[23] <= reg180c2c44[23];
           reg180c2c44[22:21] <= reg180c2c44[22:21];
           reg180c2c44[20] <= reg180c2c44[20];
           reg180c2c44[19] <= reg180c2c44[19];
         end
     end
  end

always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c44[29] <= 1'h0;
       end
     else begin
       if (write_en[211])
         begin
           reg180c2c44[29] <= write_data[29];
         end
       else
         begin
             reg180c2c44[29] <= update_meas_sram_clear_en ? n_meas_sram_clear_en : reg180c2c44[29];
         end
     end
  end

//addr = 0x180c2c50
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c50[19:12] <= 8'h0;
         reg180c2c50[7:0] <= 8'h0;
       end
     else begin
       if (write_en[214])
         begin
           reg180c2c50[19:12] <= write_data[19:12];
           reg180c2c50[7:0] <= write_data[7:0];
         end
       else
         begin
           reg180c2c50[19:12] <= reg180c2c50[19:12];
           reg180c2c50[7:0] <= reg180c2c50[7:0];
         end
     end
  end

//addr = 0x180c2c54
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c54[31:0] <= 32'h0;
       end
     else begin
       if (write_en[215])
         begin
           reg180c2c54[31:0] <= write_data[31:0];
         end
       else
         begin
           reg180c2c54[31:0] <= reg180c2c54[31:0];
         end
     end
  end

//addr = 0x180c2c58
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c58[3] <= 1'h0;
         reg180c2c58[2] <= 1'h0;
       end
     else begin
       if (write_en[216])
         begin
           reg180c2c58[3] <= write_data[3];
           reg180c2c58[2] <= write_data[2];
         end
       else
         begin
           reg180c2c58[3] <= reg180c2c58[3];
           reg180c2c58[2] <= reg180c2c58[2];
         end
     end
  end

//addr = 0x180c2c5c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c5c[31] <= 1'h0;
         reg180c2c5c[23:16] <= 8'h0;
         reg180c2c5c[9:8] <= 2'h0;
         reg180c2c5c[3] <= 1'h0;
         reg180c2c5c[1] <= 1'h0;
         reg180c2c5c[0] <= 1'h0;
       end
     else begin
       if (write_en[217])
         begin
           reg180c2c5c[31] <= write_data[31];
           reg180c2c5c[23:16] <= write_data[23:16];
           reg180c2c5c[9:8] <= write_data[9:8];
           reg180c2c5c[3] <= write_data[3];
           reg180c2c5c[1] <= write_data[1];
           reg180c2c5c[0] <= write_data[0];
         end
       else
         begin
           reg180c2c5c[31] <= reg180c2c5c[31];
           reg180c2c5c[23:16] <= reg180c2c5c[23:16];
           reg180c2c5c[9:8] <= reg180c2c5c[9:8];
           reg180c2c5c[3] <= reg180c2c5c[3];
           reg180c2c5c[1] <= reg180c2c5c[1];
           reg180c2c5c[0] <= reg180c2c5c[0];
         end
     end
  end

//addr = 0x180c2c60
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c60[31:3] <= 29'h0;
       end
     else begin
       if (write_en[218])
         begin
           reg180c2c60[31:3] <= write_data[31:3];
         end
       else
         begin
           reg180c2c60[31:3] <= reg180c2c60[31:3];
         end
     end
  end

//addr = 0x180c2c64
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c64[31:3] <= 29'h0;
       end
     else begin
       if (write_en[219])
         begin
           reg180c2c64[31:3] <= write_data[31:3];
         end
       else
         begin
           reg180c2c64[31:3] <= reg180c2c64[31:3];
         end
     end
  end

//addr = 0x180c2c68
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c68[20] <= 1'h0;
         reg180c2c68[19] <= 1'h0;
         reg180c2c68[18] <= 1'h0;
         reg180c2c68[17] <= 1'h0;
         reg180c2c68[16] <= 1'h0;
         reg180c2c68[15] <= 1'h0;
         reg180c2c68[13] <= 1'h0;
         reg180c2c68[12] <= 1'h0;
         reg180c2c68[11:8] <= 4'h2;
         reg180c2c68[7] <= 1'h1;
         reg180c2c68[6] <= 1'h1;
         reg180c2c68[5] <= 1'h0;
         reg180c2c68[4] <= 1'h0;
         reg180c2c68[3] <= 1'h0;
         reg180c2c68[2] <= 1'h0;
         reg180c2c68[1] <= 1'h0;
         reg180c2c68[0] <= 1'h0;
       end
     else begin
       if (write_en[220])
         begin
           reg180c2c68[20] <= write_data[20];
           reg180c2c68[19] <= write_data[19];
           reg180c2c68[18] <= write_data[18];
           reg180c2c68[17] <= write_data[17];
           reg180c2c68[16] <= write_data[16];
           reg180c2c68[15] <= write_data[15];
           reg180c2c68[13] <= write_data[13];
           reg180c2c68[12] <= write_data[12];
           reg180c2c68[11:8] <= write_data[11:8];
           reg180c2c68[7] <= write_data[7];
           reg180c2c68[6] <= write_data[6];
           reg180c2c68[5] <= write_data[5];
           reg180c2c68[4] <= write_data[4];
           reg180c2c68[3] <= write_data[3];
           reg180c2c68[2] <= write_data[2];
           reg180c2c68[1] <= write_data[1];
           reg180c2c68[0] <= write_data[0];
         end
       else
         begin
           reg180c2c68[20] <= reg180c2c68[20];
           reg180c2c68[19] <= reg180c2c68[19];
           reg180c2c68[18] <= reg180c2c68[18];
           reg180c2c68[17] <= reg180c2c68[17];
           reg180c2c68[16] <= reg180c2c68[16];
           reg180c2c68[15] <= reg180c2c68[15];
           reg180c2c68[13] <= reg180c2c68[13];
           reg180c2c68[12] <= reg180c2c68[12];
           reg180c2c68[11:8] <= reg180c2c68[11:8];
           reg180c2c68[7] <= reg180c2c68[7];
           reg180c2c68[6] <= reg180c2c68[6];
           reg180c2c68[5] <= reg180c2c68[5];
           reg180c2c68[4] <= reg180c2c68[4];
           reg180c2c68[3] <= reg180c2c68[3];
           reg180c2c68[2] <= reg180c2c68[2];
           reg180c2c68[1] <= reg180c2c68[1];
           reg180c2c68[0] <= reg180c2c68[0];
         end
     end
  end

//addr = 0x180c2c6c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c6c[29] <= 1'h0;
         reg180c2c6c[28] <= 1'h0;
         reg180c2c6c[27:26] <= 2'h0;
         reg180c2c6c[25:24] <= 2'h0;
         reg180c2c6c[23:22] <= 2'h0;
         reg180c2c6c[21:20] <= 2'h0;
         reg180c2c6c[19:18] <= 2'h0;
         reg180c2c6c[17:16] <= 2'h0;
         reg180c2c6c[15] <= 1'h0;
         reg180c2c6c[14] <= 1'h0;
         reg180c2c6c[13] <= 1'h0;
         reg180c2c6c[12] <= 1'h0;
         reg180c2c6c[11] <= 1'h0;
         reg180c2c6c[10] <= 1'h0;
         reg180c2c6c[9] <= 1'h0;
         reg180c2c6c[8] <= 1'h0;
         reg180c2c6c[7] <= 1'h0;
         reg180c2c6c[6] <= 1'h0;
         reg180c2c6c[5] <= 1'h0;
         reg180c2c6c[4] <= 1'h0;
         reg180c2c6c[3] <= 1'h0;
         reg180c2c6c[2] <= 1'h0;
         reg180c2c6c[1] <= 1'h0;
         reg180c2c6c[0] <= 1'h0;
       end
     else begin
       if (write_en[221])
         begin
           reg180c2c6c[29] <= write_data[29];
           reg180c2c6c[28] <= write_data[28];
           reg180c2c6c[27:26] <= write_data[27:26];
           reg180c2c6c[25:24] <= write_data[25:24];
           reg180c2c6c[23:22] <= write_data[23:22];
           reg180c2c6c[21:20] <= write_data[21:20];
           reg180c2c6c[19:18] <= write_data[19:18];
           reg180c2c6c[17:16] <= write_data[17:16];
           reg180c2c6c[15] <= write_data[15];
           reg180c2c6c[14] <= write_data[14];
           reg180c2c6c[13] <= write_data[13];
           reg180c2c6c[12] <= write_data[12];
           reg180c2c6c[11] <= write_data[11];
           reg180c2c6c[10] <= write_data[10];
           reg180c2c6c[9] <= write_data[9];
           reg180c2c6c[8] <= write_data[8];
           reg180c2c6c[7] <= write_data[7];
           reg180c2c6c[6] <= write_data[6];
           reg180c2c6c[5] <= write_data[5];
           reg180c2c6c[4] <= write_data[4];
           reg180c2c6c[3] <= write_data[3];
           reg180c2c6c[2] <= write_data[2];
           reg180c2c6c[1] <= write_data[1];
           reg180c2c6c[0] <= write_data[0];
         end
       else
         begin
           reg180c2c6c[29] <= reg180c2c6c[29];
           reg180c2c6c[28] <= reg180c2c6c[28];
           reg180c2c6c[27:26] <= reg180c2c6c[27:26];
           reg180c2c6c[25:24] <= reg180c2c6c[25:24];
           reg180c2c6c[23:22] <= reg180c2c6c[23:22];
           reg180c2c6c[21:20] <= reg180c2c6c[21:20];
           reg180c2c6c[19:18] <= reg180c2c6c[19:18];
           reg180c2c6c[17:16] <= reg180c2c6c[17:16];
           reg180c2c6c[15] <= reg180c2c6c[15];
           reg180c2c6c[14] <= reg180c2c6c[14];
           reg180c2c6c[13] <= reg180c2c6c[13];
           reg180c2c6c[12] <= reg180c2c6c[12];
           reg180c2c6c[11] <= reg180c2c6c[11];
           reg180c2c6c[10] <= reg180c2c6c[10];
           reg180c2c6c[9] <= reg180c2c6c[9];
           reg180c2c6c[8] <= reg180c2c6c[8];
           reg180c2c6c[7] <= reg180c2c6c[7];
           reg180c2c6c[6] <= reg180c2c6c[6];
           reg180c2c6c[5] <= reg180c2c6c[5];
           reg180c2c6c[4] <= reg180c2c6c[4];
           reg180c2c6c[3] <= reg180c2c6c[3];
           reg180c2c6c[2] <= reg180c2c6c[2];
           reg180c2c6c[1] <= reg180c2c6c[1];
           reg180c2c6c[0] <= reg180c2c6c[0];
         end
     end
  end

//addr = 0x180c2c70
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c70[10] <= 1'h0;
         reg180c2c70[9] <= 1'h0;
         reg180c2c70[8] <= 1'h0;
         reg180c2c70[2] <= 1'h0;
         reg180c2c70[1] <= 1'h0;
         reg180c2c70[0] <= 1'h0;
       end
     else begin
       if (write_en[222])
         begin
           reg180c2c70[10] <= write_data[10];
           reg180c2c70[9] <= write_data[9];
           reg180c2c70[8] <= write_data[8];
           reg180c2c70[2] <= write_data[2];
           reg180c2c70[1] <= write_data[1];
           reg180c2c70[0] <= write_data[0];
         end
       else
         begin
           reg180c2c70[10] <= reg180c2c70[10];
           reg180c2c70[9] <= reg180c2c70[9];
           reg180c2c70[8] <= reg180c2c70[8];
           reg180c2c70[2] <= reg180c2c70[2];
           reg180c2c70[1] <= reg180c2c70[1];
           reg180c2c70[0] <= reg180c2c70[0];
         end
     end
  end

//addr = 0x180c2c78
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c78[0] <= 1'h0;
       end
     else begin
       if (write_en[224])
         begin
           reg180c2c78[0] <= write_data[0];
         end
       else
         begin
           reg180c2c78[0] <= reg180c2c78[0];
         end
     end
  end

//addr = 0x180c2c7c
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2c7c[0] <= 1'h0;
       end
     else begin
       if (write_en[225])
         begin
           reg180c2c7c[0] <= write_data[0];
         end
       else
         begin
           reg180c2c7c[0] <= reg180c2c7c[0];
         end
     end
  end

//addr = 0x180c2f90
always @(posedge clk or negedge rst_n)
  begin 
     if(!rst_n)
       begin
         reg180c2f90[8] <= 1'h0;
         reg180c2f90[0] <= 1'h0;
       end
     else begin
       if (write_en[227])
         begin
           reg180c2f90[8] <= write_data[8];
           reg180c2f90[0] <= write_data[0];
         end
       else
         begin
           reg180c2f90[8] <= reg180c2f90[8];
           reg180c2f90[0] <= reg180c2f90[0];
         end
     end
  end

//========================================================//
//==================== read procedure ===================//
//========================================================//

reg [31:0] read_data_ah;      //wire for register hit address
always @(posedge clk or negedge rst_n)
  begin      
    if(!rst_n)
       read_data <= 32'h0;
    else
       if (read_reg) 
          read_data <= read_data_ah;

  end 

//Mux of read_data
always @(*)
  begin 
    case(1'b1)  // synopsys infer_mux_override
			addr_dec[0]:
				read_data_ah = {7'h0,
						reg180c2020[24],
						17'h0,
						reg180c2020[6],
						reg180c2020[5],
						reg180c2020[4],
						2'h0,
						reg180c2020[1],
						reg180c2020[0]};
			addr_dec[1]:
				read_data_ah = {reg180c2028[31:28],
						reg180c2028[27:24],
						reg180c2028[23:20],
						reg180c2028[19],
						2'h0,
						reg180c2028[16],
						6'h0,
						reg180c2028[9:8],
						6'h0,
						reg180c2028[1],
						reg180c2028[0]};
			addr_dec[2]:
				read_data_ah = {30'h0,
						meas_irq,//reg0x180c202c[1]
						reg180c202c[0]};
			addr_dec[3]:
				read_data_ah = {3'h0,
						reg180c2030[28],
						reg180c2030[27],
						24'h0,
						reg180c2030[2],
						reg180c2030[1:0]};
			addr_dec[4]:
				read_data_ah = {6'h0,
						ddr_reset_o_status,//reg0x180c2034[25]
						ddr_cke_o_status,//reg0x180c2034[24]
						6'h0,
						reg180c2034[17],
						reg180c2034[16],
						reg180c2034[15:12],
						9'h0,
						reg180c2034[2],
						reg180c2034[1:0]};
			addr_dec[5]:
				read_data_ah = {31'h0,
						reg180c2038[0]};
			addr_dec[6]:
				read_data_ah = {22'h0,
						reg180c203c[9:8],
						reg180c203c[7:5],
						reg180c203c[4],
						2'h0,
						reg180c203c[1],
						reg180c203c[0]};
			addr_dec[7]:
				read_data_ah = {4'h0,
						reg180c2040[27:24],
						3'h0,
						reg180c2040[20],
						reg180c2040[19],
						reg180c2040[18],
						reg180c2040[17],
						reg180c2040[16],
						reg180c2040[15:8],
						reg180c2040[7:0]};
			addr_dec[8]:
				read_data_ah = {5'h0,
						reg180c2044[26:24],
						6'h0,
						reg180c2044[17],
						reg180c2044[16],
						2'h0,
						reg180c2044[13:12],
						2'h0,
						reg180c2044[9:8],
						2'h0,
						reg180c2044[5:4],
						2'h0,
						reg180c2044[1:0]};
			addr_dec[9]:
				read_data_ah = {21'h0,
						reg180c2050[10:0]};
			addr_dec[10]:
				read_data_ah = {reg180c2060[31:28],
						4'h0,
						reg180c2060[23],
						5'h0,
						reg180c2060[17],
						reg180c2060[16],
						5'h0,
						reg180c2060[10:8],
						5'h0,
						reg180c2060[2:0]};
			addr_dec[11]:
				read_data_ah = {reg180c2064[31:24],
						reg180c2064[23],
						1'h0,
						reg180c2064[21],
						reg180c2064[20],
						8'h0,
						reg180c2064[11:0]};
			addr_dec[12]:
				read_data_ah = {18'h0,
						reg180c2068[13:8],
						2'h0,
						reg180c2068[5:0]};
			addr_dec[13]:
				read_data_ah = {reg180c2080[31:28],
						3'h0,
						reg180c2080[24],
						reg180c2080[23:12],
						1'h0,
						reg180c2080[10],
						reg180c2080[9:8],
						reg180c2080[7],
						1'h0,
						reg180c2080[5],
						reg180c2080[4],
						reg180c2080[3],
						reg180c2080[2],
						reg180c2080[1],
						reg180c2080[0]};
			addr_dec[14]:
				read_data_ah = {6'h0,
						reg180c2088[25],
						reg180c2088[24],
						22'h0,
						reg180c2088[1],
						reg180c2088[0]};
			addr_dec[15]:
				read_data_ah = {16'h0,
						reg180c2090[15:8],
						reg180c2090[7:0]};
			addr_dec[16]:
				read_data_ah = {8'h0,
						reg180c2098[23],
						reg180c2098[22],
						reg180c2098[21:16],
						reg180c2098[15:8],
						reg180c2098[7:0]};
			addr_dec[17]:
				read_data_ah = {10'h0,
						reg180c20a0[21:16],
						2'h0,
						reg180c20a0[13:8],
						7'h0,
						reg180c20a0[0]};
			addr_dec[18]:
				read_data_ah = {23'h0,
						reg180c20f0[8],
						3'h0,
						reg180c20f0[4],
						3'h0,
						reg180c20f0[0]};
			addr_dec[19]:
				read_data_ah = {reg180c2100[31],
						21'h0,
						reg180c2100[9:8],
						5'h0,
						reg180c2100[2:0]};
			addr_dec[20]:
				read_data_ah = {reg180c2110[31:0]};
			addr_dec[21]:
				read_data_ah = {reg180c2114[31:0]};
			addr_dec[22]:
				read_data_ah = {reg180c2118[31:0]};
			addr_dec[23]:
				read_data_ah = {reg180c211c[31:0]};
			addr_dec[24]:
				read_data_ah = {reg180c2120[31:0]};
			addr_dec[25]:
				read_data_ah = {reg180c2130[31:16],
						reg180c2130[15:0]};
			addr_dec[26]:
				read_data_ah = {reg180c2138[31:16],
						reg180c2138[15:0]};
			addr_dec[27]:
				read_data_ah = {reg180c2140[31:16],
						reg180c2140[15:0]};
			addr_dec[28]:
				read_data_ah = {8'h0,
						reg180c2200[23:16],
						2'h0,
						reg180c2200[13:8],
						2'h0,
						reg180c2200[5:0]};
			addr_dec[29]:
				read_data_ah = {3'h0,
						reg180c2208[28:24],
						2'h0,
						reg180c2208[21:16],
						2'h0,
						reg180c2208[13:8],
						reg180c2208[7:0]};
			addr_dec[30]:
				read_data_ah = {4'h0,
						reg180c2210[27:24],
						1'h0,
						reg180c2210[22:16],
						3'h0,
						reg180c2210[12:8],
						2'h0,
						reg180c2210[5:0]};
			addr_dec[31]:
				read_data_ah = {reg180c2218[31:24],
						6'h0,
						reg180c2218[17],
						reg180c2218[16],
						reg180c2218[15:8],
						reg180c2218[7:0]};
			addr_dec[32]:
				read_data_ah = {reg180c2220[31:28],
						2'h0,
						reg180c2220[25:20],
						3'h0,
						reg180c2220[16:12],
						3'h0,
						reg180c2220[8:4],
						reg180c2220[3:0]};
			addr_dec[33]:
				read_data_ah = {8'h0,
						reg180c2228[23:20],
						3'h0,
						reg180c2228[16:12],
						2'h0,
						reg180c2228[9:8],
						2'h0,
						reg180c2228[5:0]};
			addr_dec[34]:
				read_data_ah = {reg180c222c[31:28],
						reg180c222c[27:24],
						reg180c222c[23:20],
						reg180c222c[19:15],
						1'h0,
						reg180c222c[13:8],
						2'h0,
						reg180c222c[5:0]};
			addr_dec[35]:
				read_data_ah = {2'h0,
						reg180c2230[29:24],
						2'h0,
						reg180c2230[21:16],
						2'h0,
						reg180c2230[13:8],
						2'h0,
						reg180c2230[5:0]};
			addr_dec[36]:
				read_data_ah = {reg180c2234[31:22],
						reg180c2234[21:12],
						reg180c2234[11],
						reg180c2234[10],
						reg180c2234[9:0]};
			addr_dec[37]:
				read_data_ah = {2'h0,
						reg180c2238[29:24],
						2'h0,
						reg180c2238[21:16],
						2'h0,
						reg180c2238[13:8],
						2'h0,
						reg180c2238[5:0]};
			addr_dec[38]:
				read_data_ah = {6'h0,
						reg180c2240[25:16],
						1'h0,
						reg180c2240[14],
						reg180c2240[13],
						reg180c2240[12],
						2'h0,
						reg180c2240[9:0]};
			addr_dec[39]:
				read_data_ah = {30'h0,
						reg180c2244[1],
						reg180c2244[0]};
			addr_dec[40]:
				read_data_ah = {3'h0,
						reg180c2248[28:24],
						3'h0,
						reg180c2248[20:16],
						3'h0,
						reg180c2248[12:8],
						3'h0,
						reg180c2248[4:0]};
			addr_dec[41]:
				read_data_ah = {reg180c22a0[31:16],
						5'h0,
						reg180c22a0[10:0]};
			addr_dec[42]:
				read_data_ah = {reg180c22a4[31:16],
						reg180c22a4[15:0]};
			addr_dec[43]:
				read_data_ah = {reg180c22a8[31:24],
						1'h0,
						reg180c22a8[22:12],
						3'h0,
						reg180c22a8[8:0]};
			addr_dec[44]:
				read_data_ah = {9'h0,
						reg180c22ac[22:12],
						3'h0,
						reg180c22ac[8:0]};
			addr_dec[45]:
				read_data_ah = {3'h0,
						reg180c2300[28:24],
						3'h0,
						reg180c2300[20:16],
						3'h0,
						reg180c2300[12:8],
						3'h0,
						reg180c2300[4:0]};
			addr_dec[46]:
				read_data_ah = {18'h0,
						reg180c2304[13],
						reg180c2304[12:8],
						3'h0,
						reg180c2304[4:0]};
			addr_dec[47]:
				read_data_ah = {8'h0,
						zq_cal,//reg0x180c2600[23]
						self_refresh,//reg0x180c2600[22]
						power_down,//reg0x180c2600[21]
						modr_lpddr4_fps,//reg0x180c2600[20:19]
						modr_ca_training,//reg0x180c2600[18:11]
						modr_geardown_mode,//reg0x180c2600[10]
						modr_mpr_mode,//reg0x180c2600[9]
						modr_wl,//reg0x180c2600[8:6]
						modr_rl,//reg0x180c2600[5:1]
						modr_write_level};//reg0x180c2600[0]
			addr_dec[48]:
				read_data_ah = {30'h0,
						modr_write_preamble,//reg0x180c2608[1]
						modr_read_preamble};//reg0x180c2608[0]
			addr_dec[49]:
				read_data_ah = {rk1_parser_rbus_dbg};//reg0x180c270c[31:0]
			addr_dec[50]:
				read_data_ah = {4'h0,
						reg180c2710[27:24],
						reg180c2710[23:16],
						16'h0};
			addr_dec[51]:
				read_data_ah = {n_rk0_qos_debug};//reg0x180c2714[31:0]
			addr_dec[52]:
				read_data_ah = {reg180c2718[31],
						1'h0,
						reg180c2718[29:24],
						modr_full_data,//reg0x180c2718[23:4]
						1'h0,
						dbe_err_flag1,//reg0x180c2718[2]
						dbe_err_flag0,//reg0x180c2718[1]
						fmtr_unknown_cmd};//reg0x180c2718[0]
			addr_dec[53]:
				read_data_ah = {22'h0,
						reg180c271c[9:8],
						6'h0,
						reg180c271c[1:0]};
			addr_dec[54]:
				read_data_ah = {17'h0,
						reg180c2720[14:12],
						1'h0,
						reg180c2720[10:8],
						3'h0,
						reg180c2720[4:0]};
			addr_dec[55]:
				read_data_ah = {rk0_parser_rbus_dbg};//reg0x180c2724[31:0]
			addr_dec[56]:
				read_data_ah = {28'h0,
						rk1_wr_chop_no_mask,//reg0x180c2728[3]
						rk1_active_ddr_num_mismatch,//reg0x180c2728[2]
						rk0_wr_chop_no_mask,//reg0x180c2728[1]
						rk0_active_ddr_num_mismatch};//reg0x180c2728[0]
			addr_dec[57]:
				read_data_ah = {mc_write_ctrl_error_status};//reg0x180c272c[31:0]
			addr_dec[58]:
				read_data_ah = {mc_read_ctrl_error_status};//reg0x180c2730[31:0]
			addr_dec[59]:
				read_data_ah = {26'h0,
						reg180c2734[5:0]};
			addr_dec[60]:
				read_data_ah = {n_rk1_qos_debug};//reg0x180c2738[31:0]
			addr_dec[61]:
				read_data_ah = {8'h0,
						reg180c273c[23:16],
						15'h0,
						reg180c273c[0]};
			addr_dec[62]:
				read_data_ah = {reg180c2740[31:0]};
			addr_dec[63]:
				read_data_ah = {reg180c2744[31:0]};
			addr_dec[64]:
				read_data_ah = {reg180c2748[31:0]};
			addr_dec[65]:
				read_data_ah = {reg180c274c[31:0]};
			addr_dec[66]:
				read_data_ah = {reg180c2750[31:0]};
			addr_dec[67]:
				read_data_ah = {reg180c2754[31:0]};
			addr_dec[68]:
				read_data_ah = {reg180c2758[31:0]};
			addr_dec[69]:
				read_data_ah = {reg180c275c[31:0]};
			addr_dec[70]:
				read_data_ah = {reg180c2760[31:0]};
			addr_dec[71]:
				read_data_ah = {reg180c2764[31:0]};
			addr_dec[72]:
				read_data_ah = {reg180c2768[31:0]};
			addr_dec[73]:
				read_data_ah = {reg180c276c[31:0]};
			addr_dec[74]:
				read_data_ah = {reg180c2770[31:0]};
			addr_dec[75]:
				read_data_ah = {reg180c2774[31:0]};
			addr_dec[76]:
				read_data_ah = {reg180c2778[31:0]};
			addr_dec[77]:
				read_data_ah = {reg180c277c[31:0]};
			addr_dec[78]:
				read_data_ah = {reg180c2780[31:0]};
			addr_dec[79]:
				read_data_ah = {reg180c2784[31:0]};
			addr_dec[80]:
				read_data_ah = {reg180c2788[31:0]};
			addr_dec[81]:
				read_data_ah = {reg180c278c[31:0]};
			addr_dec[82]:
				read_data_ah = {reg180c2800[31:28],
						reg180c2800[27:24],
						reg180c2800[23:20],
						reg180c2800[19:16],
						reg180c2800[15:2],
						reg180c2800[1:0]};
			addr_dec[83]:
				read_data_ah = {reg180c2804[31:28],
						reg180c2804[27:24],
						reg180c2804[23:20],
						reg180c2804[19:16],
						reg180c2804[15:2],
						reg180c2804[1:0]};
			addr_dec[84]:
				read_data_ah = {reg180c2808[31:28],
						reg180c2808[27:24],
						reg180c2808[23:20],
						reg180c2808[19:16],
						reg180c2808[15:2],
						reg180c2808[1:0]};
			addr_dec[85]:
				read_data_ah = {reg180c280c[31:28],
						reg180c280c[27:24],
						reg180c280c[23:20],
						reg180c280c[19:16],
						reg180c280c[15:2],
						reg180c280c[1:0]};
			addr_dec[86]:
				read_data_ah = {reg180c2810[31:28],
						reg180c2810[27:24],
						reg180c2810[23:20],
						reg180c2810[19:16],
						reg180c2810[15:2],
						reg180c2810[1:0]};
			addr_dec[87]:
				read_data_ah = {reg180c2814[31:28],
						reg180c2814[27:24],
						reg180c2814[23:20],
						reg180c2814[19:16],
						reg180c2814[15:2],
						reg180c2814[1:0]};
			addr_dec[88]:
				read_data_ah = {reg180c2818[31:28],
						reg180c2818[27:24],
						reg180c2818[23:20],
						reg180c2818[19:16],
						reg180c2818[15:2],
						reg180c2818[1:0]};
			addr_dec[89]:
				read_data_ah = {reg180c281c[31:28],
						reg180c281c[27:24],
						reg180c281c[23:20],
						reg180c281c[19:16],
						reg180c281c[15:2],
						reg180c281c[1:0]};
			addr_dec[90]:
				read_data_ah = {reg180c2820[31:28],
						reg180c2820[27:24],
						reg180c2820[23:20],
						reg180c2820[19:16],
						reg180c2820[15:2],
						reg180c2820[1:0]};
			addr_dec[91]:
				read_data_ah = {reg180c2824[31:28],
						reg180c2824[27:24],
						reg180c2824[23:20],
						reg180c2824[19:16],
						reg180c2824[15:2],
						reg180c2824[1:0]};
			addr_dec[92]:
				read_data_ah = {reg180c2828[31:28],
						reg180c2828[27:24],
						reg180c2828[23:20],
						reg180c2828[19:16],
						reg180c2828[15:2],
						reg180c2828[1:0]};
			addr_dec[93]:
				read_data_ah = {reg180c2840[31:16],
						reg180c2840[15:0]};
			addr_dec[94]:
				read_data_ah = {reg180c2844[31:16],
						reg180c2844[15:0]};
			addr_dec[95]:
				read_data_ah = {reg180c2848[31:16],
						reg180c2848[15:0]};
			addr_dec[96]:
				read_data_ah = {reg180c284c[31:16],
						reg180c284c[15:0]};
			addr_dec[97]:
				read_data_ah = {reg180c2850[31:16],
						reg180c2850[15:0]};
			addr_dec[98]:
				read_data_ah = {reg180c2854[31:16],
						reg180c2854[15:0]};
			addr_dec[99]:
				read_data_ah = {reg180c2858[31:16],
						reg180c2858[15:0]};
			addr_dec[100]:
				read_data_ah = {reg180c285c[31:16],
						reg180c285c[15:0]};
			addr_dec[101]:
				read_data_ah = {reg180c2860[31:16],
						reg180c2860[15:0]};
			addr_dec[102]:
				read_data_ah = {reg180c2864[31:16],
						reg180c2864[15:0]};
			addr_dec[103]:
				read_data_ah = {reg180c2868[31:16],
						reg180c2868[15:0]};
			addr_dec[104]:
				read_data_ah = {16'h0,
						reg180c2880[15:0]};
			addr_dec[105]:
				read_data_ah = {16'h0,
						reg180c2884[15:0]};
			addr_dec[106]:
				read_data_ah = {16'h0,
						reg180c2888[15:0]};
			addr_dec[107]:
				read_data_ah = {16'h0,
						reg180c288c[15:0]};
			addr_dec[108]:
				read_data_ah = {16'h0,
						reg180c2890[15:0]};
			addr_dec[109]:
				read_data_ah = {16'h0,
						reg180c2894[15:0]};
			addr_dec[110]:
				read_data_ah = {16'h0,
						reg180c2898[15:0]};
			addr_dec[111]:
				read_data_ah = {16'h0,
						reg180c289c[15:0]};
			addr_dec[112]:
				read_data_ah = {16'h0,
						reg180c28a0[15:0]};
			addr_dec[113]:
				read_data_ah = {16'h0,
						reg180c28a4[15:0]};
			addr_dec[114]:
				read_data_ah = {16'h0,
						reg180c28a8[15:0]};
			addr_dec[115]:
				read_data_ah = {9'h0,
						reg180c2a00[22],
						2'h0,
						reg180c2a00[19],
						reg180c2a00[18],
						reg180c2a00[17],
						reg180c2a00[16],
						reg180c2a00[15],
						reg180c2a00[14],
						reg180c2a00[13],
						reg180c2a00[12],
						reg180c2a00[11],
						reg180c2a00[10],
						reg180c2a00[9],
						reg180c2a00[8],
						reg180c2a00[7],
						reg180c2a00[6],
						reg180c2a00[5:4],
						reg180c2a00[3],
						reg180c2a00[2],
						reg180c2a00[1],
						reg180c2a00[0]};
			addr_dec[116]:
				read_data_ah = {30'h0,
						reg180c2a04[1],
						reg180c2a04[0]};
			addr_dec[117]:
				read_data_ah = {reg180c2a10[31:24],
						reg180c2a10[23:16],
						reg180c2a10[15:8],
						reg180c2a10[7:0]};
			addr_dec[118]:
				read_data_ah = {reg180c2a14[31:24],
						reg180c2a14[23:16],
						16'h0};
			addr_dec[119]:
				read_data_ah = {reg180c2a18[31:20],
						1'h0,
						reg180c2a18[18:16],
						3'h0,
						reg180c2a18[12:8],
						3'h0,
						reg180c2a18[4],
						4'h0};
			addr_dec[120]:
				read_data_ah = {3'h0,
						reg180c2a1c[28:16],
						16'h0};
			addr_dec[121]:
				read_data_ah = {3'h0,
						reg180c2a20[28:16],
						3'h0,
						reg180c2a20[12:0]};
			addr_dec[122]:
				read_data_ah = {10'h0,
						reg180c2a24[21:16],
						3'h0,
						reg180c2a24[12:8],
						reg180c2a24[7:0]};
			addr_dec[123]:
				read_data_ah = {reg180c2a28[31:30],
						5'h0,
						reg180c2a28[24],
						reg180c2a28[23:20],
						3'h0,
						reg180c2a28[16:8],
						reg180c2a28[7],
						reg180c2a28[6],
						reg180c2a28[5],
						reg180c2a28[4],
						3'h0,
						reg180c2a28[0]};
			addr_dec[124]:
				read_data_ah = {6'h0,
						reg180c2a2c[25:16],
						8'h0,
						reg180c2a2c[7:4],
						reg180c2a2c[3:0]};
			addr_dec[125]:
				read_data_ah = {10'h0,
						reg180c2a30[21:16],
						13'h0,
						reg180c2a30[2],
						reg180c2a30[1],
						reg180c2a30[0]};
			addr_dec[126]:
				read_data_ah = {6'h0,
						reg180c2a34[25:16],
						15'h0,
						reg180c2a34[0]};
			addr_dec[127]:
				read_data_ah = {8'h0,
						reg180c2a3c[23:20],
						reg180c2a3c[19:16],
						reg180c2a3c[15:8],
						reg180c2a3c[7:0]};
			addr_dec[128]:
				read_data_ah = {reg180c2a60[31:28],
						reg180c2a60[27:24],
						reg180c2a60[23:20],
						reg180c2a60[19:16],
						reg180c2a60[15:12],
						reg180c2a60[11],
						reg180c2a60[10],
						reg180c2a60[9:8],
						reg180c2a60[7],
						2'h0,
						reg180c2a60[4],
						reg180c2a60[3],
						reg180c2a60[2],
						reg180c2a60[1],
						1'h0};
			addr_dec[129]:
				read_data_ah = {reg180c2a64[31:24],
						8'h0,
						reg180c2a64[15:8],
						8'h0};
			addr_dec[130]:
				read_data_ah = {reg180c2a68[31:20],
						reg180c2a68[19:8],
						4'h0,
						reg180c2a68[3:0]};
			addr_dec[131]:
				read_data_ah = {reg180c2a6c[31:28],
						2'h0,
						reg180c2a6c[25:20],
						reg180c2a6c[19:8],
						reg180c2a6c[7:4],
						3'h0,
						reg180c2a6c[0]};
			addr_dec[132]:
				read_data_ah = {22'h0,
						reg180c2a70[9:0]};
			addr_dec[133]:
				read_data_ah = {reg180c2a74[31:28],
						reg180c2a74[27:24],
						reg180c2a74[23:20],
						reg180c2a74[19:16],
						reg180c2a74[15:12],
						reg180c2a74[11:8],
						8'h0};
			addr_dec[134]:
				read_data_ah = {reg180c2a80[31:28],
						reg180c2a80[27:24],
						reg180c2a80[23:20],
						reg180c2a80[19:16],
						reg180c2a80[15:12],
						reg180c2a80[11],
						reg180c2a80[10],
						reg180c2a80[9:8],
						reg180c2a80[7],
						2'h0,
						reg180c2a80[4],
						reg180c2a80[3],
						reg180c2a80[2],
						reg180c2a80[1],
						1'h0};
			addr_dec[135]:
				read_data_ah = {reg180c2a84[31:24],
						8'h0,
						reg180c2a84[15:8],
						8'h0};
			addr_dec[136]:
				read_data_ah = {reg180c2a88[31:20],
						reg180c2a88[19:8],
						4'h0,
						reg180c2a88[3:0]};
			addr_dec[137]:
				read_data_ah = {reg180c2a8c[31:28],
						2'h0,
						reg180c2a8c[25:20],
						reg180c2a8c[19:8],
						reg180c2a8c[7:4],
						3'h0,
						reg180c2a8c[0]};
			addr_dec[138]:
				read_data_ah = {22'h0,
						reg180c2a90[9:0]};
			addr_dec[139]:
				read_data_ah = {reg180c2a94[31:28],
						reg180c2a94[27:24],
						reg180c2a94[23:20],
						reg180c2a94[19:16],
						reg180c2a94[15:12],
						reg180c2a94[11:8],
						8'h0};
			addr_dec[140]:
				read_data_ah = {reg180c2aa0[31:28],
						reg180c2aa0[27:24],
						reg180c2aa0[23:20],
						reg180c2aa0[19:16],
						reg180c2aa0[15:12],
						reg180c2aa0[11],
						reg180c2aa0[10],
						reg180c2aa0[9:8],
						reg180c2aa0[7],
						2'h0,
						reg180c2aa0[4],
						reg180c2aa0[3],
						reg180c2aa0[2],
						reg180c2aa0[1],
						1'h0};
			addr_dec[141]:
				read_data_ah = {reg180c2aa4[31:24],
						8'h0,
						reg180c2aa4[15:8],
						8'h0};
			addr_dec[142]:
				read_data_ah = {reg180c2aa8[31:20],
						reg180c2aa8[19:8],
						4'h0,
						reg180c2aa8[3:0]};
			addr_dec[143]:
				read_data_ah = {reg180c2aac[31:28],
						2'h0,
						reg180c2aac[25:20],
						reg180c2aac[19:8],
						reg180c2aac[7:4],
						3'h0,
						reg180c2aac[0]};
			addr_dec[144]:
				read_data_ah = {22'h0,
						reg180c2ab0[9:0]};
			addr_dec[145]:
				read_data_ah = {reg180c2ab4[31:28],
						reg180c2ab4[27:24],
						reg180c2ab4[23:20],
						reg180c2ab4[19:16],
						reg180c2ab4[15:12],
						reg180c2ab4[11:8],
						8'h0};
			addr_dec[146]:
				read_data_ah = {reg180c2ac0[31:28],
						reg180c2ac0[27:24],
						reg180c2ac0[23:20],
						reg180c2ac0[19:16],
						reg180c2ac0[15:12],
						reg180c2ac0[11],
						reg180c2ac0[10],
						reg180c2ac0[9:8],
						reg180c2ac0[7],
						2'h0,
						reg180c2ac0[4],
						reg180c2ac0[3],
						reg180c2ac0[2],
						reg180c2ac0[1],
						1'h0};
			addr_dec[147]:
				read_data_ah = {reg180c2ac4[31:24],
						8'h0,
						reg180c2ac4[15:8],
						8'h0};
			addr_dec[148]:
				read_data_ah = {reg180c2ac8[31:20],
						reg180c2ac8[19:8],
						4'h0,
						reg180c2ac8[3:0]};
			addr_dec[149]:
				read_data_ah = {reg180c2acc[31:28],
						2'h0,
						reg180c2acc[25:20],
						reg180c2acc[19:8],
						reg180c2acc[7:4],
						3'h0,
						reg180c2acc[0]};
			addr_dec[150]:
				read_data_ah = {22'h0,
						reg180c2ad0[9:0]};
			addr_dec[151]:
				read_data_ah = {reg180c2ad4[31:28],
						reg180c2ad4[27:24],
						reg180c2ad4[23:20],
						reg180c2ad4[19:16],
						reg180c2ad4[15:12],
						reg180c2ad4[11:8],
						8'h0};
			addr_dec[152]:
				read_data_ah = {reg180c2ae0[31:28],
						reg180c2ae0[27:24],
						reg180c2ae0[23:20],
						reg180c2ae0[19:16],
						reg180c2ae0[15:12],
						reg180c2ae0[11],
						reg180c2ae0[10],
						reg180c2ae0[9:8],
						reg180c2ae0[7],
						2'h0,
						reg180c2ae0[4],
						reg180c2ae0[3],
						reg180c2ae0[2],
						reg180c2ae0[1],
						1'h0};
			addr_dec[153]:
				read_data_ah = {reg180c2ae4[31:24],
						8'h0,
						reg180c2ae4[15:8],
						8'h0};
			addr_dec[154]:
				read_data_ah = {reg180c2ae8[31:20],
						reg180c2ae8[19:8],
						4'h0,
						reg180c2ae8[3:0]};
			addr_dec[155]:
				read_data_ah = {reg180c2aec[31:28],
						2'h0,
						reg180c2aec[25:20],
						reg180c2aec[19:8],
						reg180c2aec[7:4],
						3'h0,
						reg180c2aec[0]};
			addr_dec[156]:
				read_data_ah = {22'h0,
						reg180c2af0[9:0]};
			addr_dec[157]:
				read_data_ah = {reg180c2af4[31:28],
						reg180c2af4[27:24],
						reg180c2af4[23:20],
						reg180c2af4[19:16],
						reg180c2af4[15:12],
						reg180c2af4[11:8],
						8'h0};
			addr_dec[158]:
				read_data_ah = {reg180c2b00[31:28],
						reg180c2b00[27:24],
						reg180c2b00[23:20],
						reg180c2b00[19:16],
						reg180c2b00[15:12],
						reg180c2b00[11],
						reg180c2b00[10],
						reg180c2b00[9:8],
						reg180c2b00[7],
						2'h0,
						reg180c2b00[4],
						reg180c2b00[3],
						reg180c2b00[2],
						reg180c2b00[1],
						1'h0};
			addr_dec[159]:
				read_data_ah = {reg180c2b04[31:24],
						8'h0,
						reg180c2b04[15:8],
						8'h0};
			addr_dec[160]:
				read_data_ah = {reg180c2b08[31:20],
						reg180c2b08[19:8],
						4'h0,
						reg180c2b08[3:0]};
			addr_dec[161]:
				read_data_ah = {reg180c2b0c[31:28],
						2'h0,
						reg180c2b0c[25:20],
						reg180c2b0c[19:8],
						reg180c2b0c[7:4],
						3'h0,
						reg180c2b0c[0]};
			addr_dec[162]:
				read_data_ah = {22'h0,
						reg180c2b10[9:0]};
			addr_dec[163]:
				read_data_ah = {reg180c2b14[31:28],
						reg180c2b14[27:24],
						reg180c2b14[23:20],
						reg180c2b14[19:16],
						reg180c2b14[15:12],
						reg180c2b14[11:8],
						8'h0};
			addr_dec[164]:
				read_data_ah = {reg180c2b20[31:28],
						reg180c2b20[27:24],
						reg180c2b20[23:20],
						reg180c2b20[19:16],
						reg180c2b20[15:12],
						reg180c2b20[11],
						reg180c2b20[10],
						reg180c2b20[9:8],
						reg180c2b20[7],
						2'h0,
						reg180c2b20[4],
						reg180c2b20[3],
						reg180c2b20[2],
						reg180c2b20[1],
						1'h0};
			addr_dec[165]:
				read_data_ah = {reg180c2b24[31:24],
						8'h0,
						reg180c2b24[15:8],
						8'h0};
			addr_dec[166]:
				read_data_ah = {reg180c2b28[31:20],
						reg180c2b28[19:8],
						4'h0,
						reg180c2b28[3:0]};
			addr_dec[167]:
				read_data_ah = {reg180c2b2c[31:28],
						2'h0,
						reg180c2b2c[25:20],
						reg180c2b2c[19:8],
						reg180c2b2c[7:4],
						3'h0,
						reg180c2b2c[0]};
			addr_dec[168]:
				read_data_ah = {22'h0,
						reg180c2b30[9:0]};
			addr_dec[169]:
				read_data_ah = {reg180c2b34[31:28],
						reg180c2b34[27:24],
						reg180c2b34[23:20],
						reg180c2b34[19:16],
						reg180c2b34[15:12],
						reg180c2b34[11:8],
						8'h0};
			addr_dec[170]:
				read_data_ah = {reg180c2b40[31:28],
						reg180c2b40[27:24],
						reg180c2b40[23:20],
						reg180c2b40[19:16],
						reg180c2b40[15:12],
						reg180c2b40[11],
						reg180c2b40[10],
						reg180c2b40[9:8],
						reg180c2b40[7],
						2'h0,
						reg180c2b40[4],
						reg180c2b40[3],
						reg180c2b40[2],
						reg180c2b40[1],
						1'h0};
			addr_dec[171]:
				read_data_ah = {reg180c2b44[31:24],
						8'h0,
						reg180c2b44[15:8],
						8'h0};
			addr_dec[172]:
				read_data_ah = {reg180c2b48[31:20],
						reg180c2b48[19:8],
						4'h0,
						reg180c2b48[3:0]};
			addr_dec[173]:
				read_data_ah = {reg180c2b4c[31:28],
						2'h0,
						reg180c2b4c[25:20],
						reg180c2b4c[19:8],
						reg180c2b4c[7:4],
						3'h0,
						reg180c2b4c[0]};
			addr_dec[174]:
				read_data_ah = {22'h0,
						reg180c2b50[9:0]};
			addr_dec[175]:
				read_data_ah = {reg180c2b54[31:28],
						reg180c2b54[27:24],
						reg180c2b54[23:20],
						reg180c2b54[19:16],
						reg180c2b54[15:12],
						reg180c2b54[11:8],
						8'h0};
			addr_dec[176]:
				read_data_ah = {reg180c2b60[31:28],
						reg180c2b60[27:24],
						reg180c2b60[23:20],
						reg180c2b60[19:16],
						reg180c2b60[15:12],
						reg180c2b60[11],
						reg180c2b60[10],
						reg180c2b60[9:8],
						reg180c2b60[7],
						2'h0,
						reg180c2b60[4],
						reg180c2b60[3],
						reg180c2b60[2],
						reg180c2b60[1],
						1'h0};
			addr_dec[177]:
				read_data_ah = {reg180c2b64[31:24],
						8'h0,
						reg180c2b64[15:8],
						8'h0};
			addr_dec[178]:
				read_data_ah = {reg180c2b68[31:20],
						reg180c2b68[19:8],
						4'h0,
						reg180c2b68[3:0]};
			addr_dec[179]:
				read_data_ah = {reg180c2b6c[31:28],
						2'h0,
						reg180c2b6c[25:20],
						reg180c2b6c[19:8],
						reg180c2b6c[7:4],
						3'h0,
						reg180c2b6c[0]};
			addr_dec[180]:
				read_data_ah = {22'h0,
						reg180c2b70[9:0]};
			addr_dec[181]:
				read_data_ah = {reg180c2b74[31:28],
						reg180c2b74[27:24],
						reg180c2b74[23:20],
						reg180c2b74[19:16],
						reg180c2b74[15:12],
						reg180c2b74[11:8],
						8'h0};
			addr_dec[182]:
				read_data_ah = {reg180c2b80[31:28],
						reg180c2b80[27:24],
						reg180c2b80[23:20],
						reg180c2b80[19:16],
						reg180c2b80[15:12],
						reg180c2b80[11],
						reg180c2b80[10],
						reg180c2b80[9:8],
						reg180c2b80[7],
						2'h0,
						reg180c2b80[4],
						reg180c2b80[3],
						reg180c2b80[2],
						reg180c2b80[1],
						1'h0};
			addr_dec[183]:
				read_data_ah = {reg180c2b84[31:24],
						8'h0,
						reg180c2b84[15:8],
						8'h0};
			addr_dec[184]:
				read_data_ah = {reg180c2b88[31:20],
						reg180c2b88[19:8],
						4'h0,
						reg180c2b88[3:0]};
			addr_dec[185]:
				read_data_ah = {reg180c2b8c[31:28],
						2'h0,
						reg180c2b8c[25:20],
						reg180c2b8c[19:8],
						reg180c2b8c[7:4],
						3'h0,
						reg180c2b8c[0]};
			addr_dec[186]:
				read_data_ah = {22'h0,
						reg180c2b90[9:0]};
			addr_dec[187]:
				read_data_ah = {reg180c2b94[31:28],
						reg180c2b94[27:24],
						reg180c2b94[23:20],
						reg180c2b94[19:16],
						reg180c2b94[15:12],
						reg180c2b94[11:8],
						8'h0};
			addr_dec[188]:
				read_data_ah = {reg180c2ba0[31:28],
						reg180c2ba0[27:24],
						reg180c2ba0[23:20],
						reg180c2ba0[19:16],
						reg180c2ba0[15:12],
						reg180c2ba0[11],
						reg180c2ba0[10],
						reg180c2ba0[9:8],
						reg180c2ba0[7],
						2'h0,
						reg180c2ba0[4],
						reg180c2ba0[3],
						reg180c2ba0[2],
						reg180c2ba0[1],
						1'h0};
			addr_dec[189]:
				read_data_ah = {reg180c2ba4[31:24],
						8'h0,
						reg180c2ba4[15:8],
						8'h0};
			addr_dec[190]:
				read_data_ah = {reg180c2ba8[31:20],
						reg180c2ba8[19:8],
						4'h0,
						reg180c2ba8[3:0]};
			addr_dec[191]:
				read_data_ah = {reg180c2bac[31:28],
						2'h0,
						reg180c2bac[25:20],
						reg180c2bac[19:8],
						reg180c2bac[7:4],
						3'h0,
						reg180c2bac[0]};
			addr_dec[192]:
				read_data_ah = {22'h0,
						reg180c2bb0[9:0]};
			addr_dec[193]:
				read_data_ah = {reg180c2bb4[31:28],
						reg180c2bb4[27:24],
						reg180c2bb4[23:20],
						reg180c2bb4[19:16],
						reg180c2bb4[15:12],
						reg180c2bb4[11:8],
						8'h0};
			addr_dec[194]:
				read_data_ah = {5'h0,
						reg180c2c00[26:16],
						6'h0,
						reg180c2c00[9:8],
						reg180c2c00[7:6],
						reg180c2c00[5],
						reg180c2c00[4],
						reg180c2c00[3:0]};
			addr_dec[195]:
				read_data_ah = {reg180c2c04[31],
						4'h0,
						meas_sram_cur_w_addr,//reg0x180c2c04[26:16]
						reg180c2c04[15],
						4'h0,
						reg180c2c04[10:0]};
			addr_dec[196]:
				read_data_ah = {reg180c2c08[31],
						reg180c2c08[30],
						reg180c2c08[29],
						reg180c2c08[28],
						17'h0,
						reg180c2c08[10:9],
						reg180c2c08[8],
						meas_serial_cnt,//reg0x180c2c08[7:6]
						reg180c2c08[5],
						reg180c2c08[4],
						3'h0,
						reg180c2c08[0]};
			addr_dec[197]:
				read_data_ah = {reg180c2c0c[31:0]};
			addr_dec[198]:
				read_data_ah = {meas_timer1_cnt};//reg0x180c2c10[31:0]
			addr_dec[199]:
				read_data_ah = {7'h0,
						reg180c2c14[24],
						reg180c2c14[23:16],
						reg180c2c14[15:12],
						1'h0,
						reg180c2c14[10],
						reg180c2c14[9:8],
						8'h0};
			addr_dec[200]:
				read_data_ah = {7'h0,
						reg180c2c18[24],
						reg180c2c18[23:16],
						reg180c2c18[15:12],
						1'h0,
						reg180c2c18[10],
						reg180c2c18[9:8],
						7'h0,
						reg180c2c18[0]};
			addr_dec[201]:
				read_data_ah = {7'h0,
						reg180c2c1c[24],
						reg180c2c1c[23:16],
						reg180c2c1c[15:12],
						1'h0,
						reg180c2c1c[10],
						reg180c2c1c[9:8],
						7'h0,
						reg180c2c1c[0]};
			addr_dec[202]:
				read_data_ah = {7'h0,
						reg180c2c20[24],
						reg180c2c20[23:16],
						reg180c2c20[15:12],
						1'h0,
						reg180c2c20[10],
						reg180c2c20[9:8],
						7'h0,
						reg180c2c20[0]};
			addr_dec[203]:
				read_data_ah = {meas_cnt1_r};//reg0x180c2c24[31:0]
			addr_dec[204]:
				read_data_ah = {meas_cnt1_w};//reg0x180c2c28[31:0]
			addr_dec[205]:
				read_data_ah = {meas_cnt2_r};//reg0x180c2c2c[31:0]
			addr_dec[206]:
				read_data_ah = {meas_cnt2_w};//reg0x180c2c30[31:0]
			addr_dec[207]:
				read_data_ah = {meas_cnt3_r};//reg0x180c2c34[31:0]
			addr_dec[208]:
				read_data_ah = {meas_cnt3_w};//reg0x180c2c38[31:0]
			addr_dec[209]:
				read_data_ah = {meas_cnt4_r};//reg0x180c2c3c[31:0]
			addr_dec[210]:
				read_data_ah = {meas_cnt4_w};//reg0x180c2c40[31:0]
			addr_dec[211]:
				read_data_ah = {reg180c2c44[31],
						reg180c2c44[30],
						reg180c2c44[29],
						reg180c2c44[28],
						reg180c2c44[27:26],
						reg180c2c44[25],
						reg180c2c44[24],
						reg180c2c44[23],
						reg180c2c44[22:21],
						reg180c2c44[20],
						reg180c2c44[19],
						11'h0,
						meas_field_status};//reg0x180c2c44[7:0]
			addr_dec[212]:
				read_data_ah = {meas_sram_data_valid,//reg0x180c2c48[31]
						meas_sram_data_0};//reg0x180c2c48[30:0]
			addr_dec[213]:
				read_data_ah = {meas_sram_data_1};//reg0x180c2c4c[31:0]
			addr_dec[214]:
				read_data_ah = {12'h0,
						reg180c2c50[19:12],
						4'h0,
						reg180c2c50[7:0]};
			addr_dec[215]:
				read_data_ah = {reg180c2c54[31:0]};
			addr_dec[216]:
				read_data_ah = {28'h0,
						reg180c2c58[3],
						reg180c2c58[2],
						cnt2_irq_status,//reg0x180c2c58[1]
						cnt1_irq_status};//reg0x180c2c58[0]
			addr_dec[217]:
				read_data_ah = {reg180c2c5c[31],
						7'h0,
						reg180c2c5c[23:16],
						6'h0,
						reg180c2c5c[9:8],
						4'h0,
						reg180c2c5c[3],
						1'h0,
						reg180c2c5c[1],
						reg180c2c5c[0]};
			addr_dec[218]:
				read_data_ah = {reg180c2c60[31:3],
						3'h0};
			addr_dec[219]:
				read_data_ah = {reg180c2c64[31:3],
						3'h0};
			addr_dec[220]:
				read_data_ah = {eff_bist_done,//reg0x180c2c68[31]
						eff_bist_fail_0,//reg0x180c2c68[30]
						eff_bist_drf_done,//reg0x180c2c68[29]
						eff_drf_bist_fail_0,//reg0x180c2c68[28]
						eff_bist_drf_pause,//reg0x180c2c68[27]
						eff_bist_fail_1,//reg0x180c2c68[26]
						eff_bist_fail_all,//reg0x180c2c68[25]
						eff_drf_bist_fail_1,//reg0x180c2c68[24]
						eff_drf_bist_fail_all,//reg0x180c2c68[23]
						2'h0,
						reg180c2c68[20],
						reg180c2c68[19],
						reg180c2c68[18],
						reg180c2c68[17],
						reg180c2c68[16],
						reg180c2c68[15],
						1'h0,
						reg180c2c68[13],
						reg180c2c68[12],
						reg180c2c68[11:8],
						reg180c2c68[7],
						reg180c2c68[6],
						reg180c2c68[5],
						reg180c2c68[4],
						reg180c2c68[3],
						reg180c2c68[2],
						reg180c2c68[1],
						reg180c2c68[0]};
			addr_dec[221]:
				read_data_ah = {2'h0,
						reg180c2c6c[29],
						reg180c2c6c[28],
						reg180c2c6c[27:26],
						reg180c2c6c[25:24],
						reg180c2c6c[23:22],
						reg180c2c6c[21:20],
						reg180c2c6c[19:18],
						reg180c2c6c[17:16],
						reg180c2c6c[15],
						reg180c2c6c[14],
						reg180c2c6c[13],
						reg180c2c6c[12],
						reg180c2c6c[11],
						reg180c2c6c[10],
						reg180c2c6c[9],
						reg180c2c6c[8],
						reg180c2c6c[7],
						reg180c2c6c[6],
						reg180c2c6c[5],
						reg180c2c6c[4],
						reg180c2c6c[3],
						reg180c2c6c[2],
						reg180c2c6c[1],
						reg180c2c6c[0]};
			addr_dec[222]:
				read_data_ah = {16'h0,
						eff_meas_sram1_drf_fail_all,//reg0x180c2c70[15]
						eff_meas_sram1_fail_all,//reg0x180c2c70[14]
						eff_meas_sram1_drf_start_pause,//reg0x180c2c70[13]
						eff_meas_sram1_drf_bist_done,//reg0x180c2c70[12]
						eff_meas_sram1_bist_done,//reg0x180c2c70[11]
						reg180c2c70[10],
						reg180c2c70[9],
						reg180c2c70[8],
						eff_meas_sram0_drf_fail_all,//reg0x180c2c70[7]
						eff_meas_sram0_fail_all,//reg0x180c2c70[6]
						eff_meas_sram0_drf_start_pause,//reg0x180c2c70[5]
						eff_meas_sram0_drf_bist_done,//reg0x180c2c70[4]
						eff_meas_sram0_bist_done,//reg0x180c2c70[3]
						reg180c2c70[2],
						reg180c2c70[1],
						reg180c2c70[0]};
			addr_dec[223]:
				read_data_ah = {eff_meas_sram1_drf_bist_fail_7,//reg0x180c2c74[31]
						eff_meas_sram1_drf_bist_fail_6,//reg0x180c2c74[30]
						eff_meas_sram1_drf_bist_fail_5,//reg0x180c2c74[29]
						eff_meas_sram1_drf_bist_fail_4,//reg0x180c2c74[28]
						eff_meas_sram1_drf_bist_fail_3,//reg0x180c2c74[27]
						eff_meas_sram1_drf_bist_fail_2,//reg0x180c2c74[26]
						eff_meas_sram1_drf_bist_fail_1,//reg0x180c2c74[25]
						eff_meas_sram1_drf_bist_fail_0,//reg0x180c2c74[24]
						eff_meas_sram0_drf_bist_fail_7,//reg0x180c2c74[23]
						eff_meas_sram0_drf_bist_fail_6,//reg0x180c2c74[22]
						eff_meas_sram0_drf_bist_fail_5,//reg0x180c2c74[21]
						eff_meas_sram0_drf_bist_fail_4,//reg0x180c2c74[20]
						eff_meas_sram0_drf_bist_fail_3,//reg0x180c2c74[19]
						eff_meas_sram0_drf_bist_fail_2,//reg0x180c2c74[18]
						eff_meas_sram0_drf_bist_fail_1,//reg0x180c2c74[17]
						eff_meas_sram0_drf_bist_fail_0,//reg0x180c2c74[16]
						eff_meas_sram1_bist_fail_7,//reg0x180c2c74[15]
						eff_meas_sram1_bist_fail_6,//reg0x180c2c74[14]
						eff_meas_sram1_bist_fail_5,//reg0x180c2c74[13]
						eff_meas_sram1_bist_fail_4,//reg0x180c2c74[12]
						eff_meas_sram1_bist_fail_3,//reg0x180c2c74[11]
						eff_meas_sram1_bist_fail_2,//reg0x180c2c74[10]
						eff_meas_sram1_bist_fail_1,//reg0x180c2c74[9]
						eff_meas_sram1_bist_fail_0,//reg0x180c2c74[8]
						eff_meas_sram0_bist_fail_7,//reg0x180c2c74[7]
						eff_meas_sram0_bist_fail_6,//reg0x180c2c74[6]
						eff_meas_sram0_bist_fail_5,//reg0x180c2c74[5]
						eff_meas_sram0_bist_fail_4,//reg0x180c2c74[4]
						eff_meas_sram0_bist_fail_3,//reg0x180c2c74[3]
						eff_meas_sram0_bist_fail_2,//reg0x180c2c74[2]
						eff_meas_sram0_bist_fail_1,//reg0x180c2c74[1]
						eff_meas_sram0_bist_fail_0};//reg0x180c2c74[0]
			addr_dec[224]:
				read_data_ah = {31'h0,
						reg180c2c78[0]};
			addr_dec[225]:
				read_data_ah = {31'h0,
						reg180c2c7c[0]};
			addr_dec[226]:
				read_data_ah = {30'h0,
						rfu_cmd_lock_err,//reg0x180c2f80[1]
						precharge_all_err};//reg0x180c2f80[0]
			addr_dec[227]:
				read_data_ah = {23'h0,
						reg180c2f90[8],
						7'h0,
						reg180c2f90[0]};
			addr_dec[228]:
				read_data_ah = {23'h0,
						mc_fifo_err_int,//reg0x180c2f94[8]
						4'h0,
						rk1_err_pbk,//reg0x180c2f94[3]
						rk0_err_pbk,//reg0x180c2f94[2]
						rk1_err_active,//reg0x180c2f94[1]
						rk0_err_active};//reg0x180c2f94[0]
			default:
				read_data_ah = 32'h0;
     endcase
  end



endmodule
