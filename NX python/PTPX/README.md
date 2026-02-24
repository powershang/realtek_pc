# PTPX — 波形自動擷取流程

自動執行 PTPX 波形擷取流程，支援 `busy200` 與 `idle2busy200` 兩種模式。

## 工具

### `auto_busy200.py` — 自動波形擷取

**用法：**
```bash
python3 auto_busy200.py            # busy200 模式（預設）
python3 auto_busy200.py idle2busy  # idle2busy200 模式
```

**功能：**
- 自動依序執行各步驟命令
- 即時串流輸出執行結果
- 任一步驟失敗時自動中止
- 預設 Strip Path：`top/u_midas/main_top_apr_inst/main_top_inst/dc_mc_top_inst`

### `detect_env.sh` — 環境偵測腳本

偵測執行環境並設定相關變數。

## 需求

- 執行環境需有 `qqrsh64` 指令
- Python 3.x
