# pip install yt_dlp
# https://www.gyan.dev/ffmpeg/builds/

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import time
import re
import shutil
import yt_dlp

# --- MESSAGES словник ---
MESSAGES = {
    'uk': {
        'select_language': "Виберіть мову (uk/en/es): ",
        'disclaimer': (
            "=====================================================================\n"
            "DISCLAIMER:\n"
            "Цей проект створено виключно з освітньою метою.\n"
            "Автор не підтримує і не заохочує використання цього інструменту для\n"
            "порушення авторських прав чи інших незаконних дій.\n"
            "Користувач несе повну відповідальність за використання цієї програми.\n"
            "=====================================================================\n"
            "Ви приймаєте умови?"
        ),
        'consent_decline': "Ви не прийняли умови. Завершення роботи програми.",
        'ffmpeg_not_found': "УВАГА: ffmpeg не знайдено. Без нього неможливо об'єднати аудіо та відео.",
        'ffmpeg_install_win': "Завантажте ffmpeg з https://ffmpeg.org/download.html та додайте шлях до bin у PATH.",
        'ffmpeg_install_mac': "Виконайте в терміналі: brew install ffmpeg",
        'ffmpeg_install_linux': "Виконайте в терміналі: sudo apt-get install ffmpeg",
        'continue_without_ffmpeg': "Продовжити без об'єднання аудіо та відео?",
        'download_custom_folder': "Виберіть власну папку для завантаження:",
        'folder_no_permission': "Неможливо записати файли у {folder}. Недостатньо прав.",
        'using_default_folder': "Використовується стандартна папка: {default}",
        'choose_video_url': "Введіть URL відео YouTube:",
        'start_download': "Розпочати завантаження",
        'download_started': "Завантаження розпочато...",
        'download_complete': "Завантаження завершено!",
        'file_saved': "Файл успішно збережено:",
        'file_size': "Розмір файлу: {size} байт",
        'file_zero': "УВАГА: Файл має нульовий розмір!",
        'download_error': "Помилка при завантаженні:",
        'choose_format': "Формат завантаження:",
        'format_1': "Відео + Аудіо (один файл)",
        'format_2': "Відео (без звуку)",
        'format_3': "Аудіо (тільки звук)",
        'format_4': "Відео та Аудіо (окремі файли)",
        'choose_video_quality': "Якість відео:",
        'quality_2160': "2160p (4K)",
        'quality_1440': "1440p (2K)",
        'quality_1080': "1080p (Full HD)",
        'quality_720': "720p (HD)",
        'quality_480': "480p (SD)",
        'quality_360': "360p (Low)",
        'default_quality': "За замовчуванням (найкраще)",
        'choose_audio_quality': "Якість аудіо:",
        'audio_best': "Найкраща (до 320kbps)",
        'audio_medium': "Середня (до 192kbps)",
        'audio_low': "Низька (до 128kbps)",
        'audio_min': "Мінімальна (до 64kbps)",
        'browse': "Огляд",
        'downloading': "Завантаження: {percent}%",
        'url_empty': "URL не введено!"
    },
    'en': {
        'select_language': "Choose language (uk/en/es): ",
        'disclaimer': (
            "=====================================================================\n"
            "DISCLAIMER:\n"
            "This project is created for educational purposes only.\n"
            "The author does not support or encourage the use of this tool for\n"
            "copyright infringement or any other illegal activities.\n"
            "The user assumes full responsibility for using this program.\n"
            "=====================================================================\n"
            "Do you accept these terms?"
        ),
        'consent_decline': "You did not accept the terms. Exiting the program.",
        'ffmpeg_not_found': "WARNING: ffmpeg not found. Without it, merging audio and video is not possible.",
        'ffmpeg_install_win': "Download ffmpeg from https://ffmpeg.org/download.html and add its bin folder to PATH.",
        'ffmpeg_install_mac': "Run in terminal: brew install ffmpeg",
        'ffmpeg_install_linux': "Run in terminal: sudo apt-get install ffmpeg",
        'continue_without_ffmpeg': "Continue without merging audio and video?",
        'download_custom_folder': "Select a custom download folder:",
        'folder_no_permission': "Cannot write files to {folder}. Insufficient permissions.",
        'using_default_folder': "Default folder will be used: {default}",
        'choose_video_url': "Enter YouTube video URL:",
        'start_download': "Start Download",
        'download_started': "Download started...",
        'download_complete': "Download complete!",
        'file_saved': "File successfully saved:",
        'file_size': "File size: {size} bytes",
        'file_zero': "WARNING: File size is zero!",
        'download_error': "Error during download:",
        'choose_format': "Download format:",
        'format_1': "Video + Audio (single file)",
        'format_2': "Video Only (no audio)",
        'format_3': "Audio Only",
        'format_4': "Video and Audio (separate files)",
        'choose_video_quality': "Video Quality:",
        'quality_2160': "2160p (4K)",
        'quality_1440': "1440p (2K)",
        'quality_1080': "1080p (Full HD)",
        'quality_720': "720p (HD)",
        'quality_480': "480p (SD)",
        'quality_360': "360p (Low)",
        'default_quality': "Default (best available)",
        'choose_audio_quality': "Audio Quality:",
        'audio_best': "Best (up to 320kbps)",
        'audio_medium': "Medium (up to 192kbps)",
        'audio_low': "Low (up to 128kbps)",
        'audio_min': "Minimum (up to 64kbps)",
        'browse': "Browse",
        'downloading': "Downloading: {percent}%",
        'url_empty': "URL is not entered!"
    },
    'es': {
        'select_language': "Seleccione el idioma (uk/en/es): ",
        'disclaimer': (
            "=====================================================================\n"
            "DISCLAIMER:\n"
            "Este proyecto ha sido creado únicamente con fines educativos.\n"
            "El autor no respalda ni fomenta el uso de esta herramienta para\n"
            "la infracción de derechos de autor u otras actividades ilegales.\n"
            "El usuario asume toda la responsabilidad por el uso de este programa.\n"
            "=====================================================================\n"
            "¿Acepta estos términos?"
        ),
        'consent_decline': "No aceptó los términos. Saliendo del programa.",
        'ffmpeg_not_found': "ADVERTENCIA: No se encontró ffmpeg. Sin él, no es posible combinar audio y video.",
        'ffmpeg_install_win': "Descargue ffmpeg desde https://ffmpeg.org/download.html y añada su carpeta bin a PATH.",
        'ffmpeg_install_mac': "Ejecute en la terminal: brew install ffmpeg",
        'ffmpeg_install_linux': "Ejecute en la terminal: sudo apt-get install ffmpeg",
        'continue_without_ffmpeg': "¿Continuar sin combinar audio y video?",
        'download_custom_folder': "Seleccione una carpeta de descarga personalizada:",
        'folder_no_permission': "No se pueden escribir archivos en {folder}. Permisos insuficientes.",
        'using_default_folder': "Se usará la carpeta predeterminada: {default}",
        'choose_video_url': "Introduzca la URL del video de YouTube:",
        'start_download': "Iniciar descarga",
        'download_started': "Descarga iniciada...",
        'download_complete': "¡Descarga completa!",
        'file_saved': "Archivo guardado exitosamente:",
        'file_size': "Tamaño del archivo: {size} bytes",
        'file_zero': "ADVERTENCIA: ¡El archivo tiene tamaño cero!",
        'download_error': "Error durante la descarga:",
        'choose_format': "Formato de descarga:",
        'format_1': "Video + Audio (archivo único)",
        'format_2': "Solo video (sin audio)",
        'format_3': "Solo audio",
        'format_4': "Video y Audio (archivos separados)",
        'choose_video_quality': "Calidad de video:",
        'quality_2160': "2160p (4K)",
        'quality_1440': "1440p (2K)",
        'quality_1080': "1080p (Full HD)",
        'quality_720': "720p (HD)",
        'quality_480': "480p (SD)",
        'quality_360': "360p (Baja)",
        'default_quality': "Por defecto (el mejor)",
        'choose_audio_quality': "Calidad de audio:",
        'audio_best': "La mejor (hasta 320kbps)",
        'audio_medium': "Media (hasta 192kbps)",
        'audio_low': "Baja (hasta 128kbps)",
        'audio_min': "Mínima (hasta 64kbps)",
        'browse': "Examinar",
        'downloading': "Descargando: {percent}%",
        'url_empty': "¡No se ingresó ninguna URL!"
    }
}

def msg(key, **kwargs):
    text = MESSAGES[LANG].get(key, "")
    return text.format(**kwargs) if kwargs else text

def check_ffmpeg():
    if shutil.which("ffmpeg"):
        return True
    messagebox.showwarning("Warning", msg('ffmpeg_not_found'))
    if sys.platform.startswith('win'):
        messagebox.showinfo("Info", msg('ffmpeg_install_win'))
    elif sys.platform.startswith('darwin'):
        messagebox.showinfo("Info", msg('ffmpeg_install_mac'))
    else:
        messagebox.showinfo("Info", msg('ffmpeg_install_linux'))
    if messagebox.askyesno("Confirm", msg('continue_without_ffmpeg')):
        return False
    else:
        messagebox.showerror("Error", msg('consent_decline'))
        sys.exit(1)

def test_file_permissions(path):
    try:
        test_file = os.path.join(path, ".test_write_permissions")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (IOError, PermissionError):
        messagebox.showwarning("Warning", msg('folder_no_permission', folder=path))
        return False

# Перевірка URL на відповідність YouTube
YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+')
def is_valid_url(url):
    return bool(YOUTUBE_REGEX.match(url))

def get_download_format(format_choice, audio_quality, has_ffmpeg):
    if format_choice == "1":
        return "bestvideo+bestaudio/best" if has_ffmpeg else "best"
    elif format_choice == "2":
        return "bestvideo/best[vcodec!=none]"
    elif format_choice == "3":
        quality_map = {
            msg('audio_best'): "bestaudio",
            msg('audio_medium'): "bestaudio[abr<=192]",
            msg('audio_low'): "bestaudio[abr<=128]",
            msg('audio_min'): "bestaudio[abr<=64]"
        }
        return quality_map.get(audio_quality, "bestaudio")
    elif format_choice == "4":
        return "bestvideo,bestaudio"
    return "best"

def get_quality_format(video_quality, format_choice, has_ffmpeg):
    quality_map = {
        msg('quality_2160'): "2160",
        msg('quality_1440'): "1440",
        msg('quality_1080'): "1080",
        msg('quality_720'): "720",
        msg('quality_480'): "480",
        msg('quality_360'): "360"
    }
    height_limit = quality_map.get(video_quality)
    if height_limit:
        if format_choice in ["1", "4"]:
            return f"bestvideo[height<={height_limit}]+bestaudio/best[height<={height_limit}]" if has_ffmpeg else f"best[height<={height_limit}]"
        elif format_choice == "2":
            return f"bestvideo[height<={height_limit}]/best[height<={height_limit}][vcodec!=none]"
    return None

class YouTubeDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("700x750")
        self.configure(bg="#2d2d2d")
        self._set_dark_theme()
        
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="")
        
        self.steps = [
            "Підготовка до завантаження",
            "Завантаження відео",
            "Завантаження аудіо / Обробка",
            "Об'єднання / Збереження",
            "Завершено"
        ]
        self.step_thresholds = [20, 40, 60, 80, 100]
        self.checklist_labels = []
        
        self.main_frame = ttk.Frame(self, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self._create_widgets()
        
        self.has_ffmpeg = check_ffmpeg()
        try:
            self.iconbitmap("icon.ico")
        except:
            pass

    def _set_dark_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        bg_color = "#2d2d2d"
        fg_color = "#e0e0e0"
        accent_color = "#4caf50"
        field_bg = "#3c3f41"
        button_bg = "#4caf50"
        hover_bg = "#43a047"
        
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TButton", background=button_bg, foreground=fg_color, borderwidth=0, 
                        font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", 
                  background=[('pressed', hover_bg), ('active', hover_bg)],
                  foreground=[('pressed', 'white'), ('active', 'white')])
        style.configure("TEntry", fieldbackground=field_bg, foreground=fg_color, borderwidth=1)
        style.configure("TCombobox", fieldbackground=field_bg, foreground=bg_color, background=bg_color)
        # Налаштування для випадаючого списку Combobox
        self.option_add("*TCombobox*Listbox.background", field_bg)
        self.option_add("*TCombobox*Listbox.foreground", fg_color)
        self.option_add("*TCombobox*Listbox.selectBackground", accent_color)
        self.option_add("*TCombobox*Listbox.selectForeground", fg_color)
        style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
        style.configure("TProgressbar", background=accent_color, troughcolor=field_bg,
                        borderwidth=0, thickness=20)
        self.configure(bg=bg_color)
    
    def _create_widgets(self):
        # URL відео
        url_frame = ttk.Frame(self.main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(url_frame, text=msg('choose_video_url')).pack(anchor="w", pady=(0, 5))
        self.url_entry = ttk.Entry(url_frame, width=70)
        self.url_entry.pack(fill=tk.X, ipady=5)
        
        # Папка завантаження
        folder_frame = ttk.Frame(self.main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(folder_frame, text=msg('download_custom_folder')).pack(anchor="w", pady=(0, 5))
        folder_input_frame = ttk.Frame(folder_frame)
        folder_input_frame.pack(fill=tk.X)
        self.folder_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.folder_entry = ttk.Entry(folder_input_frame, textvariable=self.folder_var)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        browse_button = ttk.Button(folder_input_frame, text=msg('browse'), command=self._browse_folder)
        browse_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Формат завантаження
        format_frame = ttk.Frame(self.main_frame)
        format_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(format_frame, text=msg('choose_format')).pack(anchor="w", pady=(0, 5))
        formats_container = ttk.Frame(format_frame)
        formats_container.pack(fill=tk.X)
        self.format_var = tk.StringVar(value="1")
        formats = [
            ("1", msg('format_1')),
            ("2", msg('format_2')),
            ("3", msg('format_3')),
            ("4", msg('format_4'))
        ]
        for i, (val, text) in enumerate(formats):
            row_num = i // 2
            col_num = i % 2
            radio_frame = ttk.Frame(formats_container)
            radio_frame.grid(row=row_num, column=col_num, sticky="w", padx=(0, 10), pady=5)
            radio = ttk.Radiobutton(radio_frame, text=text, variable=self.format_var, value=val)
            radio.pack(side=tk.LEFT)
        
        # Якість відео
        quality_frame = ttk.Frame(self.main_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(quality_frame, text=msg('choose_video_quality')).pack(anchor="w", pady=(0, 5))
        self.video_quality_options = [
            msg('default_quality'),
            msg('quality_2160'),
            msg('quality_1440'),
            msg('quality_1080'),
            msg('quality_720'),
            msg('quality_480'),
            msg('quality_360')
        ]
        self.video_quality_var = tk.StringVar(value=self.video_quality_options[0])
        self.video_quality_combo = ttk.Combobox(quality_frame, textvariable=self.video_quality_var, 
                                                values=self.video_quality_options, state="readonly", height=10)
        self.video_quality_combo.pack(fill=tk.X, ipady=5)
        
        # Якість аудіо
        audio_frame = ttk.Frame(self.main_frame)
        audio_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(audio_frame, text=msg('choose_audio_quality')).pack(anchor="w", pady=(0, 5))
        self.audio_quality_options = [
            msg('audio_best'),
            msg('audio_medium'),
            msg('audio_low'),
            msg('audio_min')
        ]
        self.audio_quality_var = tk.StringVar(value=self.audio_quality_options[0])
        self.audio_quality_combo = ttk.Combobox(audio_frame, textvariable=self.audio_quality_var, 
                                                values=self.audio_quality_options, state="readonly", height=10)
        self.audio_quality_combo.pack(fill=tk.X, ipady=5)
        
        # Кнопка старту завантаження
        self.download_button = ttk.Button(self.main_frame, text=msg('start_download'), command=self.start_download_thread)
        self.download_button.pack(pady=20, ipadx=10, ipady=5)
        
        # Статус завантаження
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor="center", font=("Segoe UI", 11, "bold"))
        self.status_label.pack(fill=tk.X)
        
        # Прогрес-бар і відсоток
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill=tk.X)
        self.percent_label = ttk.Label(progress_frame, text="0%", font=("Segoe UI", 10, "bold"))
        self.percent_label.pack(anchor="e", pady=(5, 0))
        
        # Чекліст етапів завантаження
        checklist_frame = ttk.Frame(self.main_frame)
        checklist_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(checklist_frame, text="Етапи завантаження:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        for step in self.steps:
            label = ttk.Label(checklist_frame, text="☐ " + step)
            label.pack(anchor="w", padx=10)
            self.checklist_labels.append(label)
    
    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
    
    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", msg('url_empty'))
            return
        if not is_valid_url(url):
            messagebox.showerror("Error", "Невірний URL YouTube!")
            return
        
        self.download_button.configure(state="disabled")
        
        download_folder = self.folder_var.get().strip()
        if not os.path.isdir(download_folder) or not test_file_permissions(download_folder):
            default_path = str(Path.home() / "Downloads")
            messagebox.showinfo("Info", msg('using_default_folder', default=default_path))
            download_folder = default_path
            self.folder_var.set(download_folder)
        
        self.progress_var.set(0)
        self.percent_label.config(text="0%")
        self.status_var.set(msg('downloading', percent="0"))
        self._update_checklist(0)
        
        format_choice = self.format_var.get()
        video_quality = self.video_quality_var.get()
        audio_quality = self.audio_quality_var.get()
        
        format_option = get_download_format(format_choice, audio_quality, self.has_ffmpeg)
        quality_format = get_quality_format(video_quality, format_choice, self.has_ffmpeg)
        if quality_format:
            format_option = quality_format
        
        merge_format = None
        postprocessor_args = {}
        if format_choice == "1" and self.has_ffmpeg:
            merge_format = "mp4"
            postprocessor_args = {'ffmpeg': ['-c:a', 'aac', '-b:a', '192k']}
        
        ydl_opts = {
            'format': format_option,
            'noplaylist': True,
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.my_hook],
            'quiet': True,
        }
        if merge_format and self.has_ffmpeg:
            ydl_opts['merge_output_format'] = merge_format
        if postprocessor_args and self.has_ffmpeg:
            ydl_opts['postprocessor_args'] = postprocessor_args
        
        threading.Thread(target=self.download_video, args=(url, ydl_opts, download_folder), daemon=True).start()
    
    def my_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes_estimate', None)
            if total:
                percent = downloaded / total * 100
            else:
                try:
                    percent = float(d.get('_percent_str', '0%').strip('%').strip())
                except ValueError:
                    percent = 0
            self.after(10, lambda: self._update_progress(percent))
        elif d['status'] == 'finished':
            self.after(10, lambda: self._download_finished(d))
    
    def _update_progress(self, percent):
        self.progress_var.set(percent)
        self.status_var.set(msg('downloading', percent=f"{percent:.1f}"))
        self.percent_label.config(text=f"{percent:.1f}%")
        self._update_checklist(percent)
    
    def _update_checklist(self, percent):
        for idx, threshold in enumerate(self.step_thresholds):
            if percent >= threshold:
                self.checklist_labels[idx].configure(text="☑ " + self.steps[idx])
            else:
                self.checklist_labels[idx].configure(text="☐ " + self.steps[idx])
    
    def _download_finished(self, d):
        filename = d.get('filename', '')
        error_occurred = False
        if filename and os.path.exists(filename):
            filesize = os.path.getsize(filename)
            info_text = f"{msg('file_saved')} {os.path.basename(filename)}\n{msg('file_size', size=filesize)}"
            if filesize == 0:
                info_text += f"\n{msg('file_zero')}"
                error_occurred = True
            messagebox.showinfo("Info", info_text)
        else:
            messagebox.showerror("Error", msg('download_error') + " Файл не знайдено.")
            error_occurred = True
        
        if not error_occurred:
            self.status_var.set(msg('download_complete'))
        self.download_button.configure(state="normal")
    
    def download_video(self, url, ydl_opts, download_folder):
        try:
            self.after(0, lambda: messagebox.showinfo("Info", msg('download_started')))
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"{msg('download_error')} {e}"))
            self.after(0, lambda: self.download_button.configure(state="normal"))

def select_language():
    lang_window = tk.Tk()
    lang_window.title("Select Language / Виберіть мову / Seleccione el idioma")
    lang_window.geometry("300x200")
    lang_var = tk.StringVar(value="en")
    tk.Label(lang_window, text="Select Language / Виберіть мову / Seleccione el idioma:", font=("Segoe UI", 10, "bold")).pack(pady=10)
    
    languages = [
        ("Українська", "uk"),
        ("English", "en"),
        ("Español", "es")
    ]
    for text, code in languages:
        tk.Radiobutton(lang_window, text=text, variable=lang_var, value=code, font=("Segoe UI", 10)).pack(anchor="w", padx=20)
    
    def on_select():
        lang_window.destroy()
    tk.Button(lang_window, text="OK", command=on_select, font=("Segoe UI", 10, "bold")).pack(pady=20)
    lang_window.mainloop()
    return lang_var.get()

def show_disclaimer():
    root_temp = tk.Tk()
    root_temp.withdraw()
    consent = messagebox.askyesno("Disclaimer", msg('disclaimer'))
    root_temp.destroy()
    if not consent:
        messagebox.showerror("Error", msg('consent_decline'))
        sys.exit(1)

if __name__ == "__main__":
    LANG = select_language()
    show_disclaimer()
    app = YouTubeDownloaderApp()
    app.mainloop()
