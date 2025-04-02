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

# Language dictionaries
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
        "app_title": "=== YouTube Video Downloader ===",
        "disclaimer": """
DISCLAIMER:
This tool is created exclusively for educational purposes to demonstrate working with video APIs.
By using this program, you agree to:
- Not violate copyrights and terms of service
- Download only content that you have rights to or permission for
- Not use the program for commercial purposes without the permission of content owners

The author of the program is not responsible for any misuse of this tool.
All responsibility for using the program rests with the user.
        """,
        "accept_terms": "I agree to the terms (yes/no): ",
        "terms_rejected": "Terms not accepted. The program is terminating.",
        "enter_url": "Enter YouTube video URL: ",
        "ffmpeg_not_found": "WARNING: ffmpeg not found. Without it, it's impossible to combine audio and video.",
        "install_ffmpeg": "Please install ffmpeg:",
        "win_install_ffmpeg": "1. Download ffmpeg from https://ffmpeg.org/download.html\n2. Unpack the archive and add the path to the bin folder to the PATH environment variable",
        "mac_install_ffmpeg": "Execute in terminal: brew install ffmpeg",
        "linux_install_ffmpeg": "Execute in terminal: sudo apt-get install ffmpeg",
        "continue_without_ffmpeg": "Continue without merging audio and video? (yes/no): ",
        "download_canceled": "Download canceled. Please install ffmpeg and try again.",
        "custom_folder": "Would you like to choose a custom folder for video download? (yes/no): ",
        "selected_folder": "Selected folder: ",
        "write_permission_error": "WARNING: Cannot write files to {0}. Insufficient permissions.",
        "using_default_folder": "Default folder will be used: {0}",
        "selection_canceled": "Selection canceled. Default folder will be used: {0}",
        "step1_format": "\n=== STEP 1: Format Selection ===",
        "available_formats": "Available formats:",
        "format_1": "1. Video + audio (single file)",
        "format_2": "2. Video only (no sound)",
        "format_3": "3. Audio only",
        "format_4": "4. Download both video and audio (separate files)",
        "select_format": "Select format (1-4): ",
        "invalid_choice": "Invalid choice. The best available quality will be used.",
        "best_available": "Best available",
        "warning_no_ffmpeg": "WARNING: ffmpeg not installed, so the best available format will be used without merging.",
        "best_available_format": "Best available format",
        "video_only": "Video only (no sound)",
        "video_audio_separate": "Video and audio (separate files)",
        "step2_quality": "\n=== STEP 2: Video Quality Selection ===",
        "choose_quality": "Would you like to choose video quality? (yes/no): ",
        "available_quality": "Available quality options:",
        "quality_1": "1. 2160p (4K)",
        "quality_2": "2. 1440p (2K)",
        "quality_3": "3. 1080p (Full HD)",
        "quality_4": "4. 720p (HD)",
        "quality_5": "5. 480p (SD)",
        "quality_6": "6. 360p (Low)",
        "quality_note": "Note: if the video doesn't have the specified quality, it will be downloaded WITHOUT sound",
        "select_quality": "Select quality (1-6): ",
        "best_quality": "Best available",
        "audio_quality_options": "Available audio quality options:",
        "audio_1": "1. Best quality (up to 320kbps)",
        "audio_2": "2. Medium quality (up to 192kbps)",
        "audio_3": "3. Low quality (up to 128kbps)",
        "audio_4": "4. Minimal quality (up to 64kbps)",
        "select_audio_quality": "Select audio quality (1-4): ",
        "best_audio": "Audio - best quality",
        "medium_audio": "Audio - medium quality",
        "low_audio": "Audio - low quality",
        "minimal_audio": "Audio - minimal quality",
        "error_video_info": "Error getting video information: {0}",
        "downloading": "Downloading: {0} speed: {1} remaining: {2}",
        "download_complete": "Download complete! Checking file...",
        "file_saved": "File {0} saved ({1} bytes)",
        "file_empty": "WARNING: File has zero size! There may be a problem with the download.",
        "permission_error": "WARNING: Problem with folder access permissions: {0}",
        "error_checking_version": "Error checking yt-dlp version: {0}",
        "version_error": "Error determining version",
        "unable_to_open_folder": "Unable to open folder: {0}",
        "error_opening_folder": "Error trying to open folder: {0}",
        "permission_test_fail": "Error: Cannot find a folder with write permissions. Download not possible.",
        "alt_folder_attempt": "Attempting to use alternative folder: {0}",
        "summary_info": "\n--- Summary Information ---",
        "video_title": "Video title: {0}",
        "video_url": "Video URL: {0}",
        "download_folder": "Download folder: {0}",
        "selected_format": "Selected format: {0}",
        "ytdlp_version": "yt-dlp version: {0}",
        "expected_file": "Expected file: {0}",
        "start_download": "Start download? (yes/no): ",
        "download_started": "Download started...",
        "file_saved_success": "File successfully saved: {0}",
        "file_size": "File size: {0} bytes",
        "file_not_found": "Could not find the expected file. Searching for recently created files...",
        "recent_files": "Recently created files:",
        "recent_files_notice": "One of these files might be your downloaded video.",
        "no_recent_files": "No recently created files found in the download folder.",
        "download_problem": "PROBLEM: The video was not saved. Possible reasons:",
        "reason_1": "1. Insufficient disk space",
        "reason_2": "2. Permission problems",
        "reason_3": "3. Antivirus blocking file writing",
        "reason_4": "4. Incompatibility with the current version of yt-dlp",
        "download_finished": "Download finished!",
        "open_folder": "Would you like to open the download folder? (yes/no): ",
        "folder_opened": "Folder opened in file manager",
        "folder_open_failed": "Could not open folder automatically",
        "download_error": "Error during download: {0}",
        "diagnostics": "Attempting diagnostics...",
        "diagnostics_title": "\n--- Diagnostics ---",
        "folder_check": "1. Folder check: {0}",
        "folder_exists": "   Folder exists: {0}",
        "write_permission": "   Write permissions: {0}",
        "free_space": "   Free space: {0} bytes",
        "folder_not_exists": "   Folder does not exist!",
        "version_check": "2. yt-dlp version:",
        "version_detect_failed": "   Could not determine version",
        "simple_download": "3. Attempting to download with simplified parameters:",
        "simple_download_to": "   Downloading to {0}...",
        "simple_success": "   Success! File created ({0} bytes)",
        "simple_error": "   Error: File not created",
        "simple_download_error": "   Error during simplified download: {0}",
        "download_cancelled": "Download canceled.",
        "video_info_failed": "Could not get video information. Download canceled.",
        "select_language": "Виберіть мову / Select language / Seleccione idioma (1-3):",
        "language_1": "1. Українська",
        "language_2": "2. English",
        "language_3": "3. Español",
        "language_selected": "Selected English language / Обрано англійську мову / Idioma inglés seleccionado"
    },
    "es": {  # Spanish
        "app_title": "=== Descargador de Videos de YouTube ===",
        "disclaimer": """
AVISO LEGAL:
Esta herramienta fue creada exclusivamente con fines educativos para demostrar el trabajo con APIs de video.
Al usar este programa, acepta:
- No violar derechos de autor ni términos de servicio
- Descargar solo contenido para el que tenga derechos o permiso
- No usar el programa con fines comerciales sin el permiso de los propietarios del contenido

El autor del programa no es responsable por cualquier uso indebido de esta herramienta.
Toda la responsabilidad por el uso del programa recae en el usuario.
        """,
        "accept_terms": "Acepto los términos (sí/no): ",
        "terms_rejected": "Términos no aceptados. El programa está terminando.",
        "enter_url": "Introduce la URL del video de YouTube: ",
        "ffmpeg_not_found": "ADVERTENCIA: ffmpeg no encontrado. Sin él, es imposible combinar audio y video.",
        "install_ffmpeg": "Por favor instale ffmpeg:",
        "win_install_ffmpeg": "1. Descargue ffmpeg desde https://ffmpeg.org/download.html\n2. Descomprima el archivo y agregue la ruta a la carpeta bin a la variable de entorno PATH",
        "mac_install_ffmpeg": "Ejecute en terminal: brew install ffmpeg",
        "linux_install_ffmpeg": "Ejecute en terminal: sudo apt-get install ffmpeg",
        "continue_without_ffmpeg": "¿Continuar sin combinar audio y video? (sí/no): ",
        "download_canceled": "Descarga cancelada. Por favor instale ffmpeg e intente nuevamente.",
        "custom_folder": "¿Desea elegir una carpeta personalizada para la descarga de video? (sí/no): ",
        "selected_folder": "Carpeta seleccionada: ",
        "write_permission_error": "ADVERTENCIA: No se pueden escribir archivos en {0}. Permisos insuficientes.",
        "using_default_folder": "Se usará la carpeta predeterminada: {0}",
        "selection_canceled": "Selección cancelada. Se usará la carpeta predeterminada: {0}",
        "step1_format": "\n=== PASO 1: Selección de Formato ===",
        "available_formats": "Formatos disponibles:",
        "format_1": "1. Video + audio (archivo único)",
        "format_2": "2. Solo video (sin sonido)",
        "format_3": "3. Solo audio",
        "format_4": "4. Descargar video y audio (archivos separados)",
        "select_format": "Seleccione formato (1-4): ",
        "invalid_choice": "Elección inválida. Se usará la mejor calidad disponible.",
        "best_available": "Mejor disponible",
        "warning_no_ffmpeg": "ADVERTENCIA: ffmpeg no instalado, por lo que se utilizará el mejor formato disponible sin fusionar.",
        "best_available_format": "Mejor formato disponible",
        "video_only": "Solo video (sin sonido)",
        "video_audio_separate": "Video y audio (archivos separados)",
        "step2_quality": "\n=== PASO 2: Selección de Calidad de Video ===",
        "choose_quality": "¿Desea elegir la calidad del video? (sí/no): ",
        "available_quality": "Opciones de calidad disponibles:",
        "quality_1": "1. 2160p (4K)",
        "quality_2": "2. 1440p (2K)",
        "quality_3": "3. 1080p (Full HD)",
        "quality_4": "4. 720p (HD)",
        "quality_5": "5. 480p (SD)",
        "quality_6": "6. 360p (Baja)",
        "quality_note": "Nota: si el video no tiene la calidad especificada, se descargará SIN sonido",
        "select_quality": "Seleccione calidad (1-6): ",
        "best_quality": "Mejor disponible",
        "audio_quality_options": "Opciones de calidad de audio disponibles:",
        "audio_1": "1. Mejor calidad (hasta 320kbps)",
        "audio_2": "2. Calidad media (hasta 192kbps)",
        "audio_3": "3. Calidad baja (hasta 128kbps)",
        "audio_4": "4. Calidad mínima (hasta 64kbps)",
        "select_audio_quality": "Seleccione calidad de audio (1-4): ",
        "best_audio": "Audio - mejor calidad",
        "medium_audio": "Audio - calidad media",
        "low_audio": "Audio - calidad baja",
        "minimal_audio": "Audio - calidad mínima",
        "error_video_info": "Error al obtener información del video: {0}",
        "downloading": "Descargando: {0} velocidad: {1} restante: {2}",
        "download_complete": "¡Descarga completa! Verificando archivo...",
        "file_saved": "Archivo {0} guardado ({1} bytes)",
        "file_empty": "ADVERTENCIA: ¡El archivo tiene tamaño cero! Puede haber un problema con la descarga.",
        "permission_error": "ADVERTENCIA: Problema con los permisos de acceso a la carpeta: {0}",
        "error_checking_version": "Error al verificar la versión de yt-dlp: {0}",
        "version_error": "Error al determinar la versión",
        "unable_to_open_folder": "No se puede abrir la carpeta: {0}",
        "error_opening_folder": "Error al intentar abrir la carpeta: {0}",
        "permission_test_fail": "Error: No se puede encontrar una carpeta con permisos de escritura. Descarga no posible.",
        "alt_folder_attempt": "Intentando usar carpeta alternativa: {0}",
        "summary_info": "\n--- Información Resumida ---",
        "video_title": "Título del video: {0}",
        "video_url": "URL del video: {0}",
        "download_folder": "Carpeta de descarga: {0}",
        "selected_format": "Formato seleccionado: {0}",
        "ytdlp_version": "Versión de yt-dlp: {0}",
        "expected_file": "Archivo esperado: {0}",
        "start_download": "¿Iniciar descarga? (sí/no): ",
        "download_started": "Descarga iniciada...",
        "file_saved_success": "Archivo guardado exitosamente: {0}",
        "file_size": "Tamaño del archivo: {0} bytes",
        "file_not_found": "No se pudo encontrar el archivo esperado. Buscando archivos creados recientemente...",
        "recent_files": "Archivos creados recientemente:",
        "recent_files_notice": "Uno de estos archivos podría ser su video descargado.",
        "no_recent_files": "No se encontraron archivos creados recientemente en la carpeta de descarga.",
        "download_problem": "PROBLEMA: El video no se guardó. Posibles razones:",
        "reason_1": "1. Espacio insuficiente en disco",
        "reason_2": "2. Problemas de permisos",
        "reason_3": "3. Antivirus bloqueando la escritura de archivos",
        "reason_4": "4. Incompatibilidad con la versión actual de yt-dlp",
        "download_finished": "¡Descarga finalizada!",
        "open_folder": "¿Desea abrir la carpeta de descarga? (sí/no): ",
        "folder_opened": "Carpeta abierta en el administrador de archivos",
        "folder_open_failed": "No se pudo abrir la carpeta automáticamente",
        "download_error": "Error durante la descarga: {0}",
        "diagnostics": "Intentando diagnóstico...",
        "diagnostics_title": "\n--- Diagnóstico ---",
        "folder_check": "1. Verificación de carpeta: {0}",
        "folder_exists": "   La carpeta existe: {0}",
        "write_permission": "   Permisos de escritura: {0}",
        "free_space": "   Espacio libre: {0} bytes",
        "folder_not_exists": "   ¡La carpeta no existe!",
        "version_check": "2. Versión de yt-dlp:",
        "version_detect_failed": "   No se pudo determinar la versión",
        "simple_download": "3. Intentando descargar con parámetros simplificados:",
        "simple_download_to": "   Descargando a {0}...",
        "simple_success": "   ¡Éxito! Archivo creado ({0} bytes)",
        "simple_error": "   Error: Archivo no creado",
        "simple_download_error": "   Error durante la descarga simplificada: {0}",
        "download_cancelled": "Descarga cancelada.",
        "video_info_failed": "No se pudo obtener información del video. Descarga cancelada.",
        "select_language": "Виберіть мову / Select language / Seleccione idioma (1-3):",
        "language_1": "1. Українська",
        "language_2": "2. English",
        "language_3": "3. Español",
        "language_selected": "Idioma español seleccionado / Обрано іспанську мову / Selected Spanish language"
    }
}

def select_language():
    """Allows the user to select their preferred language"""
    print("=== YouTube Video Downloader ===")
    print("Виберіть мову / Select language / Seleccione idioma (1-3):")
    print("1. Українська")
    print("2. English")
    print("3. Español")
    
    choice = input("Вибір / Choice / Elección (1-3): ")
    
    if choice == "1":
        print("Обрано українську мову / Selected Ukrainian language / Idioma ucraniano seleccionado")
        return "uk"
    elif choice == "2":
        print("Selected English language / Обрано англійську мову / Idioma inglés seleccionado")
        return "en"
    elif choice == "3":
        print("Idioma español seleccionado / Обрано іспанську мову / Selected Spanish language")
        return "es"
    else:
        print("Invalid choice. Defaulting to English / Невірний вибір. За замовчуванням англійська / Elección inválida. Predeterminado a inglés")
        return "en"

def show_disclaimer(lang):
    """Shows the disclaimer and asks for acceptance"""
    print("\n" + "-" * 80)
    print(LANGUAGES[lang]["disclaimer"])
    print("-" * 80 + "\n")
    
    choice = input(