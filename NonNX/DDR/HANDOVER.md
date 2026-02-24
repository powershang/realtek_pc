# Handover Notes

## Design Decisions

- **Tkinter over PyQt**: 選擇 Tkinter 是因為它是 Python 內建，打包後體積小 (~10MB vs PyQt 的 100MB+)，且功能足夠此工具使用。

- **保留 CLI 相容性**: `register_comparer.py` 的 `print_*` 函式保持不變，新增 `format_*` 函式回傳字串供 GUI 使用。這樣原本用 CLI 的人不受影響。

## Caveats

- **build.bat 在某些環境可能失敗**: 直接用 `pyinstaller` 命令比較可靠。打包指令：
  ```
  pyinstaller --onefile --windowed --name "DDR_Register_Comparer" main.py
  ```

- **DLL 警告可忽略**: 打包時會出現 `Library not found` 警告 (VERSION.dll, bcrypt.dll 等)，這些是 Windows 系統 DLL，不影響執行。

- **預設檔案路徑**: GUI 啟動時會自動填入同目錄下的 `sw_SDP.tbl`、`sw_DDP.tbl`、`dc_mc1_regfile.v`（如果存在）。打包成 exe 後，這些檔案需要和 exe 放在同一目錄，或手動選擇。

## Known Limitations

- 大型檔案比較時 UI 可能短暫無回應（已用 threading 緩解，但 Tkinter 的限制仍在）
- 結果區域使用 `wrap=NONE`，長行需要水平捲動
