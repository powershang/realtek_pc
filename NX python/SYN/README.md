# SYN — Synthesis 流程控制器

管理 IC 設計後端流程，包含 Synthesis、STA、LEC、Scan，以及 MBIST 面積分析。

## 工具

### `run_syn_sta_lec_scan.py` — 流程控制器

自動執行並監控完整後端流程：Synthesis → STA → LEC → Scan。

**功能：**
- Shell-based 執行，簡化環境問題
- 各步驟：刪除舊檔 → 執行命令 → 監控 process → 等待完成檔
- 執行 log 輸出至 `syn_flow.log`
- 任一步驟失敗自動中止

**用法：**
```bash
python run_syn_sta_lec_scan.py
```

---

### `dcmc_mbist_parsing.py` — MBIST 面積解析

解析 Synthesis 報告中的 MBIST 相關面積數據。

**用法：**
```bash
python dcmc_mbist_parsing.py <report_file>
```

## 需求

- Python 3.x
- EDA 工具環境（DC、PT、Formality、TetraMAX 等）
