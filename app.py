import os
import csv
from datetime import datetime
from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plomberie_ia_enterprise_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

order_counter = 0

def get_csv_name():
    return f"RAPPORT_INTERVENTIONS_{datetime.now().strftime('%d-%m-%Y')}.csv"

@app.route('/')
def index():
    # Dashboard principal de l'artisan
    return render_template('index.html')

@app.route('/ia_test')
def cashier():
    # Simulateur de réception d'appels IA
    return render_template('cashier.html')

@app.route('/download_excel')
def download_excel():
    filename = get_csv_name()
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    return "Aucun rapport généré pour aujourd'hui.", 404

@socketio.on('new_order')
def handle_new_order(data):
    global order_counter
    order_counter += 1
    data['order_num'] = f"{order_counter:03d}"
    data['time'] = datetime.now().strftime("%H:%M")
    # Diffusion immédiate vers le smartphone de l'artisan
    emit('new_order', data, broadcast=True)

@socketio.on('finish_order_excel')
def handle_finish_excel(data):
    filename = get_csv_name()
    file_exists = os.path.isfile(filename)
    try:
        with open(filename, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            if not file_exists:
                writer.writerow(['HEURE', 'N° TICKET', 'CLIENT', 'TELEPHONE', 'TYPE', 'DIAGNOSTIC IA', 'MONTANT FIXÉ'])
            writer.writerow([
                data.get('time'),
                data.get('order_num'),
                data.get('nom'),
                data.get('tel'),
                data.get('type'),
                data.get('pizza'), # Contient le diagnostic de la panne
                f"{data.get('total')}€"
            ])
    except Exception as e:
        print(f"Erreur d'écriture Excel : {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)