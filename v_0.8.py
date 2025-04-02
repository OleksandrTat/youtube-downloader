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

def check_ffmpeg():
    """Перевіряє, чи встановлено ffmpeg, і встановлює його за необхідності"""
    try:
        # Спроба виконати команду ffmpeg -version для перевірки наявності
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("УВАГА: ffmpeg не знайдено. Без нього неможливо об'єднати аудіо та відео.")
        print("Будь ласка, встановіть ffmpeg:")
        
        if sys.platform.startswith('win'):
            print("1. Завантажте ffmpeg з https://ffmpeg.org/download.html")
            print("2. Розпакуйте архів та додайте шлях до bin-папки в змінну середовища PATH")
        elif sys.platform.startswith('darwin'):  # macOS
            print("Виконайте в терміналі: brew install ffmpeg")
        else:  # Linux
            print("Виконайте в терміналі: sudo apt-get install ffmpeg")
            
        choice = input("Продовжити без об'єднання аудіо та відео? (так/ні): ").lower()
        if choice in ["так", "yes", "y", "т"]:
            return False
        else:
            print("Завантаження скасовано. Будь ласка, встановіть ffmpeg і спробуйте знову.")
            sys.exit(1)

def get_download_path():
    """Відкриває діалогове вікно для вибору папки завантаження"""
    default_path = str(Path.home() / "Downloads")
    
    choice = input(f"Бажаєте вибрати власну папку для завантаження відео? (так/ні): ").lower()
    if choice in ["так", "yes", "y", "т"]:
        # Ініціалізація Tkinter і приховання основного вікна
        root = tk.Tk()
        root.withdraw()  # Приховати головне вікно
        root.attributes('-topmost', True)  # Примусове відображення поверх інших вікон
        
        # Відкриття діалогового вікна для вибору папки
        custom_path = filedialog.askdirectory(title="Виберіть папку для завантаження відео")
        
        if custom_path:  # Якщо користувач вибрав папку
            print(f"Вибрана папка: {custom_path}")
            # Перевірка прав на запис у вибрану папку
            if os.access(custom_path, os.W_OK):
                return custom_path
            else:
                print(f"УВАГА: Неможливо записати файли в {custom_path}. Недостатньо прав.")
                print(f"Буде використано стандартну папку: {default_path}")
                return default_path
        else:  # Якщо користувач скасував вибір
            print(f"Вибір скасовано. Буде використано стандартну папку: {default_path}")
            return default_path
    else:
        print(f"Буде використано стандартну папку: {default_path}")
        return default_path

def select_format_and_quality(has_ffmpeg):
    """Двоетапний вибір формату та якості відео"""
    print("\n=== КРОК 1: Вибір формату ===")
    print("Доступні формати:")
    print("1. Відео + аудіо (один файл)")
    print("2. Тільки відео (без звуку)")
    print("3. Тільки аудіо")
    print("4. Завантажити і відео, і аудіо (окремими файлами)")
    
    format_choice = input("Виберіть формат (1-4): ")
    
    # Ініціалізуємо змінні для зберігання налаштувань
    format_option = ""
    format_desc = ""
    merge_format = None
    postprocessor_args = {}  # Змінено з None на пустий словник
    
    # Обробка вибору формату
    if format_choice == "1":  # Відео + аудіо
        if has_ffmpeg:
            format_option = "bestvideo+bestaudio/best"
            format_desc = "Відео + аудіо (один файл)"
            merge_format = "mp4"
            # Змінено спосіб передачі аргументів постпроцесору
            postprocessor_args = {
                'ffmpeg': ['-c:a', 'aac', '-b:a', '192k']
            }
        else:
            print("УВАГА: ffmpeg не встановлено, тому буде використано найкращий доступний формат без об'єднання.")
            format_option = "best"
            format_desc = "Найкращий доступний формат"
            merge_format = None
    elif format_choice == "2":  # Тільки відео
        format_option = "bestvideo/best[vcodec!=none]"
        format_desc = "Тільки відео (без звуку)"
    elif format_choice == "3":  # Тільки аудіо
        audio_quality = select_audio_quality()
        format_option = audio_quality["format"]
        format_desc = audio_quality["desc"]
    elif format_choice == "4":  # Відео і аудіо окремими файлами
        format_option = "bestvideo,bestaudio"
        format_desc = "Відео та аудіо (окремими файлами)"
    else:
        print("Невірний вибір. Буде використано найкращу доступну якість.")
        format_option = "best"
        format_desc = "Найкраща доступна"
    
    # Якщо обрано відео або відео+аудіо, переходимо до вибору якості відео
    if format_choice in ["1", "2", "4"]:
        print("\n=== КРОК 2: Вибір якості відео ===")
        should_choose_quality = input("Бажаєте вибрати якість відео? (так/ні): ").lower()
        
        if should_choose_quality in ["так", "yes", "y", "т"]:
            video_quality = select_video_quality()
            
            # Модифікуємо формат відповідно до обраної якості
            if format_choice == "1":  # Відео + аудіо
                if has_ffmpeg:
                    if "height<=" in video_quality["format"]:
                        height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                        format_option = f"bestvideo[height<={height_limit}]+bestaudio/best[height<={height_limit}]"
                else:
                    if "height<=" in video_quality["format"]:
                        height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                        format_option = f"best[height<={height_limit}]"
            elif format_choice == "2":  # Тільки відео
                if "height<=" in video_quality["format"]:
                    height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                    format_option = f"bestvideo[height<={height_limit}]/best[height<={height_limit}][vcodec!=none]"
            elif format_choice == "4":  # Відео і аудіо окремими файлами
                if "height<=" in video_quality["format"]:
                    height_limit = video_quality["format"].split("height<=")[1].split("]")[0]
                    format_option = f"bestvideo[height<={height_limit}],bestaudio"
            
            format_desc += f" - {video_quality['desc']}"
    
    return {
        "format": format_option,
        "desc": format_desc,
        "merge_format": merge_format,
        "postprocessor_args": postprocessor_args  # Змінено структуру
    }

def select_video_quality():
    """Дозволяє користувачу вибрати якість відео"""
    print("Доступні варіанти якості:")
    print("1. 2160p (4K)")
    print("2. 1440p (2K)")
    print("3. 1080p (Full HD)")
    print("4. 720p (HD)")
    print("5. 480p (SD)")
    print("6. 360p (Low)")
    print("Примітка: якщо відео не матиме вказаної якості, воно завантажиться БЕЗ звуку")
    
    quality_choice = input("Виберіть якість (1-6): ")
    
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
        return {"format": "bestvideo", "desc": "Найкраща доступна"}

def select_audio_quality():
    """Дозволяє користувачу вибрати якість аудіо"""
    print("Доступні варіанти якості аудіо:")
    print("1. Найкраща якість (до 320kbps)")
    print("2. Середня якість (до 192kbps)")
    print("3. Низька якість (до 128kbps)")
    print("4. Мінімальна якість (до 64kbps)")
    
    quality_choice = input("Виберіть якість аудіо (1-4): ")
    
    quality_options = {
        "1": {"format": "bestaudio", "desc": "Аудіо - найкраща якість"},
        "2": {"format": "bestaudio[abr<=192]", "desc": "Аудіо - середня якість"},
        "3": {"format": "bestaudio[abr<=128]", "desc": "Аудіо - низька якість"},
        "4": {"format": "bestaudio[abr<=64]", "desc": "Аудіо - мінімальна якість"}
    }
    
    if quality_choice in quality_options:
        return quality_options[quality_choice]
    else:
        print("Невірний вибір. Буде використано найкращу доступну якість аудіо.")
        return {"format": "bestaudio", "desc": "Аудіо - найкраща якість"}

def get_video_info(url, ydl_opts):
    """Отримує інформацію про відео"""
    # Створюємо копію параметрів, щоб не змінювати оригінальні
    info_opts = ydl_opts.copy()
    info_opts['skip_download'] = True  # Не завантажувати, тільки отримати інформацію
    
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
        filename = d.get('filename', 'відео')
        print(f"\rЗавантаження: {percent} швидкість: {speed} залишилось: {eta}", end='')
    
    elif d['status'] == 'finished':
        print(f"\nЗавантаження завершено! Перевірка файлу...")
        filename = d.get('filename', 'невідомий файл')
        
        # Перевірка розміру файлу
        if os.path.exists(filename):
            filesize = os.path.getsize(filename)
            print(f"Файл {os.path.basename(filename)} збережено ({filesize} байт)")
            
            # Перевірка чи файл не порожній
            if filesize == 0:
                print("УВАГА: Файл має нульовий розмір! Можливо, виникла проблема із завантаженням.")

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
                return "Невідома версія"
    except Exception as e:
        print(f"Помилка при перевірці версії yt-dlp: {e}")
        return "Помилка визначення версії"

def open_download_directory(directory):
    """Відкриває папку з завантаженим файлом у файловому менеджері"""
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
                print(f"Неможливо відкрити папку: непідтримувана операційна система")
                return False
        else:
            print(f"Неможливо відкрити папку: шлях {directory} не існує")
            return False
    except Exception as e:
        print(f"Помилка при спробі відкрити папку: {e}")
        return False

def download_yt_video(url):
    """Завантажує відео з YouTube з вибраними параметрами"""
    # Перевіряємо наявність ffmpeg
    has_ffmpeg = check_ffmpeg()
    
    # Отримуємо шлях для завантаження
    download_path = get_download_path()
    
    # Перевіряємо права на запис у вибрану папку
    if not test_file_permissions(download_path):
        alt_path = os.path.join(os.getcwd(), "downloads")
        print(f"Спроба використання альтернативної папки: {alt_path}")
        os.makedirs(alt_path, exist_ok=True)
        if test_file_permissions(alt_path):
            download_path = alt_path
        else:
            print("Помилка: Неможливо знайти папку з правами на запис. Завантаження неможливе.")
            return
    
    # Двоетапний вибір формату та якості
    format_info = select_format_and_quality(has_ffmpeg)
    
    # Базові налаштування
    ydl_opts = {
        'format': format_info["format"],
        'noplaylist': True,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
        'noprogress': False,  # Дозволяє відображати прогрес
        'quiet': False,        # Дозволяє бачити повідомлення
        'verbose': True,       # Детальні повідомлення
    }
    
    # Якщо формат потребує об'єднання і ffmpeg встановлено
    if format_info.get("merge_format") and has_ffmpeg:
        ydl_opts['merge_output_format'] = format_info["merge_format"]
    
    # Додаємо постпроцесорні аргументи, якщо вони є - ВИПРАВЛЕНО
    if format_info.get("postprocessor_args") and has_ffmpeg and format_info["postprocessor_args"]:
        ydl_opts['postprocessor_args'] = format_info["postprocessor_args"]
    
    # Отримуємо інформацію про відео перед завантаженням
    video_info = get_video_info(url, ydl_opts)
    
    if video_info:
        print("\n--- Підсумкова інформація ---")
        print(f"Назва відео: {video_info.get('title', 'Невідомо')}")
        print(f"URL відео: {url}")
        print(f"Папка завантаження: {download_path}")
        print(f"Вибраний формат: {format_info['desc']}")
        
        # Перевірка версії yt-dlp
        print(f"Версія yt-dlp: {check_yt_dlp_version()}")
        
        # Перевірка очікуваного імені файлу
        expected_title = video_info.get('title', 'video')
        expected_ext = format_info.get("merge_format", "mp4") if has_ffmpeg and "+" in format_info["format"] else video_info.get('ext', 'mp4')
        expected_filename = os.path.join(download_path, f"{expected_title}.{expected_ext}")
        print(f"Очікуваний файл: {os.path.basename(expected_filename)}")
        
        print("----------------------------\n")
        
        confirm = input("Розпочати завантаження? (так/ні): ").lower()
        if confirm in ["так", "yes", "y", "т"]:
            try:
                print("Завантаження розпочато...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Перевіряємо, чи файл було створено
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
                        print(f"\nФайл успішно збережено: {fname}")
                        print(f"Розмір файлу: {file_size} байт")
                        break
                
                if not file_found:
                    # Пошук усіх нещодавно створених файлів
                    print("\nНе вдалося знайти очікуваний файл. Пошук нещодавно створених файлів...")
                    current_time = time.time()
                    recent_files = []
                    
                    for file in os.listdir(download_path):
                        file_path = os.path.join(download_path, file)
                        if os.path.isfile(file_path):
                            # Перевіряємо, чи файл було створено протягом останніх 5 хвилин
                            if current_time - os.path.getctime(file_path) < 300:  # 300 секунд = 5 хвилин
                                recent_files.append((file_path, os.path.getctime(file_path)))
                    
                    if recent_files:
                        # Сортуємо за часом створення (найновіші спочатку)
                        recent_files.sort(key=lambda x: x[1], reverse=True)
                        print("Нещодавно створені файли:")
                        for file_path, ctime in recent_files[:5]:  # Показуємо до 5 найновіших файлів
                            file_size = os.path.getsize(file_path)
                            print(f"- {os.path.basename(file_path)} ({file_size} байт)")
                        
                        print("\nВозможно, один з цих файлів є вашим завантаженим відео.")
                    else:
                        print("Не знайдено нещодавно створених файлів у папці завантаження.")
                        print("ПРОБЛЕМА: Відео не було збережено. Причини можуть бути:")
                        print("1. Недостатньо місця на диску")
                        print("2. Проблеми з правами доступу")
                        print("3. Антивірус блокує запис файлу")
                        print("4. Несумісність з поточною версією yt-dlp")
                
                print("\nЗавантаження завершено!")
                if file_found or recent_files:  # Якщо знайдено файл або нещодавно створені файли
                    open_dir = input("\nБажаєте відкрити папку з завантаженням? (так/ні): ").lower()
                    if open_dir in ["так", "yes", "y", "т"]:
                        if open_download_directory(download_path):
                            print("Папку відкрито у файловому менеджері")
                        else:
                            print("Не вдалося відкрити папку автоматично")
                
            except Exception as e:
                print(f"\nПомилка при завантаженні: {e}")
                print("Спроба виконати діагностику...")
                
                # Діагностика проблем
                print("\n--- Діагностика ---")
                print(f"1. Перевірка папки: {download_path}")
                if os.path.exists(download_path):
                    print(f"   Папка існує: Так")
                    print(f"   Права на запис: {'Так' if os.access(download_path, os.W_OK) else 'Ні'}")
                    print(f"   Вільне місце: {shutil.disk_usage(download_path).free} байт")
                else:
                    print(f"   Папка не існує!")
                    
                print("2. Версія yt-dlp:")
                try:
                    # Використовуємо нашу функцію для перевірки версії
                    version = check_yt_dlp_version()
                    print(f"   {version}")
                except:
                    print("   Не вдалося визначити версію")
                    
                print("3. Спроба скачати за спрощеними параметрами:")
                try:
                    simple_url = url
                    simple_path = os.path.join(os.getcwd(), "simple_download.mp4")
                    
                    print(f"   Завантаження в {simple_path}...")
                    
                    # Виконуємо через бібліотеку, а не через subprocess
                    simple_opts = {
                        'format': 'best',
                        'outtmpl': simple_path,
                        'quiet': False
                    }
                    
                    with yt_dlp.YoutubeDL(simple_opts) as ydl:
                        ydl.download([simple_url])
                    
                    if os.path.exists(simple_path):
                        print(f"   Успішно! Файл створено ({os.path.getsize(simple_path)} байт)")
                    else:
                        print("   Помилка: Файл не створено")
                except Exception as e:
                    print(f"   Помилка при спрощеному завантаженні: {e}")
        else:
            print("Завантаження скасовано.")
    else:
        print("Не вдалося отримати інформацію про відео. Завантаження скасовано.")

if __name__ == "__main__":
    print("=== YouTube Video Downloader ===")
    video_url = input("Введіть URL відео YouTube: ")
    download_yt_video(video_url)