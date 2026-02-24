# Realtek Side Projects

個人在 Realtek 工作期間開發的工具與腳本集合，涵蓋 IC 設計流程自動化、Verilog 分析、以及其他工具。

## 目錄結構

### NX python — IC 設計流程工具（NX 專案）

| 資料夾 | 功能說明 |
|--------|----------|
| [ECO_FLOW](NX%20python/ECO_FLOW/) | ECO 流程自動化，將檔案轉換為 ECO 格式 |
| [Filelist](NX%20python/Filelist/) | Verilog filelist 管理工具，MBIST 檔案擷取與同步 |
| [GENTOP](NX%20python/GENTOP/) | Verilog port 連線分析器（Pattern 版 v1） |
| [GENTOP_V2](NX%20python/GENTOP_V2/) | Verilog 連線產生器（Comment + Pattern 版 v2） |
| [LINT](NX%20python/LINT/) | Verilog Lint 錯誤自動修正工具 |
| [PTPX](NX%20python/PTPX/) | 波形自動擷取流程（busy200 / idle2busy200） |
| [QOS](NX%20python/QOS/) | QoS table register 訊號檢查器 |
| [SEQCMD](NX%20python/SEQCMD/) | VODMA 命令延遲分析器 |
| [SYN](NX%20python/SYN/) | Synthesis / STA / LEC / Scan 流程控制器 |
| [TEMP](NX%20python/TEMP/) | 臨時雜項工具腳本 |

### NonNX — 其他工具

| 資料夾 | 功能說明 |
|--------|----------|
| [DDR](NonNX/DDR/) | DDR Register 比對工具（含 GUI） |
| [SPEC parser](NonNX/SPEC%20parser/) | Verilog regfile 訊號分析器（CLI + GUI） |
| [LINE計程車](NonNX/LINE計程車/) | LINE Bot 計程車叫車系統 |
| [stock](NonNX/stock/) | 台股價值投資策略分析 |
| [RTLdiss](NonNX/RTLdiss/) | RTL 電路研究筆記（AXI Bridge） |
| [TEST](NonNX/TEST/) | 測試/示範腳本 |
| [搶票機器人](NonNX/搶票機器人/) | 拓元自動訂票機器人（含 GUI） |
