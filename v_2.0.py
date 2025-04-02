# pip install yt_dlp
# https://www.gyan.dev/ffmpeg/builds/

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import time
import yt_dlp

# --- MESSAGES словник ---
MESSAGES = {
    'uk': {
        'select_language': "Виберіть мову (uk/en): ",
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
        'select_language': "Choose language (uk/en): ",
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
    }
}

def msg(key, **kwargs):
    text = MESSAGES[LANG].get(key, "")
    return text.format(**kwargs) if kwargs else text

# --- Функції перевірок та діагностики ---
def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
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

# --- Головний клас додатку ---
class YouTubeDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("650x700")
        self.configure(bg="#1e1e1e")
        self._set_dark_theme()
        
        # Змінна для збереження прогресу
        self.progress_var = tk.DoubleVar(value=0)
        
        # Змінна для зберігання тексту статусу
        self.status_var = tk.StringVar(value="")
        
        # Створення чеклісту (етапи завантаження)
        self.steps = [
            "Підготовка до завантаження",
            "Завантаження відео",
            "Завантаження аудіо / Обробка",
            "Об'єднання / Збереження",
            "Завершено"
        ]
        # Ліміти відсотків для відмітки кожного етапу
        self.step_thresholds = [20, 40, 60, 80, 100]
        self.checklist_labels = []
        
        # Frame для кращої організації UI
        self.main_frame = ttk.Frame(self, padding="20 20 20 20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Елементи форми
        self._create_widgets()
        
        # Перевірка ffmpeg
        self.has_ffmpeg = check_ffmpeg()
        
        # Додаємо іконку (якщо доступна)
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
    
    def _set_dark_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        bg_color = "#1e1e1e"
        fg_color = "#ffffff"
        accent_color = "#3498db"
        field_bg = "#2c2c2c"
        button_bg = "#3498db"
        hover_bg = "#2980b9"
        
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TButton", background=button_bg, foreground=fg_color, borderwidth=0, 
                        font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton", 
                  background=[('pressed', hover_bg), ('active', hover_bg)],
                  foreground=[('pressed', 'white'), ('active', 'white')])
        style.configure("TEntry", fieldbackground=field_bg, foreground=fg_color, 
                        borderwidth=1)
        style.configure("TCombobox", fieldbackground=field_bg, foreground=fg_color, 
                        background=bg_color)
        style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
        style.configure("TProgressbar", background=accent_color, troughcolor=field_bg,
                        borderwidth=0, thickness=20)
        self.configure(bg=bg_color)
    
    def _create_widgets(self):
        # URL відео (row 0)
        url_frame = ttk.Frame(self.main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(url_frame, text=msg('choose_video_url')).pack(anchor="w", pady=(0, 5))
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.pack(fill=tk.X, ipady=5)
        
        # Папка завантаження (row 1)
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
        
        # Формат завантаження (row 2)
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
        
        # Якість відео (row 3)
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
        
        # Якість аудіо (row 4)
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
        
        # Кнопка старту завантаження (row 5)
        self.download_button = ttk.Button(self.main_frame, text=msg('start_download'), 
                                          command=self.start_download_thread)
        self.download_button.pack(pady=20, ipadx=10, ipady=5)
        
        # Статус завантаження (row 6)
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                      anchor="center", font=("Segoe UI", 10, "bold"))
        self.status_label.pack(fill=tk.X)
        
        # Прогрес-бар (row 7)
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, 
                                            maximum=100, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 20))
        
        # Чекліст (етапи завантаження) (row 8)
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
        
        self.download_button.configure(state="disabled")
        
        download_folder = self.folder_var.get().strip()
        if not os.path.isdir(download_folder) or not test_file_permissions(download_folder):
            default_path = str(Path.home() / "Downloads")
            messagebox.showinfo("Info", msg('using_default_folder', default=default_path))
            download_folder = default_path
            self.folder_var.set(download_folder)
        
        self.progress_var.set(0)
        self.status_var.set(msg('downloading', percent="0.0"))
        self._update_checklist(0)
        
        format_choice = self.format_var.get()
        video_quality = self.video_quality_var.get()
        audio_quality = self.audio_quality_var.get()
        format_option = ""
        merge_format = None
        postprocessor_args = {}
        
        if format_choice == "1":
            if self.has_ffmpeg:
                format_option = "bestvideo+bestaudio/best"
                merge_format = "mp4"
                postprocessor_args = {'ffmpeg': ['-c:a', 'aac', '-b:a', '192k']}
            else:
                format_option = "best"
        elif format_choice == "2":
            format_option = "bestvideo/best[vcodec!=none]"
        elif format_choice == "3":
            if audio_quality == msg('audio_best'):
                format_option = "bestaudio"
            elif audio_quality == msg('audio_medium'):
                format_option = "bestaudio[abr<=192]"
            elif audio_quality == msg('audio_low'):
                format_option = "bestaudio[abr<=128]"
            elif audio_quality == msg('audio_min'):
                format_option = "bestaudio[abr<=64]"
        elif format_choice == "4":
            format_option = "bestvideo,bestaudio"
        
        quality_map = {
            msg('quality_2160'): "2160",
            msg('quality_1440'): "1440",
            msg('quality_1080'): "1080",
            msg('quality_720'): "720",
            msg('quality_480'): "480",
            msg('quality_360'): "360"
        }
        if video_quality != msg('default_quality'):
            height_limit = quality_map.get(video_quality, "")
            if height_limit:
                if format_choice in ["1", "4"]:
                    if self.has_ffmpeg:
                        format_option = f"bestvideo[height<={height_limit}]+bestaudio/best[height<={height_limit}]"
                    else:
                        format_option = f"best[height<={height_limit}]"
                elif format_choice == "2":
                    format_option = f"bestvideo[height<={height_limit}]/best[height<={height_limit}][vcodec!=none]"
        
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
            if '_percent_str' in d:
                percent_str = d['_percent_str'].strip().replace('%', '')
                try:
                    percent = float(percent_str)
                    self.after(10, lambda: self._update_progress(percent))
                except ValueError:
                    pass
        elif d['status'] == 'finished':
            # Анімація заповнення до 100%
            self.after(10, lambda: self.animate_to_100(int(self.progress_var.get())))
            self.after(10, lambda: self._download_finished(d))
    
    def _update_progress(self, percent):
        self.progress_var.set(percent)
        self.status_var.set(msg('downloading', percent=f"{percent:.1f}"))
        self._update_checklist(percent)
    
    def _update_checklist(self, percent):
        # Оновлення чеклісту відповідно до досягнутого порогу
        for idx, threshold in enumerate(self.step_thresholds):
            if percent >= threshold:
                self.checklist_labels[idx].configure(text="☑ " + self.steps[idx])
            else:
                self.checklist_labels[idx].configure(text="☐ " + self.steps[idx])
    
    def animate_to_100(self, current):
        if current < 100:
            current += 1
            self.progress_var.set(current)
            self.status_var.set(msg('downloading', percent=f"{current:.1f}"))
            self._update_checklist(current)
            self.after(20, lambda: self.animate_to_100(current))
    
    def _download_finished(self, d):
        self.download_button.configure(state="normal")
        filename = d.get('filename', '')
        if filename and os.path.exists(filename):
            filesize = os.path.getsize(filename)
            info_text = f"{msg('file_saved')} {os.path.basename(filename)}\n{msg('file_size', size=filesize)}"
            if filesize == 0:
                info_text += f"\n{msg('file_zero')}"
            messagebox.showinfo("Info", info_text)
    
    def download_video(self, url, ydl_opts, download_folder):
        try:
            self.after(0, lambda: messagebox.showinfo("Info", msg('download_started')))
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"{msg('download_error')} {e}"))
            self.after(0, lambda: self.download_button.configure(state="normal"))

def select_language():
    root_temp = tk.Tk()
    root_temp.withdraw()
    lang_choice = simpledialog.askstring("Language", MESSAGES['en']['select_language'] + "\n" + MESSAGES['uk']['select_language'])
    root_temp.destroy()
    if lang_choice and lang_choice.lower() in ['uk', 'en']:
        return lang_choice.lower()
    else:
        messagebox.showinfo("Info", "Невірний вибір, встановлено мову за замовчуванням: uk")
        return 'uk'

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
