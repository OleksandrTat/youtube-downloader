# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import subprocess
import shutil
import time
import tempfile
import uuid
import sys
from pathlib import Path

app = Flask(__name__)

# Створюємо тимчасову папку для завантажень
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), 'youtube_downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Словник для зберігання сесій та їх стану
sessions = {}

def check_ffmpeg():
    """Перевіряє, чи встановлено ffmpeg"""
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_available_formats(url):
    """Отримує доступні формати для відео"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            
            # Отримуємо формати
            formats = []
            if 'formats' in info:
                # Фільтруємо та організовуємо формати
                video_formats = []
                audio_formats = []
                combined_formats = []
                
                for f in info['formats']:
                    format_id = f.get('format_id', '')
                    format_note = f.get('format_note', '')
                    ext = f.get('ext', '')
                    resolution = f.get('resolution', 'N/A')
                    vcodec = f.get('vcodec', '')
                    acodec = f.get('acodec', '')
                    filesize = f.get('filesize') or f.get('filesize_approx')
                    filesize_str = f"{round(filesize / (1024 * 1024), 1)}MB" if filesize else "Unknown"
                    
                    format_info = {
                        'format_id': format_id,
                        'ext': ext,
                        'resolution': resolution,
                        'note': format_note,
                        'filesize': filesize_str,
                        'has_video': vcodec != 'none',
                        'has_audio': acodec != 'none'
                    }
                    
                    # Категоризуємо формати
                    if vcodec != 'none' and acodec != 'none':
                        combined_formats.append(format_info)
                    elif vcodec != 'none':
                        video_formats.append(format_info)
                    elif acodec != 'none':
                        audio_formats.append(format_info)
                
                # Сортуємо формати
                video_formats.sort(key=lambda x: x['resolution'], reverse=True)
                audio_formats.sort(key=lambda x: x['note'], reverse=True)
                combined_formats.sort(key=lambda x: x['resolution'], reverse=True)
                
                formats = {
                    'video': video_formats,  # Обмежуємо кількість для кращого відображення
                    'audio': audio_formats,
                    'combined': combined_formats
                }
            
            return {
                'title': info.get('title', 'Невідоме відео'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Невідомо'),
                'formats': formats
            }
        except Exception as e:
            return {"error": str(e)}

def get_video_info(url, ydl_opts):
    """Отримує інформацію про відео"""
    info_opts = ydl_opts.copy()
    info_opts['skip_download'] = True
    
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            return {"error": str(e)}

def download_yt_video(url, format_option, merge_format, download_path, session_id):
    """Функція завантаження відео"""
    sessions[session_id]['status'] = 'downloading'
    
    class ProgressHook:
        def __call__(self, d):
            if d['status'] == 'downloading':
                sessions[session_id]['progress'] = {
                    'percent': d.get('_percent_str', 'N/A'),
                    'speed': d.get('_speed_str', 'N/A'),
                    'eta': d.get('_eta_str', 'N/A')
                }
            elif d['status'] == 'finished':
                sessions[session_id]['progress'] = {
                    'percent': '100%',
                    'status': 'finished',
                    'filename': d.get('filename', 'невідомий файл')
                }
    
    # Базові налаштування
    ydl_opts = {
        'format': format_option,
        'noplaylist': True,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [ProgressHook()],
        'noprogress': False,
        'quiet': False,
        'verbose': True,
    }
    
    # Якщо формат потребує об'єднання і ffmpeg встановлено
    if merge_format and check_ffmpeg():
        ydl_opts['merge_output_format'] = merge_format
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': merge_format,
        }]
        ydl_opts['postprocessor_args'] = {
            'ffmpeg': ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k']
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        # Перевіряємо, який файл було створено
        if info and 'title' in info:
            expected_title = info.get('title', 'video')
            expected_ext = info.get('ext', 'mp4')
            
            # Знаходимо файл у папці завантаження
            for file in os.listdir(download_path):
                file_path = os.path.join(download_path, file)
                if os.path.isfile(file_path) and expected_title in file:
                    # Копіюємо файл у статичну папку для доступу з браузера
                    static_path = os.path.join('static', 'downloads', session_id)
                    os.makedirs(static_path, exist_ok=True)
                    
                    new_path = os.path.join(static_path, file)
                    shutil.copy2(file_path, new_path)
                    
                    sessions[session_id]['file'] = {
                        'path': new_path,
                        'name': file,
                        'url': f'/static/downloads/{session_id}/{file}'
                    }
                    sessions[session_id]['status'] = 'completed'
                    return True
                    
        sessions[session_id]['status'] = 'error'
        sessions[session_id]['error'] = 'Не вдалося знайти завантажений файл'
        return False
        
    except Exception as e:
        sessions[session_id]['status'] = 'error'
        sessions[session_id]['error'] = str(e)
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-session', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'status': 'created',
        'progress': {},
        'commands': [],
        'responses': ["=== YouTube Video Downloader ===\nВведіть URL відео YouTube:"]
    }
    return jsonify({'session_id': session_id})

@app.route('/command', methods=['POST'])
def handle_command():
    data = request.json
    session_id = data.get('session_id')
    command = data.get('command')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Невірний ID сесії'}), 400
    
    # Додаємо команду до історії
    sessions[session_id]['commands'].append(command)
    
    # Отримуємо поточний стан сесії
    state = sessions[session_id].get('state', 'initial')
    
    # Обробка команд залежно від стану
    if state == 'initial':
        # Очікуємо URL відео
        url = command.strip()
        sessions[session_id]['url'] = url
        
        # Отримуємо інформацію про відео
        video_info = get_available_formats(url)
        
        if 'error' in video_info:
            response = f"Помилка при отриманні інформації про відео: {video_info['error']}\nСпробуйте ще раз з іншим URL."
            sessions[session_id]['responses'].append(response)
            return jsonify({'response': response})
        
        sessions[session_id]['video_info'] = video_info
        sessions[session_id]['state'] = 'format_selection'
        
        # Підготувати відповідь з доступними форматами
        response = (f"\n=== Знайдене відео: {video_info['title']} ===\n"
                    f"Тривалість: {video_info.get('duration', 0) // 60} хв {video_info.get('duration', 0) % 60} сек\n"
                    f"Автор: {video_info.get('uploader', 'Невідомо')}\n\n"
                    "=== КРОК 1: Вибір типу завантаження ===\n"
                    "Доступні опції:\n"
                    "1. Відео + аудіо (один файл)\n"
                    "2. Тільки відео (без звуку)\n"
                    "3. Тільки аудіо\n"
                    "4. Завантажити і відео, і аудіо (окремими файлами)\n"
                    "Виберіть опцію (1-4): ")
        
        sessions[session_id]['responses'].append(response)
        return jsonify({'response': response})
    
    elif state == 'format_selection':
        # Обробка вибору формату
        format_choice = command.strip()
        video_info = sessions[session_id]['video_info']
        formats = video_info.get('formats', {})
        
        if format_choice == "1":  # Відео + аудіо
            sessions[session_id]['format_type'] = 'combined'
            available_formats = formats.get('combined', [])
            if not available_formats and check_ffmpeg():
                # Якщо немає комбінованих форматів, використовуємо найкращі відео та аудіо
                sessions[session_id]['format'] = "bestvideo+bestaudio/best"
                sessions[session_id]['merge_format'] = "mp4"
                sessions[session_id]['state'] = 'confirmation'
                
                response = ("\n--- Підсумкова інформація ---\n"
                          f"Назва відео: {video_info.get('title', 'Невідомо')}\n"
                          f"URL відео: {sessions[session_id]['url']}\n"
                          f"Вибраний формат: Найкраща якість (відео + аудіо)\n"
                          "----------------------------\n\n"
                          "Розпочати завантаження? (так/ні): ")
                
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
            else:
                # Показуємо доступні комбіновані формати
                response = "\n=== КРОК 2: Вибір якості ===\nДоступні формати відео + аудіо:\n"
                for i, fmt in enumerate(available_formats, 1):
                    response += f"{i}. {fmt['resolution']} ({fmt['ext']}) - {fmt['filesize']}\n"
                response += "Виберіть номер формату: "
                
                sessions[session_id]['state'] = 'quality_selection'
                sessions[session_id]['available_formats'] = available_formats
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
                
        elif format_choice == "2":  # Тільки відео
            sessions[session_id]['format_type'] = 'video'
            available_formats = formats.get('video', [])
            if not available_formats:
                sessions[session_id]['format'] = "bestvideo/best[vcodec!=none]"
                sessions[session_id]['merge_format'] = None
                sessions[session_id]['state'] = 'confirmation'
                
                response = ("\n--- Підсумкова інформація ---\n"
                          f"Назва відео: {video_info.get('title', 'Невідомо')}\n"
                          f"URL відео: {sessions[session_id]['url']}\n"
                          f"Вибраний формат: Тільки відео (найкраща якість)\n"
                          "----------------------------\n\n"
                          "Розпочати завантаження? (так/ні): ")
                
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
            else:
                # Показуємо доступні відео формати
                response = "\n=== КРОК 2: Вибір якості ===\nДоступні формати відео (без звуку):\n"
                for i, fmt in enumerate(available_formats, 1):
                    response += f"{i}. {fmt['resolution']} ({fmt['ext']}) - {fmt['filesize']}\n"
                response += "Виберіть номер формату: "
                
                sessions[session_id]['state'] = 'quality_selection'
                sessions[session_id]['available_formats'] = available_formats
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
                
        elif format_choice == "3":  # Тільки аудіо
            sessions[session_id]['format_type'] = 'audio'
            available_formats = formats.get('audio', [])
            if not available_formats:
                sessions[session_id]['format'] = "bestaudio"
                sessions[session_id]['merge_format'] = None
                sessions[session_id]['state'] = 'confirmation'
                
                response = ("\n--- Підсумкова інформація ---\n"
                          f"Назва відео: {video_info.get('title', 'Невідомо')}\n"
                          f"URL відео: {sessions[session_id]['url']}\n"
                          f"Вибраний формат: Тільки аудіо (найкраща якість)\n"
                          "----------------------------\n\n"
                          "Розпочати завантаження? (так/ні): ")
                
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
            else:
                # Показуємо доступні аудіо формати
                response = "\n=== КРОК 2: Вибір якості ===\nДоступні формати аудіо:\n"
                for i, fmt in enumerate(available_formats, 1):
                    response += f"{i}. {fmt['note']} ({fmt['ext']}) - {fmt['filesize']}\n"
                response += "Виберіть номер формату: "
                
                sessions[session_id]['state'] = 'quality_selection'
                sessions[session_id]['available_formats'] = available_formats
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
                
        elif format_choice == "4":  # І відео, і аудіо окремо
            sessions[session_id]['format_type'] = 'separate'
            sessions[session_id]['format'] = "bestvideo,bestaudio"
            sessions[session_id]['merge_format'] = None
            
            # Перейти до підтвердження
            sessions[session_id]['state'] = 'confirmation'
            
            response = ("\n--- Підсумкова інформація ---\n"
                      f"Назва відео: {video_info.get('title', 'Невідомо')}\n"
                      f"URL відео: {sessions[session_id]['url']}\n"
                      f"Вибраний формат: Окремі файли відео та аудіо\n"
                      "----------------------------\n\n"
                      "Розпочати завантаження? (так/ні): ")
            
            sessions[session_id]['responses'].append(response)
            return jsonify({'response': response})
        else:
            # Невідомий вибір
            response = "Невідомий вибір. Будь ласка, виберіть опцію від 1 до 4."
            sessions[session_id]['responses'].append(response)
            return jsonify({'response': response})
    
    elif state == 'quality_selection':
        # Обробка вибору якості
        quality_choice = command.strip()
        available_formats = sessions[session_id].get('available_formats', [])
        
        try:
            choice_idx = int(quality_choice) - 1
            if 0 <= choice_idx < len(available_formats):
                selected_format = available_formats[choice_idx]
                
                # Зберігаємо вибраний формат
                sessions[session_id]['format'] = selected_format['format_id']
                sessions[session_id]['merge_format'] = None
                
                # Формуємо інформацію для підтвердження
                format_type = sessions[session_id]['format_type']
                format_info = ""
                
                if format_type == 'combined':
                    format_info = f"{selected_format['resolution']} ({selected_format['ext']})"
                elif format_type == 'video':
                    format_info = f"Тільки відео {selected_format['resolution']} ({selected_format['ext']})"
                elif format_type == 'audio':
                    format_info = f"Тільки аудіо {selected_format['note']} ({selected_format['ext']})"
                
                # Перейти до підтвердження
                sessions[session_id]['state'] = 'confirmation'
                
                video_info = sessions[session_id]['video_info']
                response = ("\n--- Підсумкова інформація ---\n"
                          f"Назва відео: {video_info.get('title', 'Невідомо')}\n"
                          f"URL відео: {sessions[session_id]['url']}\n"
                          f"Вибраний формат: {format_info}\n"
                          "----------------------------\n\n"
                          "Розпочати завантаження? (так/ні): ")
                
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
            else:
                response = f"Невірний вибір. Виберіть число від 1 до {len(available_formats)}."
                sessions[session_id]['responses'].append(response)
                return jsonify({'response': response})
        except ValueError:
            response = "Будь ласка, введіть число."
            sessions[session_id]['responses'].append(response)
            return jsonify({'response': response})
    
    elif state == 'confirmation':
        # Обробка підтвердження
        confirmation = command.strip().lower()
        
        if confirmation in ["так", "yes", "y", "т"]:
            response = "Завантаження розпочато...\n"
            sessions[session_id]['responses'].append(response)
            
            # Запускаємо завантаження у окремому потоці
            import threading
            
            download_path = os.path.join(DOWNLOAD_DIR, session_id)
            os.makedirs(download_path, exist_ok=True)
            
            url = sessions[session_id]['url']
            format_option = sessions[session_id]['format']
            merge_format = sessions[session_id].get('merge_format')
            
            sessions[session_id]['state'] = 'downloading'
            
            thread = threading.Thread(
                target=download_yt_video,
                args=(url, format_option, merge_format, download_path, session_id)
            )
            thread.start()
            
            return jsonify({
                'response': response,
                'status': 'downloading',
                'session_id': session_id
            })
        else:
            response = "Завантаження скасовано.\nВведіть URL іншого відео або оновіть сторінку для перезапуску."
            sessions[session_id]['state'] = 'initial'
            sessions[session_id]['responses'].append(response)
            return jsonify({'response': response})
    
    else:
        response = "Невідомий стан сесії. Будь ласка, оновіть сторінку і спробуйте знову."
        sessions[session_id]['responses'].append(response)
        return jsonify({'response': response})

@app.route('/status/<session_id>', methods=['GET'])
def get_status(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Невірний ID сесії'}), 400
    
    return jsonify({
        'status': sessions[session_id].get('status', 'unknown'),
        'progress': sessions[session_id].get('progress', {}),
        'file': sessions[session_id].get('file', {}),
        'error': sessions[session_id].get('error', '')
    })

@app.route('/downloads/<session_id>/<filename>')
def download_file(session_id, filename):
    if session_id not in sessions:
        return "Файл не знайдено", 404
    
    # Повернути файл для завантаження
    download_path = os.path.join(DOWNLOAD_DIR, session_id)
    return send_from_directory(download_path, filename, as_attachment=True)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Невірний ID сесії'}), 400
    
    # Видаляємо файли сесії
    download_path = os.path.join(DOWNLOAD_DIR, session_id)
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    
    # Видаляємо статичні файли
    static_path = os.path.join('static', 'downloads', session_id)
    if os.path.exists(static_path):
        shutil.rmtree(static_path)
    
    # Видаляємо інформацію про сесію
    sessions.pop(session_id, None)
    
    return jsonify({'success': True})

if __name__ == "__main__":
    # Створюємо статичну папку для завантажень
    os.makedirs(os.path.join('static', 'downloads'), exist_ok=True)
    
    # Запускаємо сервер
    app.run(debug=True)