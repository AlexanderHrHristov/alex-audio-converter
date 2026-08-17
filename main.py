import threading
from pathlib import Path
from PIL import Image
import tkinter.filedialog as fd
import tkinter.messagebox as mb

import customtkinter as ctk

from converter import AudioConverter
from settings import BASIC_PROFILES

from locales.en import TRANSLATIONS as EN
from locales.bg import TRANSLATIONS as BG

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("AAC Community Edition")

        # -------------------------------------------------
        # RESPONSIVE WINDOW SETTINGS
        # -------------------------------------------------

        self.update_idletasks()

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # Прозорецът използва до 94% от ширината
        # и до 90% от височината на екрана.
        self.window_width = min(
            1180,
            int(self.screen_width * 0.94)
        )

        self.window_height = min(
            720,
            int(self.screen_height * 0.90)
        )

        # Без прекалено голям minimum, защото при Windows scaling
        # T480 може да докладва по-малка логическа резолюция.
        self.window_width = max(self.window_width, 780)
        self.window_height = max(self.window_height, 590)

        x = max((self.screen_width - self.window_width) // 2, 0)
        y = max((self.screen_height - self.window_height) // 2, 0)

        self.geometry(
            f"{self.window_width}x{self.window_height}+{x}+{y}"
        )

        self.minsize(780, 590)

        # -------------------------------------------------
        # RESPONSIVE COMPONENT SIZES
        # -------------------------------------------------

        profile_count = max(len(BASIC_PROFILES), 1)

        # Свободна ширина за картите.
        cards_available_width = self.window_width - 110

        # Разстояние между картите.
        self.card_gap = 5 if self.window_width < 1000 else 8

        calculated_card_width = (
            cards_available_width
            - profile_count * self.card_gap * 2
        ) // profile_count

        # Картите се ограничават в разумни размери.
        self.card_width = max(
            132,
            min(190, calculated_card_width)
        )

        # По-ниски карти на малък екран.
        if self.window_height <= 650:
            self.card_height = 195
            self.image_size = min(
                self.card_width - 24,
                112
            )
            self.main_title_size = 23
            self.profile_title_size = 11
            self.subtitle_size = 9
            self.tab_height = 290
            self.vertical_gap = 5

        elif self.window_width < 1100:
            self.card_height = 210
            self.image_size = min(
                self.card_width - 24,
                125
            )
            self.main_title_size = 25
            self.profile_title_size = 12
            self.subtitle_size = 10
            self.tab_height = 315
            self.vertical_gap = 7

        else:
            self.card_height = 230
            self.image_size = min(
                self.card_width - 24,
                145
            )
            self.main_title_size = 28
            self.profile_title_size = 14
            self.subtitle_size = 11
            self.tab_height = 340
            self.vertical_gap = 9

        # -------------------------------------------------
        # APPLICATION STATE
        # -------------------------------------------------

        self.output_dir = Path.cwd() / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.selected_basic_profile = "Car Standard"

        # Пазим CTkImage обектите, за да не бъдат
        # премахнати от garbage collector.
        self.profile_images = {}

        # Пазим картите, за да маркираме избраната.
        self.profile_cards = {}
        
        self.language = "en"
        
        self.translations = {
            "en": EN,
            "bg": BG,
        }

        self.build_ui()

    def t(self, key):
        return self.translations.get(
            self.language,
            EN
        ).get(key, key)


    def build_ui(self):
        # Главният контейнер използва grid, което е
        # по-надеждно за responsive интерфейс.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title = ctk.CTkLabel(
            self,
            text="Alex Audio Converter",
            font=("Arial", self.main_title_size, "bold"),
        )
        title.grid(
            row=0,
            column=0,
            padx=20,
            pady=(12, self.vertical_gap),
        )

        url_width = min(
            820,
            self.window_width - 100
        )

        self.url_entry = ctk.CTkEntry(
            self,
            width=url_width,
            height=35,
            placeholder_text=self.t("paste_url"),
        )
        self.url_entry.grid(
            row=1,
            column=0,
            padx=25,
            pady=self.vertical_gap,
        )

        tabs_width = min(
            self.window_width - 50,
            (
                len(BASIC_PROFILES)
                * (self.card_width + self.card_gap * 2)
                + 35
            ),
        )

        self.tabs = ctk.CTkTabview(
            self,
            width=tabs_width,
            height=self.tab_height,
        )
        self.tabs.grid(
            row=2,
            column=0,
            padx=20,
            pady=self.vertical_gap,
            sticky="n",
        )

        self.basic_tab = self.tabs.add("Basic")
        self.build_basic_tab()

        self.build_bottom_controls()

    def build_basic_tab(self):
        self.basic_tab.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            self.basic_tab,
            text=self.t("quick_select"),
            font=("Arial", 17, "bold"),
        )
        label.grid(
            row=0,
            column=0,
            pady=(4, 2),
        )

        profiles_frame = ctk.CTkFrame(
            self.basic_tab,
            fg_color="transparent",
        )
        profiles_frame.grid(
            row=1,
            column=0,
            pady=3,
        )

        image_map = {
            # Ако преименуваш файла правилно, промени и тук
            # на assets/car_standard.png.
            "Car Standard": "assets/car_standard.png",
            "Car Premium": "assets/car_premium.png",
            "Fast Original": "assets/fast_original.png",
            "Hi-Fi": "assets/hifi.png",
            "Archive": "assets/archive.png",
        }

        for index, profile in enumerate(BASIC_PROFILES):
            card = ctk.CTkFrame(
                profiles_frame,
                width=self.card_width,
                height=self.card_height,
                corner_radius=14,
                border_width=2,
                border_color="#3b3b3b",
            )
            card.grid(
                row=0,
                column=index,
                padx=self.card_gap,
                pady=4,
            )
            card.grid_propagate(False)

            self.profile_cards[profile] = card

            img_path = image_map.get(profile)

            if img_path:
                try:
                    pil_image = Image.open(img_path)

                    image = ctk.CTkImage(
                        light_image=pil_image,
                        dark_image=pil_image,
                        size=(
                            self.image_size,
                            self.image_size,
                        ),
                    )

                    self.profile_images[profile] = image

                    image_button = ctk.CTkButton(
                        card,
                        image=image,
                        text="",
                        width=self.image_size,
                        height=self.image_size,
                        fg_color="transparent",
                        hover_color="#343434",
                        command=lambda p=profile: (
                            self.select_basic_profile(p)
                        ),
                    )
                    image_button.pack(
                        pady=(7, 2)
                    )

                except FileNotFoundError:
                    placeholder = ctk.CTkLabel(
                        card,
                        text="No image",
                        width=self.image_size,
                        height=self.image_size,
                    )
                    placeholder.pack(
                        pady=(7, 2)
                    )

            title = ctk.CTkLabel(
                card,
                text=profile,
                font=(
                    "Arial",
                    self.profile_title_size,
                    "bold",
                ),
            )
            title.pack(pady=(1, 0))

            data = BASIC_PROFILES[profile]

            bitrate = str(data["bitrate"])

            if bitrate == "lossless":
                quality_text = "LOSSLESS"
            elif bitrate == "copy":
                quality_text = "NO RE-ENCODING"
            else:
                quality_text = f"{bitrate} kbps"

            subtitle = ctk.CTkLabel(
                card,
                text=(
                    f"{data['format'].upper()} "
                    f"{quality_text}"
                ),
                font=("Arial", self.subtitle_size),
            )
            subtitle.pack(pady=(0, 3))

            select_button = ctk.CTkButton(
                card,
                text=self.t("select"),
                width=max(self.card_width - 40, 85),
                height=25,
                font=("Arial", 10),
                command=lambda p=profile: (
                    self.select_basic_profile(p)
                ),
            )
            select_button.pack(pady=(1, 5))

        self.basic_selected_label = ctk.CTkLabel(
            self.basic_tab,
            text=(
                f"{self.t('selected_profile')}: "
                "Car Standard / MP3 320 kbps"
),
            font=("Arial", 11),
        )
        self.basic_selected_label.grid(
            row=2,
            column=0,
            pady=(3, 2),
        )

        # Маркиране на профила по подразбиране.
        self.update_selected_card()

    def build_bottom_controls(self):
        bottom_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        bottom_frame.grid(
            row=3,
            column=0,
            padx=25,
            pady=(2, 10),
            sticky="ew",
        )

        bottom_frame.grid_columnconfigure(0, weight=1)

        self.folder_label = ctk.CTkLabel(
            bottom_frame,
            text=f"OUTPUT FOLDER: {self.output_dir}",
            wraplength=self.window_width - 100,
            font=("Arial", 10),
        )
        self.folder_label.grid(
            row=0,
            column=0,
            pady=2,
        )

        folder_button = ctk.CTkButton(
            bottom_frame,
            text=self.t("select_folder"),
            width=130,
            height=28,
            command=self.select_folder,
        )
        folder_button.grid(
            row=1,
            column=0,
            pady=2,
        )

        progress_width = min(
            900,
            self.window_width - 100
        )

        self.progress_bar = ctk.CTkProgressBar(
            bottom_frame,
            width=progress_width,
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(
            row=2,
            column=0,
            pady=(7, 3),
        )

        self.status_label = ctk.CTkLabel(
            bottom_frame,
            text=self.t("ready"),
            font=("Arial", 11),
        )
        self.status_label.grid(
            row=3,
            column=0,
            pady=2,
        )

        self.convert_btn = ctk.CTkButton(
            bottom_frame,
            text=self.t("convert"),
            width=180,
            height=36,
            font=("Arial", 13, "bold"),
            command=self.start_conversion,
        )
        self.convert_btn.grid(
            row=4,
            column=0,
            pady=(4, 2),
        )

    def select_basic_profile(self, profile):
        self.selected_basic_profile = profile

        data = BASIC_PROFILES[profile]
        bitrate = str(data["bitrate"])

        if bitrate == "lossless":
            quality_text = "Lossless"
        elif bitrate == "copy":
            quality_text = "No re-encoding"
        else:
            quality_text = f"{bitrate} kbps"

        self.basic_selected_label.configure(
            text=(
                f"{self.t('selected_profile')}: {profile} / "
                f"{data['format'].upper()} "
                f"{quality_text}"
            )
        )

        self.update_selected_card()

    def update_selected_card(self):
        for profile, card in self.profile_cards.items():
            if profile == self.selected_basic_profile:
                card.configure(
                    border_color="#1f6aa5",
                    border_width=3,
                )
            else:
                card.configure(
                    border_color="#3b3b3b",
                    border_width=2,
                )

    def select_folder(self):
        selected = fd.askdirectory()

        if selected:
            self.output_dir = Path(selected)

            self.folder_label.configure(
                text=f"Folder: {self.output_dir}"
            )

    def get_current_settings(self):
        profile = BASIC_PROFILES[
            self.selected_basic_profile
        ]

        return {
            "audio_format": profile["format"],
            "bitrate": profile["bitrate"],
            "split_mode": "No split",
            "timestamps_file": None,
        }

    def start_conversion(self):
        url = self.url_entry.get().strip()

        if not url:
            mb.showwarning(
                self.t("missing_url"),
                self.t("enter_url"),
            )
            return

        settings = self.get_current_settings()

        self.convert_btn.configure(
            state="disabled"
        )
        self.progress_bar.set(0)
        self.status_label.configure(
            text=self.t("starting")
        )

        worker_thread = threading.Thread(
            target=self.run_conversion,
            args=(url, settings),
            daemon=True,
        )
        worker_thread.start()

    def run_conversion(self, url, settings):
        try:
            converter = AudioConverter(
                progress_callback=self.update_progress,
                status_callback=self.update_status,
            )

            converter.convert(
                url=url,
                output_dir=str(self.output_dir),
                audio_format=settings["audio_format"],
                bitrate=settings["bitrate"],
                split_mode=settings["split_mode"],
                timestamps_file=settings[
                    "timestamps_file"
                ],
            )

            self.after(0, self.on_success)

        except Exception as error:
            error_message = str(error)

            self.after(
                0,
                lambda message=error_message: (
                    self.on_error(message)
                ),
            )

    def update_progress(self, value):
        self.after(
            0,
            lambda progress=value: (
                self.progress_bar.set(progress)
            ),
        )

    def update_status(self, text):
        self.after(
            0,
            lambda message=text: (
                self.status_label.configure(
                    text=message
                )
            ),
        )

    def on_success(self):
        self.convert_btn.configure(
            state="normal"
        )
        self.progress_bar.set(1)
        self.status_label.configure(
            text=self.t("done")
        )

        self.url_entry.delete(0, "end")

        mb.showinfo(
            self.t("done"),
            self.t("conversion_finished"),
        )


    def on_error(self, error):
        self.convert_btn.configure(
            state="normal"
        )
        self.status_label.configure(
            text=self.t("error")
        )

        mb.showerror(
            self.t("error"),
            error,
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()