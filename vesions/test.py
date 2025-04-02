# pip install yt_dlp
# https://www.gyan.dev/ffmpeg/builds/

import yt_dlp
import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import shutil
import time
import json

# Define languages and their translations
LANGUAGES = {
    "uk": {  # Ukrainian
        "app_title": "=== Завантажувач відео з YouTube ===",
        "disclaimer": """
ВІДМОВА ВІД ВІДПОВІДАЛЬНОСТІ:
Цей інструмент створено виключно в навчальних цілях для демонстрації роботи з відео API.
Використовуючи цю програму, ви погоджуєтесь:
- Не порушувати авторські права та умови використання сервісів
- Завантажувати тільки той контент, на який ви маєте права або дозвіл
- Не використовувати програму для комерційних цілей без дозволу власників контенту

Автор програми не несе відповідальності за будь-яке неправомірне використання цього інструменту.
Вся відповідальність за використання програми покладається на користувача.
        """,
        "accept_terms": "Я погоджуюсь з умовами (так/ні): ",
        "terms_rejected": "Умови не прийнято. Програма завершує роботу.",
        "enter_url": "Введіть URL відео YouTube: ",
        "ffmpeg_not_found": "УВАГА: ffmpeg не знайдено. Без нього неможливо об'єднати аудіо та відео.",
        "install_ffmpeg": "Будь ласка, встановіть ffmpeg:",
        "win_install_ffmpeg": "1. Завантажте ffmpeg з https://ffmpeg.org/download.html\n2. Розпакуйте архів та додайте шлях до bin-папки в змінну середовища PATH",
        "mac_install_ffmpeg": "Виконайте в терміналі: brew install ffmpeg",
        "linux_install_ffmpeg": "Виконайте в терміналі: sudo apt-get install ffmpeg",
        "continue_without_ffmpeg": "Продовжити без об'єднання аудіо та відео? (так/ні): ",
        "download_canceled": "Завантаження скасовано. Будь ласка, встановіть ffmpeg і спробуйте знову.",
        "custom_folder": "Бажаєте вибрати власну папку для завантаження відео? (так/ні): ",
        "selected_folder": "Вибрана папка: ",
        "write_permission_error": "УВАГА: Неможливо записати файли в {0}. Недостатньо прав.",
        "using_default_folder": "Буде використано стандартну папку: {0}",
        "selection_canceled": "Вибір скасовано. Буде використано стандартну папку: {0}",
        "step1_format": "\n=== КРОК 1: Вибір формату ===",
        "available_formats": "Доступні формати:",
        "format_1": "1. Відео + аудіо (один файл)",
        "format_2": "2. Тільки відео (без звуку)",
        "format_3": "3. Тільки аудіо",
        "format_4": "4. Завантажити і відео, і аудіо (окремими файлами)",
        "select_format": "Виберіть формат (1-4): ",
        "invalid_choice": "Невірний вибір. Буде використано найкращу доступну якість.",
        "best_available": "Найкраща доступна",
        "warning_no_ffmpeg": "УВАГА: ffmpeg не встановлено, тому буде використано найкращий доступний формат без об'єднання.",
        "best_available_format": "Найкращий доступний формат",
        "video_only": "Тільки відео (без звуку)",
        "video_audio_separate": "Відео та аудіо (окремими файлами)",
        "step2_quality": "\n=== КРОК 2: Вибір якості відео ===",
        "choose_quality": "Бажаєте вибрати якість відео? (так/ні): ",
        "available_quality": "Доступні варіанти якості:",
        "quality_1": "1. 2160p (4K)",
        "quality_2": "2. 1440p (2K)",
        "quality_3": "3. 1080p (Full HD)",
        "quality_4": "4. 720p (HD)",
        "quality_5": "5. 480p (SD)",
        "quality_6": "6. 360p (Low)",
        "quality_note": "Примітка: якщо відео не матиме вказаної якості, воно завантажиться БЕЗ звуку",
        "select_quality": "Виберіть якість (1-6): ",
        "best_quality": "Найкраща доступна",
        "audio_quality_options": "Доступні варіанти якості аудіо:",
        "audio_1": "1. Найкраща якість (до 320kbps)",
        "audio_2": "2. Середня якість (до 192kbps)",
        "audio_3": "3. Низька якість (до 128kbps)",
        "audio_4": "4. Мінімальна якість (до 64kbps)",
        "select_audio_quality": "Виберіть якість аудіо (1-4): ",
        "best_audio": "Аудіо - найкраща якість",
        "medium_audio": "Аудіо - середня якість",
        "low_audio": "Аудіо - низька якість",
        "minimal_audio": "Аудіо - мінімальна якість",
        "error_video_info": "Помилка при отриманні інформації про відео: {0}",
        "downloading": "Завантаження: {0} швидкість: {1} залишилось: {2}",
        "download_complete": "Завантаження завершено! Перевірка файлу...",
        "file_saved": "Файл {0} збережено ({1} байт)",
        "file_empty": "УВАГА: Файл має нульовий розмір! Можливо, виникла проблема із завантаженням.",
        "permission_error": "УВАГА: Проблема з правами доступу до папки: {0}",
        "error_checking_version": "Помилка при перевірці версії yt-dlp: {0}",
        "version_error": "Помилка визначення версії",
        "unable_to_open_folder": "Неможливо відкрити папку: {0}",
        "error_opening_folder": "Помилка при спробі відкрити папку: {0}",
        "permission_test_fail": "Помилка: Неможливо знайти папку з правами на запис. Завантаження неможливе.",
        "alt_folder_attempt": "Спроба використання альтернативної папки: {0}",
        "summary_info": "\n--- Підсумкова інформація ---",
        "video_title": "Назва відео: {0}",
        "video_url": "URL відео: {0}",
        "download_folder": "Папка завантаження: {0}",
        "selected_format": "Вибраний формат: {0}",
        "ytdlp_version": "Версія yt-dlp: {0}",
        "expected_file": "Очікуваний файл: {0}",
        "start_download": "Розпочати завантаження? (так/ні): ",
        "download_started": "Завантаження розпочато...",
        "file_saved_success": "Файл успішно збережено: {0}",
        "file_size": "Розмір файлу: {0} байт",
        "file_not_found": "Не вдалося знайти очікуваний файл. Пошук нещодавно створених файлів...",
        "recent_files": "Нещодавно створені файли:",
        "recent_files_notice": "Возможно, один з цих файлів є вашим завантаженим відео.",
        "no_recent_files": "Не знайдено нещодавно створених файлів у папці завантаження.",
        "download_problem": "ПРОБЛЕМА: Відео не було збережено. Причини можуть бути:",
        "reason_1": "1. Недостатньо місця на диску",
        "reason_2": "2. Проблеми з правами доступу",
        "reason_3": "3. Антивірус блокує запис файлу",
        "reason_4": "4. Несумісність з поточною версією yt-dlp",
        "download_finished": "Завантаження завершено!",
        "open_folder": "Бажаєте відкрити папку з завантаженням? (так/ні): ",
        "folder_opened": "Папку відкрито у файловому менеджері",
        "folder_open_failed": "Не вдалося відкрити папку автоматично",
        "download_error": "Помилка при завантаженні: {0}",
        "diagnostics": "Спроба виконати діагностику...",
        "diagnostics_title": "\n--- Діагностика ---",
        "folder_check": "1. Перевірка папки: {0}",
        "folder_exists": "   Папка існує: {0}",
        "write_permission": "   Права на запис: {0}",
        "free_space": "   Вільне місце: {0} байт",
        "folder_not_exists": "   Папка не існує!",
        "version_check": "2. Версія yt-dlp:",
        "version_detect_failed": "   Не вдалося визначити версію",
        "simple_download": "3. Спроба скачати за спрощеними параметрами:",
        "simple_download_to": "   Завантаження в {0}...",
        "simple_success": "   Успішно! Файл створено ({0} байт)",
        "simple_error": "   Помилка: Файл не створено",
        "simple_download_error": "   Помилка при спрощеному завантаженні: {0}",
        "download_cancelled": "Завантаження скасовано.",
        "video_info_failed": "Не вдалося отримати інформацію про відео. Завантаження скасовано.",
        "select_language": "Виберіть мову / Select language / Seleccione idioma (1-3):",
        "language_1": "1. Українська",
        "language_2": "2. English",
        "language_3": "3. Español",
        "language_selected": "Обрано українську мову / Selected Ukrainian language / Idioma ucraniano seleccionado"
    },
    "en": {  # English
        # Here you would add your English translations
        # For demonstration purposes, I'll include just a few keys
        "app_title": "=== YouTube Video Downloader ===",
        "select_language": "Виберіть мову / Select language / Seleccione idioma (1-3):",
        "language_1": "1. Українська",
        "language_2": "2. English",
        "language_3": "3. Español",
        "language_selected": "Selected English language / Обрано англійську мову / Idioma inglés seleccionado"
        # Add the rest of your English translations here
    },
    "es": {  # Spanish
        # Here you would add your Spanish translations
        # For demonstration purposes, I'll include just a few keys
        "app_title": "=== Descargador de videos de YouTube ===",
        "select_language": "Виберіть мову / Select language / Seleccione idioma (1-3):",
        "language_1": "1. Українська",
        "language_2": "2. English",
        "language_3": "3. Español",
        "language_selected": "Idioma español seleccionado / Обрано іспанську мову / Selected Spanish language"
        # Add the rest of your Spanish translations here
    }
}

# Initialize default language
current_language = "uk"  # Default to Ukrainian
strings = LANGUAGES[current_language]

def select_language():
    """Allows user to select a language"""
    global current_language, strings
    
    # Use multilingual prompt for language selection
    print("Виберіть мову / Select language / Seleccione idioma (1-3):")
    print("1. Українська")
    print("2. English")
    print("3. Español")
    
    choice = input("> ").strip()
    
    if choice == "1":
        current_language = "uk"
    elif choice == "2":
        current_language = "en"
    elif choice == "3":
        current_language = "es"
    else:
        # Default to Ukrainian if invalid choice
        current_language = "uk"
    
    strings = LANGUAGES[current_language]
    print(strings["language_selected"])
    print("\n" + strings["app_title"])

def get_string(key, *args):
    """Gets a localized string with optional formatting arguments"""
    if key in strings:
        if args:
            return strings[key].format(*args)
        return strings[key]
    else:
        # Fallback to Ukrainian if string is missing in selected language
        fallback = LANGUAGES["uk"].get(key, f"[Missing string: {key}]")
        if args:
            return fallback.format(*args)
        return fallback

def show_disclaimer():
    """Shows disclaimer and gets user agreement"""
    print("\n" + get_string("disclaimer"))
    
    while True:
        response = input(get_string("accept_terms")).lower()
        if response in ["так", "yes", "sí", "si", "y", "т", "s"]:
            return True
        elif response in ["ні", "no", "н", "n"]:
            print(get_string("terms_rejected"))
            return False
        else:
            # If user input is unclear, ask again
            pass

def check_ffmpeg():
    """Checks if ffmpeg is installed and installs it if necessary"""
    try:
        # Try to execute ffmpeg -version to check if it's available
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print(get_string("ffmpeg_not_found"))
        print(get_string("install_ffmpeg"))
        
        if sys.platform.startswith('win'):
            print(get_string("win_install_ffmpeg"))
        elif sys.platform.startswith('darwin'):  # macOS
            print(get_string("mac_install_ffmpeg"))
        else:  # Linux
            print(get_string("linux_install_ffmpeg"))
            
        choice = input(get_string("continue_without_ffmpeg")).lower()
        if choice in ["так", "yes", "sí", "si", "y", "т", "s"]:
            return False
        else:
            print(get_string("download_canceled"))
            sys.exit(1)

def get_download_path():
    """Opens a dialog window to select download folder"""
    default_path = str(Path.home() / "Downloads")
    
    choice = input(get_string("custom_folder")).lower()
    if choice in ["так", "yes", "sí", "si", "y", "т", "s"]:
        # Initialize Tkinter and hide main window
        root = tk.Tk()
        root.withdraw()  # Hide main window
        root.attributes('-topmost', True)  # Force display on top of other windows
        
        # Open dialog to select folder
        custom_path = filedialog.askdirectory(title="Select download folder")
        
        if custom_path:  # If user selected a folder
            print(get_string("selected_folder", custom_path))
            # Check write permissions to selected folder
            if os.access(custom_path, os.W_OK):
                return custom_path
            else:
                print(get_string("write_permission_error", custom_path))
                print(get_string("using_default_folder", default_path))
                return default_path
        else:  # If user canceled selection
            print(get_string("selection_canceled", default_path))
            return default_path
    else:
        print(get_string("using_default_folder", default_path))
        return default_path

def select_format_and_quality(has_ffmpeg):
    """Two-step selection of format and quality"""
    print(get_string("step1_format"))
    print(get_string("available_formats"))
    print(get_string("format_1"))
    print(get_string("format_2"))
    print(get_string("format_3"))
    print(get_string("format_4"))
    
    format_choice = input(get_string("select_format"))
    
    # Initialize variables to store settings
    format_option = ""
    format_desc = ""
    merge_format = None
    postprocessor_args = {}  # Changed from None to empty dict
    
    # Handle format selection
    if format_choice == "1":  # Video + audio
        if has_ffmpeg:
            format_option = "bestvideo+bestaudio/best"
            format_desc = get_string("format_1")
            merge_format = "mp4"
            # Changed way to pass postprocessor arguments
            postprocessor_args = {
                'ffmpeg': ['-c:a', 'aac', '-b:a', '192k']
            }
        else:
            print(get_string("warning_no_ffmpeg"))
            format_option = "best"
            format_desc = get_string("best_available_format")
            merge_format = None
    elif format_choice == "2":  # Video only
        format_option = "bestvideo/best[vcodec!=none]"
        format_desc = get_string("video_only")
    elif format_choice == "3":  # Audio only
        audio_quality = select_audio_quality()
        format_option = audio_quality["format"]
        format_desc = audio_quality["desc"]
    elif format_choice == "4":  # Video and audio as separate files
        format_option = "bestvideo,bestaudio"
        format_desc = get_string("video_audio_separate")
    else:
        print(get_string("invalid_choice"))
        format_option = "best"
        format_desc = get_string("best_available")
    
    # If video or video+audio selected, proceed to video quality selection
    if format_choice in ["1", "2", "4"]:
        print(get_string("step2_quality"))
        should_choose_quality = input(get_string("choose_quality")).lower()
        
        if should_choose_quality in ["так", "yes", "sí", "si", "y", "т", "s"]:
            video_quality = select_video_quality()
            
            # Modify format according to selected quality
            if format_choice == "1":  # Video + audio
                if has_ffmpeg:
                    if "height<=" in video_quality["format"]:
                        height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                        format_option = f"bestvideo[height<={height_limit}]+bestaudio/best[height<={height_limit}]"
                else:
                    if "height<=" in video_quality["format"]:
                        height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                        format_option = f"best[height<={height_limit}]"
            elif format_choice == "2":  # Video only
                if "height<=" in video_quality["format"]:
                    height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                    format_option = f"bestvideo[height<={height_limit}]/best[height<={height_limit}][vcodec!=none]"
            elif format_choice == "4":  # Video and audio as separate files
                if "height<=" in video_quality["format"]:
                    height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                    format_option = f"bestvideo[height<={height_limit}],bestaudio"
            
            format_desc += f" - {video_quality['desc']}"
    
    return {
        "format": format_option,
        "desc": format_desc,
        "merge_format": merge_format,
        "postprocessor_args": postprocessor_args
    }

def select_video_quality():
    """Allows user to select video quality"""
    print(get_string("available_quality"))
    print(get_string("quality_1"))
    print(get_string("quality_2"))
    print(get_string("quality_3"))
    print(get_string("quality_4"))
    print(get_string("quality_5"))
    print(get_string("quality_6"))
    print(get_string("quality_note"))
    
    quality_choice = input(get_string("select_quality"))
    
    quality_options = {
        "1": {"format": "bestvideo[height<=2160]", "desc": "2160p (4K)"},
        "2": {"format": "bestvideo[height<=1440]", "desc": "1440p (2K)"},
        "3": {"format": "bestvideo[height<=1080]", "desc": "1080p (Full HD)"},
        "4": {"format": "bestvideo[height<=720]", "desc": "720p (HD)"},
        "5": {"format": "bestvideo[height<=480]", "desc": "480p (SD)"},
        "6": {"format": "bestvideo[height<=360]", "desc": "360p (Low)"}
    }
    
    if quality_choice in quality_options:
        return quality_options[quality_choice]
    else:
        print(get_string("invalid_choice"))
        return {"format": "bestvideo", "desc": get_string("best_quality")}

def select_audio_quality():
    """Allows user to select audio quality"""
    print(get_string("audio_quality_options"))
    print(get_string("audio_1"))
    print(get_string("audio_2"))
    print(get_string("audio_3"))
    print(get_string("audio_4"))
    
    quality_choice = input(get_string("select_audio_quality"))
    
    quality_options = {
        "1": {"format": "bestaudio", "desc": get_string("best_audio")},
        "2": {"format": "bestaudio[abr<=192]", "desc": get_string("medium_audio")},
        "3": {"format": "bestaudio[abr<=128]", "desc": get_string("low_audio")},
        "4": {"format": "bestaudio[abr<=64]", "desc": get_string("minimal_audio")}
    }
    
    if quality_choice in quality_options:
        return quality_options[quality_choice]
    else:
        print(get_string("invalid_choice"))
        return {"format": "bestaudio", "desc": get_string("best_audio")}

def get_video_info(url, ydl_opts):
    """Gets video information"""
    # Create copy of parameters to avoid changing original
    info_opts = ydl_opts.copy()
    info_opts['skip_download'] = True  # Don't download, just get info
    
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            print(get_string("error_video_info", str(e)))
            return None

def my_hook(d):
    """Function to track download progress"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        filename = d.get('filename', 'video')
        print(f"\r{get_string('downloading', percent, speed, eta)}", end='')
    
    elif d['status'] == 'finished':
        print(f"\n{get_string('download_complete')}")
        filename = d.get('filename', 'unknown file')
        
        # Check file size
        if os.path.exists(filename):
            filesize = os.path.getsize(filename)
            print(get_string("file_saved", os.path.basename(filename), filesize))
            
            # Check if file is not empty
            if filesize == 0:
                print(get_string("file_empty"))

def test_file_permissions(path):
    """Checks write permissions to specified folder"""
    try:
        test_file = os.path.join(path, ".test_write_permissions")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (IOError, PermissionError) as e:
        print(get_string("permission_error", str(e)))
        return False

def check_yt_dlp_version():
    """Checks yt-dlp version and outputs it"""
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            version_dict = ydl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=False, process=False)
            if hasattr(ydl, 'version'):
                return ydl.version
            else:
                return get_string("version_error")
    except Exception as e:
        print(get_string("error_checking_version", str(e)))
        return get_string("version_error")

def open_download_directory(directory):
    """Opens folder with downloaded file in file manager"""
    try:
        if os.path.exists(directory):
            if sys.platform.startswith('win'):  # Windows
                os.startfile(directory)
                return True
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', directory], check=True)
                return True
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.run(['xdg-open', directory], check=True)
                return True
            else:
                print(get_string("unable_to_open_folder", "unsupported operating system"))
                return False
        else:
            print(get_string("unable_to_open_folder", f"path {directory} does not exist"))
            return False
    except Exception as e:
        print(get_string("error_opening_folder", str(e)))
        return False

def download_yt_video(url):
    """Downloads video from YouTube with selected parameters"""
    # Check for ffmpeg
    has_ffmpeg = check_ffmpeg()
    
    # Get download path
    download_path = get_download_path()
    
    # Check write permissions to selected folder
    if not test_file_permissions(download_path):
        alt_path = os.path.join(os.getcwd(), "downloads")
        print(get_string("alt_folder_attempt", alt_path))
        os.makedirs(alt_path, exist_ok=True)
        if test_file_permissions(alt_path):
            download_path = alt_path
        else:
            print(get_string("permission_test_fail"))
            return
    
    # Two-step selection of format and quality
    format_info = select_format_and_quality(has_ffmpeg)
    
    # Basic settings
    ydl_opts = {
        'format': format_info["format"],
        'noplaylist': True,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
        'noprogress': False,  # Allow displaying progress
        'quiet': False,        # Allow seeing messages
        'verbose': True,       # Detailed messages
    }
    
    # If format requires merging and ffmpeg is installed
    if format_info.get("merge_format") and has_ffmpeg:
        ydl_opts['merge_output_format'] = format_info["merge_format"]
    
    # Add postprocessor arguments, if they exist - FIXED
    if format_info.get("postprocessor_args") and has_ffmpeg and format_info["postprocessor_args"]:
        ydl_opts['postprocessor_args'] = format_info["postprocessor_args"]
    
    # Get video information before downloading
    video_info = get_video_info(url, ydl_opts)
    
    if video_info:
        print(get_string("summary_info"))
        print(get_string("video_title", video_info.get('title', 'Unknown')))
        print(get_string("video_url", url))
        print(get_string("download_folder", download_path))
        print(get_string("selected_format", format_info['desc']))
        
        # Check yt-dlp version
        print(get_string("ytdlp_version", check_yt_dlp_version()))
        
        # Check expected filename
        expected_title = video_info.get('title', 'video')
        expected_ext = format_info.get("merge_format", "mp4") if has_ffmpeg and "+" in format_info["format"] else video_info.get('ext', 'mp4')
        expected_filename = os.path.join(download_path, f"{expected_title}.{expected_ext}")
        print(get_string("expected_file", os.path.basename(expected_filename)))
        
        print("----------------------------\n")
        
        confirm = input(get_string("start_download")).lower()
        if confirm in ["так", "yes", "sí", "si", "y", "т", "s"]:
            try:
                print(get_string("download_started"))
                with yt_dlp.ydl.download([url]):

                    except Exception as e:
                    print(get_string("download_error", str(e)))
                    print(get_string("diagnostics"))
                    
                    # Diagnostics
                    print(get_string("diagnostics_title"))
                    print(get_string("folder_check", download_path))
                    if os.path.exists(download_path):
                        print(get_string("folder_exists", "Yes"))
                        print(get_string("write_permission", "Yes" if os.access(download_path, os.W_OK) else "No"))
                        print(get_string("free_space", shutil.disk_usage(download_path).free))
                    else:
                        print(get_string("folder_not_exists"))
                        
                    print(get_string("version_check"))
                    try:
                        # Use our function to check version
                        version = check_yt_dlp_version()
                        print(f"   {version}")
                    except:
                        print(get_string("version_detect_failed"))
                        
                    print(get_string("simple_download"))
                    try:
                        simple_url = url
                        simple_path = os.path.join(os.getcwd(), "simple_download.mp4")
                        
                        print(get_string("simple_download_to", simple_path))
                        
                        # Execute through library, not subprocess
                        simple_opts = {
                            'format': 'best',
                            'outtmpl': simple_path,
                            'quiet': False
                        }
                        
                        with yt_dlp.YoutubeDL(simple_opts) as ydl:
                            ydl.download([simple_url])
                        
                        if os.path.exists(simple_path):
                            print(get_string("simple_success", os.path.getsize(simple_path)))
                        else:
                            print(get_string("simple_error"))
                    except Exception as e:
                        print(get_string("simple_download_error", str(e)))
            else:
                print(get_string("download_cancelled"))
        else:
            print(get_string("video_info_failed"))

def save_settings(settings):
    """Saves user settings to a file"""
    try:
        with open('yt_dl_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def load_settings():
    """Loads user settings from a file"""
    try:
        if os.path.exists('yt_dl_settings.json'):
            with open('yt_dl_settings.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    # Default settings
    return {
        "language": "uk"
    }

if __name__ == "__main__":
    # Load user settings
    settings = load_settings()
    # Set language from saved settings
    if "language" in settings:
        current_language = settings["language"]
        strings = LANGUAGES[current_language]

    # Allow user to select language
    select_language()

    # Save selected language
    settings["language"] = current_language
    save_settings(settings)

    # Show disclaimer
    if not show_disclaimer():
        sys.exit(0)

    print(get_string("app_title"))
    video_url = input(get_string("enter_url"))
    download_yt_video(video_url)