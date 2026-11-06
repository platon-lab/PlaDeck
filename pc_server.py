"""PlaDeck PC-сервер. Установка: pip install pyautogui pyperclip
Запуск: python pc_server.py"""
import json
import socket
import subprocess
import sys
import threading
import webbrowser

import pyautogui
import pyperclip

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
PORT = 5151


def run(msg):
    t = msg.get("t")
    if t == "move":
        pyautogui.moveRel(msg["dx"], msg["dy"])
    elif t == "scroll":
        pyautogui.scroll(msg["dy"])
    elif t == "click":
        pyautogui.click(button=msg.get("btn", "left"), clicks=msg.get("count", 1), interval=0.05)
    elif t == "hotkey":
        pyautogui.hotkey(*msg["keys"].split("+"))
    elif t == "text":
        pyperclip.copy(msg["text"])
        pyautogui.hotkey("ctrl", "v")
    elif t == "app":
        if sys.platform.startswith("win"):
            import os
            os.startfile(msg["cmd"])
        else:
            subprocess.Popen(msg["cmd"], shell=True)
    elif t == "url":
        webbrowser.open(msg["url"])


def client(conn, addr):
    print("Подключено:", addr)
    buf = b""
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                if not line.strip():
                    continue
                try:
                    run(json.loads(line))
                except Exception as e:
                    print("Ошибка команды:", e)
    print("Отключено:", addr)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(1)
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except OSError:
        ip = "?"
    print(f"PlaDeck слушает порт {PORT}. IP этого ПК: {ip}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
