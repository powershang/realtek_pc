import re
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os

def convert_rtd_format(input_file, output_file):
    """
    Convert rtd_inl format to rtd_outl format
    From: rtd_inl(address); //value
    To: rtd_outl(address, value);
    """
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'latin-1']
    lines = None
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except:
            continue
    
    if lines is None:
        raise Exception("無法讀取檔案，請檢查檔案編碼")
    
    converted_lines = []
    converted_count = 0
    
    for line in lines:
        # More flexible pattern matching
        # Match: rtd_in, rtd_in1, rtd_inl followed by (address); //value
        match = re.search(r'(rtd_in[1l]?)\s*\(\s*([0-9a-fA-Fx]+)\s*\)\s*;\s*//\s*([0-9a-fA-Fx]+)', line, re.IGNORECASE)
        
        if match:
            # Get indentation from original line
            indent = line[:line.find(match.group(1))]
            function_name = match.group(1)
            address = match.group(2)
            value = match.group(3)
            
            # Ensure values start with 0x
            if not address.startswith('0x'):
                address = '0x' + address
            if not value.startswith('0x'):
                value = '0x' + value
            
            # Convert to rtd_outl format
            converted_line = f"{indent}rtd_outl({address},{value});\n"
            converted_lines.append(converted_line)
            converted_count += 1
        else:
            # Keep line as is if it doesn't match the pattern
            converted_lines.append(line)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(converted_lines)
    
    return converted_count, len(lines)

class RTDConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RTD Format Converter (rtd_inl → rtd_outl)")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="RTD Format Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file section
        ttk.Label(main_frame, text="輸入檔案:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=60).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="瀏覽...", command=self.browse_input).grid(
            row=1, column=2, padx=5, pady=5)
        
        # Output file section
        ttk.Label(main_frame, text="輸出檔案:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=60).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="瀏覽...", command=self.browse_output).grid(
            row=2, column=2, padx=5, pady=5)
        
        # Convert button
        convert_btn = ttk.Button(main_frame, text="開始轉換", 
                                command=self.convert, style='Accent.TButton')
        convert_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Preview section
        ttk.Label(main_frame, text="預覽/結果:", font=('Arial', 10, 'bold')).grid(
            row=5, column=0, sticky=tk.W, pady=5)
        
        # Text area for preview
        self.preview_text = scrolledtext.ScrolledText(
            main_frame, width=100, height=25, wrap=tk.WORD, 
            font=('Consolas', 9))
        self.preview_text.grid(row=6, column=0, columnspan=3, 
                              sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure row weight for text area to expand
        main_frame.rowconfigure(6, weight=1)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="就緒", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=7, column=0, columnspan=3, 
                              sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Example info
        example_frame = ttk.LabelFrame(main_frame, text="轉換範例", padding="10")
        example_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        example_text = """轉換前: rtd_inl(0xb80c1040); //0x00000000
轉換後: rtd_outl(0xb80c1040,0x00000000);"""
        ttk.Label(example_frame, text=example_text, font=('Consolas', 9), 
                 foreground='blue').pack()
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="選擇輸入檔案",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            if not self.output_file.get():
                base, ext = os.path.splitext(filename)
                self.output_file.set(f"{base}_converted{ext}")
            # Show preview
            self.show_preview()
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="選擇輸出檔案",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            defaultextension=".txt"
        )
        if filename:
            self.output_file.set(filename)
    
    def show_preview(self):
        """Show preview of input file"""
        input_path = self.input_file.get()
        if not input_path or not os.path.exists(input_path):
            return
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # Read first 5000 chars
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, "=== 輸入檔案預覽 ===\n\n")
            self.preview_text.insert(tk.END, content)
            if len(content) == 5000:
                self.preview_text.insert(tk.END, "\n\n... (僅顯示前5000字元)")
            
            self.status_label.config(text=f"已載入: {input_path}")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法讀取檔案: {str(e)}")
    
    def convert(self):
        input_path = self.input_file.get()
        output_path = self.output_file.get()
        
        # Validation
        if not input_path:
            messagebox.showwarning("警告", "請選擇輸入檔案！")
            return
        
        if not output_path:
            messagebox.showwarning("警告", "請選擇輸出檔案！")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("錯誤", "輸入檔案不存在！")
            return
        
        try:
            # Perform conversion
            self.status_label.config(text="轉換中...")
            self.root.update()
            
            converted_count, total_lines = convert_rtd_format(input_path, output_path)
            
            # Show result
            with open(output_path, 'r', encoding='utf-8') as f:
                result_content = f.read(5000)
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, "=== 轉換結果 ===\n\n")
            self.preview_text.insert(tk.END, f"總行數: {total_lines}\n")
            self.preview_text.insert(tk.END, f"已轉換: {converted_count} 行\n")
            self.preview_text.insert(tk.END, f"輸出檔案: {output_path}\n\n")
            self.preview_text.insert(tk.END, "=== 輸出檔案預覽 ===\n\n")
            self.preview_text.insert(tk.END, result_content)
            if len(result_content) == 5000:
                self.preview_text.insert(tk.END, "\n\n... (僅顯示前5000字元)")
            
            self.status_label.config(text=f"轉換完成！已轉換 {converted_count}/{total_lines} 行")
            messagebox.showinfo("完成", 
                              f"轉換完成！\n\n總行數: {total_lines}\n已轉換: {converted_count} 行\n\n輸出檔案: {output_path}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"轉換失敗: {str(e)}")
            self.status_label.config(text="轉換失敗")

def main():
    root = tk.Tk()
    app = RTDConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()