import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import ddddocr
from PIL import Image
import requests
from urllib.parse import urljoin
import os

# 用戶配置區域 - 請在此處修改您的設定
CONFIG = {
    # Chrome相關設定
    'chromedriver_path': r'D:\python work\chromedriver-win64\chromedriver.exe',  # ChromeDriver 的路徑
    'chrome_user_data_dir': r'D:\python work\chrome_user_data',  # Chrome用戶資料目錄
    'chrome_profile': 'Default',  # Chrome設定檔名稱，預設是'Default'
    
    # 瀏覽器視窗設定 - 調整為更大的尺寸以確保所有元素可見
    'window_size': {
        'width': 800,  # 增加寬度
        'height': 1020   # 增加高度
    },
    
    # 演唱會設定
    'concert': {
        'date': '2025/05/16',  # 第一個日期
        'date2': '*',  # 第二個日期 - 使用 * 表示接受任何日期
        'allow_alternative_date': True,  # 是否允許選擇替代場次
        'switch_date_attempt': 2,  # 嘗試幾次後切換到備選日期
        # 新增：卡號認證設定
        'card_auth': {
            'enabled': False,  # 是否啟用卡號認證
            'card_number': ''  # 卡號（如果啟用認證的話）
        }
    },
    
    # 票數設定
    'ticket_config': {
        'ticket_numbers': {
            'max_tickets': '3'  # 最大票數
        },
        'target_price': 2500,  # 加入目標票價設定
        'retry': {
            'max_attempts':100,  # 最大重試次數
            'delay': 0.02  # 重試間隔 (縮短為0.5秒)
        }
    },
    
    # 網站設定
    'website': {
        'base_url': 'https://tixcraft.com/activity/detail/25_eason',  # 網站基本網址
        'login_url': 'https://tixcraft.com/login',  # 登入頁面
        'activity_url': 'https://tixcraft.com/activity/detail/25_xalive',  # 活動列表頁面
    },
    
    # 調試模式設定
    'debug': {
        'enabled': True,  # 是否啟用調試模式
        'force_captcha_error': False,  # 是否強制驗證碼輸入錯誤
        'first_captcha_value': 'aabb',  # 故意輸入的錯誤驗證碼
        'error_attempts': 1,  # 故意輸入錯誤的次數
        'verbose': True,  # 是否顯示詳細日誌
        'save_screenshots': False,  # 是否保存截圖
        'save_html_source': True,  # 是否保存HTML源碼
        'html_save_path': 'html_dumps',  # 新增HTML保存路徑
    },
    
    # 等待時間設定 (單位: 秒)
    'wait_times': {
        'after_page_load': 2.0,        # 頁面載入後的等待時間
        'after_click_buy': 0.5,        # 點擊購票按鈕後的等待時間
        'after_date_select': 0.1,      # 選擇日期後的等待時間
        'after_click_order': 0.1,      # 點擊立即訂購後的等待時間
        'ticket_page_load': 0.1,       # 進入選擇張數頁面的等待時間
        'after_submit': 0.3,           # 提交表單後的等待時間
        'captcha_update': 0.2,         # 驗證碼更新的最大等待時間
    },
}
# 在全局範圍初始化 OCR 並進行預熱 
global_ocr = ddddocr.DdddOcr(show_ad=False)
print("正在預熱 OCR 模型...")
# 創建一個 1x1 的黑色圖片作為 dummy 輸入
dummy_image = Image.new('RGB', (1, 1), color='black')
dummy_image.save("dummy.png")
with open("dummy.png", "rb") as f:
    global_ocr.classification(f.read())  # 進行一次 dummy 識別
print("OCR 模型預熱完成")

def debug_log(message, driver=None, force=False):
    """輸出調試日誌"""
    if CONFIG['debug']['enabled'] and (CONFIG['debug']['verbose'] or force):
        print(f"[DEBUG] {message}")
        if driver and CONFIG['debug']['save_html_source']:
            # 避免產生遞迴呼叫
            html_filename = _save_html_source(driver, message)
            if html_filename:
                print(f"[DEBUG] 已保存HTML源碼到: {html_filename}")

def _save_html_source(driver, name=None):
    """內部使用的保存HTML源碼函數，避免遞迴呼叫"""
    try:
        timestamp = int(time.time())
        # 處理檔案名稱(移除不合法字元)
        safe_name = str(name).replace(" ", "_").replace(":", "_").replace("/", "_")[:50] if name else 'page'
        filename = f"debug_html_{safe_name}_{timestamp}.html"
        
        # 使用配置中指定的目錄
        save_path = CONFIG['debug'].get('html_save_path', 'html_dumps')
        os.makedirs(save_path, exist_ok=True)
        fullpath = os.path.join(save_path, filename)
        
        # 保存原始HTML（移除高亮功能以提高搶票效率）
        with open(fullpath, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        return fullpath
            
    except Exception as e:
        print(f"[ERROR] 保存HTML源碼失敗: {e}")
        return None

# 保留原函數供向後兼容
def save_html_source(driver, name=None):
    """保存當前網頁的HTML源碼，用於調試"""
    if CONFIG['debug']['enabled']:
        return _save_html_source(driver, name)
    return None

def debug_screenshot(driver, name):
    """保存調試截圖"""
    if CONFIG['debug']['enabled'] and CONFIG['debug']['save_screenshots']:
        try:
            filename = f"debug_{name}_{int(time.time())}.png"
            driver.save_screenshot(filename)
            debug_log(f"已保存截圖: {filename}")
        except Exception as e:
            debug_log(f"保存截圖失敗: {e}")

def setup_chrome():
    try:
        options = uc.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument(f'--window-size={CONFIG["window_size"]["width"]},{CONFIG["window_size"]["height"]}')
        
        user_data_dir = CONFIG.get('chrome_user_data_dir', '')
        
        if user_data_dir and not os.path.exists(user_data_dir):
            try:
                os.makedirs(user_data_dir)
            except Exception:
                user_data_dir = ""
        
        if user_data_dir:
            options.add_argument(f'--user-data-dir={user_data_dir}')
            profile = CONFIG.get('chrome_profile', '')
            if profile:
                options.add_argument(f'--profile-directory={profile}')
        
        driver = uc.Chrome(
            options=options,
            driver_executable_path=CONFIG['chromedriver_path']
        )
        
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            })
        except Exception:
            pass
        
        driver.set_window_size(CONFIG["window_size"]["width"], CONFIG["window_size"]["height"])
        driver.set_window_position(0, 0)
        
        return driver
    except Exception as e:
        raise

def check_login_status(driver):
    try:
        current_url = driver.current_url
        if CONFIG['website']['base_url'] not in current_url:
            driver.get(CONFIG['website']['base_url'])
            time.sleep(CONFIG['wait_times']['after_page_load'])
        
        try:
            logout_link = driver.find_element(By.LINK_TEXT, "登出")
            return True
        except:
            try:
                user_info = driver.find_element(By.CLASS_NAME, "user-name")
                return True
            except:
                return False
    except:
        return False

def click_buy_ticket(driver):
    try:
        debug_log("嘗試點擊立即購票按鈕")
        js_click = """
        var link = document.querySelector('a[href*="/activity/game/"]');
        if (link) link.click();
        """
        driver.execute_script(js_click)
        time.sleep(CONFIG['wait_times']['after_click_buy'])
        debug_screenshot(driver, "after_click_buy")
        return True
    except Exception as e:
        debug_log(f"EXCEPT: 點擊立即購票失敗: {e}")
        return False

def select_show_time(driver, attempt_count=0):
    """選擇演出場次"""
    try:
        debug_log(f"嘗試選擇演出場次 (嘗試 #{attempt_count})", driver)
        
        # 先保存當前頁面的HTML，便於診斷
        save_html_source(driver, f"before_select_date_attempt_{attempt_count}")
        
        # 從配置中獲取切換日期的門檻值
        switch_threshold = CONFIG['concert'].get('switch_date_attempt', 5)  # 默認值為5
        
        # 根據嘗試次數決定使用哪個日期 - 改進為輪流嘗試
        use_primary_date = (attempt_count % (switch_threshold * 2)) < switch_threshold
        
        if use_primary_date:
            target_date = CONFIG['concert']['date']
            debug_log(f"使用第一個日期: {target_date} (當前嘗試次數: {attempt_count})", driver)
        else:
            target_date = CONFIG['concert'].get('date2', CONFIG['concert']['date']).strip()
            debug_log(f"使用第二個日期: {target_date} (當前嘗試次數: {attempt_count})", driver)
        
        # 檢查頁面類型 - 是表格還是下拉選單
        js_check_page_type = """
        // 檢查是否有表格式的多場次
        var tableRows = document.querySelectorAll('tr.gridc');
        if (tableRows.length > 0) {
            return {
                type: 'table',
                rowCount: tableRows.length
            };
        }
        
        // 檢查是否有下拉選單
        var dateSelect = document.getElementById('dateSearchGameList');
        if (dateSelect) {
            return {
                type: 'dropdown',
                hasOptions: dateSelect.options && dateSelect.options.length > 1
            };
        }
        
        return { type: 'unknown' };
        """
        
        page_type_result = driver.execute_script(js_check_page_type)
        debug_log(f"頁面類型: {page_type_result}", driver)
        
        # 處理表格式多場次頁面
        if page_type_result.get('type') == 'table':
            return handle_table_view(driver, target_date)
        
        # 處理下拉選單式頁面
        elif page_type_result.get('type') == 'dropdown':
            return handle_dropdown_view(driver, target_date)
        
        # 未知頁面類型
        else:
            debug_log("未知的頁面類型，無法選擇日期", driver)
            return {"success": False, "reason": "unknown_page_type"}
            
    except Exception as e:
        debug_log(f"EXCEPT: 選擇場次時發生錯誤: {e}", driver)
        save_html_source(driver, f"select_time_error_attempt_{attempt_count}")
        return {"success": False, "reason": "error"}

def handle_table_view(driver, target_date):
    """處理表格式多場次頁面"""
    debug_log(f"處理表格式多場次頁面，目標日期: {target_date}", driver)
    
    # 先收集所有可見的日期和對應的按鈕狀態
    js_collect_dates = """
    var dateInfo = [];
    var rows = document.querySelectorAll('tr.gridc');
    
    for (var i = 0; i < rows.length; i++) {
        // 檢查行是否隱藏
        if (rows[i].style.display === 'none') {
            continue;
        }
        
        var dateCell = rows[i].cells[0];
        var dateText = dateCell.textContent.trim();
        var dateShort = dateText.split(' ')[0];  // 只取日期部分，格式如 "2025/03/23"
        
        // 檢查訂購按鈕
        var orderButton = rows[i].querySelector('button.btn.btn-primary');
        
        // 檢查是否有"選購一空"提示
        var soldOutDiv = rows[i].querySelector('div');
        var isSoldOut = soldOutDiv && soldOutDiv.textContent.includes('選購一空');
        
        dateInfo.push({
            fullText: dateText,
            dateOnly: dateShort,
            hasButton: !!orderButton,
            isSoldOut: isSoldOut,
            rowIndex: i
        });
    }
    
    return dateInfo;
    """
    
    date_info = driver.execute_script(js_collect_dates)
    debug_log(f"頁面中的所有場次資訊: {date_info}", driver)
    
    # 檢查目標日期格式，統一為YYYY/MM/DD格式
    target_date_short = target_date.split(' ')[0] if ' ' in target_date else target_date
    debug_log(f"目標日期簡化後: {target_date_short}", driver)
    
    # 獲取是否允許替代場次的設定
    allow_alternative = CONFIG['concert'].get('allow_alternative_date', True)
    debug_log(f"是否允許選擇替代場次: {allow_alternative}", driver)
    
    # 修改點擊邏輯以支持通配符
    js_click_by_date = f"""
    var targetDate = "{target_date_short}";
    var rows = document.querySelectorAll('tr.gridc');
    var result = {{
        success: false,
        reason: "not_found",
        targetDate: targetDate
    }};
    
    // 如果目標日期是 '*'，直接尋找第一個可用場次
    if (targetDate === '*') {{
        for (var i = 0; i < rows.length; i++) {{
            if (rows[i].style.display === 'none') continue;
            
            var soldOutDiv = rows[i].querySelector('div');
            if (soldOutDiv && soldOutDiv.textContent.includes('選購一空')) continue;
            
            var orderButton = rows[i].querySelector('button.btn.btn-primary');
            if (orderButton) {{
                var dateCell = rows[i].cells[0];
                var dateText = dateCell.textContent.trim();
                orderButton.click();
                result.success = true;
                result.reason = "clicked_wildcard";
                result.matchedDate = dateText;
                return result;
            }}
        }}
    }} else {{
        // 原有的精確匹配邏輯
        for (var i = 0; i < rows.length; i++) {{
            // 跳過隱藏行
            if (rows[i].style.display === 'none') {{
                continue;
            }}
            
            var dateCell = rows[i].cells[0];
            var dateText = dateCell.textContent.trim();
            var dateShort = dateText.split(' ')[0];  // 只取日期部分
            
            // 記錄遍歷的日期
            if (!result.checkedDates) result.checkedDates = [];
            result.checkedDates.push({{ dateShort: dateShort, fullText: dateText }});
            
            // 檢查是否精確匹配目標日期
            if (dateShort === targetDate) {{
                // 檢查是否已售完
                var soldOutDiv = rows[i].querySelector('div');
                if (soldOutDiv && soldOutDiv.textContent.includes('選購一空')) {{
                    result.exactMatchButSoldOut = true;
                    result.soldOutDate = dateText;
                    continue;  // 此場次已售完，繼續檢查其他場次
                }}
                
                // 尋找立即訂購按鈕
                var orderButton = rows[i].querySelector('button.btn.btn-primary');
                if (orderButton) {{
                    orderButton.click();
                    result.success = true;
                    result.reason = "clicked_exact_match";
                    result.matchedDate = dateText;
                    return result;
                }} else {{
                    result.exactMatchNoButton = true;
                }}
            }}
        }}
    }}
    
    // 這個參數控制是否允許選擇替代場次
    var allowAlternative = {str(allow_alternative).lower()};
    
    // 如果目標日期已售完或沒有按鈕，並且允許選擇替代場次
    if ((result.exactMatchButSoldOut || result.exactMatchNoButton) && allowAlternative) {{
        for (var i = 0; i < rows.length; i++) {{
            // 跳過隱藏行
            if (rows[i].style.display === 'none') {{
                continue;
            }}
            
            // 檢查是否已售完
            var soldOutDiv = rows[i].querySelector('div');
            if (soldOutDiv && soldOutDiv.textContent.includes('選購一空')) {{
                continue;  // 跳過已售完場次
            }}
            
            // 尋找立即訂購按鈕
            var orderButton = rows[i].querySelector('button.btn.btn-primary');
            if (orderButton) {{
                var dateCell = rows[i].cells[0];
                var alternativeDate = dateCell.textContent.trim();
                orderButton.click();
                result.success = true;
                result.reason = "clicked_alternative";
                result.alternativeDate = alternativeDate;
                return result;
            }}
        }}
    }}
    
    // 找不到任何可用場次
    return result;
    """
    
    click_result = driver.execute_script(js_click_by_date)
    debug_log(f"日期點擊結果: {click_result}", driver)
    
    if click_result.get('success', False):
        reason = click_result.get('reason', '')
        if reason == 'clicked_wildcard':
            matched_date = click_result.get('matchedDate', '')
            debug_log(f"已點擊通配符匹配的場次: {matched_date}", driver)
        elif reason == 'clicked_exact_match':
            matched_date = click_result.get('matchedDate', '')
            debug_log(f"已點擊精確匹配的場次: {matched_date}", driver)
        elif reason == 'clicked_alternative':
            alt_date = click_result.get('alternativeDate', '')
            debug_log(f"目標場次不可用，已點擊替代場次: {alt_date}", driver)
        
        time.sleep(CONFIG['wait_times']['after_click_order'])
        debug_screenshot(driver, "after_click_in_table")
        return {"success": True}
    else:
        debug_log("所有場次都無法點擊", driver)
        
        if click_result.get('exactMatchButSoldOut', False):
            sold_out_date = click_result.get('soldOutDate', '')
            debug_log(f"目標場次 {sold_out_date} 已售完", driver)
        elif click_result.get('exactMatchNoButton', False):
            debug_log(f"目標場次找不到立即訂購按鈕", driver)
        else:
            checked_dates = click_result.get('checkedDates', [])
            debug_log(f"找不到目標日期 {target_date_short}，已檢查的日期: {checked_dates}", driver)
        
        return {"success": False, "reason": "not_on_sale"}

def handle_dropdown_view(driver, target_date):
    """處理下拉選單式頁面"""
    debug_log("處理下拉選單式頁面", driver)
    
    # 獲取是否允許替代場次的設定
    allow_alternative = CONFIG['concert'].get('allow_alternative_date', True)
    debug_log(f"是否允許選擇替代場次: {allow_alternative}", driver)
    
    # 嘗試選擇日期
    js_select_date = f"""
    var select = document.getElementById('dateSearchGameList');
    var allowAlternative = {str(allow_alternative).lower()};
    
    if (!select) {{
        return {{ success: false, reason: 'element_not_found' }};
    }}
    
    if (!select.options || select.options.length <= 1) {{
        return {{ success: false, reason: 'no_options' }};
    }}
    
    // 首先尋找目標日期
    var targetIndex = -1;
    for (var i = 0; i < select.options.length; i++) {{
        if (select.options[i].text.includes('{target_date}')) {{
            targetIndex = i;
            break;
        }}
    }}
    
    // 如果找到目標日期
    if (targetIndex >= 0) {{
        select.selectedIndex = targetIndex;
        select.dispatchEvent(new Event('change'));
        return {{ success: true, selectedDate: select.options[targetIndex].text, isTargetDate: true }};
    }}
    
    // 如果沒找到目標日期，且允許替代場次，則選擇第一個可用選項
    if (allowAlternative && select.options.length > 1) {{
        // 選擇第一個非空選項（通常是索引1，因為索引0常常是"請選擇"）
        var alternativeIndex = (select.options[0].value == '') ? 1 : 0;
        if (alternativeIndex < select.options.length) {{
            select.selectedIndex = alternativeIndex;
            select.dispatchEvent(new Event('change'));
            return {{ 
                success: true, 
                selectedDate: select.options[alternativeIndex].text,
                isTargetDate: false,
                isAlternative: true
            }};
        }}
    }}
    
    return {{ 
        success: false, 
        reason: 'date_not_found',
        availableDates: Array.from(select.options).map(o => o.text)
    }};
    """
    
    select_result = driver.execute_script(js_select_date)
    debug_log(f"選擇日期結果: {select_result}", driver)
    
    if select_result.get('success', False):
        if select_result.get('isTargetDate', True):
            debug_log(f"已選擇目標日期: {select_result.get('selectedDate')}", driver)
        else:
            debug_log(f"目標日期不可用，已選擇替代日期: {select_result.get('selectedDate')}", driver)
        
        time.sleep(CONFIG['wait_times']['after_date_select'])
        
        # 尋找並點擊訂購按鈕 (移除event_id檢查)
        js_click_order = """
        var buttons = document.querySelectorAll('button.btn.btn-primary');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].dataset.href) {
                buttons[i].click();
                return true;
            }
        }
        return false;
        """
        
        if driver.execute_script(js_click_order):
            debug_log("已點擊立即訂購", driver)
            time.sleep(CONFIG['wait_times']['after_click_order'])
            debug_screenshot(driver, "after_select_time")
            return {"success": True}
        else:
            debug_log("找不到立即訂購按鈕，判定為尚未開賣", driver)
            return {"success": False, "reason": "not_on_sale"}
    else:
        reason = select_result.get('reason', 'unknown')
        debug_log(f"選擇日期失敗，原因: {reason}", driver)
        return {"success": False, "reason": "not_on_sale"}

def select_ticket_area(driver):
    target_price = CONFIG['ticket_config']['target_price']
    
    while True:
        try:
            debug_log(f"嘗試選擇票價與座位區域 (目標票價: {target_price}元)", driver)
            
            # 先保存HTML來分析頁面結構
            html_path = _save_html_source(driver, "ticket_area_selection")
            debug_log(f"已保存選擇票價頁面HTML至: {html_path}", driver)
            
            # 獲取所有區域的詳細信息，不進行點擊
            js_detail_areas = """
            var detailedAreas = [];
            document.querySelectorAll('.area-list li.select_form_a a, .area-list li.select_form_b a').forEach(link => {
                try {
                    var areaText = link.textContent.trim();
                    var areaInfo = {
                        id: link.id,
                        text: areaText,
                        className: link.className,
                        href: link.href || '',
                        attributes: {},
                        html: link.outerHTML,
                        parentHTML: link.parentNode.outerHTML.substring(0, 200) + '...'  // 只取前200字符
                    };
                    
                    // 收集所有屬性
                    for (var i = 0; i < link.attributes.length; i++) {
                        var attr = link.attributes[i];
                        areaInfo.attributes[attr.name] = attr.value;
                    }
                    
                    detailedAreas.push(areaInfo);
                } catch(e) {
                    console.error("解析區域時出錯:", e);
                }
            });
            return detailedAreas;
            """
            detailed_areas = driver.execute_script(js_detail_areas)
            debug_log(f"頁面中找到 {len(detailed_areas)} 個票區元素，詳細信息：", driver)
            for i, area in enumerate(detailed_areas):
                debug_log(f"區域 {i+1}: ID={area['id']}, 文本={area['text']}", driver)
                debug_log(f"   HTML: {area['html']}", driver)
                debug_log(f"   屬性: {area['attributes']}", driver)
            
            # 修改 JavaScript 以改進價格解析邏輯
            js_get_areas = """
            var availableAreas = [];
            document.querySelectorAll('.area-list li.select_form_a a, .area-list li.select_form_b a').forEach(link => {
                try {
                    var areaText = link.textContent.trim();
                    // 改善價格匹配邏輯：優先匹配「價格：X元」的格式
                    var priceMatch = areaText.match(/價格：\s*(\d+)\s*元/);
                    var price = 0;
                    
                    if (priceMatch && priceMatch[1]) {
                        // 優先使用「價格：X元」格式
                        price = parseInt(priceMatch[1]);
                    } else {
                        // 備用方案：繼續使用舊的匹配邏輯
                        var oldPriceMatch = areaText.match(/(\\d+)(?=\\s*(?:區|站區|剩餘))/g);
                        price = oldPriceMatch ? parseInt(oldPriceMatch[oldPriceMatch.length - 1]) : 0;
                    }
                    
                    // 匹配剩餘票數
                    var ticketsMatch = areaText.match(/剩餘\\s*(\\d+)/);
                    var remainingTickets = ticketsMatch ? parseInt(ticketsMatch[1]) : 0;
                    
                    var areaInfo = {
                        id: link.id,
                        text: areaText,
                        price: price,
                        remainingTickets: remainingTickets,
                        isRestrictedArea: areaText.toLowerCase().includes('視線') || 
                                        areaText.toLowerCase().includes('身障')
                    };
                    
                    // 新增：记录更多调试信息
                    areaInfo.debugInfo = {
                        priceMatches: areaText.match(/\\d+/g) || [],
                        fullText: areaText,
                        hasLabel: areaText.includes('價格'),
                        hasRemaining: areaText.includes('剩餘')
                    };
                    
                    availableAreas.push(areaInfo);
                } catch(e) {
                    console.error("解析區域時出錯:", e);
                }
            });
            return availableAreas;
            """
            available_areas = driver.execute_script(js_get_areas)
            
            # 詳細記錄每個區域的調試信息
            for i, area in enumerate(available_areas):
                debug_info = area.get('debugInfo', {})
                debug_log(f"區域 {i+1} 解析結果: ID={area['id']}, 文本='{area['text']}'", driver)
                debug_log(f"  價格解析結果: {area['price']}元, 剩餘票數: {area['remainingTickets']}", driver)
                debug_log(f"  調試信息: 文本中的數字={debug_info.get('priceMatches')}, "
                         f"有價格標籤={debug_info.get('hasLabel')}, "
                         f"有剩餘標籤={debug_info.get('hasRemaining')}", driver)
            
            # 過濾掉受限制的區域，並按照價格排序
            if available_areas:
                # 先過濾掉受限制的區域
                unrestricted_areas = [area for area in available_areas if not area['isRestrictedArea']]
                
                if unrestricted_areas:
                    # 按照與目標價格的接近程度排序
                    sorted_areas = sorted(unrestricted_areas, 
                                       key=lambda x: (abs(x['price'] - target_price), -x['remainingTickets']))
                    
                    debug_log(f"找到 {len(sorted_areas)} 個可用非受限制區域", driver)
                    for area in sorted_areas:
                        debug_log(f"可選擇區域: {area['id']} - {area['text']} "
                                f"(價格: {area['price']}元, 剩餘票數: {area['remainingTickets']})", driver)
                    
                    # 選擇最符合條件的區域
                    best_area = sorted_areas[0]
                    debug_log(f"選擇最佳區域: {best_area['text']} (價格: {best_area['price']}元)", driver)
                    
                    # 點擊選擇的區域
                    js_click_area = f"""
                    document.getElementById('{best_area['id']}').click();
                    return true;
                    """
                    click_result = driver.execute_script(js_click_area)
                    
                    if click_result:
                        debug_log(f"已選擇區域: {best_area['text']}", driver)
                        debug_screenshot(driver, "after_select_area")
                        
                        # 保存點擊後的HTML
                        after_click_html = _save_html_source(driver, "after_select_area")
                        debug_log(f"已保存選擇區域後的HTML至: {after_click_html}", driver)
                        
                        time.sleep(0.5)
                        return True
            
            # 如果沒找到合適區域，嘗試滾動頁面
            debug_log("未找到合適區域，嘗試滾動頁面", driver)
            js_scroll = """
            var areaList = document.querySelector('.area-list');
            if (areaList) {
                areaList.scrollIntoView({behavior: 'smooth', block: 'center'});
                return true;
            }
            window.scrollTo(0, 0);
            window.scrollBy(0, 300);
            return false;
            """
            driver.execute_script(js_scroll)
            debug_log("頁面已滾動，等待重新檢查", driver)
            time.sleep(1)
            
        except Exception as e:
            debug_log(f"EXCEPT: 選擇票價與座位時發生錯誤: {e}", driver)
            time.sleep(0.5)
            continue  # 發生錯誤時繼續重試

def select_ticket_number_and_verify(driver):
    try:
        debug_log("進入選擇張數頁面")
        time.sleep(CONFIG['wait_times']['ticket_page_load'])
        debug_screenshot(driver, "ticket_number_page")
        
        # 定義選擇票數的函數，以便重複使用
        def select_ticket_number():
            # 先檢查元素是否直接可見
            js_check_select = """
            var select = document.querySelector('#TicketForm_ticketPrice_04');
            if (select) {
                var rect = select.getBoundingClientRect();
                var isVisible = (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
                return { found: true, visible: isVisible, id: '#TicketForm_ticketPrice_04' };
            }
            
            // 如果找不到主要選擇器，嘗試其他選擇器
            var selects = document.querySelectorAll('select[id^="TicketForm_ticketPrice"]');
            if (selects.length > 0) {
                var rect = selects[0].getBoundingClientRect();
                var isVisible = (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
                return { found: true, visible: isVisible, id: selects[0].id };
            }
            
            return { found: false, visible: false, id: null };
            """
            
            select_result = driver.execute_script(js_check_select)
            debug_log(f"票數選擇器檢查結果: {select_result}")
            
            # 如果找到元素但不可見，嘗試滾動到元素
            if select_result.get('found', False) and not select_result.get('visible', False):
                selector_id = select_result.get('id')
                debug_log(f"找到票數選擇器但不可見，嘗試滾動: {selector_id}")
                
                js_scroll = f"""
                var element = document.querySelector('{selector_id}');
                if (element) {{
                    element.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    return true;
                }}
                return false;
                """
                driver.execute_script(js_scroll)
                time.sleep(0.5)  # 等待滾動完成
            
            # 如果找到主選擇器，直接使用
            js_select_number = f"""
            var select = document.querySelector('#TicketForm_ticketPrice_04');
            if (select) {{
                select.value = '{CONFIG['ticket_config']['ticket_numbers']['max_tickets']}';
                select.dispatchEvent(new Event('change'));
                return true;
            }}
            return false;
            """
            if driver.execute_script(js_select_number):
                debug_log(f"已選擇張數: {CONFIG['ticket_config']['ticket_numbers']['max_tickets']}")
                return True
            
            # 如果主選擇器不可用，使用替代方法
            debug_log("使用替代方法選擇張數")
            js_select_number_alt = f"""
            var selects = document.querySelectorAll('select[id^="TicketForm_ticketPrice"]');
            if (selects.length > 0) {{
                selects[0].value = '{CONFIG['ticket_config']['ticket_numbers']['max_tickets']}';
                selects[0].dispatchEvent(new Event('change'));
                return true;
            }}
            return false;
            """
            result = driver.execute_script(js_select_number_alt)
            debug_log(f"替代方法選擇張數結果: {result}")
            return result
        
        # 定義勾選同意條款的函數，以便重複使用
        def check_agree():
            # 先檢查同意條款複選框是否直接可見
            js_check_checkbox = """
            var checkbox = document.querySelector('#TicketForm_agree');
            if (checkbox) {
                var rect = checkbox.getBoundingClientRect();
                var isVisible = (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
                return { found: true, visible: isVisible, id: '#TicketForm_agree' };
            }
            
            // 如果找不到主要選擇器，嘗試其他選擇器
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (var i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i].id.includes('agree') || checkboxes[i].name.includes('agree')) {
                    var rect = checkboxes[i].getBoundingClientRect();
                    var isVisible = (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                    return { found: true, visible: isVisible, id: '#' + checkboxes[i].id };
                }
            }
            
            return { found: false, visible: false, id: null };
            """
            
            checkbox_result = driver.execute_script(js_check_checkbox)
            debug_log(f"同意條款複選框檢查結果: {checkbox_result}")
            
            # 如果找到元素但不可見，嘗試滾動到元素
            if checkbox_result.get('found', False) and not checkbox_result.get('visible', False):
                selector_id = checkbox_result.get('id')
                debug_log(f"找到同意條款複選框但不可見，嘗試滾動: {selector_id}")
                
                js_scroll = f"""
                var element = document.querySelector('{selector_id}');
                if (element) {{
                    element.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    return true;
                }}
                return false;
                """
                driver.execute_script(js_scroll)
                time.sleep(0.5)  # 等待滾動完成
            
            # 如果找到主複選框，直接使用
            js_check_agree = """
            var checkbox = document.querySelector('#TicketForm_agree');
            if (checkbox) {
                checkbox.checked = true;
                checkbox.dispatchEvent(new Event('change'));
                checkbox.dispatchEvent(new Event('click'));
                return true;
            }
            return false;
            """
            if driver.execute_script(js_check_agree):
                debug_log("已勾選同意條款")
                return True
            
            # 如果主複選框不可用，使用替代方法
            debug_log("使用替代方法勾選同意條款")
            js_check_agree_alt = """
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            for (var i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i].id.includes('agree') || checkboxes[i].name.includes('agree')) {
                    checkboxes[i].checked = true;
                    checkboxes[i].dispatchEvent(new Event('change'));
                    checkboxes[i].dispatchEvent(new Event('click'));
                    return true;
                }
            }
            return false;
            """
            result = driver.execute_script(js_check_agree_alt)
            debug_log(f"替代方法勾選同意條款結果: {result}")
            return result
        
        # 初始選擇票數
        select_ticket_number()
        
        # 初始勾選同意條款
        check_agree()
        
        debug_screenshot(driver, "after_select_number")

        # 處理驗證碼
        retry_count = 0
        previous_answers = set()  # 記錄已嘗試過的答案，避免重複提交
        ocr = ddddocr.DdddOcr(show_ad=False)
        
        while retry_count < CONFIG['ticket_config']['retry']['max_attempts']:
            try:
                debug_log(f"驗證碼處理嘗試 #{retry_count + 1}")
                
                # 每次重試時都重新選擇票數和勾選同意條款
                if retry_count > 0:
                    debug_log("重新選擇票數和勾選同意條款")
                    select_ticket_number()
                    check_agree()
                
                # 確保驗證碼圖片可見
                js_check_captcha_visible = """
                var captcha = document.getElementById('TicketForm_verifyCode-image');
                if (captcha) {
                    var rect = captcha.getBoundingClientRect();
                    var isVisible = (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                    
                    if (!isVisible) {
                        captcha.scrollIntoView({behavior: 'smooth', block: 'center'});
                        return false;
                    }
                    return true;
                }
                return false;
                """
                captcha_visible = driver.execute_script(js_check_captcha_visible)
                debug_log(f"驗證碼圖片可見性: {captcha_visible}")
                
                # 獲取驗證碼圖片
                try:
                    captcha_img = driver.find_element(By.ID, "TicketForm_verifyCode-image")
                    debug_log("找到驗證碼圖片")
                except:
                    try:
                        captcha_img = driver.find_element(By.CSS_SELECTOR, "img[src*='verifyCode']")
                        debug_log("使用CSS選擇器找到驗證碼圖片")
                    except:
                        debug_log("找不到驗證碼圖片，重試")
                        retry_count += 1
                        continue
                
                if captcha_img is None:
                    debug_log("驗證碼圖片為空，重試")
                    retry_count += 1
                    continue
                
                # 檢查是否在故意錯誤的嘗試次數範圍內
                if CONFIG['debug']['enabled'] and CONFIG['debug']['force_captcha_error'] and retry_count < CONFIG['debug']['error_attempts']:
                    # 根據嘗試次數生成數字驗證碼：1, 2, 3...
                    captcha_text = str(retry_count + 1)  # 轉換為字符串
                    debug_log(f"調試模式: 第 {retry_count + 1} 次故意輸入數字驗證碼 '{captcha_text}'", force=True)
                else:
                    try:
                        # 直接截取驗證碼圖片元素
                        debug_log("截取驗證碼圖片")
                        captcha_img.screenshot("captcha_screenshot.png")
                        
                        # 使用 ddddocr 識別截圖
                        with open("captcha_screenshot.png", "rb") as f:
                            screenshot_data = f.read()
                        
                        captcha_text = ocr.classification(screenshot_data)
                        debug_log(f"驗證碼識別結果: '{captcha_text}'")
                        
                    except Exception as e:
                        debug_log(f"截圖或識別時發生錯誤: {e}")
                        # 嘗試使用 JavaScript 獲取驗證碼圖片
                        try:
                            js_get_captcha = """
                            var img = document.getElementById('TicketForm_verifyCode-image');
                            return img ? img.src : '';
                            """
                            captcha_src = driver.execute_script(js_get_captcha)
                            if captcha_src:
                                debug_log(f"使用JavaScript獲取驗證碼圖片URL")
                                img_url = urljoin(driver.current_url, captcha_src)
                                response = requests.get(img_url, timeout=5)
                                if response.status_code == 200:
                                    js_img_data = response.content
                                    captcha_text = ocr.classification(js_img_data)
                                    debug_log(f"JavaScript獲取圖片識別結果: '{captcha_text}'")
                        except Exception as js_error:
                            debug_log(f"使用JavaScript獲取驗證碼時發生錯誤: {js_error}")
                
                # 檢查是否為空或已嘗試過
                if not captcha_text or (captcha_text in previous_answers and retry_count > 0):
                    debug_log(f"驗證碼為空或已嘗試過，等待下一次嘗試")
                    retry_count += 1
                    continue
                
                # 記錄已嘗試過的答案
                previous_answers.add(captcha_text)
                
                # 輸入驗證碼
                js_input_captcha = f"""
                var input = document.querySelector('#TicketForm_verifyCode');
                if (input) {{
                    input.value = '{captcha_text}';
                    input.dispatchEvent(new Event('input'));
                    return true;
                }}
                return false;
                """
                if driver.execute_script(js_input_captcha):
                    debug_log(f"已輸入驗證碼: '{captcha_text}'")
                    #input(f"驗證碼已輸入，值為 '{captcha_text}'。請檢查頁面並按 Enter 繼續...")
                else:
                    debug_log("找不到驗證碼輸入欄位")
                    #input("找不到驗證碼輸入欄位。請檢查頁面並按 Enter 繼續...")

                # 點擊確認按鈕
                js_click_confirm = """
                var confirmBtn = document.querySelector('button[type="submit"].btn-primary');
                if (confirmBtn) {
                    confirmBtn.click();
                    return true;
                }
                return false;
                """
                ##input("按Enter繼續...")
                if driver.execute_script(js_click_confirm):
                    debug_log("已點擊確認張數按鈕")
                    
                    # 等待看看是否成功
                    time.sleep(CONFIG['wait_times']['after_submit'])
                    
                    #input("按Enter繼續...")

                    # 檢查是否有警告框(Alert)
                    try:
                        # 嘗試獲取警告框文本
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        debug_log(f"檢測到警告框: {alert_text}", force=True)
                        
                        # 如果警告框包含驗證碼錯誤的訊息
                        if "驗證碼不正確" in alert_text or "請重新輸入" in alert_text:
                            debug_log("驗證碼錯誤，將接受警告並重試", force=True)
                            alert.accept()  # 點擊確定按鈕關閉警告框
                            # 移除 reload_captcha() 的調用，因為系統會自動刷新驗證碼
                            retry_count += 1
                            continue
                        else:
                            # 其他類型的警告，接受並繼續
                            alert.accept()
                    except:
                        # 沒有警告框，繼續檢查是否成功
                        # 檢查是否跳轉到"即將前往結帳"頁面
                        try:
                            # 檢查頁面是否包含"即將前往結帳"或"請勿進行任何操作"的文字
                            checkout_text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '即將前往結帳') or contains(text(), '請勿進行任何操作')]")
                            
                            if checkout_text_elements:
                                debug_log("檢測到'即將前往結帳'頁面，訂票已完成", force=True)
                                # 保存成功頁面的截圖
                                try:
                                    debug_screenshot(driver, "checkout_redirect_success")
                                except Exception as e:
                                    debug_log(f"保存結帳頁面截圖失敗: {e}")
                                return True
                        except Exception as e:
                            debug_log(f"檢查結帳頁面時發生錯誤: {e}")
                        debug_log("沒有檢測到警告框")
                    
                    try:
                        debug_screenshot(driver, f"after_submit_{retry_count}")
                    except Exception as e:
                        debug_log(f"保存截圖失敗，可能是因為警告框: {e}")
                    
                    # 檢查是否已經進入下一頁或有成功指標
                    js_check_success = """
                    // 檢查URL
                    var isSuccessUrl = window.location.href.includes('ticket/check') || 
                                      window.location.href.includes('ticket/result') ||
                                      window.location.href.includes('ticket/payment');
                    
                    // 檢查頁面內容
                    var pageText = document.body.innerText;
                    var hasSuccessIndicators = pageText.includes('購票確認') || 
                                              pageText.includes('訂單編號') || 
                                              pageText.includes('付款方式') ||
                                              pageText.includes('購買會員聯絡資訊') ||
                                              (pageText.includes('請於') && pageText.includes('秒內完成資料填寫'));
                    
                    // 檢查是否有進度條並且已經到達第三步或更後面
                    var progressSteps = document.querySelectorAll('.progress-step');
                    var progressSuccess = false;
                    if (progressSteps.length > 0) {
                        for (var i = 2; i < progressSteps.length; i++) {
                            if (progressSteps[i].classList.contains('active')) {
                                progressSuccess = true;
                                break;
                            }
                        }
                    }
                    
                    // 檢查是否仍在驗證碼或選票數量頁面
                    var isOnVerificationPage = window.location.href.includes('ticket/verify') || 
                                               pageText.includes('驗證碼') || 
                                               pageText.includes('選擇票數');
                    
                    return {
                        isSuccessUrl: isSuccessUrl,
                        hasSuccessIndicators: hasSuccessIndicators,
                        progressSuccess: progressSuccess,
                        isOnVerificationPage: isOnVerificationPage,
                        currentUrl: window.location.href
                    };
                    """
                    try:
                        result = driver.execute_script(js_check_success)
                        debug_log(f"成功檢查結果: {result}")
                        
                        if result['isOnVerificationPage']:
                            debug_log("檢查錯誤：仍在驗證碼頁面")
                            retry_count += 1
                            continue
                        else:
                            if result['isSuccessUrl'] and result['hasSuccessIndicators'] and result['progressSuccess']:
                                debug_log("驗證成功，已進入下一步")
                                return True
                            else:
                                debug_log("檢查錯誤：未達到成功條件")
                                retry_count += 1
                                continue
                    except Exception as e:
                        debug_log(f"檢查成功指標時發生錯誤: {e}")
                else:
                    debug_log("找不到確認按鈕")
                
                debug_log(f"重試驗證碼 ({retry_count + 1}/{CONFIG['ticket_config']['retry']['max_attempts']})")
                retry_count += 1
                time.sleep(CONFIG['ticket_config']['retry']['delay'])
                
            except Exception as e:
                debug_log(f"EXCEPT: 處理驗證碼時發生錯誤: {e}")
                
                # 檢查是否有警告框(Alert)，這可能是在其他地方發生的錯誤
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    debug_log(f"檢測到警告框: {alert_text}", force=True)
                    alert.accept()  # 點擊確定按鈕關閉警告框
                except:
                    pass
                
                retry_count += 1
                time.sleep(CONFIG['ticket_config']['retry']['delay'])
        
        debug_log("驗證碼處理失敗，已達最大重試次數")
        return False
        
    except Exception as e:
        debug_log(f"EXCEPT: 選擇票數和驗證碼時發生錯誤: {e}", force=True)
        
        # 檢查是否有警告框(Alert)，這可能是在其他地方發生的錯誤
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            debug_log(f"檢測到警告框: {alert_text}", force=True)
            alert.accept()  # 點擊確定按鈕關閉警告框
        except:
            pass
            
        # 在異常處理中添加明確的失敗日誌
        debug_log("因異常返回 False", force=True)
        return False

# 定義一個通用的重新載入驗證碼函數
def reload_captcha():
    try:
        captcha_img = driver.find_element(By.ID, "TicketForm_verifyCode-image")
        # 記錄當前驗證碼圖片的 src 和 naturalWidth
        js_get_img_info = """
        var img = document.getElementById('TicketForm_verifyCode-image');
        return {
            src: img.src,
            width: img.naturalWidth,
            complete: img.complete
        };
        """
        old_info = driver.execute_script(js_get_img_info)
        
        # 點擊重新載入
        captcha_img.click()
        debug_log("已點擊驗證碼圖片重新載入")
        
        # 等待直到圖片真的改變且載入完成或超時
        max_wait = CONFIG['wait_times']['captcha_update']
        start_time = time.time()
        while time.time() - start_time < max_wait:
            current_info = driver.execute_script(js_get_img_info)
            
            # 檢查圖片是否已更新且完全載入
            if (current_info['src'] != old_info['src'] and 
                current_info['complete'] and 
                current_info['width'] > 0):
                debug_log("驗證碼圖片已成功更新且載入完成")
                time.sleep(0.1)  # 額外小等一下以確保渲染完成
                return True
            time.sleep(0.1)
        
        debug_log("等待驗證碼更新超時", force=True)
        return False
    except:
        debug_log("EXCEPT: 重新載入驗證碼失敗")
        return False

def handle_card_auth(driver):
    """智慧檢測並處理卡號認證頁面"""
    if not CONFIG['concert']['card_auth']['enabled']:
        return True  # 如果未啟用卡號認證，直接返回成功
    
    try:
        debug_log("開始檢測卡號認證頁面", driver)
        
        # 獲取頁面 HTML 源碼
        page_source = driver.page_source.lower()
        
        # 檢測卡號相關關鍵字 (更全面的關鍵字列表)
        card_keywords = [
            # 中文關鍵字
            '卡號', '信用卡', '預售', '認證', 'visa', 'mastercard', 'master card', 
            'american express', 'amex', 'jcb', 'discover', 'diners',
            # 英文關鍵字
            'card number', 'credit card', 'presale', 'verification',
            'cardholder', 'card holder', 'payment card',
            # 卡號格式關鍵字 (常見的卡號前綴)
            '4[0-9]', '5[0-9]', '3[0-9]', '6[0-9]',  # Visa, Master, Amex, Discover 等
            # 其他可能的關鍵字
            'infinite', 'world', 'platinum', 'gold', 'classic',
            '請輸入', '請填入', 'please enter', 'enter your'
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
            debug_log(f"檢測到卡號認證頁面 (關鍵字: {detected_keyword})...", driver)
            
            # 智慧尋找卡號輸入框
            card_input = None
            
            # 擴展的輸入框選擇器列表
            input_selectors = [
                # 通過 name 屬性查找
                "input[name*='card']",
                "input[name*='number']",
                "input[name*='num']",
                "input[name*='verification']",
                "input[name*='verify']",
                "input[name*='presale']",
                
                # 通過 id 屬性查找
                "input[id*='card']",
                "input[id*='number']",
                "input[id*='num']",
                "input[id*='verification']",
                "input[id*='verify']",
                "input[id*='presale']",
                
                # 通過 placeholder 屬性查找
                "input[placeholder*='卡號']",
                "input[placeholder*='card']",
                "input[placeholder*='number']",
                "input[placeholder*='請輸入']",
                "input[placeholder*='enter']",
                
                # 通過 class 屬性查找
                "input[class*='card']",
                "input[class*='number']",
                "input[class*='verify']",
                
                # 通用輸入框類型
                "input[type='text']",
                "input[type='password']",
                "input[type='tel']",
                "input[type='number']",
                
                # 最後兜底：所有 input
                "input"
            ]
            
            # 逐個嘗試選擇器
            for selector in input_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                # 過濾出可能的卡號輸入框
                for element in elements:
                    try:
                        # 檢查元素是否可見且可編輯
                        if element.is_displayed() and element.is_enabled():
                            # 獲取元素的各種屬性
                            name_attr = element.get_attribute('name') or ''
                            id_attr = element.get_attribute('id') or ''
                            placeholder_attr = element.get_attribute('placeholder') or ''
                            class_attr = element.get_attribute('class') or ''
                            
                            # 組合所有屬性進行檢查
                            all_attrs = (name_attr + ' ' + id_attr + ' ' + placeholder_attr + ' ' + class_attr).lower()
                            
                            # 檢查是否包含卡號相關屬性
                            card_related_attrs = ['card', 'number', 'num', 'verification', 'verify', 'presale', '卡號']
                            
                            if any(attr in all_attrs for attr in card_related_attrs):
                                card_input = element
                                debug_log(f"找到卡號輸入框 (選擇器: {selector})", driver)
                                break
                            
                            # 如果沒找到明確的卡號輸入框，但只有一個文本輸入框，也可能是卡號輸入框
                            if not card_input and element.get_attribute('type') in ['text', 'tel', 'number']:
                                card_input = element
                                debug_log(f"使用可能的卡號輸入框 (選擇器: {selector})", driver)
                    
                    except Exception:
                        continue
                
                if card_input:
                    break
            
            if card_input:
                # 輸入卡號
                card_number = CONFIG['concert']['card_auth']['card_number']
                card_input.clear()
                card_input.send_keys(card_number)
                debug_log(f"已輸入卡號: {card_number}", driver)
                
                # 智慧尋找提交按鈕
                submit_button = None
                
                # 擴展的按鈕選擇器列表
                button_selectors = [
                    # 標準提交按鈕
                    "button[type='submit']",
                    "input[type='submit']",
                    
                    # 通過 class 查找
                    "button.btn",
                    "input.btn",
                    "button[class*='submit']",
                    "button[class*='confirm']",
                    "button[class*='verify']",
                    
                    # 通過 id 查找
                    "button[id*='submit']",
                    "button[id*='confirm']",
                    "button[id*='verify']",
                    "input[id*='submit']",
                    "input[id*='confirm']",
                    
                    # 任何按鈕
                    "button",
                    "input[type='button']"
                ]
                
                # XPath 選擇器 (通過文字內容)
                xpath_selectors = [
                    "//button[contains(text(), '送出')]",
                    "//button[contains(text(), '確認')]",
                    "//button[contains(text(), '提交')]",
                    "//button[contains(text(), '驗證')]",
                    "//button[contains(text(), '認證')]",
                    "//button[contains(text(), 'submit')]",
                    "//button[contains(text(), 'confirm')]",
                    "//button[contains(text(), 'verify')]",
                    "//input[@value='送出']",
                    "//input[@value='確認']",
                    "//input[@value='提交']",
                    "//input[@value='驗證']",
                    "//input[@value='認證']",
                    "//input[@value='submit']",
                    "//input[@value='confirm']",
                    "//input[@value='verify']"
                ]
                
                # 先嘗試 CSS 選擇器
                for selector in button_selectors:
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
                
                # 如果 CSS 選擇器找不到，嘗試 XPath
                if not submit_button:
                    for selector in xpath_selectors:
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
                
                if submit_button:
                    submit_button.click()
                    debug_log("已提交卡號認證資訊", driver)
                    time.sleep(2)  # 等待頁面跳轉
                    return True
                else:
                    debug_log("找不到提交按鈕，可能需要手動提交", driver)
                    # 即使找不到提交按鈕，也返回 True，因為卡號已經填入了
                    return True
            else:
                debug_log("找不到卡號輸入框，可能需要手動輸入", driver)
                return True  # 返回 True 繼續流程，可能頁面已經處理好了
        else:
            # 沒有檢測到卡號認證頁面，直接返回成功
            debug_log("未檢測到卡號認證頁面", driver)
            return True
            
    except Exception as e:
        debug_log(f"處理卡號認證時發生錯誤: {str(e)}", driver)
        return True  # 發生錯誤時也返回 True，不中斷流程

if __name__ == "__main__":
    driver = None
    try:
        print("=== 拓元自動訂票程式 ===")
        print(f"調試模式: {'啟用' if CONFIG['debug']['enabled'] else '停用'}")
        if CONFIG['debug']['enabled'] and CONFIG['debug']['force_captcha_error']:
            print(f"注意: 第一次驗證碼將故意輸入錯誤值 '{CONFIG['debug']['first_captcha_value']}'")
        
        # 新增：顯示卡號認證設定
        if CONFIG['concert']['card_auth']['enabled']:
            print(f"卡號認證: 啟用")
        else:
            print(f"卡號認證: 停用")
        
        driver = setup_chrome()
        
        # 訪問拓元網站
        print("正在訪問拓元網站...")
        driver.get(CONFIG['website']['base_url'])
        time.sleep(CONFIG['wait_times']['after_page_load'])
        
        # 檢查登入狀態
        if check_login_status(driver):
            print("已經登入！")
        else:
            print("請手動登入")
            input("登入完成後請按Enter繼續...")
        
        # 自動刷新循環 - 無限次嘗試
        attempt_count = 10
        
        # 使用無限循環，不設置上限 // 為了等開票
        while True:
            attempt_count += 1
            print(f"嘗試 #{attempt_count}")
            
            # 新增：處理卡號認證 (在點擊購票按鈕之前或之後都可以)
            if not handle_card_auth(driver):
                print("卡號認證處理失敗，繼續嘗試...")
                time.sleep(0.5)
                continue
            
            # 步驟1: 點擊立即購票
            click_result = click_buy_ticket(driver)
            if not click_result:
                print("點擊購票按鈕失敗")
                time.sleep(0.5)
                continue
            
            # 再次嘗試處理卡號認證 (有些網站在點擊購票後才出現認證頁面)
            if not handle_card_auth(driver):
                print("點擊購票後卡號認證處理失敗，繼續嘗試...")
                time.sleep(0.5)
                continue
            
            # 步驟2: 選擇場次 - 傳入 attempt_count
            select_time_result = select_show_time(driver, attempt_count)
            
            # 檢查選擇場次的結果
            if not select_time_result.get("success", False):
                reason = select_time_result.get("reason", "unknown")
                print(f"選擇場次失敗，原因: {reason}，將重新點擊立即購票")
                time.sleep(0.5)
                continue
            
            # 只有在選擇場次成功時，才繼續選擇票價
            print("成功選擇場次")
            
            # 步驟3: 選擇票價與座位
            if select_ticket_area(driver):
                print("成功進入票價選擇頁面")
                
                # 步驟4: 選擇票數並處理驗證碼
                if select_ticket_number_and_verify(driver):
                    print("成功選擇票數並處理驗證碼")
                    print("恭喜！訂票流程已完成")
                    # 成功完成，但不退出循環，讓用戶決定是否繼續
                    user_input = input("訂票已完成。是否繼續嘗試？(y/n): ")
                    if user_input.lower() != 'y':
                        break
                else:
                    user_input = input("選擇票數並處理驗證碼失敗, 訂票應該已完成。是否繼續嘗試？(y/n): ")
                    if user_input.lower() != 'y':
                        break
            else:
                print("選擇票價與座位失敗，將重新執行整個流程")
                time.sleep(0.5)
                continue  # 繼續下一輪迴圈，即回到步驟1
        
        print(f"程序已完成，共嘗試 {attempt_count} 次")
        input("請按Enter結束程式...")
        
    except Exception as e:
        print(f"EXCEPT: 發生錯誤: {e}")
        # 即使發生未預期的錯誤，也嘗試捕獲並繼續
        try:
            print("嘗試恢復並繼續...")
            driver.get(CONFIG['website']['base_url'])
            time.sleep(CONFIG['wait_times']['after_page_load'])
            # 這裡可以添加更多恢復邏輯
        except:
            print("EXCEPT: 無法恢復，程序將終止")
    finally:
        if driver:
            print("關閉瀏覽器...")
            try:
                driver.quit()
            except:
                pass