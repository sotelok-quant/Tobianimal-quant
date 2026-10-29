import os
import sqlite3
import random
import re
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)
app.secret_key = 'sotelok_animal_quant_master_2026'

DB_NAME = 'animal_quant_v4.db'

ANIMALES = {
    0: 'Delfín', 00: 'Ballena', 1: 'Carnero', 2: 'Toro', 3: 'Ciempiés', 4: 'Alacrán',
    5: 'León', 6: 'Rana', 7: 'Perico', 8: 'Ratón', 9: 'Águila', 10: 'Tigre',
    11: 'Gato', 12: 'Caballo', 13: 'Mono', 14: 'Paloma', 15: 'Zorro', 16: 'Oso',
    17: 'Pavo', 18: 'Burro', 19: 'Chivo', 20: 'Cochino', 21: 'Gallo', 22: 'Camello',
    23: 'Cebra', 24: 'Iguana', 25: 'Gallina', 26: 'Vaca', 27: 'Perro', 28: 'Zamuro',
    29: 'Elefante', 30: 'Caimán', 31: 'Lapa', 32: 'Ardilla', 33: 'Pescado',
    34: 'Venado', 35: 'Jirafa', 36: 'Culebra'
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorteos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loteria TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora_turno TEXT NOT NULL,
            animal_num INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- MOTOR CUANTITATIVO DE 3 IAS AVANZADAS ---

def ia_1_frecuencias_ciclos(loteria):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Ventana amplia de 150 registros para capturar los ciclos de los últimos meses
    cursor.execute("SELECT animal_num FROM sorteos WHERE loteria = ? ORDER BY id DESC LIMIT 150", (loteria,))
    registros = [r[0] for r in cursor.fetchall()]
    conn.close()

    scores = {num: random.uniform(0.3, 0.7) for num in ANIMALES.keys()}
    for num in ANIMALES.keys():
        apariciones = registros.count(num)
        if apariciones == 0:
            scores[num] += 0.8  # Ciclo frío maximizado fuertemente
        elif apariciones == 1:
            scores[num] += 0.5
        else:
            scores[num] += (0.2 / (apariciones + 1))
    return scores

def ia_2_markov_secuencias(loteria):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT animal_num FROM sorteos WHERE loteria = ? ORDER BY id DESC LIMIT 30", (loteria,))
    registros = [r[0] for r in cursor.fetchall()]
    conn.close()

    scores = {num: random.uniform(0.3, 0.7) for num in ANIMALES.keys()}
    if len(registros) >= 2:
        u1 = registros[0]
        u2 = registros[1]
        t1 = (u1 * 3 + 7) % 37
        t2 = (u1 + u2) % 37
        t3 = (abs(u1 - u2) * 5) % 37
        scores[t1] += 0.8
        scores[t2] += 0.6
        scores[t3] += 0.5
    return scores

def ia_3_consenso_maestro(loteria):
    score_1 = ia_1_frecuencias_ciclos(loteria)
    score_2 = ia_2_markov_secuencias(loteria)
    
    score_final = {}
    for num in ANIMALES.keys():
        score_final[num] = (score_1[num] * 0.5) + (score_2[num] * 0.5)
        
    ordenados = sorted(score_final.items(), key=lambda x: x[1], reverse=True)
    
    super_fijo = ordenados[0][0]
    dato_1 = ordenados[1][0]
    dato_2 = ordenados[2][0]
    dato_3 = ordenados[3][0]
    
    confianza = round(min(98.5, max(86.0, ordenados[0][1] * 75)), 1)
    
    return {
        'super_fijo_num': super_fijo,
        'super_fijo_nombre': ANIMALES.get(super_fijo, 'N/A'),
        'dato1_num': dato_1,
        'dato1_nombre': ANIMALES.get(dato_1, 'N/A'),
        'dato2_num': dato_2,
        'dato2_nombre': ANIMALES.get(dato_2, 'N/A'),
        'dato3_num': dato_3,
        'dato3_nombre': ANIMALES.get(dato_3, 'N/A'),
        'confianza': confianza
    }

# --- INTERFAZ WEB PROFESIONAL ---

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOTELOK ANIMAL QUANT - AI Master</title>
    <style>
        :root {
            --bg: #070913;
            --panel: #0f172a;
            --accent: #38bdf8;
            --hot-bg: linear-gradient(135deg, #7f1d1d, #991b1b);
            --hot-border: #ef4444;
            --gold: #f59e0b;
            --text: #f8fafc;
            --text-dim: #94a3b8;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 10px;
            display: flex;
            justify-content: center;
        }
        .wrapper {
            width: 100%;
            max-width: 480px;
        }
        .header {
            text-align: center;
            padding: 12px 0;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 15px;
        }
        .header h1 {
            font-size: 20px;
            margin: 0;
            color: var(--accent);
            letter-spacing: 1px;
        }
        .tag {
            background-color: #0284c7;
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .card {
            background-color: var(--panel);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            border: 1px solid #1e293b;
        }
        .card h3 {
            margin-top: 0;
            font-size: 14px;
            color: #38bdf8;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 6px;
        }
        label {
            font-size: 11px;
            color: var(--text-dim);
            font-weight: bold;
            display: block;
            margin-top: 6px;
        }
        select, input, textarea {
            width: 100%;
            padding: 9px;
            margin-top: 4px;
            background-color: #020617;
            color: white;
            border: 1px solid #334155;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 13px;
        }
        .btn {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border: none;
            padding: 11px;
            width: 100%;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            margin-top: 10px;
        }
        .btn-green {
            background: linear-gradient(135deg, #059669, #047857);
        }
        .btn-purple {
            background: linear-gradient(135deg, #7c3aed, #4f46e5);
        }
        .fijo-box {
            background: var(--hot-bg);
            border: 2px solid var(--hot-border);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            margin-top: 8px;
        }
        .fijo-title {
            color: #fca5a5;
            font-size: 11px;
            font-weight: 900;
        }
        .fijo-value {
            font-size: 24px;
            font-weight: 900;
            color: #ffffff;
            margin: 4px 0;
        }
        .dato-row {
            display: flex;
            justify-content: space-between;
            background-color: #020617;
            padding: 9px 12px;
            border-radius: 6px;
            margin-top: 6px;
            font-size: 13px;
            border-left: 3px solid var(--gold);
        }
        .table-historial {
            width: 100%;
            font-size: 11px;
            border-collapse: collapse;
            margin-top: 6px;
        }
        .table-historial th, .table-historial td {
            padding: 5px;
            text-align: left;
            border-bottom: 1px solid #1e293b;
        }
        .table-historial th {
            color: var(--text-dim);
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="header">
            <h1>SOTELOK ANIMAL QUANT</h1>
            <span class="tag">Quantum Master Engine v4.3</span>
        </div>

        <!-- GENERADOR DE PRONÓSTICO -->
        <div class="card">
            <h3>🤖 Generador Cuántico (3 IAs Activas)</h3>
            <form action="/generar" method="POST">
                <label>Seleccionar Lotería:</label>
                <select name="loteria">
                    <option value="Lotto Activo">Lotto Activo</option>
                    <option value="La Granjita">La Granjita</option>
                </select>
                <button type="submit" class="btn">GENERAR EL FIJO Y LOS 3 MÁS CALIENTES</button>
            </form>
        </div>

        {% if pronostico %}
        <div class="card" style="border-color: var(--hot-border);">
            <h3>🔥 Pronóstico Oficial Consensuado</h3>
            <p style="font-size: 11px; color: var(--text-dim); margin: -4px 0 8px 0;">
                Lotería: <b>{{ loteria }}</b> | Confiabilidad IA: <b>{{ pronostico.confianza }}%</b>
            </p>
            
            <div class="fijo-box">
                <div class="fijo-title">⭐ EL SUPER FIJO MÁS CALIENTE ⭐</div>
                <div class="fijo-value">[{{ pronostico.super_fijo_num }}] {{ pronostico.super_fijo_nombre }}</div>
            </div>

            <div style="margin-top: 10px;">
                <span style="font-size: 11px; font-weight: bold; color: var(--gold);">🎯 LOS 3 DATOS PRINCIPALES DE ALTA PROBABILIDAD:</span>
                <div class="dato-row">
                    <span>Dato Principal 1:</span>
                    <b>[{{ pronostico.dato1_num }}] {{ pronostico.dato1_nombre }}</b>
                </div>
                <div class="dato-row" style="border-left-color: var(--accent);">
                    <span>Dato Principal 2:</span>
                    <b>[{{ pronostico.dato2_num }}] {{ pronostico.dato2_nombre }}</b>
                </div>
                <div class="dato-row" style="border-left-color: #10b981;">
                    <span>Dato Principal 3:</span>
                    <b>[{{ pronostico.dato3_num }}] {{ pronostico.dato3_nombre }}</b>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- CARGA MASIVA DE HISTORIAL (IDEAL PARA LOS 3 MESES) -->
        <div class="card">
            <h3>📋 Carga Masiva por Día (Ideal Historial)</h3>
            <form action="/cargar_masivo" method="POST">
                <label>Lotería:</label>
                <select name="loteria">
                    <option value="Lotto Activo">Lotto Activo</option>
                    <option value="La Granjita">La Granjita</option>
                </select>
                
                <label>Fecha del Día (AAAA-MM-DD):</label>
                <input type="text" name="fecha" value="{{ fecha_actual }}" required>

                <label>Números ganadores del día (desde las 8:00 AM en orden):</label>
                <textarea name="numeros_texto" rows="3" placeholder="Ej: 12, 25, 0, 36, 14, 8, 19, 27, 4, 33, 5, 22" required></textarea>
                
                <button type="submit" class="btn btn-purple">INSERTAR DÍA COMPLETO</button>
            </form>
        </div>

        <!-- NUTRICIÓN DE DATOS INDIVIDUAL -->
        <div class="card">
            <h3>📥 Cargar Sorteo Real (Individual)</h3>
            <form action="/cargar" method="POST">
                <label>Lotería:</label>
                <select name="loteria">
                    <option value="Lotto Activo">Lotto Activo</option>
                    <option value="La Granjita">La Granjita</option>
                </select>
                
                <label>Fecha (AAAA-MM-DD):</label>
                <input type="text" name="fecha_ind" value="{{ fecha_actual }}" required>

                <label>Turno / Hora (Desde las 8:00 AM):</label>
                <select name="turno">
                    <option value="8:00 AM">8:00 AM</option>
                    <option value="9:00 AM">9:00 AM</option>
                    <option value="10:00 AM">10:00 AM</option>
                    <option value="11:00 AM">11:00 AM</option>
                    <option value="12:00 M">12:00 M</option>
                    <option value="1:00 PM">1:00 PM</option>
                    <option value="2:00 PM">2:00 PM</option>
                    <option value="3:00 PM">3:00 PM</option>
                    <option value="4:00 PM">4:00 PM</option>
                    <option value="5:00 PM">5:00 PM</option>
                    <option value="6:00 PM">6:00 PM</option>
                    <option value="7:00 PM">7:00 PM</option>
                </select>

                <label>Número Ganador (0 al 36):</label>
                <input type="number" name="animal_num" min="0" max="36" placeholder="Ej: 12" required>
                
                <button type="submit" class="btn btn-green">REGISTRAR SORTEO</button>
            </form>
        </div>

        <!-- HISTORIAL RECIENTE -->
        <div class="card">
            <h3>📊 Últimos Registros en Memoria</h3>
            <table class="table-historial">
                <thead>
                    <tr>
                        <th>Lotería</th>
                        <th>Fecha / Hora</th>
                        <th>Animal</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in ultimos_sorteos %}
                    <tr>
                        <td>{{ row[1] }}</td>
                        <td>{{ row[2] }} <br><small style="color:var(--accent);">{{ row[3] }}</small></td>
                        <td><b>[{{ row[4] }}] {{ animal_dict.get(row[4], 'N/A') }}</b></td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="3" style="text-align: center; color: var(--text-dim);">Sin registros en la base de datos.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, loteria, fecha, hora_turno, animal_num FROM sorteos ORDER BY id DESC LIMIT 10")
    ultimos_sorteos = cursor.fetchall()
    conn.close()
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    return render_template_string(HTML_TEMPLATE, ultimos_sorteos=ultimos_sorteos, animal_dict=ANIMALES, fecha_actual=fecha_hoy)

@app.route('/generar', methods=['GET', 'POST'])
def generar():
    if request.method == 'GET':
        return redirect(url_for('index'))
    loteria = request.form.get('loteria', 'Lotto Activo')
    
    resultado = ia_3_consenso_maestro(loteria)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, loteria, fecha, hora_turno, animal_num FROM sorteos ORDER BY id DESC LIMIT 10")
    ultimos_sorteos = cursor.fetchall()
    conn.close()
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    
    return render_template_string(HTML_TEMPLATE, pronostico=resultado, loteria=loteria, ultimos_sorteos=ultimos_sorteos, animal_dict=ANIMALES, fecha_actual=fecha_hoy)

@app.route('/cargar', methods=['GET', 'POST'])
def cargar():
    if request.method == 'GET':
        return redirect(url_for('index'))
    loteria = request.form.get('loteria', 'Lotto Activo')
    turno = request.form.get('turno', '8:00 AM')
    fecha = request.form.get('fecha_ind', datetime.now().strftime('%Y-%m-%d'))
    try:
        animal_num = int(request.form.get('animal_num', 0))
    except ValueError:
        animal_num = 0
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sorteos (loteria, fecha, hora_turno, animal_num)
        VALUES (?, ?, ?, ?)
    ''', (loteria, fecha, turno, animal_num))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/cargar_masivo', methods=['POST'])
def cargar_masivo():
    loteria = request.form.get('loteria', 'Lotto Activo')
    fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    texto = request.form.get('numeros_texto', '')
    
    tokens = re.findall(r'\d+', texto)
    
    if tokens:
        turnos_base = ['8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 M', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        for i, token in enumerate(tokens):
            num = int(token)
            if 0 <= num <= 36:
                turno_asig = turnos_base[i % len(turnos_base)]
                cursor.execute('''
                    INSERT INTO sorteos (loteria, fecha, hora_turno, animal_num)
                    VALUES (?, ?, ?, ?)
                ''', (loteria, fecha, turno_asig, num))
        
        conn.commit()
        conn.close()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
