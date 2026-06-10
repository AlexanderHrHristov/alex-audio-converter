import threading
from pathlib import Path
from PIL import Image
import tkinter.filedialog as fd
import tkinter.messagebox as mb

import customtkinter as ctk

from converter import AudioConverter
from settings import BASIC_PROFILES, FORMATS, BITRATES, SPLIT_MODES


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AAC - Alex Audio Converter v0.9")
        self.geometry("1120x860")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.output_dir = Path.cwd() / "output"
        self.timestamps_file = None
        self.selected_basic_profile = "Car Standard"
        self.profile_images = {}

        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(
            self,
            text="Alex Audio Converter",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=20)

        self.url_entry = ctk.CTkEntry(
            self,
            width=650,
            placeholder_text="Постави YouTube линк или аудио линк..."
        )
        self.url_entry.pack(pady=10)

        self.tabs = ctk.CTkTabview(self, width=1100, height=430)
        self.tabs.pack(pady=15)

        self.basic_tab = self.tabs.add("Basic")
        self.advanced_tab = self.tabs.add("Advanced")

        self.build_basic_tab()
        self.build_advanced_tab()

        self.folder_label = ctk.CTkLabel(
            self,
            text=f"Папка: {self.output_dir}",
            wraplength=650
        )
        self.folder_label.pack(pady=5)

        folder_btn = ctk.CTkButton(
            self,
            text="Избери папка",
            command=self.choose_folder
        )
        folder_btn.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, width=960)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=15)

        self.status_label = ctk.CTkLabel(self, text="Готов за работа.")
        self.status_label.pack(pady=5)

        self.convert_btn = ctk.CTkButton(
            self,
            text="Convert",
            height=44,
            command=self.start_conversion
        )
        self.convert_btn.pack(pady=15)

    def build_basic_tab(self):
        label = ctk.CTkLabel(
            self.basic_tab,
            text="Бърз избор",
            font=("Arial", 20, "bold")
        )
        label.pack(pady=10)

        profiles_frame = ctk.CTkFrame(self.basic_tab)
        profiles_frame.pack(pady=10)

        image_map = {
            "Car Standard": "assets/car_standart.png",
            "Car Premium": "assets/car_premium.png",
            "Fast Original": "assets/fast_original.png",
            "Hi-Fi": "assets/hifi.png",
            "Archive": "assets/archive.png",
        }

        for index, profile in enumerate(BASIC_PROFILES):
            row = 0
            col = index

            card = ctk.CTkFrame(
                profiles_frame,
                width=190,
                height=250,
                corner_radius=16
            )
            card.grid(row=row, column=col, padx=10, pady=10)
            card.grid_propagate(False)

            img_path = image_map.get(profile)

            if img_path:
                try:
                    image = ctk.CTkImage(
                        light_image=Image.open(img_path),
                        dark_image=Image.open(img_path),
                        size=(170, 170)
                    )
                    self.profile_images[profile] = image

                    img_label = ctk.CTkLabel(card, image=image, text="")
                    img_label.pack(pady=(10, 5))
                except FileNotFoundError:
                    placeholder = ctk.CTkLabel(card, text="No image", height=95)
                    placeholder.pack(pady=(10, 5))

            title = ctk.CTkLabel(
                card,
                text=profile,
                font=("Arial", 15, "bold")
            )
            title.pack(pady=(5, 2))

            data = BASIC_PROFILES[profile]
            subtitle = ctk.CTkLabel(
                card,
                text=f"{data['format'].upper()} {data['bitrate']}",
                font=("Arial", 12)
            )
            subtitle.pack(pady=(0, 8))

            btn = ctk.CTkButton(
                card,
                text="Избери",
                width=120,
                command=lambda p=profile: self.select_basic_profile(p)
            )
            btn.pack(pady=5)

        self.basic_selected_label = ctk.CTkLabel(
            self.basic_tab,
            text="Избран профил: Car Standard / MP3 320"
        )
        self.basic_selected_label.pack(pady=10)

    def build_advanced_tab(self):
        grid = ctk.CTkFrame(self.advanced_tab)
        grid.pack(pady=20)

        ctk.CTkLabel(grid, text="Формат").grid(row=0, column=0, padx=10, pady=10)
        self.format_box = ctk.CTkComboBox(grid, values=FORMATS)
        self.format_box.set("mp3")
        self.format_box.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(grid, text="Битрейт").grid(row=1, column=0, padx=10, pady=10)
        self.bitrate_box = ctk.CTkComboBox(grid, values=BITRATES)
        self.bitrate_box.set("320")
        self.bitrate_box.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(grid, text="Split mode").grid(row=2, column=0, padx=10, pady=10)
        self.split_box = ctk.CTkComboBox(grid, values=SPLIT_MODES)
        self.split_box.set("No split")
        self.split_box.grid(row=2, column=1, padx=10, pady=10)

        self.timestamps_btn = ctk.CTkButton(
            grid,
            text="Избери timestamps .txt",
            command=self.choose_timestamps_file
        )
        self.timestamps_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def select_basic_profile(self, profile):
        self.selected_basic_profile = profile
        data = BASIC_PROFILES[profile]

        self.basic_selected_label.configure(
            text=f"Избран профил: {profile} / {data['format'].upper()} {data['bitrate']}"
        )

    def choose_folder(self):
        selected = fd.askdirectory()
        if selected:
            self.output_dir = Path(selected)
            self.folder_label.configure(text=f"Папка: {self.output_dir}")

    def choose_timestamps_file(self):
        selected = fd.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if selected:
            self.timestamps_file = selected
            mb.showinfo("Timestamps", "Файлът е избран.")

    def get_current_settings(self):
        current_tab = self.tabs.get()

        if current_tab == "Basic":
            profile = BASIC_PROFILES[self.selected_basic_profile]
            return {
                "audio_format": profile["format"],
                "bitrate": profile["bitrate"],
                "split_mode": "No split",
                "timestamps_file": None,
            }

        return {
            "audio_format": self.format_box.get(),
            "bitrate": self.bitrate_box.get(),
            "split_mode": self.split_box.get(),
            "timestamps_file": self.timestamps_file,
        }

    def start_conversion(self):
        url = self.url_entry.get().strip()

        if not url:
            mb.showwarning("Липсва линк", "Постави линк.")
            return

        settings = self.get_current_settings()

        self.convert_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Стартиране...")

        thread = threading.Thread(
            target=self.run_conversion,
            args=(url, settings),
            daemon=True
        )
        thread.start()

    def run_conversion(self, url, settings):
        try:
            converter = AudioConverter(
                progress_callback=lambda value: self.after(
                    0, lambda: self.progress_bar.set(value)
                ),
                status_callback=lambda text: self.after(
                    0, lambda: self.status_label.configure(text=text)
                ),
            )

            converter.convert(
                url=url,
                output_dir=str(self.output_dir),
                audio_format=settings["audio_format"],
                bitrate=settings["bitrate"],
                split_mode=settings["split_mode"],
                timestamps_file=settings["timestamps_file"],
            )

            self.after(0, self.on_success)

        except Exception as e:
            error_message = str(e)
            self.after(0, lambda: self.on_error(error_message))

    def on_success(self):
        self.convert_btn.configure(state="normal")
        self.progress_bar.set(1)
        self.status_label.configure(text="Готово!")
        mb.showinfo("Готово", "Конвертирането приключи.")

    def on_error(self, error):
        self.convert_btn.configure(state="normal")
        self.status_label.configure(text="Грешка.")
        mb.showerror("Грешка", error)

if __name__ == "__main__":
    app = App()
    app.mainloop()