#!/usr/bin/env python3
"""
Enhanced Register Signal Analyzer GUI Tool

A graphical user interface for analyzing register signals with editing capabilities:
1. Loading regif.v file for mapping relationships
2. Loading user's rtd_outl file for address-value pairs
3. Generating signal names and corresponding values
4. EDITING signal values and regenerating RTD_OUTL statements
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import re
from typing import Dict, List, NamedTuple, Optional, Set
from collections import defaultdict
import os
import copy
import fnmatch  # 添加萬用字元匹配支援

class SignalMapping(NamedTuple):
    signal_name: str
    register_name: str
    bit_range: str
    start_bit: int
    end_bit: int

class EditableSignalInfo:
    def __init__(self, signal_name: str, register_name: str, bit_range: str, 
                 start_bit: int, end_bit: int, original_value: int):
        self.signal_name = signal_name
        self.register_name = register_name
        self.bit_range = bit_range
        self.start_bit = start_bit
        self.end_bit = end_bit
        self.original_value = original_value
        self.current_value = original_value
        self.modified = False

class RegisterAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Register Signal Analyzer GUI")
        self.root.geometry("1400x900")
        
        # Data storage
        self.signal_mappings: List[SignalMapping] = []
        self.address_values: Dict[str, int] = {}
        self.results: Dict[str, Dict[str, Dict]] = {}
        self.editable_signals: Dict[str, Dict[str, EditableSignalInfo]] = {}
        self.rtd_file_order: List[str] = []  # 記錄原始RTD檔案的地址順序
        self.rtd_original_addresses: Set[str] = set()  # 記錄原始RTD檔案中的地址（用於判斷缺失）
        self.rtd_original_lines: List[str] = []  # 記錄原始檔案的完整行內容（包含註解）
        
        # Address mapping support for multiple identical signal sets (user configurable)
        self.address_prefixes = ['180c2', '180c3', '180c4', '180c5']  # 支援的地址前綴 (預設值)
        self.base_prefix = '180c2'  # 基準前綴，regfile中主要使用這個前綴建立mapping (預設值)
        
        # Remove short channel support - use address_prefixes for all cases
        
        # Enable/disable multi-channel mapping
        self.enable_multi_channel = True
        
        # File paths
        self.regfile_path = ""
        self.rtd_file_path = ""
        
        # RTD format preference
        self.rtd_format_var = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.analysis_frame = ttk.Frame(self.notebook)
        self.rtd_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.analysis_frame, text="分析結果")
        self.notebook.add(self.rtd_frame, text="RTD_OUTL 輸出")
        self.notebook.add(self.settings_frame, text="設定")
        
        # Create edit signal tabs for each address prefix
        self.edit_frames = {}
        self.signal_trees = {}
        self.edit_filter_vars = {}
        
        # Setup main tabs
        self.setup_analysis_tab(self.analysis_frame)
        self.setup_rtd_tab(self.rtd_frame)
        self.setup_settings_tab(self.settings_frame)
        
        # Initialize edit signal tabs
        self.setup_edit_signal_tabs()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("準備就緒。請選擇RegIF和RTD檔案。")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_analysis_tab(self, parent):
        """Setup the analysis results tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # File selection and controls
        top_frame = ttk.Frame(parent)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 10))
        top_frame.columnconfigure(1, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(top_frame, text="檔案選擇", padding="10")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # RegIF file selection
        ttk.Label(file_frame, text="RegIF 檔案 (.v):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.regfile_var = tk.StringVar()
        regfile_entry = ttk.Entry(file_frame, textvariable=self.regfile_var, state='readonly')
        regfile_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="瀏覽", 
                  command=self.browse_regfile).grid(row=0, column=2)
        
        # RTD file selection
        ttk.Label(file_frame, text="RTD_OUTL 檔案:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.rtd_file_var = tk.StringVar()
        rtd_entry = ttk.Entry(file_frame, textvariable=self.rtd_file_var, state='readonly')
        rtd_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="瀏覽", 
                  command=self.browse_rtd_file).grid(row=1, column=2, pady=(10, 0))
        
        # Control buttons
        control_frame = ttk.Frame(top_frame)
        control_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(control_frame, text="解析檔案", 
                  command=self.parse_files, style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="重置變更", 
                  command=self.reset_changes).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="清除結果", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="匯出結果", 
                  command=self.export_results).pack(side=tk.LEFT, padx=(0, 10))
        
        # Filter options
        filter_frame = ttk.Frame(top_frame)
        filter_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(filter_frame, text="篩選:").pack(side=tk.LEFT, padx=(0, 10))
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=20)
        filter_entry.pack(side=tk.LEFT, padx=(0, 10))
        filter_entry.bind('<KeyRelease>', self.on_filter_change)
        
        ttk.Button(filter_frame, text="顯示全部", 
                  command=self.show_all_results).pack(side=tk.LEFT, padx=(0, 10))
        
        # Add wildcard help label
        help_label = ttk.Label(filter_frame, text="(支援子字串和萬用字元: * ?)", font=('Arial', 8))
        help_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Results text area
        text_frame = ttk.Frame(parent)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                     font=('Consolas', 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        

        
    def setup_rtd_tab(self, parent):
        """Setup the RTD output tab."""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Instructions and controls
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        instruction_label = ttk.Label(control_frame, 
            text="生成的 RTD_OUTL 語句 (準備替換原始 .tbl 檔案):",
            font=('Arial', 10))
        instruction_label.pack(side=tk.LEFT)
        
        # Add format options
        self.rtd_format_var = tk.StringVar(value="clean")
        ttk.Radiobutton(control_frame, text="不帶註解", variable=self.rtd_format_var, 
                       value="clean", command=self.generate_rtd_outl).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Radiobutton(control_frame, text="註解(add modify comment)", variable=self.rtd_format_var, 
                       value="commented", command=self.generate_rtd_outl).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(control_frame, text="複製到剪貼簿", 
                  command=self.copy_rtd_to_clipboard).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(control_frame, text="保存 RTD 檔案", 
                  command=self.save_rtd_file).pack(side=tk.RIGHT)
        
        # RTD output text area
        text_frame = ttk.Frame(parent)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.rtd_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                 font=('Consolas', 10))
        self.rtd_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_settings_tab(self, parent):
        """Setup the settings tab for address mapping configuration."""
        parent.columnconfigure(0, weight=1)
        
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main settings frame
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="地址映射設定", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Multi-channel mapping enable/disable
        mapping_frame = ttk.LabelFrame(main_frame, text="多通道地址映射", padding="15")
        mapping_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.enable_multi_channel_var = tk.BooleanVar(value=self.enable_multi_channel)
        enable_check = ttk.Checkbutton(
            mapping_frame, 
            text="啟用多通道地址映射", 
            variable=self.enable_multi_channel_var,
            command=self.on_multi_channel_toggle
        )
        enable_check.pack(anchor=tk.W)
        
        info_label = ttk.Label(
            mapping_frame,
            text="啟用後，不同前綴的地址將映射到基準前綴進行信號查找。",
            font=('Arial', 9),
            foreground='gray'
        )
        info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Base prefix settings
        base_frame = ttk.LabelFrame(main_frame, text="基準地址前綴", padding="15")
        base_frame.pack(fill=tk.X, pady=(0, 15))
        base_frame.columnconfigure(1, weight=1)
        
        ttk.Label(base_frame, text="基準前綴:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.base_prefix_var = tk.StringVar(value=self.base_prefix)
        base_entry = ttk.Entry(base_frame, textvariable=self.base_prefix_var, width=15)
        base_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        base_info = ttk.Label(
            base_frame,
            text="RegIF 檔案中使用的參考地址前綴 (例如 '180c2')",
            font=('Arial', 9),
            foreground='gray'
        )
        base_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Supported prefixes settings
        prefixes_frame = ttk.LabelFrame(main_frame, text="支援的地址前綴", padding="15")
        prefixes_frame.pack(fill=tk.X, pady=(0, 15))
        prefixes_frame.columnconfigure(1, weight=1)
        
        ttk.Label(prefixes_frame, text="地址前綴:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.address_prefixes_var = tk.StringVar(value=', '.join(self.address_prefixes))
        prefixes_entry = ttk.Entry(prefixes_frame, textvariable=self.address_prefixes_var, width=40)
        prefixes_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        prefixes_info = ttk.Label(
            prefixes_frame,
            text="以逗號分隔的地址前綴列表 (例如 '180c2, 180c3, 180c4, 180c5')",
            font=('Arial', 9),
            foreground='gray'
        )
        prefixes_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Example section
        example_frame = ttk.LabelFrame(main_frame, text="配置範例", padding="15")
        example_frame.pack(fill=tk.X, pady=(0, 15))
        
        example_text = tk.Text(example_frame, height=8, wrap=tk.WORD, font=('Consolas', 9))
        example_text.pack(fill=tk.X)
        
        examples = """多通道地址映射工作原理：
1. RegIF 檔案包含使用基準前綴的信號定義 (例如 reg180c6xxx)
2. RTD 檔案可以包含不同前綴的地址 (例如 180c2xxx, 180c3xxx 等)
3. 工具將 RTD 地址映射到基準前綴進行信號查找

範例 1 - 使用 180c6 作為基準：
基準前綴: 180c6
地址前綴: 180c2, 180c3, 180c4, 180c5, 180c6
→ RegIF 應包含：assign signal = reg180c6800[31:28];
→ 180c2800, 180c3800 將映射到 reg180c6800 進行信號查找

範例 2 - 使用 180c2 作為基準 (預設)：
基準前綴: 180c2  
地址前綴: 180c2, 180c3, 180c4, 180c5
→ RegIF 應包含：assign signal = reg180c2800[31:28];
→ 180c3800, 180c4800 將映射到 reg180c2800 進行信號查找

重要提示：更改設定後，如果檔案已加載，將自動重新解析。"""
        
        example_text.insert(tk.END, examples)
        example_text.configure(state='disabled')
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="應用設定", 
                  command=self.apply_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="重置為預設", 
                  command=self.reset_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="保存設定", 
                  command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="載入設定", 
                  command=self.load_settings).pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def setup_edit_signal_tabs(self):
        """Setup individual edit signal tabs for each address prefix."""
        # 保存當前標籤頁
        current_tab = None
        try:
            current_tab = self.notebook.select()
            current_tab_text = self.notebook.tab(current_tab, "text") if current_tab else None
        except:
            current_tab = None
            current_tab_text = None
        
        # Remove existing edit signal tabs
        tabs_to_remove = []
        for i in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(i, "text")
            if tab_text.startswith("編輯"):
                tabs_to_remove.append(i)
        
        # Remove tabs in reverse order to maintain indices
        for tab_index in reversed(tabs_to_remove):
            self.notebook.forget(tab_index)
        
        # Clear existing edit signal data structures
        self.edit_frames = {}
        self.signal_trees = {}
        self.edit_filter_vars = {}
        
        for prefix in self.address_prefixes:
            # Create a new frame for each prefix
            edit_frame = ttk.Frame(self.notebook)
            self.edit_frames[prefix] = edit_frame
            self.notebook.add(edit_frame, text=f"編輯 {prefix} 信號")
            
            # Setup grid configuration
            edit_frame.columnconfigure(0, weight=1)
            edit_frame.rowconfigure(3, weight=1)
            
            # Instructions and controls
            instruction_label = ttk.Label(edit_frame, 
                text=f"雙擊 '當前(十進位)' 或 '當前(十六進位)' 欄位直接編輯數值 ({prefix} 通道)。Enter確認，Escape取消。",
                font=('Arial', 10))
            instruction_label.grid(row=0, column=0, pady=(10, 5), sticky=tk.W)
            
            # Filter options for this prefix
            filter_frame = ttk.Frame(edit_frame)
            filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            ttk.Label(filter_frame, text="篩選:").pack(side=tk.LEFT, padx=(0, 10))
            self.edit_filter_vars[prefix] = tk.StringVar()
            filter_entry = ttk.Entry(filter_frame, textvariable=self.edit_filter_vars[prefix], width=20)
            filter_entry.pack(side=tk.LEFT, padx=(0, 10))
            filter_entry.bind('<KeyRelease>', lambda event, p=prefix: self.on_edit_filter_change(event, p))
            
            ttk.Button(filter_frame, text="顯示全部", 
                      command=lambda p=prefix: self.show_all_edit_signals(p)).pack(side=tk.LEFT, padx=(0, 10))
            
            # Add wildcard help label
            help_label = ttk.Label(filter_frame, text="(支援子字串和萬用字元: * ?)", font=('Arial', 8))
            help_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Copy values controls
            copy_frame = ttk.Frame(edit_frame)
            copy_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # 只在非基準前綴的頁面上顯示複製按鈕
            if prefix != self.base_prefix:
                ttk.Button(copy_frame, text=f"複製 {self.base_prefix} 的值到此通道", 
                          command=lambda p=prefix: self.copy_base_values_to_channel(p)).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Label(copy_frame, text=f"通道: {prefix}", font=('Arial', 12, 'bold')).pack(side=tk.RIGHT)
            
            # Create treeview for editable signals
            tree_frame = ttk.Frame(edit_frame)
            tree_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            tree_frame.columnconfigure(0, weight=1)
            tree_frame.rowconfigure(0, weight=1)
            
            # Treeview with scrollbars
            signal_tree = ttk.Treeview(tree_frame, 
                columns=('Address', 'Signal', 'BitRange', 'OrigDec', 'OrigHex', 'CurrentDec', 'CurrentHex'), 
                show='headings')
            self.signal_trees[prefix] = signal_tree
            
            # Configure columns
            signal_tree.heading('Address', text='地址')
            signal_tree.heading('Signal', text='信號名稱')
            signal_tree.heading('BitRange', text='位元範圍')
            signal_tree.heading('OrigDec', text='原始(十進位)')
            signal_tree.heading('OrigHex', text='原始(十六進位)')
            signal_tree.heading('CurrentDec', text='當前(十進位)')
            signal_tree.heading('CurrentHex', text='當前(十六進位)')
            
            signal_tree.column('Address', width=120)
            signal_tree.column('Signal', width=200)
            signal_tree.column('BitRange', width=80)
            signal_tree.column('OrigDec', width=100)
            signal_tree.column('OrigHex', width=100)
            signal_tree.column('CurrentDec', width=100)
            signal_tree.column('CurrentHex', width=100)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=signal_tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=signal_tree.xview)
            signal_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Grid layout
            signal_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            # Configure tag styles for modified signals
            signal_tree.tag_configure('modified', background='lightblue')
            
            # Bind events for inline editing
            signal_tree.bind('<Double-1>', lambda event, p=prefix: self.on_signal_double_click_inline(event, p))
            signal_tree.bind('<Button-1>', lambda event, p=prefix: self.on_signal_click(event, p))
            
            # Store current editing state for this tree
            setattr(signal_tree, 'editing_item', None)
            setattr(signal_tree, 'editing_column', None)
            
        # 嘗試恢復到合理的標籤頁
        try:
            # 如果之前不在編輯標籤頁，嘗試恢復
            if current_tab_text and not current_tab_text.startswith("編輯"):
                # 找到對應的標籤頁
                for i in range(self.notebook.index("end")):
                    if self.notebook.tab(i, "text") == current_tab_text:
                        self.notebook.select(i)
                        break
            else:
                # 如果之前在編輯標籤頁，切換到分析結果頁
                for i in range(self.notebook.index("end")):
                    if self.notebook.tab(i, "text") == "分析結果":
                        self.notebook.select(i)
                        break
        except:
            # 如果都失敗了，就保持預設
            pass
    
    def browse_regfile(self):
        """Browse and select RegIF file."""
        filename = filedialog.askopenfilename(
            title="選擇 RegIF 檔案",
            filetypes=[("Verilog files", "*.v"), ("所有檔案", "*.*")]
        )
        if filename:
            self.regfile_path = filename
            self.regfile_var.set(os.path.basename(filename))
            self.status_var.set(f"RegIF 檔案加載: {os.path.basename(filename)}")
    
    def browse_rtd_file(self):
        """Browse and select RTD_OUTL file."""
        filename = filedialog.askopenfilename(
            title="選擇 RTD_OUTL 檔案",
            filetypes=[("Table files", "*.tbl"), ("Text files", "*.txt"), ("所有檔案", "*.*")]
        )
        if filename:
            self.rtd_file_path = filename
            self.rtd_file_var.set(os.path.basename(filename))
            self.status_var.set(f"RTD 檔案加載: {os.path.basename(filename)}")
    
    def parse_files(self):
        """Parse both files and generate results."""
        if not self.regfile_path or not self.rtd_file_path:
            messagebox.showerror("錯誤", "請先選擇 RegIF 和 RTD_OUTL 檔案！")
            return
        
        try:
            self.status_var.set("解析檔案中...")
            self.root.update()
            
            # Parse regfile for signal mappings
            self.parse_regfile()
            
            # Parse RTD file for address-value pairs
            self.parse_rtd_file()
            
            # Calculate signal values
            self.calculate_signal_values()
            
            # Create editable signal info
            self.create_editable_signals()
            
            # Display results
            self.display_results()
            self.generate_rtd_outl()
            
            # Setup edit signal tabs with new data
            self.setup_edit_signal_tabs()
            
            # Populate all edit trees after tabs are created
            self.populate_edit_tree()
            
            # Show statistics
            total_signals = sum(len(signals) for signals in self.results.values())
            total_addresses = len(self.results)
            
            self.status_var.set(f"解析完成！找到 {total_signals} 個信號，跨越 {total_addresses} 個地址")
            
            # Show current configuration
            config_info = f"設定:\n"
            config_info += f"多通道地址映射: {'啟用' if self.enable_multi_channel else '禁用'}\n"
            if self.enable_multi_channel:
                config_info += f"基準前綴: {self.base_prefix}\n"
                config_info += f"支援前綴: {', '.join(self.address_prefixes)}\n"
            
            messagebox.showinfo("成功", 
                f"檔案解析成功！\n\n"
                f"RegIF: {os.path.basename(self.regfile_path)}\n"
                f"RTD: {os.path.basename(self.rtd_file_path)}\n\n"
                f"結果: {total_signals} 個信號，跨越 {total_addresses} 個地址\n\n"
                f"{config_info}")
                
        except Exception as e:
            self.status_var.set("解析過程中發生錯誤。")
            messagebox.showerror("錯誤", f"錯誤解析檔案: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def parse_regfile(self):
        """Parse the Verilog regfile to extract signal-to-register mappings."""
        self.signal_mappings = []
        assign_pattern = r'assign\s+(\w+)\s*=\s*(reg[0-9a-fA-F]+)\[(\d+):?(\d+)?\];'
        
        with open(self.regfile_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                match = re.match(assign_pattern, line)
                if match:
                    signal_name = match.group(1)
                    register_name = match.group(2)
                    
                    if match.group(4):  # Range like [31:28]
                        start_bit = int(match.group(3))
                        end_bit = int(match.group(4))
                        bit_range = f"[{start_bit}:{end_bit}]"
                    else:  # Single bit like [0]
                        start_bit = end_bit = int(match.group(3))
                        bit_range = f"[{start_bit}]"
                    
                    mapping = SignalMapping(
                        signal_name=signal_name,
                        register_name=register_name,
                        bit_range=bit_range,
                        start_bit=start_bit,
                        end_bit=end_bit
                    )
                    self.signal_mappings.append(mapping)
    
    def parse_rtd_file(self):
        """Parse the RTD file to extract address-to-value mappings."""
        self.address_values = {}
        self.rtd_file_order = []  # 重置順序記錄
        self.rtd_original_addresses = set()  # 重置原始地址記錄
        self.rtd_original_lines = []  # 重置原始行記錄
        rtd_pattern = r'rtd_outl\(0x([0-9a-fA-F]+),0x([0-9a-fA-F]+)\);(.*)$'
        
        with open(self.rtd_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                original_line = line.rstrip()  # 保留原始行（移除右側空白）
                self.rtd_original_lines.append(original_line)
                
                line = line.strip()
                match = re.match(rtd_pattern, line)
                if match:
                    address = match.group(1).lower()
                    value = int(match.group(2), 16)
                    self.address_values[address] = value
                    # 記錄地址在原始檔案中的順序
                    if address not in self.rtd_file_order:
                        self.rtd_file_order.append(address)
                        self.rtd_original_addresses.add(address)  # 記錄原始地址
    
    def extract_bit_field(self, value: int, start_bit: int, end_bit: int) -> int:
        """Extract bit field from a value."""
        if start_bit == end_bit:
            return (value >> start_bit) & 1
        else:
            mask = (1 << (start_bit - end_bit + 1)) - 1
            return (value >> end_bit) & mask
    
    def set_bit_field(self, original_value: int, new_field_value: int, start_bit: int, end_bit: int) -> int:
        """Set bit field in a value."""
        if start_bit == end_bit:
            # Single bit
            mask = 1 << start_bit
            return (original_value & ~mask) | ((new_field_value & 1) << start_bit)
        else:
            # Bit range
            field_width = start_bit - end_bit + 1
            mask = ((1 << field_width) - 1) << end_bit
            return (original_value & ~mask) | ((new_field_value & ((1 << field_width) - 1)) << end_bit)
    
    def calculate_signal_values(self):
        """Calculate actual signal values based on mappings and RTD values, supporting multiple channel mappings."""
        results = defaultdict(dict)
        
        # 對每個RTD檔案中的地址進行處理
        for address, register_value in self.address_values.items():
            
            # 檢查是否為支援的地址前綴（只有在啟用多通道映射時才轉換）
            if self.enable_multi_channel and self.is_supported_address_prefix(address):
                # 轉換到基準地址以查找mapping
                base_address = self.convert_address_to_base(address)
                
                # 查找符合這個base address的signal mappings
                for mapping in self.signal_mappings:
                    mapping_addr = mapping.register_name[3:]  # Remove 'reg' prefix
                    
                    # 檢查是否匹配（支援完整地址或短地址格式）
                    address_matches = (mapping_addr == base_address or 
                                     (len(base_address) <= 4 and mapping_addr.endswith(base_address)))
                    
                    if address_matches:
                        signal_value = self.extract_bit_field(
                            register_value, 
                            mapping.start_bit, 
                            mapping.end_bit
                        )
                        
                        signal_name = mapping.signal_name
                        
                        # 建立顯示用的register name，使用實際地址前綴
                        display_register_name = f"reg{address}"
                        
                        results[address][signal_name] = {
                            'value': signal_value,
                            'register_value': hex(register_value),
                            'bit_range': mapping.bit_range,
                            'register_name': display_register_name,  # 使用實際地址的register name
                            'base_mapping': mapping.register_name,   # 保留原始mapping資訊供內部使用
                            'channel': None,
                            'start_bit': mapping.start_bit,
                            'end_bit': mapping.end_bit
                        }
            else:
                # 不支援的地址前綴，使用原始邏輯
                for mapping in self.signal_mappings:
                    reg_addr = mapping.register_name[3:]  # Remove 'reg' prefix
                    
                    if reg_addr == address:
                        register_value = self.address_values[address]
                        signal_value = self.extract_bit_field(
                            register_value, 
                            mapping.start_bit, 
                            mapping.end_bit
                        )
                        
                        results[address][mapping.signal_name] = {
                            'value': signal_value,
                            'register_value': hex(register_value),
                            'bit_range': mapping.bit_range,
                            'register_name': mapping.register_name,  # 直接使用原始register name
                            'base_mapping': mapping.register_name,
                            'channel': None,
                            'start_bit': mapping.start_bit,
                            'end_bit': mapping.end_bit
                        }
        
        self.results = dict(results)
    
    def create_editable_signals(self):
        """Create editable signal information, supporting multiple channel mappings and grouped by prefix."""
        # Reset editable signals - now organized by prefix
        self.editable_signals = defaultdict(lambda: defaultdict(dict))
        
        # 對每個RTD檔案中的地址進行處理
        for address, register_value in self.address_values.items():
            # 檢測這個地址屬於哪個前綴
            address_prefix = self.get_address_prefix(address)
            
            # 檢查是否為支援的地址前綴（只有在啟用多通道映射時才轉換）
            if self.enable_multi_channel and self.is_supported_address_prefix(address):
                # 轉換到基準地址以查找mapping
                base_address = self.convert_address_to_base(address)
                
                # 查找符合這個base address的signal mappings
                for mapping in self.signal_mappings:
                    mapping_addr = mapping.register_name[3:]  # Remove 'reg' prefix
                    
                    # 檢查是否匹配（支援完整地址或短地址格式）
                    address_matches = (mapping_addr == base_address or 
                                     (len(base_address) <= 4 and mapping_addr.endswith(base_address)))
                    
                    if address_matches:
                        signal_value = self.extract_bit_field(
                            register_value, 
                            mapping.start_bit, 
                            mapping.end_bit
                        )
                        
                        signal_name = mapping.signal_name
                        
                        # 建立顯示用的register name，使用實際地址前綴
                        display_register_name = f"reg{address}"
                        
                        editable_info = EditableSignalInfo(
                            signal_name=signal_name,
                            register_name=display_register_name,  # 使用實際地址的register name
                            bit_range=mapping.bit_range,
                            start_bit=mapping.start_bit,
                            end_bit=mapping.end_bit,
                            original_value=signal_value
                        )
                        
                        # 按前綴和地址組織信號
                        self.editable_signals[address_prefix][address][signal_name] = editable_info
            else:
                # 不支援的地址前綴，使用原始邏輯
                for mapping in self.signal_mappings:
                    reg_addr = mapping.register_name[3:]  # Remove 'reg' prefix
                    
                    if reg_addr == address:
                        register_value = self.address_values[address]
                        signal_value = self.extract_bit_field(
                            register_value, 
                            mapping.start_bit, 
                            mapping.end_bit
                        )
                        
                        editable_info = EditableSignalInfo(
                            signal_name=mapping.signal_name,
                            register_name=mapping.register_name,  # 直接使用原始register name
                            bit_range=mapping.bit_range,
                            start_bit=mapping.start_bit,
                            end_bit=mapping.end_bit,
                            original_value=signal_value
                        )
                        
                        # 按前綴和地址組織信號
                        self.editable_signals[address_prefix][address][mapping.signal_name] = editable_info
    
    def populate_edit_tree_for_prefix(self, prefix: str, filter_text=""):
        """Populate the edit tree for a specific prefix with signal data."""
        if prefix not in self.signal_trees:
            return
        
        signal_tree = self.signal_trees[prefix]
        
        # Clear existing data
        for item in signal_tree.get_children():
            signal_tree.delete(item)
        
        if prefix not in self.editable_signals:
            return
        
        # Collect addresses that will be displayed (after filtering)
        addresses_to_show = []
        for address in sorted(self.editable_signals[prefix].keys()):
            signals = self.editable_signals[prefix][address]
            
            # Apply filter if specified
            if filter_text:
                filtered_signals = {}
                for signal_name, signal_info in signals.items():
                    # Support wildcard matching for signal names, addresses, and register names
                    if (self.wildcard_match(signal_name, filter_text) or 
                        self.wildcard_match(address, filter_text) or
                        self.wildcard_match(signal_info.register_name, filter_text)):
                        filtered_signals[signal_name] = signal_info
                if filtered_signals:  # Only include if there are signals to show
                    addresses_to_show.append((address, filtered_signals))
            else:
                addresses_to_show.append((address, signals))
        
        # Add signals to tree with spacing between addresses
        for addr_index, (address, signals) in enumerate(addresses_to_show):
            # Sort signals by bit position (from bit31 to bit0)
            # Sort by start_bit in descending order (high to low)
            sorted_signals = sorted(signals.items(), key=lambda x: x[1].start_bit, reverse=True)
            
            # Add signals for this address
            for signal_name, signal_info in sorted_signals:
                
                # Format current values with modification indicator
                current_dec_display = str(signal_info.current_value)
                current_hex_display = f"0x{signal_info.current_value:x}"
                if signal_info.modified:
                    current_dec_display += " *"
                    current_hex_display += " *"
                
                item_id = signal_tree.insert('', 'end', values=(
                    f"0x{address.upper()}",
                    signal_info.signal_name,
                    signal_info.bit_range,
                    signal_info.original_value,
                    f"0x{signal_info.original_value:x}",
                    current_dec_display,
                    current_hex_display
                ))
                
                # Store signal info in item for later reference (we'll use the values themselves for identification)
                
                # Highlight modified signals
                if signal_info.modified:
                    signal_tree.item(item_id, tags=['modified'])
            
            # Add spacing between addresses (except after the last address)
            if addr_index < len(addresses_to_show) - 1:
                # Insert empty row for spacing
                signal_tree.insert('', 'end', values=(
                    "", "", "", "", "", "", ""
                ))
    
    def populate_edit_tree(self, filter_text=""):
        """Populate edit trees for all prefixes with signal data."""
        for prefix in self.address_prefixes:
            filter_text_for_prefix = ""
            if hasattr(self, 'edit_filter_vars') and prefix in self.edit_filter_vars:
                filter_text_for_prefix = self.edit_filter_vars[prefix].get().strip()
            self.populate_edit_tree_for_prefix(prefix, filter_text_for_prefix)
    
    def on_signal_double_click(self, event, prefix: str = None):
        """Handle double-click on signal in edit tree."""
        # 如果沒有指定prefix，這是舊的事件調用，先確定是哪個樹
        if prefix is None:
            # 嘗試從event對象確定是哪個樹
            widget = event.widget
            prefix = None
            for p, tree in self.signal_trees.items():
                if tree == widget:
                    prefix = p
                    break
            if prefix is None:
                return
        
        signal_tree = self.signal_trees[prefix]
        selection = signal_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = signal_tree.item(item, 'values')
        
        # Skip empty rows (spacing rows)
        if not values[0] or not values[1]:
            return
            
        address = values[0][2:].lower()  # Remove '0x' and convert to lowercase
        signal_name = values[1]
        current_value = values[5].replace(' *', '')  # Remove modification marker (now in CurrentDec column)
        
        # Get the signal info from the new data structure
        if (prefix in self.editable_signals and 
            address in self.editable_signals[prefix] and 
            signal_name in self.editable_signals[prefix][address]):
            
            signal_info = self.editable_signals[prefix][address][signal_name]
            
            # Calculate max value based on bit range
            if signal_info.start_bit == signal_info.end_bit:
                max_value = 1
            else:
                max_value = (1 << (signal_info.start_bit - signal_info.end_bit + 1)) - 1
            
            # Show custom edit dialog with hex support
            new_value = self.show_signal_edit_dialog(signal_name, signal_info, max_value)
            
            if new_value is not None:
                # Update the signal
                signal_info.current_value = new_value
                signal_info.modified = (new_value != signal_info.original_value)
                
                # Refresh the tree for this prefix with current filter
                filter_text = ""
                if hasattr(self, 'edit_filter_vars') and prefix in self.edit_filter_vars:
                    filter_text = self.edit_filter_vars[prefix].get().strip()
                self.populate_edit_tree_for_prefix(prefix, filter_text)
                
                # Update RTD output
                self.generate_rtd_outl()
                
                self.status_var.set(f"已修改 {signal_name} 為 {new_value}")
    
    def show_signal_edit_dialog(self, signal_name: str, signal_info: EditableSignalInfo, max_value: int):
        """顯示支援16進位輸入的信號編輯對話框"""
        # 創建自定義對話框
        dialog = tk.Toplevel(self.root)
        dialog.title("編輯信號值")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中顯示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = [None]  # 用列表來存儲結果，因為內部函數需要修改它
        
        # 標題
        title_label = ttk.Label(dialog, text=f"編輯信號: {signal_name}", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # 信號資訊
        info_frame = ttk.LabelFrame(dialog, text="信號資訊", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"位元範圍: {signal_info.bit_range}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"原始值: {signal_info.original_value} (0x{signal_info.original_value:x})").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"當前值: {signal_info.current_value} (0x{signal_info.current_value:x})").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"最大值: {max_value} (0x{max_value:x})").pack(anchor=tk.W)
        
        # 輸入區域
        input_frame = ttk.LabelFrame(dialog, text="新值", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 十進位輸入
        dec_frame = ttk.Frame(input_frame)
        dec_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(dec_frame, text="十進位:").pack(side=tk.LEFT, padx=(0, 10))
        dec_var = tk.StringVar(value=str(signal_info.current_value))
        dec_entry = ttk.Entry(dec_frame, textvariable=dec_var, width=15)
        dec_entry.pack(side=tk.LEFT)
        
        # 十六進位輸入
        hex_frame = ttk.Frame(input_frame)
        hex_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(hex_frame, text="十六進位:").pack(side=tk.LEFT, padx=(0, 10))
        hex_var = tk.StringVar(value=f"{signal_info.current_value:x}")
        hex_entry = ttk.Entry(hex_frame, textvariable=hex_var, width=15)
        hex_entry.pack(side=tk.LEFT)
        
        # 同步更新十進位和十六進位輸入
        def on_dec_change(*args):
            try:
                value = int(dec_var.get())
                if 0 <= value <= max_value:
                    hex_var.set(f"{value:x}")
            except ValueError:
                pass
        
        def on_hex_change(*args):
            try:
                hex_str = hex_var.get()
                if hex_str.startswith('0x'):
                    hex_str = hex_str[2:]
                value = int(hex_str, 16)
                if 0 <= value <= max_value:
                    dec_var.set(str(value))
            except ValueError:
                pass
        
        dec_var.trace('w', on_dec_change)
        hex_var.trace('w', on_hex_change)
        
        # 按鈕
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_ok():
            try:
                # 優先使用十進位輸入
                value = int(dec_var.get())
                if 0 <= value <= max_value:
                    result[0] = value
                    dialog.destroy()
                else:
                    messagebox.showerror("錯誤", f"值必須在 0 到 {max_value} 之間")
            except ValueError:
                try:
                    # 嘗試十六進位輸入
                    hex_str = hex_var.get()
                    if hex_str.startswith('0x'):
                        hex_str = hex_str[2:]
                    value = int(hex_str, 16)
                    if 0 <= value <= max_value:
                        result[0] = value
                        dialog.destroy()
                    else:
                        messagebox.showerror("錯誤", f"值必須在 0 到 {max_value} 之間")
                except ValueError:
                    messagebox.showerror("錯誤", "請輸入有效的數值")
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="確定", command=on_ok).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.LEFT)
        
        # 焦點設置到十進位輸入框
        dec_entry.focus_set()
        dec_entry.select_range(0, tk.END)
        
        # 等待對話框關閉
        dialog.wait_window()
        
        return result[0]
    
    def on_signal_click(self, event, prefix: str):
        """Handle single click to finish any ongoing inline editing."""
        signal_tree = self.signal_trees[prefix]
        self.finish_inline_editing(signal_tree)
    
    def on_signal_double_click_inline(self, event, prefix: str):
        """Handle double-click for inline editing."""
        signal_tree = self.signal_trees[prefix]
        
        # Finish any ongoing editing first
        self.finish_inline_editing(signal_tree)
        
        # Get clicked item and column
        item = signal_tree.identify('item', event.x, event.y)
        column = signal_tree.identify('column', event.x, event.y)
        
        if not item or not column:
            return
        
        # Check if this is an editable column (CurrentDec or CurrentHex)
        columns = signal_tree['columns']
        if column not in ['#6', '#7']:  # CurrentDec and CurrentHex columns
            return
            
        column_name = columns[int(column[1:])-1]  # Convert column id to name
        if column_name not in ['CurrentDec', 'CurrentHex']:
            return
        
        # Get item values
        values = signal_tree.item(item, 'values')
        if not values or len(values) < 7:
            return
        
        # Skip empty rows (spacing rows)
        if not values[0] or not values[1]:
            return
        
        # Get signal information
        address = values[0][2:].lower()  # Remove '0x' and convert to lowercase
        signal_name = values[1]
        
        # Get the signal info from data structure
        if (prefix in self.editable_signals and 
            address in self.editable_signals[prefix] and 
            signal_name in self.editable_signals[prefix][address]):
            
            signal_info = self.editable_signals[prefix][address][signal_name]
            self.start_inline_editing(signal_tree, item, column, column_name, signal_info, prefix, address, signal_name)
    
    def start_inline_editing(self, tree, item, column, column_name, signal_info, prefix, address, signal_name):
        """Start inline editing for a cell."""
        # Get the bounding box of the cell
        bbox = tree.bbox(item, column)
        if not bbox:
            return
        
        # Calculate max value based on bit range
        if signal_info.start_bit == signal_info.end_bit:
            max_value = 1
        else:
            max_value = (1 << (signal_info.start_bit - signal_info.end_bit + 1)) - 1
        
        # Create entry widget for editing
        entry = tk.Entry(tree)
        
        # Set initial value based on column type
        if column_name == 'CurrentDec':
            initial_value = str(signal_info.current_value)
        else:  # CurrentHex
            initial_value = f"{signal_info.current_value:x}"
        
        entry.insert(0, initial_value)
        entry.select_range(0, tk.END)
        
        # Position the entry widget
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.focus_set()
        
        # Store editing state
        tree.editing_item = item
        tree.editing_column = column
        tree.editing_entry = entry
        tree.editing_signal_info = signal_info
        tree.editing_column_name = column_name
        tree.editing_max_value = max_value
        tree.editing_prefix = prefix
        tree.editing_address = address
        tree.editing_signal_name = signal_name
        
        # Bind events
        def on_return(event):
            self.finish_inline_editing(tree, save=True)
            
        def on_escape(event):
            self.finish_inline_editing(tree, save=False)
            
        def on_focus_out(event):
            self.finish_inline_editing(tree, save=True)
        
        entry.bind('<Return>', on_return)
        entry.bind('<Escape>', on_escape)
        entry.bind('<FocusOut>', on_focus_out)
    
    def finish_inline_editing(self, tree, save=True):
        """Finish inline editing and optionally save the value."""
        if not hasattr(tree, 'editing_item') or not tree.editing_item:
            return
        
        if not hasattr(tree, 'editing_entry'):
            return
            
        entry = tree.editing_entry
        
        if save:
            try:
                new_text = entry.get().strip()
                if new_text:
                    # Parse the new value based on column type
                    if tree.editing_column_name == 'CurrentDec':
                        new_value = int(new_text)
                    else:  # CurrentHex
                        # Handle both "f" and "0xf" formats
                        if new_text.startswith('0x'):
                            new_text = new_text[2:]
                        new_value = int(new_text, 16)
                    
                    # Validate range
                    if 0 <= new_value <= tree.editing_max_value:
                        # Update the signal
                        signal_info = tree.editing_signal_info
                        signal_info.current_value = new_value
                        signal_info.modified = (new_value != signal_info.original_value)
                        
                        # Refresh the tree for this prefix
                        filter_text = ""
                        if hasattr(self, 'edit_filter_vars') and tree.editing_prefix in self.edit_filter_vars:
                            filter_text = self.edit_filter_vars[tree.editing_prefix].get().strip()
                        self.populate_edit_tree_for_prefix(tree.editing_prefix, filter_text)
                        
                        # Update RTD output
                        self.generate_rtd_outl()
                        
                        self.status_var.set(f"已修改 {tree.editing_signal_name} 為 {new_value}")
                    else:
                        messagebox.showerror("錯誤", f"值必須在 0 到 {tree.editing_max_value} 之間")
                        
            except ValueError:
                messagebox.showerror("錯誤", f"請輸入有效的{'十進位' if tree.editing_column_name == 'CurrentDec' else '十六進位'}數值")
        
        # Clean up
        entry.destroy()
        tree.editing_item = None
        tree.editing_column = None
        if hasattr(tree, 'editing_entry'):
            delattr(tree, 'editing_entry')
    
    def reset_changes(self):
        """Reset all signal changes to original values."""
        for prefix in self.editable_signals:
            for address in self.editable_signals[prefix]:
                for signal_name in self.editable_signals[prefix][address]:
                    signal_info = self.editable_signals[prefix][address][signal_name]
                    signal_info.current_value = signal_info.original_value
                    signal_info.modified = False
        
        self.populate_edit_tree()
        self.generate_rtd_outl()
        self.status_var.set("所有變更已重置為原始值。")
    
    def calculate_register_value(self, address: str) -> int:
        """Calculate the register value based on current signal values."""
        # Find which prefix this address belongs to
        address_prefix = self.get_address_prefix(address)
        
        if (address_prefix not in self.editable_signals or 
            address not in self.editable_signals[address_prefix]):
            return self.address_values.get(address, 0)
        
        # Start with original register value
        register_value = self.address_values.get(address, 0)
        
        # Apply all signal modifications
        for signal_name, signal_info in self.editable_signals[address_prefix][address].items():
            register_value = self.set_bit_field(
                register_value,
                signal_info.current_value,
                signal_info.start_bit,
                signal_info.end_bit
            )
        
        return register_value
    
    def generate_rtd_outl(self):
        """Generate RTD_OUTL statements based on current signal values, preserving original comments."""
        if not self.editable_signals:
            return
        
        self.rtd_text.delete(1.0, tk.END)
        
        # Check format preference
        format_type = getattr(self, 'rtd_format_var', None)
        is_clean_format = format_type and format_type.get() == "clean"
        
        # Header (only for commented format)
        if not is_clean_format:
            header = "// 生成的 RTD_OUTL 語句\n"
            header += "// 基於修改後的信號值 (保留原始註解)\n"
            header += f"// RegIF 檔案: {os.path.basename(self.regfile_path)}\n"
            header += f"// 原始 RTD 檔案: {os.path.basename(self.rtd_file_path)}\n\n"
            self.rtd_text.insert(tk.END, header)
        
        # 取得修改過的地址和新值
        modified_values = {}
        modified_count = 0
        
        # 計算每個地址的新值（包括原始的和動態創建的）
        for address in self.rtd_file_order:
            register_value = self.calculate_register_value(address)
            original_value = self.address_values.get(address, 0)
            
            # Check if any signals were modified for this address
            has_modifications = False
            address_prefix = self.get_address_prefix(address)
            if (address_prefix in self.editable_signals and 
                address in self.editable_signals[address_prefix]):
                has_modifications = any(
                    signal_info.modified 
                    for signal_info in self.editable_signals[address_prefix][address].values()
                )
            
            if has_modifications or register_value != original_value:
                modified_values[address] = register_value
                modified_count += 1
        
        # 處理每一行原始內容，保留註解
        rtd_pattern = r'rtd_outl\(0x([0-9a-fA-F]+),0x([0-9a-fA-F]+)\);(.*)$'
        
        # 記錄已處理的地址
        processed_addresses = set()
        
        for original_line in self.rtd_original_lines:
            match = re.match(rtd_pattern, original_line, re.IGNORECASE)
            if match:
                address = match.group(1).lower()
                original_comment = match.group(3)  # 保留原始註解
                processed_addresses.add(address)
                
                if address in modified_values:
                    # 使用修改後的值，保留原始註解
                    new_value = modified_values[address]
                    addr_upper = address.upper()
                    if not is_clean_format:
                        modified_line = f"rtd_outl(0x{addr_upper},{new_value:#010x});{original_comment} // MODIFIED"
                    else:
                        modified_line = f"rtd_outl(0x{addr_upper},{new_value:#010x});{original_comment}"
                    self.rtd_text.insert(tk.END, modified_line + "\n")
                else:
                    # 完全保留原始行
                    self.rtd_text.insert(tk.END, original_line + "\n")
            else:
                # 不是rtd_outl語句的行（可能是純註解或空行），完全保留
                self.rtd_text.insert(tk.END, original_line + "\n")
        
        # 【新增】處理動態創建的地址（不在原始文件中的地址）
        for address in self.rtd_file_order:
            if address not in processed_addresses:
                # 這是動態創建的地址
                register_value = self.calculate_register_value(address)
                addr_upper = address.upper()
                if not is_clean_format:
                    created_line = f"rtd_outl(0x{addr_upper},{register_value:#010x}); // CREATED"
                else:
                    created_line = f"rtd_outl(0x{addr_upper},{register_value:#010x});"
                self.rtd_text.insert(tk.END, created_line + "\n")
        
        # Footer (only for commented format)
        if not is_clean_format:
            footer = f"\n// 摘要: {len(self.rtd_file_order)} 個地址, {modified_count} 個已修改\n"
            self.rtd_text.insert(tk.END, footer)
    
    def copy_rtd_to_clipboard(self):
        """Copy RTD output to clipboard."""
        content = self.rtd_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_var.set("RTD_OUTL 內容已複製到剪貼簿。")
    
    def save_rtd_file(self):
        """Save RTD output to file."""
        if not self.editable_signals:
            messagebox.showwarning("警告", "沒有 RTD 內容可保存。請先解析檔案。")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存 RTD_OUTL 檔案",
            defaultextension=".tbl",
            filetypes=[("Table files", "*.tbl"), ("Text files", "*.txt"), ("所有檔案", "*.*")]
        )
        
        if filename:
            try:
                content = self.rtd_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("成功", f"RTD_OUTL 檔案已保存至 {filename}")
                self.status_var.set(f"RTD 檔案已保存: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"保存 RTD 檔案時發生錯誤: {str(e)}")
    
    def display_results(self, filter_text=""):
        """Display the analysis results in the text area."""
        self.results_text.delete(1.0, tk.END)
        
        if not self.results:
            self.results_text.insert(tk.END, "沒有結果可顯示。請先解析檔案。")
            return
        
        total_signals = 0
        displayed_addresses = 0
        
        # Header
        header = f"註冊信號分析結果\n"
        header += f"RegIF 檔案: {os.path.basename(self.regfile_path)}\n"
        header += f"RTD 檔案: {os.path.basename(self.rtd_file_path)}\n"
        header += "=" * 80 + "\n\n"
        self.results_text.insert(tk.END, header)
        
        # Process results by address order
        for address in sorted(self.results.keys()):
            signals = self.results[address]
            if not signals:
                continue
            
            # Apply filter if specified
            if filter_text:
                filtered_signals = {}
                for signal_name, signal_info in signals.items():
                    # Support wildcard matching for signal names and addresses
                    if (self.wildcard_match(signal_name, filter_text) or 
                        self.wildcard_match(address, filter_text) or
                        self.wildcard_match(signal_info['register_name'], filter_text)):
                        filtered_signals[signal_name] = signal_info
                if not filtered_signals:
                    continue
                signals = filtered_signals
            
            displayed_addresses += 1
            total_signals += len(signals)
            
            # Address header
            register_value = signals[list(signals.keys())[0]]['register_value']
            address_header = f"=== 地址 0x{address.upper()} (值: {register_value}) ===\n"
            self.results_text.insert(tk.END, address_header)
            
            # Sort signals by bit position (from bit31 to bit0)
            # Sort by start_bit in descending order (high to low)
            sorted_signals = sorted(signals.items(), key=lambda x: x[1]['start_bit'], reverse=True)
            
            # Signals for this address
            for signal_name, signal_info in sorted_signals:
                line = f"{signal_name:<35} = {signal_info['register_name']}{signal_info['bit_range']:<12} = {signal_info['value']:<6} (0x{signal_info['value']:x})\n"
                self.results_text.insert(tk.END, line)
            
            self.results_text.insert(tk.END, "\n")
        
        # Footer
        footer = f"\n摘要: {total_signals} 個信號，跨越 {displayed_addresses} 個地址"
        if filter_text:
            footer += f" (已根據 '{filter_text}' 篩選)"
        self.results_text.insert(tk.END, footer)
    
    def wildcard_match(self, text: str, pattern: str) -> bool:
        """Check if text matches pattern with wildcard support (* and ?) or substring match."""
        if not pattern:
            return True
        
        text_lower = text.lower()
        pattern_lower = pattern.lower()
        
        # If pattern contains wildcards, use fnmatch
        if '*' in pattern_lower or '?' in pattern_lower:
            return fnmatch.fnmatch(text_lower, pattern_lower)
        else:
            # Otherwise, use substring matching (like original behavior)
            return pattern_lower in text_lower
    
    def on_filter_change(self, event):
        """Handle filter text change."""
        filter_text = self.filter_var.get().strip()
        if hasattr(self, 'results') and self.results:
            self.display_results(filter_text)
    
    def show_all_results(self):
        """Show all results without filter."""
        self.filter_var.set("")
        if hasattr(self, 'results') and self.results:
            self.display_results()
    
    def on_edit_filter_change(self, event, prefix: str = None):
        """Handle edit filter text change for a specific prefix."""
        # 如果沒有指定prefix，嘗試從event對象確定
        if prefix is None:
            widget = event.widget
            prefix = None
            for p, var in self.edit_filter_vars.items():
                # 找到對應的StringVar
                if hasattr(var, 'trace_info') and len(var.trace_info()) > 0:
                    # 這裡需要其他方法來確定prefix
                    pass
            # 如果找不到，就刷新所有
            if prefix is None:
                self.populate_edit_tree()
                return
        
        filter_text = self.edit_filter_vars[prefix].get().strip()
        if hasattr(self, 'editable_signals') and self.editable_signals:
            self.populate_edit_tree_for_prefix(prefix, filter_text)
    
    def show_all_edit_signals(self, prefix: str):
        """Show all edit signals for a specific prefix without filter."""
        self.edit_filter_vars[prefix].set("")
        if prefix in self.editable_signals and self.editable_signals[prefix]:
            self.populate_edit_tree_for_prefix(prefix, "")
    
    def clear_results(self):
        """Clear all results and reset the tool."""
        self.results_text.delete(1.0, tk.END)
        self.rtd_text.delete(1.0, tk.END)
        
        # Clear all signal trees
        if hasattr(self, 'signal_trees'):
            for prefix, signal_tree in self.signal_trees.items():
                for item in signal_tree.get_children():
                    signal_tree.delete(item)
        
        # Clear filter variables
        if hasattr(self, 'filter_var'):
            self.filter_var.set("")
        if hasattr(self, 'edit_filter_vars'):
            for prefix in self.edit_filter_vars:
                self.edit_filter_vars[prefix].set("")
        
        self.signal_mappings = []
        self.address_values = {}
        self.results = {}
        self.editable_signals = {}
        self.rtd_file_order = []  # 清空順序記錄
        self.status_var.set("結果已清除。準備進行新的分析。")
    
    def export_results(self):
        """Export results to a text file."""
        if not self.results:
            messagebox.showwarning("警告", "沒有結果可匯出。請先解析檔案。")
            return
        
        filename = filedialog.asksaveasfilename(
            title="匯出結果",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("所有檔案", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write("註冊信號分析結果\n")
                    f.write(f"RegIF 檔案: {os.path.basename(self.regfile_path)}\n")
                    f.write(f"RTD 檔案: {os.path.basename(self.rtd_file_path)}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Write results
                    total_signals = 0
                    for address in sorted(self.results.keys()):
                        signals = self.results[address]
                        if not signals:
                            continue
                        
                        total_signals += len(signals)
                        register_value = signals[list(signals.keys())[0]]['register_value']
                        f.write(f"=== 地址 0x{address.upper()} (值: {register_value}) ===\n")
                        
                        # Sort signals by bit position (from bit31 to bit0)
                        sorted_signals = sorted(signals.items(), key=lambda x: x[1]['start_bit'], reverse=True)
                        
                        for signal_name, signal_info in sorted_signals:
                            f.write(f"{signal_name:<35} = {signal_info['register_name']}{signal_info['bit_range']:<12} = {signal_info['value']:<6} (0x{signal_info['value']:x})\n")
                        
                        f.write("\n")
                    
                    f.write(f"\n摘要: {total_signals} 個信號，跨越 {len(self.results)} 個地址\n")
                
                messagebox.showinfo("成功", f"結果已匯出至 {filename}")
                self.status_var.set(f"結果已匯出至 {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"匯出結果時發生錯誤: {str(e)}")

    def convert_address_to_base(self, address: str) -> str:
        """
        轉換地址到基準前綴以查找signal mapping
        例如：180c3800 -> 180c2800, 200b0abc -> 200a0abc, 3aa0 -> 2aa0
        """
        address_lower = address.lower()
        
        # 檢查所有支援的地址前綴
        for prefix in self.address_prefixes:
            if address_lower.startswith(prefix) and prefix != self.base_prefix:
                # 將前綴替換為基準前綴
                suffix = address_lower[len(prefix):]
                return self.base_prefix + suffix
        
        # 如果已經是基準前綴或不匹配任何前綴，直接返回原地址
        return address_lower
    
    def is_supported_address_prefix(self, address: str) -> bool:
        """檢查地址是否使用支援的前綴"""
        address_lower = address.lower()
        return any(address_lower.startswith(prefix) for prefix in self.address_prefixes)
    
    def get_address_prefix(self, address: str) -> str:
        """獲取地址的前綴"""
        address_lower = address.lower()
        for prefix in self.address_prefixes:
            if address_lower.startswith(prefix):
                return prefix
        # 如果沒有匹配的前綴，返回地址本身的前4個字符作為前綴
        return address_lower[:4] if len(address_lower) >= 4 else address_lower
    
    def copy_base_values_to_channel(self, target_prefix: str):
        """複製基準前綴的值到目標通道"""
        if target_prefix == self.base_prefix:
            messagebox.showinfo("提示", "目標通道與基準通道相同，無需複製。")
            return
        
        if self.base_prefix not in self.editable_signals:
            messagebox.showerror("錯誤", f"基準通道 {self.base_prefix} 沒有數據。")
            return
        
        if target_prefix not in self.editable_signals:
            messagebox.showerror("錯誤", f"目標通道 {target_prefix} 沒有數據。")
            return
        
        # 收集要複製的地址和不匹配的地址
        base_addresses = set()
        target_addresses = set()
        
        for address in self.editable_signals[self.base_prefix]:
            # 獲得地址的offset部分（去除前綴）
            base_offset = address[len(self.base_prefix):]
            base_addresses.add(base_offset)
        
        # 【關鍵修復】基於原始RTD文件判斷目標通道有哪些地址
        for address in self.rtd_original_addresses:  # 只考虑原始RTD文件中的地址
            if address.startswith(target_prefix):
                target_offset = address[len(target_prefix):]
                target_addresses.add(target_offset)
        
        # 檢查地址是否匹配
        common_offsets = base_addresses.intersection(target_addresses)
        missing_in_target = base_addresses - target_addresses
        
        # 準備複製訊息 - 確保總是被定義
        copy_message = f"確定要將 {self.base_prefix} 的值複製到 {target_prefix} 嗎？\n"
        
        # 處理缺少的地址
        missing_list = []
        
        if missing_in_target:
            missing_list = [f"{target_prefix}{offset}" for offset in missing_in_target]

            if common_offsets:
                # 有匹配的地址，自動複製，但告知缺少的地址
                copy_message += f"\n將複製 {len(common_offsets)} 個匹配的地址。\n"
                copy_message += f"⚠️ 注意：目標通道缺少 {len(missing_in_target)} 個地址:\n"
                copy_message += "\n".join(missing_list[:5])
                if len(missing_list) > 5:
                    copy_message += f"\n... 還有 {len(missing_list)-5} 個地址"
                copy_message += f"\n\n複製完成後會詢問是否要創建缺少的地址。"
            else:
                # 沒有任何匹配的地址，顯示錯誤
                messagebox.showerror(
                    "無匹配地址", 
                    f"目標通道完全沒有匹配的地址，無法進行複製。\n\n缺少的地址:\n" + 
                    "\n".join(missing_list[:10]) + 
                    (f"\n... 還有 {len(missing_list)-10} 個地址" if len(missing_list) > 10 else "") +
                    f"\n\n請先確保目標通道有對應的地址。"
                )
                return
        else:
            # 沒有缺少的地址，顯示正常的複製訊息
            if common_offsets:
                copy_message += f"\n將複製 {len(common_offsets)} 個匹配的地址。"

        # 確認複製操作
        if not messagebox.askyesno("確認複製", copy_message):
            return
        
        force_address_level_copy = True  # True = 地址級別, False = 信號級別
        
        # 執行複製
        copied_count = 0
        try:
            for offset in common_offsets:
                base_address = self.base_prefix + offset
                target_address = target_prefix + offset
                
                base_signals = self.editable_signals[self.base_prefix][base_address]
                target_signals = self.editable_signals[target_prefix][target_address]
                
                if force_address_level_copy:
                    # 地址級別複製 - 強制複製所有信號
                    for signal_name in target_signals:
                        if signal_name in base_signals:
                            base_signal = base_signals[signal_name]
                            target_signal = target_signals[signal_name]
                            
                            # 強制複製，不管值是否相同
                            target_signal.current_value = base_signal.current_value
                            target_signal.modified = (target_signal.current_value != target_signal.original_value)
                            copied_count += 1
                else:
                    # 信號級別複製 - 原始邏輯
                    for signal_name in base_signals:
                        if signal_name in target_signals:
                            base_signal = base_signals[signal_name]
                            target_signal = target_signals[signal_name]
                            
                            # 只複製不同的值
                            if base_signal.current_value != target_signal.current_value:
                                target_signal.current_value = base_signal.current_value
                                target_signal.modified = (target_signal.current_value != target_signal.original_value)
                                copied_count += 1
            
            # 刷新UI
            self.populate_edit_tree_for_prefix(target_prefix)
            self.generate_rtd_outl()
            
            # 處理缺少的地址 - 添加詢問創建邏輯
            if missing_in_target:
                create_missing = messagebox.askyesno(
                    "創建缺少的地址",
                    f"複製完成！發現目標通道 {target_prefix} 缺少 {len(missing_in_target)} 個地址。\n\n"
                    f"缺少的地址:\n" + 
                    "\n".join(missing_list[:10]) + 
                    (f"\n... 還有 {len(missing_list)-10} 個地址" if len(missing_list) > 10 else "") +
                    f"\n\n是否要為這些缺少的地址創建對應的 RTD 條目？\n"
                    f"(將使用基準通道 {self.base_prefix} 的值)"
                )
                
                if create_missing:
                    self.create_missing_addresses(target_prefix, missing_in_target)
            
            messagebox.showinfo(
                "複製完成", 
                f"成功複製了 {copied_count} 個信號值從 {self.base_prefix} 到 {target_prefix}。"
            )
            self.status_var.set(f"已複製 {copied_count} 個信號值到 {target_prefix}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"複製過程中發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_multi_channel_toggle(self):
        """Handle multi-channel mapping toggle."""
        self.enable_multi_channel = self.enable_multi_channel_var.get()
        self.status_var.set(f"多通道地址映射 {'啟用' if self.enable_multi_channel else '禁用'}")
    
    def apply_settings(self):
        """Apply current settings from the UI."""
        try:
            # Store old settings for comparison
            old_enable_multi_channel = self.enable_multi_channel
            old_base_prefix = self.base_prefix
            old_address_prefixes = self.address_prefixes[:]
            
            # Update multi-channel enable
            self.enable_multi_channel = self.enable_multi_channel_var.get()
            
            # Update base prefix
            new_base_prefix = self.base_prefix_var.get().strip().lower()
            if not new_base_prefix:
                messagebox.showerror("錯誤", "基準前綴不能為空！")
                return
            self.base_prefix = new_base_prefix
            
            # Update address prefixes
            prefixes_str = self.address_prefixes_var.get().strip()
            if prefixes_str:
                new_prefixes = [p.strip().lower() for p in prefixes_str.split(',') if p.strip()]
                if not new_prefixes:
                    messagebox.showerror("錯誤", "至少需要一個地址前綴！")
                    return
                self.address_prefixes = new_prefixes
            
            # Check if settings actually changed
            settings_changed = (
                old_enable_multi_channel != self.enable_multi_channel or
                old_base_prefix != self.base_prefix or
                old_address_prefixes != self.address_prefixes
            )
            
            # Show success message
            success_msg = (
                f"設定已應用成功！\n\n"
                f"多通道地址映射: {'啟用' if self.enable_multi_channel else '禁用'}\n"
                f"基準前綴: {self.base_prefix}\n"
                f"地址前綴: {', '.join(self.address_prefixes)}"
            )
            
            # If files are already loaded and settings changed, automatically re-parse
            if settings_changed and self.regfile_path and self.rtd_file_path and self.signal_mappings:
                success_msg += "\n\n自動重新解析檔案，使用新的設定..."
                messagebox.showinfo("成功", success_msg)
                
                # Re-parse with new settings
                self.status_var.set("使用新的設定重新解析檔案...")
                self.root.update()
                
                # Re-calculate signal values with new settings
                self.calculate_signal_values()
                
                # Re-create editable signals
                self.create_editable_signals()
                
                # Update displays
                self.display_results()
                self.generate_rtd_outl()
                
                # Re-setup edit signal tabs with new prefixes
                self.setup_edit_signal_tabs()
                
                # Populate all edit trees after tabs are created
                self.populate_edit_tree()
                
                # Show final status
                total_signals = sum(len(signals) for signals in self.results.values())
                total_addresses = len(self.results)
                self.status_var.set(f"設定已應用並重新解析檔案！找到 {total_signals} 個信號，跨越 {total_addresses} 個地址")
                
            else:
                messagebox.showinfo("成功", success_msg)
                if not settings_changed:
                    self.status_var.set("設定已應用 (未檢測到變更)")
                else:
                    self.status_var.set("設定已應用成功")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"應用設定時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def reset_settings(self):
        """Reset settings to default values."""
        # Default values
        default_address_prefixes = ['180c2', '180c3', '180c4', '180c5']
        default_base_prefix = '180c2'
        default_enable_multi_channel = True
        
        # Update UI variables
        self.enable_multi_channel_var.set(default_enable_multi_channel)
        self.base_prefix_var.set(default_base_prefix)
        self.address_prefixes_var.set(', '.join(default_address_prefixes))
        
        # Update internal variables
        self.enable_multi_channel = default_enable_multi_channel
        self.base_prefix = default_base_prefix
        self.address_prefixes = default_address_prefixes
        
        self.status_var.set("設定已重置為預設值")
        messagebox.showinfo("重置", "設定已重置為預設值")
    
    def save_settings(self):
        """Save current settings to a file."""
        import json
        import datetime
        
        filename = filedialog.asksaveasfilename(
            title="保存設定",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("所有檔案", "*.*")]
        )
        
        if filename:
            try:
                # Get current UI values (in case they haven't been applied yet)
                current_enable_multi_channel = self.enable_multi_channel_var.get()
                current_base_prefix = self.base_prefix_var.get().strip().lower()
                current_address_prefixes_str = self.address_prefixes_var.get().strip()
                
                # Parse address prefixes
                if current_address_prefixes_str:
                    current_address_prefixes = [p.strip().lower() for p in current_address_prefixes_str.split(',') if p.strip()]
                else:
                    current_address_prefixes = self.address_prefixes
                
                # Validate settings before saving
                if not current_base_prefix:
                    messagebox.showerror("錯誤", "基準前綴不能為空！")
                    return
                if not current_address_prefixes:
                    messagebox.showerror("錯誤", "至少需要一個地址前綴！")
                    return
                
                settings = {
                    'enable_multi_channel': current_enable_multi_channel,
                    'base_prefix': current_base_prefix,
                    'address_prefixes': current_address_prefixes,
                    'version': '1.2',
                    'saved_at': datetime.datetime.now().isoformat(),
                    'description': 'Enhanced Register Signal Analyzer Settings'
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                # Show saved settings in message
                saved_settings_info = (
                    f"已保存設定:\n"
                    f"多通道地址映射: {'啟用' if current_enable_multi_channel else '禁用'}\n"
                    f"基準前綴: {current_base_prefix}\n"
                    f"地址前綴: {', '.join(current_address_prefixes)}"
                )
                
                messagebox.showinfo("設定保存成功", 
                    f"設定已保存至 {os.path.basename(filename)}\n\n{saved_settings_info}")
                self.status_var.set(f"設定已保存: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"保存設定時發生錯誤: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            # User cancelled the file dialog
            self.status_var.set("取消保存設定")
    
    def load_settings(self):
        """Load settings from a file."""
        import json
        
        filename = filedialog.askopenfilename(
            title="載入設定",
            filetypes=[("JSON files", "*.json"), ("所有檔案", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Validate settings format
                if not isinstance(settings, dict):
                    raise ValueError("無效的設定檔案格式")
                
                # Update internal variables with validation
                self.enable_multi_channel = settings.get('enable_multi_channel', True)
                self.base_prefix = settings.get('base_prefix', '180c2')
                self.address_prefixes = settings.get('address_prefixes', ['180c2', '180c3', '180c4', '180c5'])
                
                # Validate loaded values
                if not isinstance(self.enable_multi_channel, bool):
                    self.enable_multi_channel = True
                if not isinstance(self.base_prefix, str) or not self.base_prefix.strip():
                    self.base_prefix = '180c2'
                if not isinstance(self.address_prefixes, list) or not self.address_prefixes:
                    self.address_prefixes = ['180c2', '180c3', '180c4', '180c5']
                
                # Update UI variables and force refresh
                self.enable_multi_channel_var.set(self.enable_multi_channel)
                self.base_prefix_var.set(self.base_prefix)
                self.address_prefixes_var.set(', '.join(self.address_prefixes))
                
                # Force UI update
                self.root.update_idletasks()
                
                # Show loaded settings in message
                loaded_settings_info = (
                    f"已載入設定:\n"
                    f"多通道地址映射: {'啟用' if self.enable_multi_channel else '禁用'}\n"
                    f"基準前綴: {self.base_prefix}\n"
                    f"地址前綴: {', '.join(self.address_prefixes)}\n\n"
                    f"點擊 '應用設定' 以激活載入的配置。"
                )
                
                messagebox.showinfo("設定載入成功", 
                    f"設定已從 {os.path.basename(filename)} 載入\n\n{loaded_settings_info}")
                self.status_var.set(f"設定已載入: {os.path.basename(filename)} - UI 已更新")
                
            except json.JSONDecodeError:
                messagebox.showerror("錯誤", "無效的 JSON 檔案格式")
            except Exception as e:
                messagebox.showerror("錯誤", f"載入設定時發生錯誤: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            # User cancelled the file dialog
            self.status_var.set("取消載入設定")

    def create_missing_addresses(self, target_prefix: str, missing_offsets: set):
        """為目標前綴創建缺少的地址條目"""
        created_count = 0
        
        try:
            for offset in missing_offsets:
                base_address = self.base_prefix + offset
                target_address = target_prefix + offset
                
                # 檢查基準地址是否存在
                if (self.base_prefix in self.editable_signals and 
                    base_address in self.editable_signals[self.base_prefix]):
                    
                    # 獲取基準地址的寄存器值
                    base_register_value = self.address_values.get(base_address, 0)
                    
                    # 在address_values中添加新地址
                    self.address_values[target_address] = base_register_value
                    
                    # 在rtd_file_order中添加新地址（如果還沒有的話）
                    if target_address not in self.rtd_file_order:
                        # 找到合適的插入位置（按地址順序）
                        insert_index = len(self.rtd_file_order)
                        for i, existing_addr in enumerate(self.rtd_file_order):
                            if target_address < existing_addr:
                                insert_index = i
                                break
                        self.rtd_file_order.insert(insert_index, target_address)
                    
                    # 【移除這行】不要修改 rtd_original_lines
                    # new_rtd_line = f"rtd_outl(0x{target_address.upper()},0x{base_register_value:08x}); // CREATED"
                    # self.rtd_original_lines.append(new_rtd_line)
                    
                    created_count += 1
            
            # 重新計算信號值以包含新地址
            self.calculate_signal_values()
            self.create_editable_signals()
            
            # 重新設置編輯信號頁籤
            self.setup_edit_signal_tabs()
            self.populate_edit_tree()
            
            # 重新生成RTD輸出
            self.generate_rtd_outl()
            
            messagebox.showinfo(
                "創建完成",
                f"成功創建了 {created_count} 個新的地址條目到 {target_prefix}。"
            )
            self.status_var.set(f"已創建 {created_count} 個新地址到 {target_prefix}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"創建地址時發生錯誤: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the enhanced GUI application."""
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    # Try to use a modern theme if available
    try:
        style.theme_use('winnative')  # Windows
    except:
        try:
            style.theme_use('clam')  # Cross-platform
        except:
            pass  # Use default theme
    
    # Create and configure the application
    app = RegisterAnalyzerGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main() 