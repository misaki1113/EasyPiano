import RPi.GPIO as GPIO
import pygame
import time
from pynput import keyboard

# === 超音波センサーのGPIO設定 ===
TRIG = 15
ECHO = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# === 音声ファイルの設定 ===
pygame.mixer.init()
sounds = {
    's': pygame.mixer.Sound('1.mp3'),   # ド
    'e': pygame.mixer.Sound('2.mp3'),   # ド＃
    'd': pygame.mixer.Sound('3.mp3'),   # レ
    'r': pygame.mixer.Sound('4.mp3'),   # レ＃
    'f': pygame.mixer.Sound('5.mp3'),   # ミ
    'g': pygame.mixer.Sound('6.mp3'),   # ファ
    'y': pygame.mixer.Sound('7.mp3'),   # ファ＃
    'h': pygame.mixer.Sound('8.mp3'),   # ソ
    'u': pygame.mixer.Sound('9.mp3'),   # ソ＃
    'j': pygame.mixer.Sound('10.mp3'),  # ラ
    'i': pygame.mixer.Sound('11.mp3'),  # ラ＃
    'k': pygame.mixer.Sound('12.mp3'),  # シ
    'l': pygame.mixer.Sound('13.mp3')   # ド
}

# 再生中のサウンド
current_sound = None

# === 超音波センサーで距離を測定する関数 ===
def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
    while GPIO.input(ECHO) == 1:
        end_time = time.time()
    
    distance = (end_time - start_time) * 34300 / 2  # 距離を計算 (cm)
    return distance

# === 音量を距離に基づいて調整する関数 ===
def adjust_volume():
    global current_sound
    min_volume = 0.2
    max_volume = 0.8
    while True:
        if current_sound:
            dist = get_distance()
            volume = 1 - dist / 5
            volume = max(min_volume, min(max_volume, volume))
            current_sound.set_volume(volume)
            print(f"Distance: {dist:.2f} cm, Volume: {volume:.2f}")
        time.sleep(0.1)

# === キーボード入力を検知する関数 ===
def on_press(key):
    global current_sound
    try:
        if key.char in sounds:
            if current_sound:
                current_sound.stop()  # 再生中の音を停止
            current_sound = sounds[key.char]
            current_sound.play()
    except AttributeError:
        pass

# === メイン処理 ===
try:
    # 音量調整を別スレッドで実行
    import threading
    volume_thread = threading.Thread(target=adjust_volume, daemon=True)
    volume_thread.start()
    
    # キーボードリスナーの開始
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

except KeyboardInterrupt:
    print("\n終了します...")
finally:
    GPIO.cleanup()

