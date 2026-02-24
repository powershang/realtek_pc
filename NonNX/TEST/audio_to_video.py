import os
import re
import time
import argparse
from datetime import datetime
from google.cloud import speech_v1p1beta1 as speech
from google.api_core.exceptions import GoogleAPIError
import google.generativeai as genai
from moviepy.editor import AudioFileClip, ImageClip, TextClip, CompositeVideoClip
import pysrt
from pydub import AudioSegment
import numpy as np
from PIL import Image

# 配置環境變數和API密鑰
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/google-credentials.json"
GEMINI_API_KEY = "your_gemini_api_key"
genai.configure(api_key=GEMINI_API_KEY)

def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='將音檔轉為帶翻譯字幕的影片')
    parser.add_argument('audio_file', type=str, help='音檔路徑')
    parser.add_argument('--source_language', type=str, default='zh-TW', help='源語言代碼')
    parser.add_argument('--target_language', type=str, default='en', help='目標語言代碼')
    parser.add_argument('--background_image', type=str, default=None, help='背景圖片路徑')
    parser.add_argument('--output_dir', type=str, default='output', help='輸出目錄')
    parser.add_argument('--title', type=str, default='', help='影片標題')
    return parser.parse_args()

def prepare_audio(audio_file):
    """預處理音頻文件，確保格式正確"""
    print(f"預處理音頻: {audio_file}")
    # 載入音頻
    audio = AudioSegment.from_file(audio_file)
    
    # 轉換為單聲道，採樣率為16kHz（Google Speech API的推薦設置）
    audio = audio.set_channels(1).set_frame_rate(16000)
    
    # 保存為臨時WAV文件
    temp_file = "temp_audio.wav"
    audio.export(temp_file, format="wav")
    
    return temp_file

def transcribe_audio(audio_file, language_code='zh-TW'):
    """使用Google Speech-to-Text API轉錄音頻"""
    print(f"開始將音頻轉錄為文字，語言: {language_code}")
    client = speech.SpeechClient()
    
    # 讀取音頻文件
    with open(audio_file, "rb") as audio_file:
        content = audio_file.read()
    
    # 配置音頻
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=True,
        enable_speaker_diarization=True,
        diarization_speaker_count=2,  # 假設有兩個發言者
        model="latest_long",  # 使用長音頻模型
    )
    
    # 發送請求
    try:
        operation = client.long_running_recognize(config=config, audio=audio)
        print("轉錄處理中...")
        response = operation.result(timeout=900)  # 最多等待15分鐘
        
        # 處理結果
        transcript_with_timestamps = []
        for result in response.results:
            for i, alternative in enumerate(result.alternatives):
                if i == 0:  # 只取最可能的轉錄結果
                    for word_info in alternative.words:
                        start_time = word_info.start_time.total_seconds()
                        end_time = word_info.end_time.total_seconds()
                        word = word_info.word
                        speaker_tag = word_info.speaker_tag
                        transcript_with_timestamps.append({
                            'text': word,
                            'start_time': start_time,
                            'end_time': end_time,
                            'speaker': f'Speaker {speaker_tag}'
                        })
        
        return transcript_with_timestamps
    except GoogleAPIError as e:
        print(f"Google API錯誤: {e}")
        return []
    except Exception as e:
        print(f"轉錄過程中發生錯誤: {e}")
        return []

def group_transcription_by_speaker_and_sentence(transcript_words, pause_threshold=1.0):
    """將詞彙分組為完整的句子，並按照發言者分組"""
    if not transcript_words:
        return []
    
    sentences = []
    current_sentence = {
        'text': transcript_words[0]['text'],
        'start_time': transcript_words[0]['start_time'],
        'end_time': transcript_words[0]['end_time'],
        'speaker': transcript_words[0]['speaker']
    }
    
    for i in range(1, len(transcript_words)):
        word = transcript_words[i]
        prev_word = transcript_words[i-1]
        
        # 檢查是否為同一個發言者，或者詞與詞之間的時間間隔是否超過閾值
        if (word['speaker'] != prev_word['speaker'] or 
            word['start_time'] - prev_word['end_time'] > pause_threshold):
            # 結束當前句子
            sentences.append(current_sentence)
            # 開始新句子
            current_sentence = {
                'text': word['text'],
                'start_time': word['start_time'],
                'end_time': word['end_time'],
                'speaker': word['speaker']
            }
        else:
            # 繼續當前句子
            current_sentence['text'] += ' ' + word['text']
            current_sentence['end_time'] = word['end_time']
    
    # 添加最後一個句子
    if current_sentence:
        sentences.append(current_sentence)
    
    print(f"共分析出{len(sentences)}個句子")
    return sentences

def translate_sentences(sentences, source_lang='zh-TW', target_lang='en'):
    """使用Gemini API翻譯句子"""
    print(f"開始翻譯，從{source_lang}翻譯到{target_lang}")
    
    # 準備批量翻譯
    texts_to_translate = [sentence['text'] for sentence in sentences]
    translations = []
    
    # 使用Gemini模型
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )
    
    # 批量處理，每次處理10個句子
    batch_size = 10
    for i in range(0, len(texts_to_translate), batch_size):
        batch = texts_to_translate[i:i+batch_size]
        
        # 構建提示
        prompt = f"""請將以下{source_lang}句子翻譯成{target_lang}，保持原意並使翻譯自然流暢。
只需返回翻譯結果，保持原句子的順序，每行一個翻譯結果。
不要添加任何解釋、標記或編號。

原文:
"""
        for text in batch:
            prompt += f"{text}\n"
        
        try:
            response = model.generate_content(prompt)
            # 處理回應
            if response.text:
                # 分割並清理響應文本
                translated_batch = response.text.strip().split('\n')
                # 確保翻譯結果與輸入數量匹配
                if len(translated_batch) == len(batch):
                    translations.extend(translated_batch)
                else:
                    # 如果數量不匹配，逐個翻譯
                    for text in batch:
                        single_prompt = f"請將以下{source_lang}句子翻譯成{target_lang}，只返回翻譯結果：\n{text}"
                        single_response = model.generate_content(single_prompt)
                        if single_response.text:
                            translations.append(single_response.text.strip())
                        else:
                            translations.append(text)  # 如果翻譯失敗，使用原文
            else:
                # 翻譯失敗，使用原文
                translations.extend(batch)
        except Exception as e:
            print(f"翻譯時發生錯誤: {e}")
            # 翻譯失敗，使用原文
            translations.extend(batch)
        
        # 避免API限流
        time.sleep(1)
    
    # 將翻譯結果添加到原始句子數據中
    for i, sentence in enumerate(sentences):
        sentence['translation'] = translations[i] if i < len(translations) else sentence['text']
    
    return sentences

def create_srt_file(sentences, output_file):
    """創建SRT字幕文件"""
    print(f"創建SRT字幕文件: {output_file}")
    subs = pysrt.SubRipFile()
    
    for i, sentence in enumerate(sentences):
        start_time = sentence['start_time']
        end_time = sentence['end_time']
        
        # 確保字幕顯示時間足夠
        min_duration = 1.0  # 最小1秒
        if end_time - start_time < min_duration:
            end_time = start_time + min_duration
        
        # 創建字幕項
        sub = pysrt.SubRipItem(
            index=i+1,
            start=pysrt.SubRipTime(seconds=start_time),
            end=pysrt.SubRipTime(seconds=end_time),
            text=f"{sentence['speaker']}: {sentence['text']}\n{sentence['translation']}"
        )
        subs.append(sub)
    
    # 保存SRT文件
    subs.save(output_file, encoding='utf-8')
    return output_file

def create_background(width=1920, height=1080, color=(240, 240, 240), title=None, output_path="background.jpg"):
    """創建背景圖片"""
    print("創建背景圖片")
    img = Image.new('RGB', (width, height), color)
    
    # 如果有標題則添加到圖片上
    if title:
        from PIL import ImageDraw, ImageFont
        try:
            # 嘗試加載字體
            font = ImageFont.truetype("arial.ttf", 60)
        except IOError:
            # 如果找不到指定字體，使用默認字體
            font = ImageFont.load_default()
        
        draw = ImageDraw.Draw(img)
        # 計算文本寬度以實現居中
        text_width = draw.textlength(title, font=font)
        position = ((width - text_width) / 2, 100)
        draw.text(position, title, fill=(0, 0, 0), font=font)
    
    img.save(output_path)
    return output_path

def create_video(audio_file, srt_file, background_image, output_file, fps=30, width=1920, height=1080):
    """創建帶字幕的視頻"""
    print(f"開始創建視頻: {output_file}")
    
    # 加載音頻
    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration
    
    # 背景圖片
    background_clip = ImageClip(background_image).set_duration(duration)
    
    # 加載字幕
    subs = pysrt.open(srt_file)
    subtitle_clips = []
    
    for sub in subs:
        start_time = sub.start.ordinal / 1000.0
        end_time = sub.end.ordinal / 1000.0
        
        # 將字幕文本分為兩行
        text_parts = sub.text.split('\n')
        
        # 如果存在兩行則分別處理
        if len(text_parts) >= 2:
            # 原文與發言者
            origin_text = text_parts[0]
            text_clip1 = TextClip(origin_text, fontsize=36, color='white', bg_color='black',
                                  size=(width*0.9, None), method='caption').set_position(('center', height*0.6))
            text_clip1 = text_clip1.set_start(start_time).set_end(end_time)
            
            # 翻譯文本
            trans_text = text_parts[1]
            text_clip2 = TextClip(trans_text, fontsize=36, color='yellow', bg_color='black',
                                  size=(width*0.9, None), method='caption').set_position(('center', height*0.7))
            text_clip2 = text_clip2.set_start(start_time).set_end(end_time)
            
            subtitle_clips.extend([text_clip1, text_clip2])
        else:
            # 只有一行
            text_clip = TextClip(sub.text, fontsize=36, color='white', bg_color='black',
                                 size=(width*0.9, None), method='caption').set_position(('center', height*0.65))
            text_clip = text_clip.set_start(start_time).set_end(end_time)
            subtitle_clips.append(text_clip)
    
    # 合成視頻
    video = CompositeVideoClip([background_clip] + subtitle_clips)
    
    # 添加音頻
    video = video.set_audio(audio_clip)
    
    # 輸出視頻
    video.write_videofile(output_file, fps=fps, codec="libx264", audio_codec="aac")
    
    return output_file

def main():
    args = parse_arguments()
    
    # 創建輸出目錄
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # 生成輸出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.splitext(os.path.basename(args.audio_file))[0]
    output_base = f"{args.output_dir}/{base_filename}_{timestamp}"
    
    # 預處理音頻
    processed_audio = prepare_audio(args.audio_file)
    
    # 語音識別
    transcript = transcribe_audio(processed_audio, args.source_language)
    
    # 按發言者和句子分組
    sentences = group_transcription_by_speaker_and_sentence(transcript)
    
    # 翻譯
    translated_sentences = translate_sentences(sentences, args.source_language, args.target_language)
    
    # 創建SRT文件
    srt_file = create_srt_file(translated_sentences, f"{output_base}.srt")
    
    # 創建或使用背景圖片
    if args.background_image and os.path.exists(args.background_image):
        background_image = args.background_image
    else:
        background_image = create_background(title=args.title, output_path=f"{output_base}_bg.jpg")
    
    # 創建視頻
    output_video = f"{output_base}.mp4"
    create_video(args.audio_file, srt_file, background_image, output_video)
    
    # 清理臨時文件
    if os.path.exists("temp_audio.wav"):
        os.remove("temp_audio.wav")
    
    print(f"處理完成！輸出文件: {output_video}")

if __name__ == "__main__":
    main()