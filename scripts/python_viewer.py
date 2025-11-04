#!/usr/bin/env python3
"""
Simple Tkinter viewer that mimics the Electron viewer behavior without npm.

Features:
- Displays ASCII overlay for configured seconds
- Shows a non-closable window (overrides close button). Window can be killed via Task Manager.
- Accepts a password to unlock early, or closes when the countdown reaches zero.
- Reads configuration from an env file (viewer/.env) via --env or from environment variables.
"""
from __future__ import annotations
import argparse
import os
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import font as tkfont


def load_env(path: Path):
    env = {}
    if path and path.exists():
        for line in path.read_text().splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    # Also overlay with current environment
    for k in ['PASSWORD', 'DURATION', 'ASCII_SECONDS', 'WHITELIST']:
        if k in os.environ:
            env[k] = os.environ[k]
    return env


class ViewerApp:
    def __init__(self, password: str, duration: int, ascii_seconds: int):
        self.password = password or ''
        self.duration = duration
        self.ascii_seconds = ascii_seconds
        self.root = tk.Tk()
        self.root.title('Viewer')
        # Prevent normal close
        self.root.protocol('WM_DELETE_WINDOW', self.on_close_attempt)
        # Fullscreen or sizable window
        self.root.geometry('800x600')

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)

        # ASCII overlay
        self.ascii_label = tk.Label(self.frame, text=self.sample_ascii(), justify='center')
        self.ascii_label.pack(pady=10)
        # Password entry
        self.pw_var = tk.StringVar()
        tk.Label(self.frame, text='Enter password to unlock:').pack()
        tk.Entry(self.frame, textvariable=self.pw_var, show='*').pack()
        tk.Button(self.frame, text='Unlock', command=self.try_unlock).pack(pady=8)

        self.timer_label = tk.Label(self.frame, text='')
        self.timer_label.pack(pady=8)

        self.unlocked = False

    def sample_ascii(self):
        return r"""
   ____  _   _ ____  _   _ _____ ____ 
  / ___|| | | |  _ \| | | | ____|  _ \
 | |  _ | | | | |_) | | | |  _| | |_) |
 | |_| || |_| |  __/| |_| | |___|  _ <
  \____| \___/|_|    \___/|_____|_| \_\
"""

    def on_close_attempt(self):
        # Block normal close attempts
        print('Close attempt was blocked. Use password or wait for timer, or kill process via Task Manager.')

    def try_unlock(self):
        if self.pw_var.get() == self.password:
            self.unlocked = True
            self.root.destroy()

    def run(self):
        # Show ASCII for ascii_seconds then hide
        if self.ascii_seconds > 0:
            self.root.after(self.ascii_seconds * 1000, lambda: self.ascii_label.pack_forget())

        def countdown():
            start = time.time()
            while True:
                if self.unlocked:
                    return
                elapsed = int(time.time() - start)
                remaining = max(0, self.duration - elapsed)
                self.timer_label.config(text=f'Time remaining: {remaining}s')
                if remaining <= 0:
                    # Time expired, allow exit
                    try:
                        self.root.destroy()
                    except Exception:
                        pass
                    return
                time.sleep(1)

        t = threading.Thread(target=countdown, daemon=True)
        t.start()
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', help='Path to env file containing PASSWORD, DURATION, ASCII_SECONDS')
    args = parser.parse_args()
    env = {}
    if args.env:
        env = load_env(Path(args.env))
    else:
        env = load_env(None)

    password = env.get('PASSWORD', '')
    duration = int(env.get('DURATION', '30'))
    ascii_seconds = int(env.get('ASCII_SECONDS', '3'))

    app = ViewerApp(password=password, duration=duration, ascii_seconds=ascii_seconds)
    app.run()


if __name__ == '__main__':
    main()
