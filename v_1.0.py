# pip install yt_dlp
# https://www.gyan.dev/ffmpeg/builds/

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import shutil
import time
import yt_dlp

# Словники з текстами для кожної мови
MESSAGES = {
    'uk': {
        'disclaimer': """
=====================================================================
DISCLAIMER:
Цей проект створено виключно з освітньою метою.
Автор не підтримує і не заохочує використання цього інструменту для
порушення авторських прав чи інших незаконних дій.
Користувач несе повну відповідальність за використання цієї програми.
=====================================================================
Ви приймаєте умови? (так/ні): """,
        'consent_decline': "Ви не прийняли умови. Завершення роботи програми.",
        'ffmpeg_not_found': "УВАГА: ffmpeg не знайдено. Без нього неможливо об'єднати аудіо та відео.",
        'ffmpeg_install_win': "1. Завантажте ffmpeg з https://ffmpeg.org/download.html\n2. Розпакуйте архів та додайте шлях до bin-папки в змінну середовища PATH",
        'ffmpeg_install_mac': "Виконайте в терміналі: brew install ffmpeg",
        'ffmpeg_install_linux': "Виконайте в терміналі: sudo apt-get install ffmpeg",
        'continue_without_ffmpeg': "Продовжити без об'єднання аудіо та відео? (так/ні): ",
        'download_custom_folder': "Бажаєте вибрати власну папку для завантаження відео? (так/ні): ",
        'selected_folder': "Вибрана папка: ",
        'folder_no_permission': "УВАГА: Неможливо записати файли в {folder}. Недостатньо прав.",
        'using_default_folder': "Буде використано стандартну папку: {default}",
        'format_step': "\n=== КРОК 1: Вибір формату ===",
        'format_options': "Доступні формати:\n1. Відео + аудіо (один файл)\n2. Тільки відео (без звуку)\n3. Тільки аудіо\n4. Завантажити і відео, і аудіо (окремими файлами)",
        'choose_format': "Виберіть формат (1-4): ",
        'quality_step': "\n=== КРОК 2: Вибір якості відео ===",
        'choose_video_quality_q': "Бажаєте вибрати якість відео? (так/ні): ",
        'video_quality_options': "Доступні варіанти якості:\n1. 2160p (4K)\n2. 1440p (2K)\n3. 1080p (Full HD)\n4. 720p (HD)\n5. 480p (SD)\n6. 360p (Low)\nПримітка: якщо відео не матиме вказаної якості, воно завантажиться БЕЗ звуку",
        'choose_video_quality': "Виберіть якість (1-6): ",
        'audio_quality_options': "Доступні варіанти якості аудіо:\n1. Найкраща якість (до 320kbps)\n2. Середня якість (до 192kbps)\n3. Низька якість (до 128kbps)\n4. Мінімальна якість (до 64kbps)",
        'choose_audio_quality': "Виберіть якість аудіо (1-4): ",
        'video_info_title': "\n--- Підсумкова інформація ---",
        'video_title': "Назва відео: ",
        'video_url': "URL відео: ",
        'download_folder': "Папка завантаження: ",
        'selected_format': "Вибраний формат: ",
        'yt_dlp_version': "Версія yt-dlp: ",
        'expected_file': "Очікуваний файл: ",
        'start_download': "Розпочати завантаження? (так/ні): ",
        'download_started': "Завантаження розпочато...",
        'download_complete': "\nЗавантаження завершено! Перевірка файлу...",
        'file_saved': "\nФайл успішно збережено: ",
        'file_size': "Розмір файлу: {size} байт",
        'file_zero': "УВАГА: Файл має нульовий розмір! Можливо, виникла проблема із завантаженням.",
        'search_recent_files': "\nНе вдалося знайти очікуваний файл. Пошук нещодавно створених файлів...",
        'recent_files_found': "Нещодавно створені файли:",
        'possible_file': "\nВозможно, один з цих файлів є вашим завантаженим відео.",
        'no_recent_files': "Не знайдено нещодавно створених файлів у папці завантаження.",
        'download_issue': "ПРОБЛЕМА: Відео не було збережено. Причини можуть бути:",
        'issue_list': "1. Недостатньо місця на диску\n2. Проблеми з правами доступу\n3. Антивірус блокує запис файлу\n4. Несумісність з поточною версією yt-dlp",
        'download_finished': "\nЗавантаження завершено!",
        'open_folder_q': "\nБажаєте відкрити папку з завантаженням? (так/ні): ",
        'folder_opened': "Папку відкрито у файловому менеджері",
        'folder_open_failed': "Не вдалося відкрити папку автоматично",
        'download_cancelled': "Завантаження скасовано.",
        'video_info_fail': "Не вдалося отримати інформацію про відео. Завантаження скасовано.",
        'diagnostics': "\n--- Діагностика ---",
        'folder_exists': "1. Перевірка папки: ",
        'folder_exists_yes': "   Папка існує: Так",
        'folder_exists_no': "   Папка не існує!",
        'write_permission': "   Права на запис: {perm}",
        'free_space': "   Вільне місце: {space} байт",
        'yt_dlp_version_diag': "2. Версія yt-dlp:",
        'version_diag': "   {version}",
        'simple_download': "3. Спроба скачати за спрощеними параметрами:",
        'simple_downloading': "   Завантаження в {path}...",
        'simple_success': "   Успішно! Файл створено ({size} байт)",
        'simple_fail': "   Помилка: Файл не створено",
        'simple_exception': "   Помилка при спрощеному завантаженні: {error}",
        'open_folder_error': "Неможливо відкрити папку: непідтримувана операційна система",
        'open_folder_not_exist': "Неможливо відкрити папку: шлях {folder} не існує",
        'open_folder_exception': "Помилка при спробі відкрити папку: {error}",
        'choose_video_url': "Введіть URL відео YouTube: "
    },
    'en': {
        'disclaimer': """
=====================================================================
DISCLAIMER:
This project is created for educational purposes only.
The author does not support or encourage the use of this tool for 
copyright infringement or any other illegal activities.
The user assumes full responsibility for using this program.
=====================================================================
Do you accept these terms? (yes/no): """,
        'consent_decline': "You did not accept the terms. Exiting the program.",
        'ffmpeg_not_found': "WARNING: ffmpeg not found. Without it, merging audio and video is not possible.",
        'ffmpeg_install_win': "1. Download ffmpeg from https://ffmpeg.org/download.html\n2. Extract the archive and add the bin folder to your PATH environment variable",
        'ffmpeg_install_mac': "Run in terminal: brew install ffmpeg",
        'ffmpeg_install_linux': "Run in terminal: sudo apt-get install ffmpeg",
        'continue_without_ffmpeg': "Continue without merging audio and video? (yes/no): ",
        'download_custom_folder': "Do you want to choose a custom folder for downloading videos? (yes/no): ",
        'selected_folder': "Selected folder: ",
        'folder_no_permission': "WARNING: Cannot write files to {folder}. Insufficient permissions.",
        'using_default_folder': "Default folder will be used: {default}",
        'format_step': "\n=== STEP 1: Choose Format ===",
        'format_options': "Available formats:\n1. Video + Audio (single file)\n2. Video Only (no audio)\n3. Audio Only\n4. Download both video and audio (separate files)",
        'choose_format': "Choose format (1-4): ",
        'quality_step': "\n=== STEP 2: Choose Video Quality ===",
        'choose_video_quality_q': "Do you want to choose the video quality? (yes/no): ",
        'video_quality_options': "Available quality options:\n1. 2160p (4K)\n2. 1440p (2K)\n3. 1080p (Full HD)\n4. 720p (HD)\n5. 480p (SD)\n6. 360p (Low)\nNote: if the video doesn't have the specified quality, it will be downloaded WITHOUT audio",
        'choose_video_quality': "Choose quality (1-6): ",
        'audio_quality_options': "Available audio quality options:\n1. Best quality (up to 320kbps)\n2. Medium quality (up to 192kbps)\n3. Low quality (up to 128kbps)\n4. Minimum quality (up to 64kbps)",
        'choose_audio_quality': "Choose audio quality (1-4): ",
        'video_info_title': "\n--- Final Information ---",
        'video_title': "Video Title: ",
        'video_url': "Video URL: ",
        'download_folder': "Download Folder: ",
        'selected_format': "Selected format: ",
        'yt_dlp_version': "yt-dlp version: ",
        'expected_file': "Expected file: ",
        'start_download': "Start download? (yes/no): ",
        'download_started': "Download started...",
        'download_complete': "\nDownload complete! Checking file...",
        'file_saved': "\nFile successfully saved: ",
        'file_size': "File size: {size} bytes",
        'file_zero': "WARNING: File size is zero! There might have been a download issue.",
        'search_recent_files': "\nCould not find the expected file. Searching for recently created files...",
        'recent_files_found': "Recently created files:",
        'possible_file': "\nPerhaps one of these files is your downloaded video.",
        'no_recent_files': "No recently created files found in the download folder.",
        'download_issue': "ISSUE: The video was not saved. Possible reasons:",
        'issue_list': "1. Insufficient disk space\n2. Permission issues\n3. Antivirus blocking file write\n4. Incompatibility with current yt-dlp version",
        'download_finished': "\nDownload finished!",
        'open_folder_q': "\nDo you want to open the download folder? (yes/no): ",
        'folder_opened': "Folder opened in file manager",
        'folder_open_failed': "Failed to open folder automatically",
        'download_cancelled': "Download cancelled.",
        'video_info_fail': "Failed to retrieve video info. Download cancelled.",
        'diagnostics': "\n--- Diagnostics ---",
        'folder_exists': "1. Checking folder: ",
        'folder_exists_yes': "   Folder exists: Yes",
        'folder_exists_no': "   Folder does not exist!",
        'write_permission': "   Write permission: {perm}",
        'free_space': "   Free space: {space} bytes",
        'yt_dlp_version_diag': "2. yt-dlp version:",
        'version_diag': "   {version}",
        'simple_download': "3. Attempting simple download:",
        'simple_downloading': "   Downloading to {path}...",
        'simple_success': "   Success! File created ({size} bytes)",
        'simple_fail': "   Error: File not created",
        'simple_exception': "   Exception during simple download: {error}",
        'open_folder_error': "Cannot open folder: unsupported OS",
        'open_folder_not_exist': "Cannot open folder: path {folder} does not exist",
        'open_folder_exception': "Exception when opening folder: {error}",
        'choose_video_url': "Enter YouTube video URL: "
    }
}

def select_language():
    """Функція для вибору мови (ukr/en)"""
    lang_choice = input("Виберіть мову / Choose language (uk/en): ").strip().lower()
    if lang_choice not in ['uk', 'en']:
        print("Невірний вибір, встановлено мову за замовчуванням: uk")
        return 'uk'
    return lang_choice

LANG = select_language()

def msg(key, **kwargs):
    """Допоміжна функція для отримання повідомлення відповідно до вибраної мови"""
    text = MESSAGES[LANG].get(key, "")
    if kwargs:
        return text.format(**kwargs)
    return text

def show_disclaimer_and_get_consent():
    consent = input(msg('disclaimer')).strip().lower()
    if consent not in ["yes", "y", "так", "т"]:
        print(msg('consent_decline'))
        exit(1)

# Викликаємо функцію, щоб показати дисклеймер та отримати згоду користувача
show_disclaimer_and_get_consent()

def check_ffmpeg():
    """Перевіряє, чи встановлено ffmpeg, і встановлює його за необхідності"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print(msg('ffmpeg_not_found'))
        if sys.platform.startswith('win'):
            print(msg('ffmpeg_install_win'))
        elif sys.platform.startswith('darwin'):
            print(msg('ffmpeg_install_mac'))
        else:
            print(msg('ffmpeg_install_linux'))
            
        choice = input(msg('continue_without_ffmpeg')).lower()
        if choice in ["так", "yes", "y", "т"]:
            return False
        else:
            print(msg('consent_decline'))
            sys.exit(1)

def get_download_path():
    """Відкриває діалогове вікно для вибору папки завантаження"""
    default_path = str(Path.home() / "Downloads")
    
    choice = input(msg('download_custom_folder')).lower()
    if choice in ["так", "yes", "y", "т"]:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        custom_path = filedialog.askdirectory(title=msg('selected_folder'))
        
        if custom_path:
            print(msg('selected_folder') + custom_path)
            if os.access(custom_path, os.W_OK):
                return custom_path
            else:
                print(msg('folder_no_permission', folder=custom_path))
                print(msg('using_default_folder', default=default_path))
                return default_path
        else:
            print(msg('using_default_folder', default=default_path))
            return default_path
    else:
        print(msg('using_default_folder', default=default_path))
        return default_path

def select_format_and_quality(has_ffmpeg):
    """Двоетапний вибір формату та якості відео"""
    print(msg('format_step'))
    print(msg('format_options'))
    
    format_choice = input(msg('choose_format'))
    
    format_option = ""
    format_desc = ""
    merge_format = None
    postprocessor_args = {}
    
    if format_choice == "1":
        if has_ffmpeg:
            format_option = "bestvideo+bestaudio/best"
            format_desc = msg('selected_format') + "Video + Audio (single file)"
            merge_format = "mp4"
            postprocessor_args = {
                'ffmpeg': ['-c:a', 'aac', '-b:a', '192k']
            }
        else:
            print(msg('ffmpeg_not_found'))
            format_option = "best"
            format_desc = msg('selected_format') + "Best available format"
            merge_format = None
    elif format_choice == "2":
        format_option = "bestvideo/best[vcodec!=none]"
        format_desc = msg('selected_format') + "Video Only (no audio)"
    elif format_choice == "3":
        audio_quality = select_audio_quality()
        format_option = audio_quality["format"]
        format_desc = audio_quality["desc"]
    elif format_choice == "4":
        format_option = "bestvideo,bestaudio"
        format_desc = msg('selected_format') + "Video and Audio (separate files)"
    else:
        print(msg('selected_format') + "Best available")
        format_option = "best"
        format_desc = "Best available"
    
    if format_choice in ["1", "2", "4"]:
        print(msg('quality_step'))
        should_choose_quality = input(msg('choose_video_quality_q')).lower()
        
        if should_choose_quality in ["так", "yes", "y", "т"]:
            video_quality = select_video_quality()
            
            if format_choice == "1":
                if has_ffmpeg:
                    if "height<=" in video_quality["format"]:
                        height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                        format_option = f"bestvideo[height<={height_limit}]+bestaudio/best[height<={height_limit}]"
                else:
                    if "height<=" in video_quality["format"]:
                        height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                        format_option = f"best[height<={height_limit}]"
            elif format_choice == "2":
                if "height<=" in video_quality["format"]:
                    height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                    format_option = f"bestvideo[height<={height_limit}]/best[height<={height_limit}][vcodec!=none]"
            elif format_choice == "4":
                if "height<=" in video_quality["format"]:
                    height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                    format_option = f"bestvideo[height<={height_limit}],bestaudio"
            
            format_desc += " - " + video_quality['desc']
    
    return {
        "format": format_option,
        "desc": format_desc,
        "merge_format": merge_format,
        "postprocessor_args": postprocessor_args
    }

def select_video_quality():
    """Дозволяє користувачу вибрати якість відео"""
    print(msg('video_quality_options'))
    quality_choice = input(msg('choose_video_quality'))
    
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
        print("Невірний вибір. Буде використано найкращу доступну якість.")
        return {"format": "bestvideo", "desc": "Best available"}

def select_audio_quality():
    """Дозволяє користувачу вибрати якість аудіо"""
    print(msg('audio_quality_options'))
    quality_choice = input(msg('choose_audio_quality'))
    
    quality_options = {
        "1": {"format": "bestaudio", "desc": "Audio - best quality"},
        "2": {"format": "bestaudio[abr<=192]", "desc": "Audio - medium quality"},
        "3": {"format": "bestaudio[abr<=128]", "desc": "Audio - low quality"},
        "4": {"format": "bestaudio[abr<=64]", "desc": "Audio - minimum quality"}
    }
    
    if quality_choice in quality_options:
        return quality_options[quality_choice]
    else:
        print("Невірний вибір. Буде використано найкращу доступну якість аудіо.")
        return {"format": "bestaudio", "desc": "Audio - best quality"}

def get_video_info(url, ydl_opts):
    """Отримує інформацію про відео"""
    info_opts = ydl_opts.copy()
    info_opts['skip_download'] = True
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            print(f"Помилка при отриманні інформації про відео: {e}")
            return None

def my_hook(d):
    """Функція для відстеження прогресу завантаження"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\rЗавантаження: {percent} швидкість: {speed} залишилось: {eta}", end='')
    elif d['status'] == 'finished':
        print(f"\n{msg('download_complete')}")
        filename = d.get('filename', 'невідомий файл')
        if os.path.exists(filename):
            filesize = os.path.getsize(filename)
            print(msg('file_saved') + os.path.basename(filename))
            print(msg('file_size', size=filesize))
            if filesize == 0:
                print(msg('file_zero'))

def test_file_permissions(path):
    """Перевіряє права на запис у вказану папку"""
    try:
        test_file = os.path.join(path, ".test_write_permissions")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (IOError, PermissionError) as e:
        print(f"УВАГА: Проблема з правами доступу до папки: {e}")
        return False

def check_yt_dlp_version():
    """Перевіряє версію yt-dlp та виводить її"""
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            version_dict = ydl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=False, process=False)
            if hasattr(ydl, 'version'):
                return ydl.version
            else:
                return "Невідома версія" if LANG == 'uk' else "Unknown version"
    except Exception as e:
        print(f"Помилка при перевірці версії yt-dlp: {e}")
        return "Помилка визначення версії" if LANG == 'uk' else "Error determining version"

def open_download_directory(directory):
    """Відкриває папку з завантаженим файлом у файловому менеджері"""
    try:
        if os.path.exists(directory):
            if sys.platform.startswith('win'):
                os.startfile(directory)
                return True
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', directory], check=True)
                return True
            elif sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', directory], check=True)
                return True
            else:
                print(msg('open_folder_error'))
                return False
        else:
            print(msg('open_folder_not_exist', folder=directory))
            return False
    except Exception as e:
        print(msg('open_folder_exception', error=e))
        return False

def download_yt_video(url):
    """Завантажує відео з YouTube з вибраними параметрами"""
    has_ffmpeg = check_ffmpeg()
    download_path = get_download_path()
    
    if not test_file_permissions(download_path):
        alt_path = os.path.join(os.getcwd(), "downloads")
        print(msg('using_default_folder', default=alt_path))
        os.makedirs(alt_path, exist_ok=True)
        if test_file_permissions(alt_path):
            download_path = alt_path
        else:
            print("Помилка: Неможливо знайти папку з правами на запис. Завантаження неможливе.")
            return
    
    format_info = select_format_and_quality(has_ffmpeg)
    
    ydl_opts = {
        'format': format_info["format"],
        'noplaylist': True,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
        'noprogress': False,
        'quiet': False,
        'verbose': True,
    }
    
    if format_info.get("merge_format") and has_ffmpeg:
        ydl_opts['merge_output_format'] = format_info["merge_format"]
    
    if format_info.get("postprocessor_args") and has_ffmpeg and format_info["postprocessor_args"]:
        ydl_opts['postprocessor_args'] = format_info["postprocessor_args"]
    
    video_info = get_video_info(url, ydl_opts)
    
    if video_info:
        print(msg('video_info_title'))
        print(msg('video_title') + video_info.get('title', 'Невідомо'))
        print(msg('video_url') + url)
        print(msg('download_folder') + download_path)
        print(msg('selected_format') + format_info['desc'])
        print(msg('yt_dlp_version') + str(check_yt_dlp_version()))
        
        expected_title = video_info.get('title', 'video')
        expected_ext = format_info.get("merge_format", "mp4") if has_ffmpeg and "+" in format_info["format"] else video_info.get('ext', 'mp4')
        expected_filename = os.path.join(download_path, f"{expected_title}.{expected_ext}")
        print(msg('expected_file') + os.path.basename(expected_filename))
        print("----------------------------\n")
        
        confirm = input(msg('start_download')).lower()
        if confirm in ["так", "yes", "y", "т"]:
            try:
                print(msg('download_started'))
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                sanitized_filename = expected_filename.replace('|', '_').replace(':', '_')
                possible_filenames = [
                    expected_filename,
                    sanitized_filename,
                    os.path.join(download_path, f"{expected_title.replace('|', '_').replace(':', '_')}.{expected_ext}")
                ]
                
                file_found = False
                for fname in possible_filenames:
                    if os.path.exists(fname):
                        file_size = os.path.getsize(fname)
                        file_found = True
                        print("\n" + msg('file_saved') + fname)
                        print(msg('file_size', size=file_size))
                        break
                
                if not file_found:
                    print(msg('search_recent_files'))
                    current_time = time.time()
                    recent_files = []
                    
                    for file in os.listdir(download_path):
                        file_path = os.path.join(download_path, file)
                        if os.path.isfile(file_path):
                            if current_time - os.path.getctime(file_path) < 300:
                                recent_files.append((file_path, os.path.getctime(file_path)))
                    
                    if recent_files:
                        recent_files.sort(key=lambda x: x[1], reverse=True)
                        print(msg('recent_files_found'))
                        for file_path, ctime in recent_files[:5]:
                            file_size = os.path.getsize(file_path)
                            print(f"- {os.path.basename(file_path)} ({file_size} байт)")
                        print(msg('possible_file'))
                    else:
                        print(msg('no_recent_files'))
                        print(msg('download_issue'))
                        print(msg('issue_list'))
                
                print(msg('download_finished'))
                if file_found or recent_files:
                    open_dir = input(msg('open_folder_q')).lower()
                    if open_dir in ["так", "yes", "y", "т"]:
                        if open_download_directory(download_path):
                            print(msg('folder_opened'))
                        else:
                            print(msg('folder_open_failed'))
            except Exception as e:
                print(f"\nПомилка при завантаженні: {e}")
                print("Спроба виконати діагностику...")
                print(msg('diagnostics'))
                print(msg('folder_exists') + download_path)
                if os.path.exists(download_path):
                    print(msg('folder_exists_yes'))
                    print(msg('write_permission', perm='Так' if os.access(download_path, os.W_OK) else 'Ні'))
                    print(msg('free_space', space=shutil.disk_usage(download_path).free))
                else:
                    print(msg('folder_exists_no'))
                    
                print(msg('yt_dlp_version_diag'))
                try:
                    version = check_yt_dlp_version()
                    print(msg('version_diag', version=version))
                except:
                    print("   Не вдалося визначити версію")
                    
                print(msg('simple_download'))
                try:
                    simple_url = url
                    simple_path = os.path.join(os.getcwd(), "simple_download.mp4")
                    print(msg('simple_downloading', path=simple_path))
                    
                    simple_opts = {
                        'format': 'best',
                        'outtmpl': simple_path,
                        'quiet': False
                    }
                    
                    with yt_dlp.YoutubeDL(simple_opts) as ydl:
                        ydl.download([simple_url])
                    
                    if os.path.exists(simple_path):
                        print(msg('simple_success', size=os.path.getsize(simple_path)))
                    else:
                        print(msg('simple_fail'))
                except Exception as e:
                    print(msg('simple_exception', error=e))
        else:
            print(msg('download_cancelled'))
    else:
        print(msg('video_info_fail'))

if __name__ == "__main__":
    print("=== YouTube Video Downloader ===")
    video_url = input(msg('choose_video_url'))
    download_yt_video(video_url)
