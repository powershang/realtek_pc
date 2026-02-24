# SEQCMD — VODMA 命令延遲分析器

分析 ncverilog log 檔中的 VODMA 命令延遲，支援 Python 與 Perl 兩個版本。

## 工具

### `seqcmd_latency_parser.py` — VODMA 延遲分析（Python）

**功能：**
- 追蹤 VODMA 命令與對應回應
- 計算命令發出到完成的延遲
- 兩種分析模式：
  - **Separate 模式**：各 VODMA 類型獨立分析
  - **Combined 模式**（`-c`）：多種 VODMA 類型合併為單一 client
- 統計輸出：逐命令延遲、平均延遲、最大延遲、命令總數
- 延遲分佈圖（`-p`，輸出至 `plots/` 目錄）
- 時間過濾（`-t`，只分析指定時間點之後的命令）

**用法：**
```bash
python seqcmd_latency_parser.py <logfile> <vodma_type1> [vodma_type2 ...]
python seqcmd_latency_parser.py <logfile> -c <type1> <type2>   # combined 模式
python seqcmd_latency_parser.py <logfile> -p <type1>            # 產生圖表
python seqcmd_latency_parser.py <logfile> -t 1000 <type1>       # 從 t=1000 開始分析
```

### `seqcmd_latency_parser.pl` — VODMA 延遲分析（Perl）

Perl 版本，功能相同，適用於 EDA 環境。

### `tcheck_diff.py` — Timing Check 差異比對

比對兩份 timing check 報告的差異。
