import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from test import *  # 導入原始程式的所有功能
import threading  # 添加在文件開頭的import部分
import queue  # 添加 queue 模塊
from selenium.webdriver.common.by import By
import time

class TicketBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("拓元自動訂票程式")
        self.root.geometry("800x600")
        
        # 添加停止標誌
        self.stop_flag = False
        
        # 保存當前運行的線程
        self.bot_thread = None
        
        # 創建主要的 notebook（分頁）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # 創建各個分頁
        self.setup_main_tab()
        self.setup_concert_tab()
        self.setup_ticket_tab()
        self.setup_advanced_tab()
        
        # 創建底部的按鈕
        self.create_bottom_buttons()
        
        # 載入配置
        self.load_config()

    def setup_main_tab(self):
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text='基本設定')
        
        # Chrome 設定
        chrome_group = ttk.LabelFrame(main_frame, text="Chrome 設定", padding=10)
        chrome_group.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(chrome_group, text="ChromeDriver 路徑:").pack(anchor='w')
        self.chrome_path = ttk.Entry(chrome_group, width=50)
        self.chrome_path.pack(fill='x', pady=2)
        
        ttk.Label(chrome_group, text="用戶資料目錄:").pack(anchor='w')
        self.user_data_dir = ttk.Entry(chrome_group, width=50)
        self.user_data_dir.pack(fill='x', pady=2)
        
        # 網站設定
        web_group = ttk.LabelFrame(main_frame, text="網站設定", padding=10)
        web_group.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(web_group, text="活動網址:").pack(anchor='w')
        self.activity_url = ttk.Entry(web_group, width=50)
        self.activity_url.pack(fill='x', pady=2)

    def setup_concert_tab(self):
        concert_frame = ttk.Frame(self.notebook)
        self.notebook.add(concert_frame, text='演唱會設定')
        
        # 日期設定
        date_group = ttk.LabelFrame(concert_frame, text="場次設定", padding=10)
        date_group.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(date_group, text="首選日期 (YYYY/MM/DD):").pack(anchor='w')
        self.concert_date = ttk.Entry(date_group)
        self.concert_date.pack(fill='x', pady=2)
        
        ttk.Label(date_group, text="備選日期 (YYYY/MM/DD 或 * 表示任意):").pack(anchor='w')
        self.concert_date2 = ttk.Entry(date_group)
        self.concert_date2.pack(fill='x', pady=2)
        
        self.allow_alternative = tk.BooleanVar()
        ttk.Checkbutton(date_group, text="自動選擇任意場次", 
                       variable=self.allow_alternative).pack(anchor='w', pady=5)
        
        # 添加說明文字
        explanation = "說明：系統將優先嘗試首選日期，然後是備選日期。若勾選「自動選擇任意場次」，\n在兩者都無法訂到票時，會自動嘗試任何可用場次。"
        ttk.Label(date_group, text=explanation, wraplength=400).pack(anchor='w', pady=5)

        # 簡化的卡號認證設定
        card_group = ttk.LabelFrame(concert_frame, text="卡號認證設定", padding=10)
        card_group.pack(fill='x', padx=5, pady=5)
        
        self.enable_card_auth = tk.BooleanVar()
        ttk.Checkbutton(card_group, text="啟用自動卡號認證", 
                       variable=self.enable_card_auth,
                       command=self.toggle_card_auth_input).pack(anchor='w', pady=2)
        
        # 卡號輸入框
        card_number_frame = ttk.Frame(card_group)
        card_number_frame.pack(fill='x', pady=5)
        
        ttk.Label(card_number_frame, text="卡號:").pack(anchor='w')
        self.card_number = ttk.Entry(card_number_frame, state='disabled', show='*')
        self.card_number.pack(fill='x', pady=2)
        
        # 添加說明文字
        card_explanation = ("說明：系統會自動檢測頁面是否需要卡號認證，如有需要會自動填入您提供的卡號。\n"
                           "可輸入完整卡號或部分卡號，程式會直接填入您輸入的內容。")
        self.card_auth_label = ttk.Label(card_group, text=card_explanation, wraplength=400, state='disabled')
        self.card_auth_label.pack(anchor='w', pady=5)

    def toggle_card_auth_input(self):
        """切換卡號認證輸入框的啟用狀態"""
        if self.enable_card_auth.get():
            self.card_number.configure(state='normal')
            self.card_auth_label.configure(state='normal')
        else:
            self.card_number.configure(state='disabled')
            self.card_auth_label.configure(state='disabled')

    def setup_ticket_tab(self):
        ticket_frame = ttk.Frame(self.notebook)
        self.notebook.add(ticket_frame, text='票券設定')
        
        # 票券設定
        ticket_group = ttk.LabelFrame(ticket_frame, text="票券設定", padding=10)
        ticket_group.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(ticket_group, text="購票張數:").pack(anchor='w')
        self.ticket_number = ttk.Spinbox(ticket_group, from_=1, to=4, width=10)
        self.ticket_number.pack(fill='x', pady=2)
        
        ttk.Label(ticket_group, text="目標票價:").pack(anchor='w')
        self.target_price = ttk.Entry(ticket_group)
        self.target_price.pack(fill='x', pady=2)

    def setup_advanced_tab(self):
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text='進階設定')
        
        # 調試設定
        debug_group = ttk.LabelFrame(advanced_frame, text="調試設定", padding=10)
        debug_group.pack(fill='x', padx=5, pady=5)
        
        self.debug_enabled = tk.BooleanVar()
        ttk.Checkbutton(debug_group, text="啟用調試模式", 
                       variable=self.debug_enabled).pack(anchor='w')
        
        self.save_screenshots = tk.BooleanVar()
        ttk.Checkbutton(debug_group, text="保存截圖", 
                       variable=self.save_screenshots).pack(anchor='w')
        
        # 新增HTML保存選項
        self.save_html = tk.BooleanVar()
        ttk.Checkbutton(debug_group, text="保存HTML源碼", 
                       variable=self.save_html).pack(anchor='w')
        
        # 新增HTML保存路徑
        html_path_frame = ttk.Frame(debug_group)
        html_path_frame.pack(fill='x', pady=5)
        ttk.Label(html_path_frame, text="HTML保存路徑:").pack(side='left')
        self.html_save_path = ttk.Entry(html_path_frame)
        self.html_save_path.pack(side='left', fill='x', expand=True, padx=5)
        self.html_save_path.insert(0, "html_dumps")  # 預設路徑
        ttk.Button(html_path_frame, text="選擇", command=self.select_html_path).pack(side='right')

    def create_bottom_buttons(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="開始搶票", 
                                     command=self.start_bot)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止搶票", 
                                    command=self.stop_bot, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="儲存設定", 
                  command=self.save_config).pack(side='left', padx=5)

    def load_config(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 載入設定到 GUI
                self.chrome_path.insert(0, config['chromedriver_path'])
                self.user_data_dir.insert(0, config['chrome_user_data_dir'])
                self.activity_url.insert(0, config['website']['activity_url'])
                self.concert_date.insert(0, config['concert']['date'])
                self.concert_date2.insert(0, config['concert']['date2'])
                self.allow_alternative.set(config['concert']['allow_alternative_date'])
                
                # 修改：載入卡號認證設定
                if 'card_auth' in config['concert']:
                    self.enable_card_auth.set(config['concert']['card_auth']['enabled'])
                    if config['concert']['card_auth']['enabled']:
                        self.card_number.configure(state='normal')
                        self.card_auth_label.configure(state='normal')
                        self.card_number.insert(0, config['concert']['card_auth'].get('card_number', ''))
                
                self.ticket_number.insert(0, config['ticket_config']['ticket_numbers']['max_tickets'])
                self.target_price.insert(0, str(config['ticket_config']['target_price']))
                self.debug_enabled.set(config['debug']['enabled'])
                self.save_screenshots.set(config['debug']['save_screenshots'])
                self.save_html.set(config['debug']['save_html_source'])
                self.html_save_path.insert(0, config['debug']['html_save_path'])
        except Exception as e:
            messagebox.showerror("錯誤", f"EXCEPT: 載入配置時發生錯誤：{str(e)}")

    def save_config(self):
        try:
            # 不再將首選日期自動設為*，保留用戶的原始輸入
            config = {
                'chromedriver_path': self.chrome_path.get(),
                'chrome_user_data_dir': self.user_data_dir.get(),
                'chrome_profile': 'Default',
                'window_size': {'width': 800, 'height': 1020},
                'concert': {
                    'date': self.concert_date.get(),
                    'date2': self.concert_date2.get(),
                    'allow_alternative_date': self.allow_alternative.get(),
                    'switch_date_attempt': 2,
                    # 修改：卡號認證設定
                    'card_auth': {
                        'enabled': self.enable_card_auth.get(),
                        'card_number': self.card_number.get() if self.enable_card_auth.get() else ''
                    }
                },
                'ticket_config': {
                    'ticket_numbers': {'max_tickets': self.ticket_number.get()},
                    'target_price': int(self.target_price.get()),
                    'retry': {'max_attempts': 100, 'delay': 0.02}
                },
                'website': {
                    'base_url': self.activity_url.get(),
                    'login_url': 'https://tixcraft.com/login',
                    'activity_url': self.activity_url.get()
                },
                'debug': {
                    'enabled': self.debug_enabled.get(),
                    'force_captcha_error': False,
                    'first_captcha_value': 'aabb',
                    'error_attempts': 1,
                    'verbose': True,
                    'save_screenshots': self.save_screenshots.get(),
                    'save_html_source': self.save_html.get(),
                    'html_save_path': self.html_save_path.get()
                },
                'wait_times': {
                    'after_page_load': 2.0,
                    'after_click_buy': 0.5,
                    'after_date_select': 0.1,
                    'after_click_order': 0.1,
                    'ticket_page_load': 0.1,
                    'after_submit': 0.3,
                    'captcha_update': 0.2
                }
            }
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("成功", "配置已儲存")
        except Exception as e:
            messagebox.showerror("錯誤", f"EXCEPT: 儲存配置時發生錯誤：{str(e)}")

    def start_bot(self):
        try:
            # 重置停止標誌
            self.stop_flag = False
            
            # 更新按鈕狀態
            self.start_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            
            # 先儲存當前配置
            self.save_config()
            
            # 重新載入配置到全局 CONFIG
            with open('config.json', 'r', encoding='utf-8') as f:
                global CONFIG
                CONFIG.update(json.load(f))
            
            # 創建進度窗口
            progress_window = tk.Toplevel(self.root)
            progress_window.title("搶票進行中")
            progress_window.geometry("400x200")
            
            # 添加狀態標籤
            status_label = ttk.Label(progress_window, text="初始化中...")
            status_label.pack(pady=20)
            
            # 添加進度條
            progress = ttk.Progressbar(progress_window, mode='indeterminate')
            progress.pack(fill='x', padx=20)
            progress.start()
            
            # 使用線程執行搶票程序
            bot_thread = threading.Thread(
                target=self.run_bot,
                args=(progress_window, status_label),
                daemon=True  # 設置為守護線程，這樣主程序關閉時線程會自動結束
            )
            
            # 保存線程引用
            self.bot_thread = bot_thread
            bot_thread.start()
            
        except Exception as e:
            messagebox.showerror("錯誤", f"EXCEPT: 啟動搶票程序時發生錯誤：{str(e)}")
            self.reset_buttons()

    def stop_bot(self):
        self.stop_flag = True
        self.stop_button.configure(state='disabled')
        # 按鈕狀態會在 run_bot 結束時重置

    def reset_buttons(self):
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')

    def run_bot(self, progress_window, status_label):
        driver = None
        try:
            def update_status(text):
                self.root.after(0, lambda t=text: status_label.config(text=t))

            def show_error(error_msg):
                self.root.after(0, lambda m=error_msg: messagebox.showerror("錯誤", f"EXCEPT: {m}"))

            def show_message(title, msg):
                self.root.after(0, lambda t=title, m=msg: messagebox.showinfo(t, m))

            def show_warning(title, msg):
                self.root.after(0, lambda t=title, m=msg: messagebox.showwarning(t, m))

            def ask_yes_no(title, msg):
                return messagebox.askyesno(title, msg)

            def handle_card_auth(driver):
                """智慧檢測並處理卡號認證頁面"""
                if not CONFIG['concert']['card_auth']['enabled']:
                    return True  # 如果未啟用卡號認證，直接返回成功
                
                try:
                    # 處理可能存在的 alert
                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        update_status(f"檢測到 Alert: {alert_text}")
                        debug_log(f"檢測到 Alert: {alert_text}", driver)
                        alert.accept()  # 接受 alert
                        time.sleep(1)
                    except:
                        pass  # 沒有 alert，繼續
                    
                    # 獲取頁面 HTML 源碼
                    page_source = driver.page_source.lower()
                    
                    # 檢測卡號相關關鍵字
                    card_keywords = [
                        'visa infinite presale', 'visa infinite', 'presale', 
                        '卡號前6碼', '卡號前', 'checkcode', 'check code',
                        '請輸入visa', '請輸入卡號', 'greyinput'
                    ]
                    
                    # 檢查是否包含卡號相關關鍵字
                    card_auth_detected = False
                    detected_keyword = ""
                    
                    for keyword in card_keywords:
                        if keyword in page_source:
                            card_auth_detected = True
                            detected_keyword = keyword
                            break
                    
                    if card_auth_detected:
                        update_status(f"檢測到卡號認證頁面 (關鍵字: {detected_keyword})...")
                        debug_log(f"檢測到卡號認證頁面 (關鍵字: {detected_keyword})...", driver)
                        
                        # 智慧尋找卡號輸入框 - 優先使用精確選擇器
                        card_input = None
                        
                        # 精確的輸入框選擇器列表（按優先級排序）
                        input_selectors = [
                            # 最精確的選擇器 - 根據 HTML 源碼
                            "input[name='checkCode']",  # 這是正確的卡號輸入框
                            "input.greyInput",          # 根據 class 名稱
                            
                            # 其他可能的選擇器
                            "input[name*='check']",
                            "input[name*='code']",
                            "input[name*='card']",
                            "input[name*='number']",
                            "input[name*='verification']",
                            "input[name*='verify']",
                            "input[name*='presale']",
                            
                            # 通過 class 屬性查找（排除搜尋框）
                            "input[class*='grey']:not([id='txt_search'])",
                            "input[class*='input']:not([id='txt_search'])",
                            "input[class*='card']:not([id='txt_search'])",
                            
                            # 通用輸入框類型（排除搜尋框）
                            "input[type='text']:not([id='txt_search']):not([class*='search'])",
                        ]
                        
                        # 逐個嘗試選擇器
                        for selector in input_selectors:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                
                                for element in elements:
                                    try:
                                        # 檢查元素是否可見且可編輯
                                        if element.is_displayed() and element.is_enabled():
                                            # 獲取元素的各種屬性
                                            name_attr = element.get_attribute('name') or ''
                                            id_attr = element.get_attribute('id') or ''
                                            class_attr = element.get_attribute('class') or ''
                                            
                                            # 排除搜尋框
                                            if id_attr == 'txt_search' or 'search' in class_attr.lower():
                                                continue
                                            
                                            card_input = element
                                            update_status(f"找到卡號輸入框 (name={name_attr}, class={class_attr})")
                                            debug_log(f"找到卡號輸入框 (name={name_attr}, class={class_attr})", driver)
                                            break
                                    
                                    except Exception as e:
                                        debug_log(f"檢查輸入框時出錯: {str(e)}", driver)
                                        continue
                                
                                if card_input:
                                    break
                                    
                            except Exception as e:
                                debug_log(f"使用選擇器 {selector} 時出錯: {str(e)}", driver)
                                continue
                        
                        if card_input:
                            # 輸入卡號
                            card_number = CONFIG['concert']['card_auth']['card_number']
                            
                            # 混合式錯誤處理
                            input_success = False
                            
                            try:
                                # 方法1：直接輸入（最快）
                                card_input.clear()
                                card_input.send_keys(card_number)
                                
                                # 驗證輸入
                                if card_input.get_attribute('value') == card_number:
                                    input_success = True
                                    update_status(f"已輸入卡號: {card_number}")
                                    debug_log(f"已輸入卡號: {card_number}", driver)
                                
                            except Exception:
                                pass  # 繼續嘗試方法2
                            
                            if not input_success:
                                try:
                                    # 方法2：加短延遲重試
                                    debug_log("直接輸入失敗，嘗試延遲輸入", driver)
                                    card_input.clear()
                                    time.sleep(0.1)
                                    card_input.send_keys(card_number)
                                    
                                    update_status(f"已輸入卡號: {card_number} (延遲方法)")
                                    debug_log(f"已輸入卡號: {card_number} (延遲方法)", driver)
                                    
                                except Exception as e:
                                    debug_log(f"卡號輸入完全失敗: {str(e)}", driver)
                                    update_status("卡號輸入失敗，繼續流程...")
                                    # 不中斷流程，讓程式繼續
                                
                            # 智慧尋找提交按鈕
                            submit_button = None
                            
                            # 精確的按鈕選擇器列表
                            button_selectors = [
                                # 最精確的選擇器
                                "button[type='submit']",
                                "input[type='submit']",
                                
                                # 通過 class 查找
                                "button.btn",
                                "button.btn-primary",
                                "input.btn",
                                
                                # 任何按鈕
                                "button",
                                "input[type='button']"
                            ]
                            
                            # XPath 選擇器 (通過文字內容)
                            xpath_selectors = [
                                "//button[contains(text(), '送出')]",
                                "//button[contains(text(), '確認')]",
                                "//button[contains(text(), '提交')]",
                                "//input[@value='送出']",
                                "//input[@value='確認']",
                                "//input[@value='提交']"
                            ]
                            
                            # 先嘗試 CSS 選擇器
                            for selector in button_selectors:
                                try:
                                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                    for element in elements:
                                        try:
                                            if element.is_displayed() and element.is_enabled():
                                                submit_button = element
                                                break
                                        except:
                                            continue
                                    if submit_button:
                                        break
                                except:
                                    continue
                            
                            # 如果 CSS 選擇器找不到，嘗試 XPath
                            if not submit_button:
                                for selector in xpath_selectors:
                                    try:
                                        elements = driver.find_elements(By.XPATH, selector)
                                        for element in elements:
                                            try:
                                                if element.is_displayed() and element.is_enabled():
                                                    submit_button = element
                                                    break
                                            except:
                                                continue
                                        if submit_button:
                                            break
                                    except:
                                        continue
                            
                            if submit_button:
                                submit_button.click()
                                update_status("已提交卡號認證資訊")
                                debug_log("已提交卡號認證資訊", driver)
                                
                                # 快速檢測並處理提交後的確認彈窗
                                max_wait_time = 10   # 增加到10秒
                                check_interval = 0.1  # 保持100毫秒檢查一次
                                elapsed_time = 0
                                
                                update_status("正在檢測確認彈窗...")
                                debug_log("正在檢測確認彈窗...", driver)
                                
                                while elapsed_time < max_wait_time:
                                    try:
                                        # 嘗試檢測彈窗
                                        alert = driver.switch_to.alert
                                        alert_text = alert.text
                                        update_status(f"檢測到確認彈窗: {alert_text}")
                                        debug_log(f"檢測到確認彈窗: {alert_text}", driver)
                                        
                                        # 直接點擊確定，不管內容是什麼
                                        alert.accept()
                                        update_status("已確認彈窗，繼續下一步")
                                        debug_log("已確認彈窗，繼續下一步", driver)
                                        
                                        # 短暫等待頁面跳轉
                                        time.sleep(0.5)
                                        return True
                                        
                                    except Exception:
                                        # 沒有彈窗，繼續等待
                                        time.sleep(check_interval)
                                        elapsed_time += check_interval
                                
                                # 如果超過最大等待時間仍沒有彈窗，可能不需要彈窗確認
                                update_status("未檢測到確認彈窗，可能已直接跳轉")
                                debug_log("未檢測到確認彈窗，可能已直接跳轉", driver)
                                return True
                                
                            else:
                                update_status("找不到提交按鈕，可能需要手動提交")
                                debug_log("找不到提交按鈕，可能需要手動提交", driver)
                                # 即使找不到提交按鈕，也返回 True，因為卡號已經填入了
                                return True
                        else:
                            update_status("找不到卡號輸入框，可能需要手動輸入")
                            debug_log("找不到卡號輸入框，可能需要手動輸入", driver)
                            return True  # 返回 True 繼續流程，可能頁面已經處理好了
                    else:
                        # 沒有檢測到卡號認證頁面，直接返回成功
                        debug_log("未檢測到卡號認證頁面", driver)
                        return True
                        
                except Exception as e:
                    update_status(f"處理卡號認證時發生錯誤: {str(e)}")
                    debug_log(f"處理卡號認證時發生錯誤: {str(e)}", driver)
                    return True  # 發生錯誤時也返回 True，不中斷流程

            update_status("正在啟動瀏覽器...")
            driver = setup_chrome()
            
            update_status("正在訪問拓元網站...")
            driver.get(CONFIG['website']['base_url'])
            time.sleep(CONFIG['wait_times']['after_page_load'])
            
            if not check_login_status(driver):
                update_status("請在瀏覽器中完成登入...")
                
                # 創建一個自定義對話框
                login_dialog = tk.Toplevel(self.root)
                login_dialog.title("登入提示")
                login_dialog.geometry("400x150")
                login_dialog.transient(self.root)  # 設為主窗口的子窗口
                login_dialog.grab_set()  # 模態窗口
                
                ttk.Label(login_dialog, text="請在瀏覽器中登入您的帳號，完成後點擊確定", 
                         wraplength=350).pack(pady=20)
                
                login_completed = threading.Event()
                
                def on_confirm():
                    login_dialog.destroy()
                    login_completed.set()
                
                ttk.Button(login_dialog, text="確定", command=on_confirm).pack(pady=10)
                
                # 等待用戶確認
                self.root.after(100, login_dialog.focus_set)  # 設置焦點到對話框
                
                # 等待事件
                while not login_completed.is_set() and not self.stop_flag:
                    time.sleep(0.1)  # 小睡一下避免 CPU 佔用過高
                    self.root.update()  # 重要：更新 GUI
                
                if self.stop_flag:
                    if login_dialog.winfo_exists():
                        login_dialog.destroy()
                    update_status("搶票程序已停止")
                    return
            
            update_status("開始搶票流程...")
            
            # 搶票主循環
            attempt_count = 0
            use_alternative = False  # 控制是否使用備選日期
            use_any_date = False     # 新增：控制是否嘗試任意場次
            alternative_attempts = 0  # 記錄備選日期嘗試次數
            max_alternative_attempts = 2  # 最大備選日期嘗試次數
            
            # 保存原始日期設置
            original_date1 = CONFIG['concert']['date']
            original_date2 = CONFIG['concert']['date2']

            while not self.stop_flag:
                attempt_count += 1
                
                # 決定使用哪個日期
                if use_any_date and CONFIG['concert']['allow_alternative_date']:
                    # 任意場次模式
                    CONFIG['concert']['date'] = '*'
                    date_str = "任意"
                elif use_alternative and original_date2 != '*' and original_date2 != '':
                    # 備選日期模式
                    CONFIG['concert']['date'] = original_date2
                    date_str = "備選"
                else:
                    # 首選日期模式
                    CONFIG['concert']['date'] = original_date1
                    use_alternative = False
                    use_any_date = False
                    date_str = "首選"
                
                update_status(f"第 {attempt_count} 次嘗試 ({date_str}日期)...")
                
                # 步驟1：點擊立即購票
                update_status("正在點擊立即購票...")
                click_result = click_buy_ticket(driver)
                if not click_result:
                    update_status("點擊購票按鈕失敗")
                    time.sleep(0.5)
                    continue
                
                # 步驟2：選擇場次
                select_time_result = select_show_time(driver, attempt_count)
                
                if select_time_result.get("success", False):
                    update_status(f"已選擇{date_str}場次...")
                    
                    # 步驟3：在選擇場次成功後，檢查並處理卡號認證
                    update_status("=== 準備檢查卡號認證 ===")
                    debug_log("=== 準備檢查卡號認證 ===", driver)
                    
                    #update_status("等待5秒後開始卡號認證檢查...")
                    #debug_log("等待5秒後開始卡號認證檢查...", driver)
                    #time.sleep(5)  # 等待5秒
                    
                    update_status("開始檢查是否需要卡號認證...")
                    debug_log("開始檢查是否需要卡號認證...", driver)
                    
                    if not handle_card_auth(driver):
                        update_status("卡號認證處理失敗，繼續下一次嘗試...")
                        debug_log("卡號認證處理失敗，繼續下一次嘗試...", driver)
                        continue
                    
                    update_status("=== 卡號認證檢查完成 ===")
                    debug_log("=== 卡號認證檢查完成 ===", driver)
                    
                    #update_status("等待5秒後繼續下一步...")
                    #debug_log("等待5秒後繼續下一步...", driver)
                    #time.sleep(5)  # 等待5秒
                    
                    # 步驟4：選擇票價區域（在卡號認證之後）
                    if select_ticket_area(driver):
                        update_status("已選擇票價區域...")
                        
                        # 步驟5：選擇票數並處理驗證碼
                        update_status("正在處理票數選擇和驗證碼...")
                        
                        if select_ticket_number_and_verify(driver):
                            update_status("搶票成功！")
                            show_message("成功", "恭喜！訂票流程已完成")
                            if not ask_yes_no("繼續嘗試", "訂票已完成。是否繼續嘗試？"):
                                show_warning("付款提醒", 
                                    "請注意：在關閉程式前，請先確認您已完成訂票和付款流程！瀏覽器視窗將保持開啟，以便您處理後續步驟。")
                                driver_to_keep = driver
                                driver = None
                                break
                        else:
                            update_status("選擇票數並處理驗證碼失敗，訂票可能已完成")
                            
                            if not ask_yes_no("可能已完成", "選擇票數並處理驗證碼失敗，訂票可能已完成。是否繼續嘗試？"):
                                show_warning("付款提醒", "請注意：在關閉程式前，請先確認您已完成訂票和付款流程！瀏覽器視窗將保持開啟，以便您處理後續步驟。")
                                driver_to_keep = driver
                                driver = None
                                break
                    else:
                        update_status(f"選擇票價區域失敗，重新嘗試...")
                else:
                    reason = select_time_result.get("reason", "unknown")
                    update_status(f"選擇場次失敗，原因: {reason}，重新嘗試...")
                    
                    # 處理日期切換邏輯
                    if not use_alternative and not use_any_date and original_date2 != '':
                        # 首選日期失敗，切換到備選日期
                        use_alternative = True
                        alternative_attempts = 0
                        update_status("首選日期無法選擇，嘗試備選日期...")
                    elif use_alternative:
                        # 備選日期嘗試一定次數後
                        alternative_attempts += 1
                        if alternative_attempts >= max_alternative_attempts:
                            if CONFIG['concert']['allow_alternative_date']:
                                # 如果允許選擇替代場次，切換到任意場次模式
                                use_any_date = True
                                use_alternative = False
                                update_status("備選日期也無法選擇，嘗試任意可用場次...")
                            else:
                                # 不允許選擇替代場次，回到首選日期
                                use_alternative = False
                                update_status("備選日期也無法選擇，回到首選日期...")
                    elif use_any_date:
                        # 如果在任意場次模式下仍然失敗，回到首選日期重新開始循環
                        use_any_date = False
                        update_status("任意場次也無法選擇，回到首選日期重新開始...")
                
                if self.stop_flag:
                    update_status("搶票程序已停止")
                    break
                
                time.sleep(0.5)
            
            if self.stop_flag:
                update_status("搶票程序已手動停止")
                show_message("已停止", "搶票程序已停止")
                
        except Exception as e:
            show_error(str(e))
        finally:
            # 確保恢復原始設置
            if 'CONFIG' in globals() and 'original_date1' in locals():
                CONFIG['concert']['date'] = original_date1
            
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            self.root.after(0, progress_window.destroy)
            self.root.after(0, self.reset_buttons)

    def select_html_path(self):
        """選擇HTML保存路徑"""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="選擇HTML保存目錄")
        if path:
            self.html_save_path.delete(0, tk.END)
            self.html_save_path.insert(0, path)

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketBotGUI(root)
    root.mainloop() 