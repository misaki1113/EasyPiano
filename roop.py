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

# 押されているキーを管理するセット
pressed_keys = set()

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
    global pressed_keys
    min_volume = 0.2  # 最小音量
    max_volume = 0.8  # 最大音量

    while True:
        for key in pressed_keys:
            dist = get_distance()
            # 音量を計算して制限
            volume = max(min_volume, min(max_volume, 1 - dist / 50))
            sounds[key].set_volume(volume)
            print(f"Distance: {dist:.2f} cm, Volume: {volume:.2f}")
        time.sleep(0.1)

# === キーボードのキー押下時の処理 ===
def on_press(key):
    try:
        if key.char in sounds and key.char not in pressed_keys:
            pressed_keys.add(key.char)
            sounds[key.char].play(loops=-1)  # 音をループ再生
            print(f"Playing sound for key: {key.char}")
    except AttributeError:
        pass

# === キーボードのキー離した時の処理 ===
def on_release(key):
    try:
        if key.char in sounds and key.char in pressed_keys:
            pressed_keys.remove(key.char)
            sounds[key.char].stop()  # 音を停止
            print(f"Stopped sound for key: {key.char}")
    except AttributeError:
        pass

# === メイン処理 ===
try:
    # 音量調整スレッドを開始
    import threading
    volume_thread = threading.Thread(target=adjust_volume, daemon=True)
    volume_thread.start()

    # キーボードリスナーを開始
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

except KeyboardInterrupt:
    print("\n終了します...")
finally:
    GPIO.cleanup()
