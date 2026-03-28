import os
import csv
from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plomberie-secret-123'
# On autorise toutes les connexions pour que le PC et le TEL se parlent
socketio = SocketIO(app, cors_allowed_origins="*")

# Dossier pour le rapport Excel/CSV
REPORT_FILE = 'rapport_interventions.csv'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ia_test')
def cashier():
    return render_template('cashier.html')

# --- C'EST CETTE PARTIE QUI FAIT LE PONT ---
@socketio.on('new_order')
def handle_new_order(data):
    print("Nouvelle mission reçue de l'IA:", data)
    # On renvoie la mission à TOUS les écrans connectés (ton téléphone)
    emit('new_order', data, broadcast=True)

@socketio.on('finish_order_excel')
def save_to_excel(data):
    file_exists = os.path.isfile(REPORT_FILE)
    with open(REPORT_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['ID', 'Date/Heure', 'Type', 'Client', 'Panne', 'Total (€)', 'Adresse'])
        
        writer.writerow([
            data.get('id'),
            data.get('time'),
            data.get('type'),
            data.get('nom'),
            data.get('pizza'),
            data.get('total'),
            data.get('adresse')
        ])

@app.route('/download_excel')
def download_excel():
    if os.path.exists(REPORT_FILE):
        return send_file(REPORT_FILE, as_attachment=True)
    return "Aucun rapport généré pour le moment.", 404

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
