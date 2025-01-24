import RPi.GPIO as GPIO
import pygame
import time
from pynput import keyboard

# === 超音波センサーのGPIO設定 ===
TRIG = 23
ECHO = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# === 音声ファイルの設定 ===
pygame.mixer.init()
sounds = {
    'a': pygame.mixer.Sound('C4.wav'),  # Aキー: ド
    's': pygame.mixer.Sound('D4.wav'),  # Sキー: レ
    'd': pygame.mixer.Sound('E4.wav')   # Dキー: ミ
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
    while True:
        if current_sound:
            dist = get_distance()
            volume = max(0, min(1, 1 - dist / 50))  # 50cm以内を音量1に正規化
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

