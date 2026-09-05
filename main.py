import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key
import json
import os

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        self.clicking = False
        self.listener = None
        self.mouse = Controller()
        self.click_thread = None
        self.start_key = Key.f6
        self.stop_key = Key.f7
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self.root, text="Auto Clicker", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for controls
        control_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
        control_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Click Rate
        ttk.Label(control_frame, text="Clicks Per Second:").grid(row=0, column=0, sticky="w", pady=5)
        self.cps_var = tk.DoubleVar(value=10.0)
        cps_spinbox = ttk.Spinbox(control_frame, from_=1, to=100, textvariable=self.cps_var, width=10)
        cps_spinbox.grid(row=0, column=1, sticky="w", padx=5)
        
        # Mouse Button
        ttk.Label(control_frame, text="Mouse Button:").grid(row=1, column=0, sticky="w", pady=5)
        self.button_var = tk.StringVar(value="left")
        button_combo = ttk.Combobox(control_frame, textvariable=self.button_var, 
                                    values=["left", "right", "middle"], width=8, state="readonly")
        button_combo.grid(row=1, column=1, sticky="w", padx=5)
        
        # Start Key
        ttk.Label(control_frame, text="Start Key (F6):").grid(row=2, column=0, sticky="w", pady=5)
        self.start_key_label = ttk.Label(control_frame, text="F6", relief="sunken", width=10)
        self.start_key_label.grid(row=2, column=1, sticky="w", padx=5)
        
        # Stop Key
        ttk.Label(control_frame, text="Stop Key (F7):").grid(row=3, column=0, sticky="w", pady=5)
        self.stop_key_label = ttk.Label(control_frame, text="F7", relief="sunken", width=10)
        self.stop_key_label.grid(row=3, column=1, sticky="w", padx=5)
        
        # Status
        ttk.Label(control_frame, text="Status:").grid(row=4, column=0, sticky="w", pady=5)
        self.status_label = ttk.Label(control_frame, text="Stopped", foreground="red", font=("Helvetica", 10, "bold"))
        self.status_label.grid(row=4, column=1, sticky="w", padx=5)
        
        # Button Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(padx=10, pady=10, fill="x")
        
        self.start_btn = ttk.Button(button_frame, text="Start (F6)", command=self.start_clicking)
        self.start_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop (F7)", command=self.stop_clicking, state="disabled")
        self.stop_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Info Frame
        info_frame = ttk.LabelFrame(self.root, text="Instructions", padding=10)
        info_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        info_text = tk.Text(info_frame, height=8, width=45, wrap="word", state="disabled")
        info_text.pack(fill="both", expand=True)
        
        self.root.after(100, lambda: self.update_info_text(info_text))
        
    def update_info_text(self, text_widget):
        text_widget.config(state="normal")
        text_widget.delete(1.0, "end")
        info = """1. Set your desired click rate (clicks per second)
2. Choose which mouse button to click
3. Press F6 to START clicking
4. Press F7 to STOP clicking
5. Settings are auto-saved

⚠️ WARNING: Use responsibly and only on your own systems!"""
        text_widget.insert(1.0, info)
        text_widget.config(state="disabled")
    
    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="Running", foreground="green")
            self.save_settings()
            
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
            
            self.start_listener()
    
    def stop_clicking(self):
        if self.clicking:
            self.clicking = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.status_label.config(text="Stopped", foreground="red")
    
    def click_loop(self):
        button = Button.left if self.button_var.get() == "left" else \
                 Button.right if self.button_var.get() == "right" else Button.middle
        
        interval = 1.0 / self.cps_var.get()
        
        while self.clicking:
            self.mouse.click(button, 1)
            time.sleep(interval)
    
    def start_listener(self):
        if self.listener is None:
            self.listener = Listener(on_press=self.on_key_press)
            self.listener.start()
    
    def on_key_press(self, key):
        try:
            if key == self.start_key and not self.clicking:
                self.root.after(0, self.start_clicking)
            elif key == self.stop_key and self.clicking:
                self.root.after(0, self.stop_clicking)
        except AttributeError:
            pass
    
    def save_settings(self):
        settings = {
            "cps": self.cps_var.get(),
            "button": self.button_var.get()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
    
    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    self.cps_var.set(settings.get("cps", 10.0))
                    self.button_var.set(settings.get("button", "left"))
            except:
                pass
    
    def on_closing(self):
        self.clicking = False
        if self.listener:
            self.listener.stop()
        self.save_settings()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
