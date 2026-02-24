import sys
import os
import psutil
import wave
import pyaudio
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QComboBox, 
                            QListWidget, QFileDialog, QMessageBox, QToolButton, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import win32gui
import win32process
import pyautogui
import re
import tempfile
import shutil

# 測試 FFmpeg 是否能正常工作
def test_ffmpeg(ffmpeg_path):
    try:
        import subprocess
        result = subprocess.run([ffmpeg_path, "-version"], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode == 0:
            print(f"FFmpeg 版本信息: {result.stdout.splitlines()[0]}")
            return True
        else:
            print(f"FFmpeg 執行錯誤: {result.stderr}")
            return False
    except Exception as e:
        print(f"測試 FFmpeg 時發生錯誤: {e}")
        return False

# 在導入 pydub 之前先設定環境變量
ffmpeg_dir = r"D:\python_work\ffmpeg-2025-04-23-git-25b0a8e295-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_dir

# 確保 ffmpeg (無副檔名) 也存在
ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
ffmpeg_no_ext = os.path.join(ffmpeg_dir, "ffmpeg")
ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")
ffprobe_no_ext = os.path.join(ffmpeg_dir, "ffprobe")

# 如果 ffmpeg.exe 存在但 ffmpeg 不存在，複製一個不帶副檔名的版本
if os.path.exists(ffmpeg_exe) and not os.path.exists(ffmpeg_no_ext):
    try:
        shutil.copy2(ffmpeg_exe, ffmpeg_no_ext)
        print(f"已複製 ffmpeg.exe 到 ffmpeg")
    except Exception as e:
        print(f"複製 ffmpeg 檔案時出錯: {e}")

if os.path.exists(ffprobe_exe) and not os.path.exists(ffprobe_no_ext):
    try:
        shutil.copy2(ffprobe_exe, ffprobe_no_ext)
        print(f"已複製 ffprobe.exe 到 ffprobe")
    except Exception as e:
        print(f"複製 ffprobe 檔案時出錯: {e}")

from pydub import AudioSegment

# 測試 FFmpeg 是否正常工作
if os.path.exists(ffmpeg_exe) and test_ffmpeg(ffmpeg_exe):
    AudioSegment.converter = ffmpeg_exe
    AudioSegment.ffmpeg = ffmpeg_exe
    AudioSegment.ffprobe = ffprobe_exe
    print(f"已設定 FFmpeg 路徑: {ffmpeg_exe}")
    FFMPEG_AVAILABLE = True
else:
    print(f"警告：FFmpeg 無法正常工作，將使用 WAV 格式。")
    FFMPEG_AVAILABLE = False

class AudioRecorder(QThread):
    update_time = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)  # 新增狀態更新訊號
    
    def __init__(self, filename, target_pid=None, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.target_pid = target_pid
        self.is_recording = False
        self.frames = []  # 用於存儲所有音訊數據
        self.audio_format = pyaudio.paInt16
        self.channels = 1  # 改為單聲道以減少檔案大小
        self.rate = 44100
        self.chunk = 1024
    
    def run(self):
        try:
            self._run_impl()
        except Exception as e:
            import traceback
            error_msg = f"錄音過程發生錯誤: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.error.emit(error_msg)
            self.finished.emit(self.filename)
    
    def _run_impl(self):
        self.is_recording = True
        self.frames = []
        
        p = None
        stream = None
        
        try:
            p = pyaudio.PyAudio()
            
            # 打印所有可用設備的信息
            print("\n可用的音訊設備:")
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                print(f"設備 {i}: {info['name']}")
                print(f"  輸入通道: {info['maxInputChannels']}")
                print(f"  輸出通道: {info['maxOutputChannels']}")
                print(f"  默認採樣率: {info['defaultSampleRate']}")
                print(f"  主機API: {p.get_host_api_info_by_index(info['hostApi'])['name']}")
            
            # 尋找立體混音設備
            target_device_index = None
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    device_name = info['name'].lower()
                    if ('stereo mix' in device_name or 
                        '立體混音' in device_name or 
                        'what u hear' in device_name or
                        'loopback' in device_name or
                        'wave out' in device_name or
                        '擷取' in device_name):
                        target_device_index = i
                        print(f"找到系統聲音錄製設備: {info['name']} (索引: {i})")
                        # 使用設備的建議設定
                        self.channels = min(2, int(info['maxInputChannels']))
                        self.rate = int(info['defaultSampleRate'])
                        break
            
            if target_device_index is None:
                print("未找到立體混音設備，將使用默認麥克風")
                target_device_index = p.get_default_input_device_info()['index']
                
                # 顯示給用戶
                self.error.emit("警告：未找到立體混音設備，無法錄製系統聲音。\n"
                                "將使用麥克風錄音。建議您在聲音設定中啟用「立體混音」。")
            
            print(f"開啟設備 {target_device_index}，設定: 通道={self.channels}, 採樣率={self.rate}")
            
            # 打開音訊流
            stream = p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=target_device_index,
                frames_per_buffer=self.chunk
            )
            
            start_time = time.time()
            last_update = start_time
            
            # 直接將音訊數據存入 self.frames
            print("開始錄製音訊...")
            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # 更新時間（每秒一次）
                    current_time = time.time()
                    if current_time - last_update >= 1.0:
                        elapsed = int(current_time - start_time)
                        self.update_time.emit(elapsed)
                        last_update = current_time
                        print(f"錄製進行中... {elapsed}秒")
                except IOError as e:
                    print(f"讀取音訊數據時發生錯誤: {e}")
                    time.sleep(0.1)
            
            print("錄製停止")
            
        except Exception as e:
            print(f"錄音過程中發生錯誤: {e}")
            raise
        
        finally:
            # 釋放音訊資源
            if stream:
                stream.stop_stream()
                stream.close()
            if p:
                p.terminate()
        
        # 儲存音訊檔案 (直接使用WAV格式)
        if self.frames:
            try:
                # 檢查是否有錄音數據
                if len(self.frames) == 0:
                    raise Exception("沒有錄製到任何音訊數據")
                    
                # 確保有效的保存路徑
                save_dir = os.path.dirname(self.filename)
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                    
                # 保存為WAV
                wav_filename = os.path.splitext(self.filename)[0] + '.wav'
                self.status_update.emit("正在處理音訊數據...")
                
                try:
                    print(f"正在保存WAV文件到: {wav_filename}")
                    wf = wave.open(wav_filename, 'wb')
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(p.get_sample_size(self.audio_format))
                    wf.setframerate(self.rate)
                    
                    # 將錄音數據合併在一起再寫入
                    all_data = b''.join(self.frames)
                    print(f"音訊數據大小: {len(all_data)} bytes")
                    
                    # 逐塊寫入以避免一次性處理太多數據
                    chunk_size = 1024 * 1024  # 1MB chunks
                    for i in range(0, len(all_data), chunk_size):
                        chunk = all_data[i:i+chunk_size]
                        wf.writeframes(chunk)
                        
                    wf.close()
                    print(f"WAV檔案已成功保存")
                    
                    self.filename = wav_filename
                    print(f"檔案已保存為WAV: {wav_filename}")
                
                except Exception as e:
                    print(f"寫入WAV文件時發生錯誤: {e}")
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"無法保存WAV文件: {str(e)}")
                
            except Exception as e:
                print(f"保存檔案時出錯: {e}")
                import traceback
                traceback.print_exc()
                self.error.emit(f"保存錄音時發生錯誤: {str(e)}")
                raise
        else:
            error_msg = "沒有錄製到任何音訊資料，請確認錄音設備正常工作"
            print(error_msg)
            self.error.emit(error_msg)
            raise Exception(error_msg)
        
        self.finished.emit(self.filename)
    
    def stop(self):
        print("停止錄製...")
        self.is_recording = False


class WindowPicker(QToolButton):
    windowPicked = pyqtSignal(int, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("選擇視窗")
        self.setCursor(Qt.ArrowCursor)
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.pickWindow()
    
    def pickWindow(self):
        try:
            import win32gui
            import win32process
            import win32con
            import time
            
            # 設置鼠標形狀為十字
            self.parent().setCursor(Qt.CrossCursor)
            
            # 顯示說明訊息
            QMessageBox.information(self, "選擇視窗", 
                "請將滑鼠移到想錄音的視窗上，然後按下Alt+Tab切換到該視窗。\n\n"
                "之後回到此程式，點擊「確認選擇」按鈕。")
            
            # 創建一個簡單的對話框讓用戶確認選擇
            from PyQt5.QtWidgets import QDialog, QVBoxLayout
            
            dialog = QDialog(self)
            dialog.setWindowTitle("確認視窗選擇")
            layout = QVBoxLayout()
            
            # 顯示當前視窗信息
            info_label = QLabel("正在獲取視窗信息...")
            layout.addWidget(info_label)
            
            confirm_button = QPushButton("確認選擇")
            layout.addWidget(confirm_button)
            
            cancel_button = QPushButton("取消")
            layout.addWidget(cancel_button)
            
            dialog.setLayout(layout)
            
            # 更新函數
            def update_info():
                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                info_label.setText(f"當前選中視窗:\n{window_title}\n(PID: {pid})")
                dialog.pid = pid
                dialog.window_title = window_title
            
            # 定時器更新視窗信息
            update_timer = QTimer()
            update_timer.timeout.connect(update_info)
            update_timer.start(500)  # 每0.5秒更新一次
            
            # 連接按鈕事件
            confirm_button.clicked.connect(lambda: dialog.accept())
            cancel_button.clicked.connect(lambda: dialog.reject())
            
            # 顯示對話框
            result = dialog.exec_()
            update_timer.stop()
            
            # 恢復鼠標形狀
            self.parent().setCursor(Qt.ArrowCursor)
            
            if result == QDialog.Accepted:
                pid = dialog.pid
                window_title = dialog.window_title
                self.windowPicked.emit(pid, window_title)
            
        except Exception as e:
            QMessageBox.warning(self, "錯誤", f"選取視窗失敗: {str(e)}")
            self.parent().setCursor(Qt.ArrowCursor)


class RecordVoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorder = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_process_list)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('系統錄音工具')  # 更改標題
        self.setMinimumSize(500, 400)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 程式選擇區域 - 使其可選但非必要
        process_label = QLabel('可選：為錄音檔命名的程式 (非必選):')  # 修改標籤
        self.process_list = QListWidget()
        self.refresh_button = QPushButton('重新整理')
        self.refresh_button.clicked.connect(self.refresh_process_list)
        
        process_layout = QVBoxLayout()
        process_layout.addWidget(process_label)
        process_layout.addWidget(self.process_list)
        
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_button)
        
        # 添加視窗選擇器 - 同樣是可選的
        self.window_picker = WindowPicker()
        self.window_picker.setText("選擇視窗(可選)")  # 修改按鈕文字
        self.window_picker.windowPicked.connect(self.on_window_picked)
        refresh_layout.addWidget(self.window_picker)
        
        # 檢測是否有可用的系統錄音設備
        self.check_stereo_mix_button = QPushButton('檢測系統錄音設備')
        self.check_stereo_mix_button.clicked.connect(self.check_audio_device)
        process_layout.addWidget(self.check_stereo_mix_button)
        
        # 添加系統錄音說明
        system_audio_label = QLabel(
            "本工具會錄製所有系統聲音，包括所有程式的音訊輸出。\n"
            "如果您想為音訊檔案命名，可以從上方列表選擇一個程式。"
        )
        system_audio_label.setStyleSheet("color: blue;")
        
        process_layout.addLayout(refresh_layout)
        process_layout.addWidget(system_audio_label)  # 添加說明文字
        
        # 添加錄音時長限制選項
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("錄音時長限制:"))
        
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["不限制", "5分鐘", "10分鐘", "30分鐘", "1小時"])
        duration_layout.addWidget(self.duration_combo)
        
        process_layout.addLayout(duration_layout)
        
        # 錄音控制區域
        control_layout = QHBoxLayout()
        
        self.record_button = QPushButton('開始錄音')
        self.record_button.setStyleSheet("font-size: 14px; font-weight: bold;")  # 強調錄音按鈕
        self.record_button.clicked.connect(self.toggle_recording)
        
        self.time_label = QLabel('00:00')
        
        self.save_dir_button = QPushButton('選擇儲存位置')
        self.save_dir_button.clicked.connect(self.select_save_dir)
        
        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.save_dir_button)
        
        # 儲存位置顯示
        self.save_dir = os.path.expanduser('~')
        self.save_dir_label = QLabel(f'儲存位置: {self.save_dir}')
        
        # 顯示 FFmpeg 狀態
        ffmpeg_status = QLabel()
        if FFMPEG_AVAILABLE:
            ffmpeg_status.setText(f"FFmpeg 已就緒: {ffmpeg_exe}")
            ffmpeg_status.setStyleSheet("color: green;")
        else:
            ffmpeg_status.setText("FFmpeg 未找到或無法正常工作，錄音將以 WAV 格式保存")
            ffmpeg_status.setStyleSheet("color: red;")
        
        # 組合所有佈局
        main_layout.addLayout(process_layout)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.save_dir_label)
        main_layout.addWidget(ffmpeg_status)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 初始化程式列表
        self.refresh_process_list()
        # 開始定時刷新程式列表
        self.timer.start(10000)  # 由5秒改為10秒更新一次
        
    def refresh_process_list(self):
        self.process_list.clear()
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 過濾掉沒有視窗界面的程式
                if proc.name() not in ["System", "svchost.exe", "csrss.exe"]:
                    # 僅使用程式名稱和PID，不搜集視窗標題
                    processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        processes.sort()
        self.process_list.addItems(processes)
    
    def select_save_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self, '選擇儲存位置', self.save_dir)
        if dir_name:
            self.save_dir = dir_name
            self.save_dir_label.setText(f'儲存位置: {self.save_dir}')
    
    def toggle_recording(self):
        if self.recorder and self.recorder.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        # 即使不選擇程式也能錄音
        # if not self.process_list.currentItem():
        #     QMessageBox.warning(self, '警告', '請先選擇一個程式')
        #     return
        
        # 使用選擇的程式名稱（如果有）
        process_name = "系統音訊"
        if self.process_list.currentItem():
            selected_process = self.process_list.currentItem().text()
            process_name = selected_process.split(" (PID")[0]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 直接使用WAV格式，避免轉換問題
        filename = os.path.join(self.save_dir, f"{process_name}_{timestamp}.wav")
        
        # 不需要傳遞 target_pid
        self.recorder = AudioRecorder(filename)
        self.recorder.update_time.connect(self.update_time_label)
        self.recorder.finished.connect(self.recording_finished)
        self.recorder.error.connect(self.recording_error)
        self.recorder.status_update.connect(self.update_status)  # 連接狀態更新訊號
        
        # 設置錄音時間限制
        duration_text = self.duration_combo.currentText()
        max_duration = 0  # 0表示不限制
        
        if duration_text == "5分鐘":
            max_duration = 5 * 60
        elif duration_text == "10分鐘":
            max_duration = 10 * 60
        elif duration_text == "30分鐘":
            max_duration = 30 * 60
        elif duration_text == "1小時":
            max_duration = 60 * 60
        
        # 設置定時器自動停止錄音
        if max_duration > 0:
            QTimer.singleShot(max_duration * 1000, self.stop_recording_if_active)
        
        # 開始錄音
        self.recorder.start()
        
        # 更新界面
        self.record_button.setText('停止錄音')
        self.refresh_button.setEnabled(False)
        self.save_dir_button.setEnabled(False)
    
    def stop_recording(self):
        if self.recorder:
            self.record_button.setEnabled(False)
            self.record_button.setText('正在停止...')
            # 先更新UI，然後再停止錄音
            QApplication.processEvents()
            
            self.recorder.stop()
            self.record_button.setText('儲存中...')
    
    def update_time_label(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        self.time_label.setText(f'{minutes:02d}:{seconds:02d}')
    
    def recording_finished(self, filepath):
        self.record_button.setEnabled(True)
        self.record_button.setText('開始錄音')
        self.time_label.setText('00:00')
        self.refresh_button.setEnabled(True)
        self.save_dir_button.setEnabled(True)
        
        # 釋放錄音器佔用的記憶體
        if self.recorder:
            self.recorder.deleteLater()
            self.recorder = None
        
        # 主動要求垃圾回收
        import gc
        gc.collect()
        
        QMessageBox.information(self, '完成', f'錄音已儲存到:\n{filepath}')

    def on_window_picked(self, pid, window_title):
        # 在列表中尋找對應的程序並選取
        for i in range(self.process_list.count()):
            item_text = self.process_list.item(i).text()
            if f"(PID: {pid})" in item_text:
                self.process_list.setCurrentRow(i)
                break
        else:
            QMessageBox.information(self, "資訊", 
                f"已選擇視窗: {window_title} (PID: {pid})\n但在當前列表中未找到對應程序。")

    def recording_error(self, error_msg):
        # 只有在處理狀態訊息時更新按鈕文字，不彈出對話框
        if "正在處理音訊數據" in error_msg or "正在轉換" in error_msg:
            self.record_button.setText(error_msg)
            return
        
        # 警告訊息不需要彈出錯誤對話框，只顯示在按鈕上
        if "警告：" in error_msg:
            self.record_button.setText("注意")
            QMessageBox.warning(self, '注意', error_msg)
            return
            
        # 處理真正的錯誤
        self.record_button.setText("錄音錯誤")
        QMessageBox.critical(self, '錄音錯誤', f"錄音過程中發生錯誤:\n{error_msg}")
        
        # 重置界面
        self.record_button.setEnabled(True)
        self.record_button.setText('開始錄音')
        self.time_label.setText('00:00')
        self.refresh_button.setEnabled(True)
        self.save_dir_button.setEnabled(True)

    def stop_recording_if_active(self):
        if self.recorder and self.recorder.is_recording:
            self.stop_recording()
            QMessageBox.information(self, "自動停止", "已達到預設的錄音時間限制，錄音已自動停止。")

    def check_audio_device(self):
        """檢測系統是否有可用的立體混音設備"""
        p = pyaudio.PyAudio()
        stereo_mix_found = False
        device_name = ""
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                name = info['name'].lower()
                if ('stereo mix' in name or '立體混音' in name or 
                    'what u hear' in name or 'loopback' in name or 
                    'wave out' in name or '擷取' in name):
                    stereo_mix_found = True
                    device_name = info['name']
                    break
        
        p.terminate()
        
        # 檢測 FFmpeg 狀態
        ffmpeg_status = "FFmpeg 已就緒" if FFMPEG_AVAILABLE else "FFmpeg 未找到 (將使用 WAV 格式)"
        
        if stereo_mix_found:
            QMessageBox.information(self, '檢測結果', 
                f"找到系統錄音設備: {device_name}\n"
                f"FFmpeg 狀態: {ffmpeg_status}")
        else:
            QMessageBox.warning(self, '檢測結果', 
                "未找到系統錄音設備。您需要在Windows聲音設定中啟用「立體混音」：\n\n"
                "1. 右鍵點擊工作列的喇叭圖示\n"
                "2. 選擇「聲音」\n"
                "3. 切換到「錄製」標籤\n"
                "4. 右鍵點擊空白處，選擇「顯示已停用的裝置」\n"
                "5. 找到「立體混音」，右鍵啟用\n"
                "6. 如果仍未看到，請確認您的音效卡驅動是否支援此功能\n\n"
                f"FFmpeg 狀態: {ffmpeg_status}")

    def update_status(self, status_msg):
        # 處理狀態更新訊息
        self.record_button.setText(status_msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RecordVoiceApp()
    window.show()
    sys.exit(app.exec_())