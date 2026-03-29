import customtkinter as ctk
import pyperclip
import threading
import time
import json
import os

# --- Visual Theme Constants ---
ACCENT_COLOR = "#3A7EBF"  # Professional Blue
DANGER_COLOR = "#E74C3C"  # Soft Red
BG_COLOR_DARK = "#1A1A1A"  # Deep Charcoal


class Clipper(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Clipper")
        self.geometry("480x650")
        ctk.set_appearance_mode("dark")

        # Persistence Setup
        self.history_file = os.path.expanduser("~/.clipper_history.json")
        self.last_clip = ""
        self.history = self.load_data()

        # --- Grid Configuration ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # History area expands
        self.configure(fg_color=BG_COLOR_DARK)

        # 1. Header Section
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="CLIPPER",
            font=("Cantarell", 28, "bold"),
            text_color=ACCENT_COLOR
        )
        self.title_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            self.header_frame,
            text=f"{len(self.history)} items saved",
            font=("Cantarell", 12),
            text_color="gray"
        )
        self.count_label.pack(side="right", pady=(10, 0))

        # 2. Scrollable History Area
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            label_text="",
            fg_color="#242424",
            corner_radius=15,
            scrollbar_button_color=ACCENT_COLOR
        )
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # 3. Footer Section
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.clear_btn = ctk.CTkButton(
            self.footer_frame,
            text="Clear All History",
            font=("Cantarell", 13, "bold"),
            fg_color="transparent",
            border_width=2,
            border_color=DANGER_COLOR,
            text_color=DANGER_COLOR,
            hover_color="#331818",
            height=40,
            command=self.clear_history
        )
        self.clear_btn.pack(fill="x")

        # Build initial UI
        self.refresh_ui()

        # Start Monitor
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def load_data(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f)
        self.count_label.configure(text=f"{len(self.history)} items saved")

    def copy_to_clipboard(self, text, button):
        self.last_clip = text
        pyperclip.copy(text)

        # Elegant Visual Feedback
        button.configure(fg_color=ACCENT_COLOR, text_color="white", text="✨ Copied to System!")
        self.after(1000, self.refresh_ui)  # Refresh UI to reset colors after 1s

    def refresh_ui(self):
        # Clear current widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.history:
            # Show empty state
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="\n\nNo clips found yet.\nStart copying text!",
                font=("Cantarell", 14),
                text_color="gray"
            )
            empty_lbl.pack(pady=50)
            return

        for item in self.history:
            # Main Container for the "Card"
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#2D2D2D", corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)

            display_text = (item[:55] + '...') if len(item) > 55 else item

            # The Content Button
            btn = ctk.CTkButton(
                card,
                text=display_text,
                anchor="w",
                fg_color="transparent",
                hover_color="#3D3D3D",
                font=("Cantarell", 13),
                height=45,
                corner_radius=8
            )
            btn.configure(command=lambda i=item, b=btn: self.copy_to_clipboard(i, b))
            btn.pack(fill="x", padx=2, pady=2)

    def monitor_loop(self):
        while True:
            try:
                current_paste = pyperclip.paste()
                if current_paste and current_paste.strip() != self.last_clip:
                    clean_paste = current_paste.strip()
                    if not self.history or clean_paste != self.history[0]:
                        self.last_clip = clean_paste
                        self.history.insert(0, clean_paste)
                        self.history = self.history[:50]
                        self.save_data()
                        self.after(0, self.refresh_ui)
            except:
                pass
            time.sleep(1.0)

    def clear_history(self):
        self.history = []
        self.save_data()
        self.refresh_ui()


if __name__ == "__main__":
    app = Clipper()
    app.mainloop()