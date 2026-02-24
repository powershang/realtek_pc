#!/usr/bin/env python3
"""
DDR Register Comparison Tool - GUI Application
使用 Tkinter 建立的圖形介面
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import json
from pathlib import Path

from register_comparer import (
    parse_regfile_v,
    parse_register_file_with_snapshots,
    compare_registers,
    compare_snapshots,
    format_report,
    format_snapshot_report,
    format_register_map,
    format_single_file_report,
    extract_all_mr_values,
    compare_mr_values,
    format_mr_report,
    SPECIAL_RANGES,
)

# 嘗試載入內建 regmap (打包版本使用)
try:
    from embedded_regmap import get_embedded_reg_map, has_embedded_regmap
    HAS_EMBEDDED_REGMAP = has_embedded_regmap()
except ImportError:
    HAS_EMBEDDED_REGMAP = False
    def get_embedded_reg_map():
        return {}
    def has_embedded_regmap():
        return False


class DDRComparerApp:
    """DDR Register Comparison Tool GUI 應用程式"""

    # 聯絡資訊
    CONTACT = "shane_wu #25696"
    VERSION = "1.0.0"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"DDR Register Comparison Tool - Contact: {self.CONTACT}")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # 儲存最後的報告結果
        self.last_report = ""
        self.reg_map = {}

        # 內建 regmap 模式 (打包版本會啟用)
        self.embedded_mode = HAS_EMBEDDED_REGMAP
        if self.embedded_mode:
            self.reg_map = get_embedded_reg_map()

        # Config 檔案路徑
        self.config_file = Path(__file__).parent / "ddr_comparer_config.json"

        self.setup_ui()
        self.setup_default_paths()
        self._load_last_config()  # 自動載入上次設定

        # 視窗關閉時自動儲存設定
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def setup_ui(self):
        """建立 UI 元件"""
        # 建立選單列
        self._create_menu()

        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 設定 grid 權重讓視窗可以縮放
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # 結果區域可擴展

        self._create_file_selection(main_frame)
        self._create_buttons(main_frame)
        self._create_results_area(main_frame)
        self._create_status_bar(main_frame)

    def _create_file_selection(self, parent):
        """建立檔案選擇區域"""
        frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(1, weight=1)

        # File 1
        ttk.Label(frame, text="File 1 (*.tbl):").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
        self.file1_var = tk.StringVar()
        self.file1_entry = ttk.Entry(frame, textvariable=self.file1_var, width=60)
        self.file1_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=2)
        ttk.Button(frame, text="Browse...", command=lambda: self._browse_file(self.file1_var, "tbl")).grid(
            row=0, column=2, padx=(0, 5), pady=2
        )

        # File 2
        ttk.Label(frame, text="File 2 (*.tbl):").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
        self.file2_var = tk.StringVar()
        self.file2_entry = ttk.Entry(frame, textvariable=self.file2_var, width=60)
        self.file2_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=2)
        ttk.Button(frame, text="Browse...", command=lambda: self._browse_file(self.file2_var, "tbl")).grid(
            row=1, column=2, padx=(0, 5), pady=2
        )

        # Regfile (optional) - 只在非內建模式時顯示
        self.regfile_var = tk.StringVar()
        self.use_regfile_var = tk.BooleanVar(value=True)

        if not self.embedded_mode:
            ttk.Label(frame, text="Regfile (*.v):").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=2)
            self.regfile_entry = ttk.Entry(frame, textvariable=self.regfile_var, width=60)
            self.regfile_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
            ttk.Button(frame, text="Browse...", command=lambda: self._browse_file(self.regfile_var, "v")).grid(
                row=2, column=2, padx=(0, 5), pady=2
            )
            ttk.Checkbutton(frame, text="Use", variable=self.use_regfile_var).grid(row=2, column=3, padx=5, pady=2)
            ddr_type_row = 3
        else:
            # 內建模式：regfile 已內建，不需要選擇
            self.regfile_entry = None
            ddr_type_row = 2

        # DDR Type selection (for CMD decoding)
        ttk.Label(frame, text="DDR Type:").grid(row=ddr_type_row, column=0, sticky="w", padx=(0, 10), pady=2)
        self.ddr_type_var = tk.StringVar(value="LPDDR4")
        ddr_type_combo = ttk.Combobox(frame, textvariable=self.ddr_type_var, values=["LPDDR4", "LPDDR5"], width=15, state="readonly")
        ddr_type_combo.grid(row=ddr_type_row, column=1, sticky="w", padx=(0, 10), pady=2)

        # 內建模式時顯示不同的提示
        if self.embedded_mode:
            ttk.Label(frame, text=f"(Embedded regmap: {len(self.reg_map)} defs)").grid(
                row=ddr_type_row, column=2, columnspan=2, sticky="w", padx=(0, 10), pady=2
            )
        else:
            ttk.Label(frame, text="(CMD decode only for LPDDR4)").grid(row=ddr_type_row, column=2, columnspan=2, sticky="w", padx=(0, 10), pady=2)

    def _create_buttons(self, parent):
        """建立按鈕區域"""
        frame = ttk.Frame(parent)
        frame.grid(row=1, column=0, sticky="w", pady=(0, 10))

        self.compare_btn = ttk.Button(frame, text="Compare", command=self._run_comparison, width=15)
        self.compare_btn.grid(row=0, column=0, padx=(0, 10))

        self.parse_file1_btn = ttk.Button(frame, text="Parse File 1", command=lambda: self._run_parse(1), width=15)
        self.parse_file1_btn.grid(row=0, column=1, padx=(0, 10))

        self.parse_file2_btn = ttk.Button(frame, text="Parse File 2", command=lambda: self._run_parse(2), width=15)
        self.parse_file2_btn.grid(row=0, column=2, padx=(0, 10))

        self.clear_btn = ttk.Button(frame, text="Clear", command=self._clear_all, width=15)
        self.clear_btn.grid(row=0, column=3, padx=(0, 10))

        self.export_btn = ttk.Button(frame, text="Export Report...", command=self._export_report, width=15)
        self.export_btn.grid(row=0, column=4, padx=(0, 10))

        self.show_map_btn = ttk.Button(frame, text="Show Reg Map", command=self._show_register_map, width=15)
        self.show_map_btn.grid(row=0, column=5, padx=(0, 10))

    def _create_results_area(self, parent):
        """建立結果顯示區域"""
        frame = ttk.LabelFrame(parent, text="Results", padding="5")
        frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # 使用等寬字體的捲動文字區域
        self.results_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            state=tk.DISABLED,
            width=100,
            height=25
        )
        self.results_text.grid(row=0, column=0, sticky="nsew")

        # 水平捲軸
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.results_text.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.results_text.configure(xscrollcommand=h_scrollbar.set)

    def _create_status_bar(self, parent):
        """建立狀態列"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky="ew")

    def setup_default_paths(self):
        """設定預設檔案路徑"""
        script_dir = Path(__file__).parent

        # 檢查預設檔案是否存在
        default_file1 = script_dir / "sw_SDP.tbl"
        default_file2 = script_dir / "sw_DDP.tbl"
        default_regfile = script_dir / "dc_mc1_regfile.v"

        if default_file1.exists():
            self.file1_var.set(str(default_file1))
        if default_file2.exists():
            self.file2_var.set(str(default_file2))
        if default_regfile.exists():
            self.regfile_var.set(str(default_regfile))

    def _create_menu(self):
        """建立選單列"""
        menubar = tk.Menu(self.root)

        # File 選單
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Config...", command=self._load_config, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Config...", command=self._save_config, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menubar)

        # 綁定快捷鍵
        self.root.bind("<Control-o>", lambda e: self._load_config())
        self.root.bind("<Control-s>", lambda e: self._save_config())

    def _get_config(self) -> dict:
        """取得目前設定"""
        return {
            "file1": self.file1_var.get(),
            "file2": self.file2_var.get(),
            "regfile": self.regfile_var.get(),
            "use_regfile": self.use_regfile_var.get(),
            "ddr_type": self.ddr_type_var.get(),
        }

    def _apply_config(self, config: dict):
        """套用設定"""
        if "file1" in config:
            self.file1_var.set(config["file1"])
        if "file2" in config:
            self.file2_var.set(config["file2"])
        if "regfile" in config:
            self.regfile_var.set(config["regfile"])
        if "use_regfile" in config:
            self.use_regfile_var.set(config["use_regfile"])
        if "ddr_type" in config:
            self.ddr_type_var.set(config["ddr_type"])

    def _save_config(self):
        """儲存設定到檔案"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="ddr_comparer_config.json",
            initialdir=Path(__file__).parent
        )
        if filename:
            try:
                config = self._get_config()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self._set_status(f"Config saved to {Path(filename).name}")

                # 同時更新自動載入的 config
                self.config_file = Path(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {e}")

    def _load_config(self):
        """從檔案載入設定"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=Path(__file__).parent
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._apply_config(config)
                self._set_status(f"Config loaded from {Path(filename).name}")

                # 更新自動載入的 config 路徑
                self.config_file = Path(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")

    def _load_last_config(self):
        """自動載入上次的設定"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self._apply_config(config)
            except Exception:
                pass  # 忽略載入錯誤，使用預設值

    def _auto_save_config(self):
        """自動儲存目前設定（不需使用者確認）"""
        try:
            config = self._get_config()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 忽略儲存錯誤

    def _on_closing(self):
        """視窗關閉時的處理"""
        self._auto_save_config()
        self.root.destroy()

    def _browse_file(self, string_var: tk.StringVar, file_type: str):
        """開啟檔案選擇對話框"""
        filetypes = {
            "tbl": [("Table files", "*.tbl"), ("Text files", "*.txt"), ("All files", "*.*")],
            "v": [("Verilog files", "*.v"), ("All files", "*.*")]
        }

        # 取得目前路徑作為初始目錄
        current_path = string_var.get()
        initial_dir = Path(current_path).parent if current_path and Path(current_path).parent.exists() else Path(__file__).parent

        filename = filedialog.askopenfilename(
            filetypes=filetypes.get(file_type, [("All files", "*.*")]),
            initialdir=initial_dir
        )
        if filename:
            string_var.set(filename)

    def _set_status(self, message: str):
        """設定狀態列訊息"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def _disable_ui(self):
        """停用 UI 元件"""
        self.compare_btn.config(state=tk.DISABLED)
        self.parse_file1_btn.config(state=tk.DISABLED)
        self.parse_file2_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self.show_map_btn.config(state=tk.DISABLED)

    def _enable_ui(self):
        """啟用 UI 元件"""
        self.compare_btn.config(state=tk.NORMAL)
        self.parse_file1_btn.config(state=tk.NORMAL)
        self.parse_file2_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)
        self.show_map_btn.config(state=tk.NORMAL)

    def _run_comparison(self):
        """執行比較"""
        file1 = self.file1_var.get()
        file2 = self.file2_var.get()

        if not file1 or not file2:
            messagebox.showerror("Error", "Please select both input files")
            return

        if not Path(file1).exists():
            messagebox.showerror("Error", f"File not found: {file1}")
            return
        if not Path(file2).exists():
            messagebox.showerror("Error", f"File not found: {file2}")
            return

        self._set_status("Comparing...")
        self._disable_ui()

        # 在背景執行緒中執行比較，避免 UI 凍結
        thread = threading.Thread(target=self._compare_thread, args=(file1, file2))
        thread.daemon = True
        thread.start()

    def _compare_thread(self, file1: str, file2: str):
        """在背景執行緒中執行比較"""
        try:
            # 載入 regfile (非內建模式時才需要)
            if not self.embedded_mode:
                regfile = self.regfile_var.get()
                if regfile and self.use_regfile_var.get() and Path(regfile).exists():
                    self.reg_map = parse_regfile_v(regfile)
                else:
                    self.reg_map = {}
            # else: embedded_mode 時，reg_map 已在 __init__ 中載入

            # 解析檔案
            regs1, snaps1 = parse_register_file_with_snapshots(file1)
            regs2, snaps2 = parse_register_file_with_snapshots(file2)

            # 比較一般 registers
            result = compare_registers(regs1, regs2)

            # 比較 snapshots
            all_snap_diffs = {}
            for range_start, _ in SPECIAL_RANGES[:4]:  # 只取前 4 個 (channel 0-3)
                all_snap_diffs[range_start] = compare_snapshots(
                    snaps1[range_start],
                    snaps2[range_start],
                    range_start
                )

            # 產生報告
            file1_name = Path(file1).name
            file2_name = Path(file2).name
            ddr_type = self.ddr_type_var.get()

            # 提取 MR 值並比較 (僅 LPDDR4)
            mr1 = extract_all_mr_values(snaps1, ddr_type)
            mr2 = extract_all_mr_values(snaps2, ddr_type)
            mr_diff = compare_mr_values(mr1, mr2)

            # 判斷 regfile 來源
            if self.embedded_mode:
                regfile_info = "Embedded"
            else:
                regfile = self.regfile_var.get()
                regfile_info = Path(regfile).name if regfile and self.reg_map else "Not loaded"

            report_parts = []
            report_parts.append(f"Comparing: {file1_name} vs {file2_name}")
            report_parts.append(f"Regfile: {regfile_info}")
            report_parts.append(f"Register definitions loaded: {len(self.reg_map)}")
            report_parts.append(f"DDR Type: {ddr_type}")
            report_parts.append("")
            report_parts.append(format_report(result, file1_name, file2_name, self.reg_map))
            report_parts.append(format_snapshot_report(all_snap_diffs, file1_name, file2_name, self.reg_map, ddr_type))

            # 加入 MR 比較報告 (僅 LPDDR4)
            if ddr_type == "LPDDR4" and (mr1 or mr2):
                report_parts.append(format_mr_report(mr_diff, file1_name, file2_name, mr1, mr2))

            report = "\n".join(report_parts)

            # 計算差異數量
            diff_count = len(result['value_diff'])
            # MR 差異按 rank 分開統計
            if ddr_type == "LPDDR4":
                rank0_diff = len(mr_diff.get('rank0', {}).get('value_diff', []))
                rank1_diff = len(mr_diff.get('rank1', {}).get('value_diff', []))
                mr_diff_count = rank0_diff + rank1_diff
                summary = f"Done - {diff_count} register diff, {mr_diff_count} MR diff (R0:{rank0_diff}, R1:{rank1_diff})"
            else:
                mr_diff_count = 0
                summary = f"Done - {diff_count} register diff"

            # 更新 UI (在主執行緒中)
            self.root.after(0, lambda: self._display_result(report, summary))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._show_error(error_msg))
        finally:
            self.root.after(0, self._enable_ui)

    def _run_parse(self, file_num: int):
        """執行單一檔案解析"""
        file_var = self.file1_var if file_num == 1 else self.file2_var
        filepath = file_var.get()

        if not filepath:
            messagebox.showerror("Error", f"Please select File {file_num}")
            return

        if not Path(filepath).exists():
            messagebox.showerror("Error", f"File not found: {filepath}")
            return

        self._set_status(f"Parsing File {file_num}...")
        self._disable_ui()

        thread = threading.Thread(target=self._parse_thread, args=(filepath,))
        thread.daemon = True
        thread.start()

    def _parse_thread(self, filepath: str):
        """在背景執行緒中執行單一檔案解析"""
        try:
            # 載入 regfile (非內建模式時才需要)
            if not self.embedded_mode:
                regfile = self.regfile_var.get()
                if regfile and self.use_regfile_var.get() and Path(regfile).exists():
                    self.reg_map = parse_regfile_v(regfile)
                else:
                    self.reg_map = {}

            regs, snaps = parse_register_file_with_snapshots(filepath)
            file_name = Path(filepath).name
            ddr_type = self.ddr_type_var.get()

            report_parts = []

            if self.embedded_mode:
                regfile_info = "Embedded"
            else:
                regfile = self.regfile_var.get()
                regfile_info = Path(regfile).name if regfile and self.reg_map else "Not loaded"

            report_parts.append(f"Parsing: {file_name}")
            report_parts.append(f"Regfile: {regfile_info}")
            report_parts.append(f"Register definitions loaded: {len(self.reg_map)}")
            report_parts.append(f"DDR Type: {ddr_type}")
            report_parts.append("")
            report_parts.append(format_single_file_report(file_name, regs, snaps, self.reg_map, ddr_type))

            report = "\n".join(report_parts)
            summary = f"Done - {len(regs)} registers, {sum(len(snaps.get(rs, [])) for rs in [0xb80c2100, 0xb80c3100, 0xb80c4100, 0xb80c5100])} triggers"

            self.root.after(0, lambda: self._display_result(report, summary))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self._show_error(error_msg))
        finally:
            self.root.after(0, self._enable_ui)

    def _display_result(self, report: str, summary: str):
        """顯示比較結果"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, report)
        self.results_text.config(state=tk.DISABLED)
        self.results_text.see(1.0)  # 捲動到頂部
        self._set_status(summary)
        self.last_report = report

    def _show_error(self, message: str):
        """顯示錯誤訊息"""
        messagebox.showerror("Error", f"Comparison failed: {message}")
        self._set_status("Error occurred")

    def _clear_all(self):
        """清除所有輸入和結果"""
        self.file1_var.set("")
        self.file2_var.set("")
        self.regfile_var.set("")
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.last_report = ""
        self.reg_map = {}
        self._set_status("Ready")

    def _export_report(self):
        """匯出報告到檔案"""
        if not self.last_report:
            messagebox.showwarning("Warning", "No report to export. Run comparison first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")],
            initialfile="comparison_report.txt"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.last_report)
                messagebox.showinfo("Success", f"Report saved to:\n{filename}")
                self._set_status(f"Report exported to {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")

    def _show_register_map(self):
        """顯示 register map"""
        regfile = self.regfile_var.get()

        if not regfile:
            messagebox.showwarning("Warning", "Please select a regfile first.")
            return

        if not Path(regfile).exists():
            messagebox.showerror("Error", f"Regfile not found: {regfile}")
            return

        try:
            reg_map = parse_regfile_v(regfile)
            if not reg_map:
                messagebox.showinfo("Info", "No register definitions found in the regfile.")
                return

            report = format_register_map(reg_map)

            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, report)
            self.results_text.config(state=tk.DISABLED)
            self.results_text.see(1.0)
            self._set_status(f"Loaded {len(reg_map)} register definitions")
            self.last_report = report
            self.reg_map = reg_map

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load regfile: {e}")


def main():
    """主程式進入點"""
    root = tk.Tk()
    app = DDRComparerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
