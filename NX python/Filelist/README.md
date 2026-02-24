# Filelist — Verilog Filelist 管理工具

管理 Verilog `.f` filelist 的一組工具，主要用於 MBIST 相關檔案的擷取、複製與同步。

## 工具清單

### `dcmc_sync_filelist.py` — MBIST Filelist 同步工具

從一或多個 `.f` filelist 中擷取所有 MBIST 相關檔案路徑，將檔案複製到本地子目錄，並產生新的 filelist。

**用法：**
```bash
python dcmc_sync_filelist.py <input1.f> [input2.f ...] [source_path] [options]
```

**選項：**
```
-o, --output-dir        輸出子目錄名稱（預設：mbist_files）
-f, --filelist          輸出 filelist 檔名（預設：mbist_filelist.f）
-u, --update-original   自動更新原始 .f 檔使用本地路徑
-c, --copy-cells        自動擷取並複製 SRAM cell 檔案
--cell-path             SRAM cell 來源路徑（搭配 -c 使用）
```

### `FileCMDList.py` — 檔案命令清單產生器

批次產生檔案相關命令清單。

### `auto_fixed_unresolved.py` — 未解析路徑自動修正

自動修正 filelist 中無法解析的檔案路徑。

## 輸入格式

`.f` filelist 內含 `$PROJECT_HOME` 變數的路徑，例如：
```
$PROJECT_HOME/rtl/mbist/mbist_ctrl.v
$PROJECT_HOME/rtl/mbist/mbist_core.v
```
