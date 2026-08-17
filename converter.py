import imageio_ffmpeg
from pathlib import Path
import yt_dlp


class AudioConverter:
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback

    def _progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)

            if total and self.progress_callback:
                self.progress_callback(downloaded / total)

            if self.status_callback:
                self.status_callback("Downloading...")

        elif d["status"] == "finished":
            if self.progress_callback:
                self.progress_callback(1)

            if self.status_callback:
                self.status_callback("Converting...")

    def convert(
        self,
        url: str,
        output_dir: str,
        audio_format: str = "mp3",
        bitrate: str = "320",
        split_mode: str = "No split",
        timestamps_file: str | None = None,
    ):
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        output_template = str(output_dir / "%(title)s.%(ext)s")
        
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        if audio_format == "original":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "noplaylist": True,
                "ffmpeg_location": ffmpeg_path,
                "progress_hooks": [self._progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return

        postprocessor = {
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
        }

        if audio_format in ["mp3", "m4a", "ogg", "opus"] and bitrate != "lossless":
            postprocessor["preferredquality"] = bitrate

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "ffmpeg_location": ffmpeg_path,
            "progress_hooks": [self._progress_hook],
            "postprocessors": [postprocessor],
        }

        if split_mode == "By chapters":
            ydl_opts["split_chapters"] = True

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if split_mode == "By silence":
            # TODO: тук ще добавим ffmpeg silence detection
            pass

        if split_mode == "From timestamps file":
            # TODO: тук ще четем timestamps .txt и ще режем файла
            pass