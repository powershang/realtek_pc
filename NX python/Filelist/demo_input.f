// Demo input filelist - 模擬您的.f檔案
// 這個檔案包含各種路徑，其中一些包含mbist

// 一般檔案 (不會被處理)
$PROJECT_HOME/hardware/rtl/common/common_defines.v
$PROJECT_HOME/hardware/rtl/cpu/cpu_core.v

// mbist相關檔案 (會被提取和複製)
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_cmd_2p/mbist_mc_fifo_cmd_2p_con.v
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_cmd_2p/wrap_mbist_mc_fifo_cmd_2p.v
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_cmd_2p/drf_mbist_mc_fifo_cmd_2p.v
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_cmd_2p/mbist_mc_fifo_cmd_2p_synchronizer.v
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_cmd_2p/mbist_mc_fifo_cmd_2p.v

// 更多一般檔案
$PROJECT_HOME/hardware/rtl/memory/memory_controller.v

// 更多mbist檔案
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_rdata_2p/mbist_mc_fifo_rdata_2p_con.v
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_rdata_2p/mbist_mc_fifo_rdata_2p.v
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_rdata_2p/wrap_mbist_mc_fifo_rdata_2p.v

// 其他檔案
$PROJECT_HOME/hardware/rtl/interface/interface_defines.v

// 更多mbist檔案在不同目錄
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_wdata_2p/mbist_mc_fifo_wdata_2p.v
$PROJECT_HOME/hardware/rtl/mbist/mbist_mc_fifo_wdata_2p/drf_mbist_mc_fifo_wdata_2p.v 