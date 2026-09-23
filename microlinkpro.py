import os
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox

class MicroLinkPro:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroLink Pro — Android Mic Receiver")
        self.root.geometry("450x380")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")  # Dark Modern Slate Palette

        self.scrcpy_process = None
        self.is_running = False

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_ui(self):
        # Top Header Banner
        header_frame = tk.Frame(self.root, bg="#1e293b", height=70)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            header_frame, 
            text="🎙️ MicroLink Pro", 
            font=("Segoe UI", 18, "bold"), 
            fg="#f8fafc", 
            bg="#1e293b"
        )
        title_lbl.pack(side="top", pady=(12, 2))

        subtitle_lbl = tk.Label(
            header_frame, 
            text="Seamless Android Microphone Bridge for Linux", 
            font=("Segoe UI", 9), 
            fg="#94a3b8", 
            bg="#1e293b"
        )
        subtitle_lbl.pack(side="top")

        # Main Body Container
        body_frame = tk.Frame(self.root, bg="#0f172a")
        body_frame.pack(fill="both", expand=True, padx=25, pady=20)

        # Status Badge Indicator
        self.status_card = tk.Frame(body_frame, bg="#1e293b", highlightbackground="#334155", highlightthickness=1)
        self.status_card.pack(fill="x", pady=(0, 20))

        self.status_dot = tk.Label(self.status_card, text="●", font=("Segoe UI", 14), fg="#ef4444", bg="#1e293b")
        self.status_dot.pack(side="left", padx=(15, 5), pady=10)

        self.status_lbl = tk.Label(
            self.status_card, 
            text="Status: Disconnected", 
            font=("Segoe UI", 11, "bold"), 
            fg="#cbd5e1", 
            bg="#1e293b"
        )
        self.status_lbl.pack(side="left", pady=10)

        # Control Buttons Container
        btn_frame = tk.Frame(body_frame, bg="#0f172a")
        btn_frame.pack(fill="x", pady=5)

        # Start Button
        self.start_btn = tk.Button(
            btn_frame, 
            text="▶ START MIC", 
            font=("Segoe UI", 11, "bold"), 
            bg="#10b981", 
            fg="#ffffff", 
            activebackground="#059669",
            activeforeground="#ffffff",
            bd=0, 
            cursor="hand2",
            height=2,
            command=self.start_mic_thread
        )
        self.start_btn.pack(fill="x", pady=(0, 10))

        # Stop Button
        self.stop_btn = tk.Button(
            btn_frame, 
            text="■ STOP MIC", 
            font=("Segoe UI", 11, "bold"), 
            bg="#334155", 
            fg="#64748b", 
            activebackground="#475569",
            activeforeground="#ffffff",
            bd=0, 
            cursor="hand2",
            height=2,
            state="disabled",
            command=self.stop_mic
        )
        self.stop_btn.pack(fill="x")

        # Footer Info Note
        footer_lbl = tk.Label(
            body_frame, 
            text="💡 Connect phone via USB with USB Debugging enabled.\nOnce started, your phone mic becomes the default system mic.", 
            font=("Segoe UI", 8), 
            fg="#64748b", 
            bg="#0f172a",
            justify="center"
        )
        footer_lbl.pack(side="bottom", pady=(15, 0))

    def check_tools(self):
        missing = []
        if not shutil.which("scrcpy"):
            missing.append("scrcpy")
        if not shutil.which("pactl"):
            missing.append("pulseaudio-utils")
        
        if missing:
            messagebox.showerror(
                "Missing System Tools",
                f"Required tools are not installed: {', '.join(missing)}\n\n"
                f"Run this terminal command to install:\nsudo apt install {' '.join(missing)}"
            )
            return False
        return True

    def setup_pulse_audio(self):
        try:
            # Create null-sink and remap source for virtual mic
            subprocess.run(
                ["pactl", "load-module", "module-null-sink", "sink_name=remote_mic", "sink_properties=device.description=Android_Virtual_Mic"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            subprocess.run(
                ["pactl", "load-module", "module-remap-source", "master=remote_mic.monitor", "source_name=android_mic", "source_properties=device.description=Android_Mic_Input"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            # Set as default system microphone automatically
            subprocess.run(
                ["pactl", "set-default-source", "android_mic"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            messagebox.showerror("Audio Module Error", f"Failed to initialize virtual mic: {e}")
            return False

    def start_mic_thread(self):
        if not self.check_tools():
            return
        
        # Run process in background thread to keep UI smooth and lag-free
        threading.Thread(target=self.start_mic, daemon=True).start()

    def start_mic(self):
        if self.is_running:
            return

        if not self.setup_pulse_audio():
            return

        env = os.environ.copy()
        env["PULSE_SINK"] = "remote_mic"

        try:
            # Command to stream audio, disable video, keep mic active, and keep screen off
            cmd = ["scrcpy", "--audio-source=mic", "--no-video", "--stay-awake", "--turn-screen-off"]
            self.scrcpy_process = subprocess.Popen(cmd, env=env)
            
            self.is_running = True
            
            # Update UI elements
            self.root.after(0, self.update_ui_started)

            # Monitor process until stopped
            self.scrcpy_process.wait()

            # If stopped externally
            if self.is_running:
                self.root.after(0, self.stop_mic)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Execution Error", f"Could not launch scrcpy: {e}"))
            self.root.after(0, self.stop_mic)

    def update_ui_started(self):
        self.status_dot.config(fg="#10b981")
        self.status_lbl.config(text="Status: Microphone Connected & Active", fg="#f8fafc")
        
        self.start_btn.config(state="disabled", bg="#1e293b", fg="#64748b", cursor="arrow")
        self.stop_btn.config(state="normal", bg="#ef4444", fg="#ffffff", cursor="hand2")

    def stop_mic(self):
        self.is_running = False

        if self.scrcpy_process:
            try:
                self.scrcpy_process.terminate()
            except Exception:
                pass
            self.scrcpy_process = None

        # Reset UI
        self.status_dot.config(fg="#ef4444")
        self.status_lbl.config(text="Status: Disconnected", fg="#cbd5e1")

        self.start_btn.config(state="normal", bg="#10b981", fg="#ffffff", cursor="hand2")
        self.stop_btn.config(state="disabled", bg="#334155", fg="#64748b", cursor="arrow")

    def on_closing(self):
        self.stop_mic()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MicroLinkPro(root)
    root.mainloop()
