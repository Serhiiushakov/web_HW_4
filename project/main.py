from flask import Flask, request, send_from_directory, render_template
import threading
import socket
import json
from datetime import datetime
import os

app = Flask(__name__)

# Створення директорії для збереження даних, якщо вона не існує
STORAGE_FOLDER = os.path.join(os.path.dirname(__file__), 'storage')
DATA_FILE = os.path.join(STORAGE_FOLDER, 'data.json')
os.makedirs(STORAGE_FOLDER, exist_ok=True)

# Ініціалізація файлу даних, якщо він не існує
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Шляхи для сторінок
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        send_message_to_udp_server({'username': username, 'message': message})
        return 'Message sent!'
    return render_template('message.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.root_path, filename)

# Відправка повідомлення на UDP сервер
def send_message_to_udp_server(message_data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 5000)
    message = json.dumps(message_data).encode('utf-8')
    sock.sendto(message, server_address)

# UDP сервер для отримання повідомлень
def udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 5000)
    sock.bind(server_address)
    while True:
        data, _ = sock.recvfrom(4096)
        message_data = json.loads(data.decode('utf-8'))
        save_message_to_json(message_data)

# Збереження повідомлення у файл JSON
def save_message_to_json(message_data):
    timestamp = datetime.now().isoformat()
    with open(DATA_FILE, 'r+') as f:
        data = json.load(f)
        data[timestamp] = message_data
        f.seek(0)
        json.dump(data, f, indent=4)

# Запуск Flask і UDP серверів у різних потоках
if __name__ == '__main__':
    threading.Thread(target=udp_server, daemon=True).start()
    app.run(port=3000)
