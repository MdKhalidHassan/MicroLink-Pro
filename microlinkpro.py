import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox
from multiprocessing import freeze_support

class MicroLinkVirtualMicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroLink - Phone to PC Virtual Mic")
        self.root.geometry("520x420")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.audio_process = None
        self.virtual_sink_loaded = False
        self.is_streaming = False
        self.device_connected = False

        self.setup_ui()

        # ব্যাকগ্রাউন্ডে অনবরত অটোমেটিক ফোন কানেকশন চেক চালু
        self.check_thread = threading.Thread(target=self.auto_check_device, daemon=True)
        self.check_thread.start()

    def setup_ui(self):
        title_label = tk.Label(
            self.root, 
            text="MicroLink Virtual Mic Engine", 
            font=("Helvetica", 16, "bold"), 
            bg="#1e1e2e", 
            fg="#cdd6f4"
        )
        title_label.pack(pady=15)

        # অটো-স্ট্যাটাস ফ্রেম (লাইভ কানেকশন আপডেট দেখাবে)
        status_frame = tk.Frame(self.root, bg="#313244", bd=1, relief="solid")
        status_frame.pack(fill="x", padx=30, pady=10)

        self.status_label = tk.Label(
            status_frame, 
            text="USB Status: Scanning Phone Connection...", 
            font=("Helvetica", 10, "bold"), 
            bg="#313244", 
            fg="#f9e2af"
        )
        self.status_label.pack(pady=12)

        # মাইক্রোফোন স্টার্ট/স্টপ বাটন
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=40, pady=15)

        self.start_mic_btn = tk.Button(
            btn_frame, 
            text="🎙️ Start Virtual Microphone", 
            font=("Helvetica", 11, "bold"), 
            bg="#a6e3a1", 
            fg="#11111b", 
            activebackground="#94e2d5", 
            relief="flat", 
            cursor="hand2", 
            command=self.start_microphone,
            state="disabled"
        )
        self.start_mic_btn.pack(fill="x", pady=5, ipady=6)

        self.stop_mic_btn = tk.Button(
            btn_frame, 
            text="🛑 Stop Virtual Microphone", 
            font=("Helvetica", 11, "bold"), 
            bg="#f38ba8", 
            fg="#11111b", 
            activebackground="#f5e0dc", 
            relief="flat", 
            cursor="hand2", 
            command=self.stop_microphone,
            state="disabled"
        )
        self.stop_mic_btn.pack(fill="x", pady=5, ipady=6)

        self.info_label = tk.Label(
            self.root,
            text="Note: Select 'MicroLinkInput' as your PC's Input Device/Microphone",
            font=("Helvetica", 9, "italic"),
            bg="#1e1e2e",
            fg="#bac2de"
        )
        self.info_label.pack(pady=8)

    def setup_virtual_mic(self):
        """Linux-এ পিসির মূল মাইক্রোফোন ইনপুট তৈরি করার ব্যাকএন্ড লজিক"""
        try:
            # আগে থেকে ভার্চুয়াল সিঙ্ক থাকলে রিমুভ করে নতুন করে লোড করা
            subprocess.run(["pactl", "unload-module", "module-remap-source"], capture_output=True)
            subprocess.run(["pactl", "unload-module", "module-null-sink"], capture_output=True)

            cmd1 = [
                "pactl", "load-module", "module-null-sink", 
                "sink_name=MicroLinkSink", 
                "sink_properties=device.description=MicroLinkVirtualSink"
            ]
            cmd2 = [
                "pactl", "load-module", "module-remap-source", 
                "master=MicroLinkSink.monitor", 
                "source_name=MicroLinkInput", 
                "source_properties=device.description=MicroLinkInput"
            ]

            subprocess.run(cmd1, check=True, capture_output=True)
            subprocess.run(cmd2, check=True, capture_output=True)
            self.virtual_sink_loaded = True
        except Exception as e:
            print(f"Virtual Mic Setup Warning: {str(e)}")

    def auto_check_device(self):
        """ব্যাকগ্রাউন্ডে অটো ফোন কানেকশন চেক করবে"""
        while True:
            try:
                result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                lines = result.stdout.strip().split("\n")
                devices = [line.split()[0] for line in lines[1:] if "device" in line and not "unauthorized" in line]

                if devices:
                    self.device_connected = True
                    dev_id = devices[0]
                    if not self.is_streaming:
                        self.root.after(0, lambda: self.status_label.config(
                            text=f"USB Status: Phone Ready [{dev_id}]", fg="#a6e3a1"
                        ))
                        self.root.after(0, lambda: self.start_mic_btn.config(state="normal"))
                else:
                    self.device_connected = False
                    if self.is_streaming:
                        self.stop_microphone()
                    self.root.after(0, lambda: self.status_label.config(
                        text="USB Status: No USB Device Found", fg="#f38ba8"
                    ))
                    self.root.after(0, lambda: self.start_mic_btn.config(state="disabled"))
                    self.root.after(0, lambda: self.stop_mic_btn.config(state="disabled"))

            except Exception:
                self.root.after(0, lambda: self.status_label.config(
                    text="USB Status: ADB Missing!", fg="#f38ba8"
                ))

            time.sleep(2)

    def start_microphone(self):
        if not self.device_connected:
            messagebox.showwarning("Warning", "Phone is not connected via USB!")
            return

        # ভার্চুয়াল মাইক ইনপুট ইনিশিয়ালাইজ করা
        self.setup_virtual_mic()

        self.is_streaming = True
        self.start_mic_btn.config(state="disabled")
        self.stop_mic_btn.config(state="normal")
        self.status_label.config(
            text="🎙️ Mic Active: Streaming to MicroLinkInput...", fg="#89b4fa"
        )

        threading.Thread(target=self.run_audio_stream, daemon=True).start()

    def run_audio_stream(self):
        try:
            # scrcpy অডিও স্ট্রিম সরাসরি MicroLinkSink এ পুশ করবে
            env = os.environ.copy()
            env["PULSE_SINK"] = "MicroLinkSink"

            cmd = ["scrcpy", "--no-video", "--audio-source=mic"]
            self.audio_process = subprocess.Popen(
                cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            self.audio_process.wait()
        except Exception as e:
            if self.is_streaming:
                self.root.after(0, lambda: messagebox.showerror("Audio Error", f"Failed: {str(e)}"))
                self.stop_microphone()

    def stop_microphone(self):
        self.is_streaming = False
        if self.audio_process:
            self.audio_process.terminate()
            self.audio_process = None

        # ভার্চুয়াল মাইক আনলোড করা
        subprocess.run(["pactl", "unload-module", "module-remap-source"], capture_output=True)
        subprocess.run(["pactl", "unload-module", "module-null-sink"], capture_output=True)

        self.start_mic_btn.config(state="normal" if self.device_connected else "disabled")
        self.stop_mic_btn.config(state="disabled")

        if self.device_connected:
            self.status_label.config(text="USB Status: Phone Ready (Mic Stopped)", fg="#a6e3a1")
        else:
            self.status_label.config(text="USB Status: Disconnected", fg="#f38ba8")

if __name__ == "__main__":
    freeze_support()
    root = tk.Tk()
    app = MicroLinkVirtualMicApp(root)

    def on_closing():
        if app.audio_process:
            app.audio_process.terminate()
        subprocess.run(["pactl", "unload-module", "module-remap-source"], capture_output=True)
        subprocess.run(["pactl", "unload-module", "module-null-sink"], capture_output=True)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
