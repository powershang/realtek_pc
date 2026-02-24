#!/usr/bin/env python3
"""
DDR Register Comparison Tool - GUI Version
主程式進入點

用法:
  python main.py          # 啟動 GUI
  python main.py --help   # 顯示說明

打包成執行檔:
  pip install pyinstaller
  pyinstaller --onefile --windowed --name "DDR_Register_Comparer" main.py

Contact: shane_wu #25696
Version: 1.0.0
"""

__author__ = "shane_wu #25696"
__version__ = "1.0.0"

import sys


def main():
    """主程式"""
    # 檢查是否要顯示說明
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print(__doc__)
        print("\nFor CLI usage, run: python register_comparer.py --help")
        return 0

    # 啟動 GUI
    from gui_app import DDRComparerApp
    import tkinter as tk

    root = tk.Tk()
    app = DDRComparerApp(root)
    root.mainloop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
