import os
import sqlite3
import random
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)
app.secret_key = 'sotelok_animal_quant_secret_key_2026'

# --- CONFIGURACIÓN DE BASE DE DATOS Y MOTOR CUANTITATIVO ---
DB_NAME = 'animal_quant.db'

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
            fecha DATE NOT NULL,
            hora TEXT NOT NULL,
            animal_num INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_pronosticos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            loteria TEXT,
            super_fijo INTEGER,
            opcional_1 INTEGER,
            opcional_2 INTEGER,
            score_confianza REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- SISTEMA DE CONSENSO DE 3 IAS (MOTORES ANALÍTICOS) ---

def ia_1_estadistica_frecuencias(loteria):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT animal_num FROM sorteos WHERE loteria = ? ORDER BY id DESC LIMIT 50", (loteria,))
    registros = [r[0] for r in cursor.fetchall()]
    conn.close()

    scores = {num: random.uniform(0.1, 0.5) for num in ANIMALES.keys()}
    
    if registros:
        for num in ANIMALES.keys():
            conteo = registros.count(num)
            if 1 <= conteo <= 3:
                scores[num] += 0.4
            elif conteo == 0:
                scores[num] += 0.2
    return scores

def ia_2_secuencias_markov(loteria):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT animal_num FROM sorteos WHERE loteria = ? ORDER BY id DESC LIMIT 20", (loteria,))
    registros = [r[0] for r in cursor.fetchall()]
    conn.close()

    scores = {num: random.uniform(0.1, 0.5) for num in ANIMALES.keys()}
    
    if len(registros) >= 2:
        ultimo = registros[0]
        siguiente_prob = (ultimo + 7) % 37
        scores[siguiente_prob] += 0.5
        scores[(ultimo + 12) % 37] += 0.3
        
    return scores

def ia_3_maestra_sintetizadora(loteria):
    score_ia1 = ia_1_estadistica_frecuencias(loteria)
    score_ia2 = ia_2_secuencias_markov(loteria)
    
    score_final = {}
    for num in ANIMALES.keys():
        score_final[num] = (score_ia1[num] * 0.5) + (score_ia2[num] * 0.5)
    
    ordenados = sorted(score_final.items(), key=lambda x: x[1], reverse=True)
    
    super_fijo = ordenados[0][0]
    opcional_1 = ordenados[1][0]
    opcional_2 = ordenados[2][0]
    confianza = round(ordenados[0][1] * 100, 2)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historial_pronosticos (loteria, super_fijo, opcional_1, opcional_2, score_confianza)
        VALUES (?, ?, ?, ?, ?)
    ''', (loteria, super_fijo, opcional_1, opcional_2, confianza))
    conn.commit()
    conn.close()
    
    return {
        'super_fijo_num': super_fijo,
        'super_fijo_nombre': ANIMALES.get(super_fijo, 'Animal'),
        'opcional1_num': opcional_1,
        'opcional1_nombre': ANIMALES.get(opcional_1, 'Animal'),
        'opcional2_num': opcional_2,
        'opcional2_nombre': ANIMALES.get(opcional_2, 'Animal'),
        'confianza': confianza
    }

# --- RUTAS DE LA APLICACIÓN WEB ---

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOTELOK ANIMAL QUANT - AI Engine</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent: #38bdf8;
            --hot: #ef4444;
            --gold: #f59e0b;
            --text: #f8fafc;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text);
            margin: 0;
            padding: 15px;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 480px;
        }
        .header {
            text-align: center;
            padding: 15px 0;
            border-bottom: 2px solid #334155;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 20px;
            margin: 0;
            color: var(--accent);
            letter-spacing: 1px;
        }
        .badge-ai {
            background-color: #0284c7;
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 12px;
            text-transform: uppercase;
            font-weight: bold;
        }
        .card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #334155;
        }
        .btn {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border: none;
            padding: 12px;
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
            font-size: 15px;
            cursor: pointer;
            margin-top: 10px;
        }
        .fijo-box {
            background: linear-gradient(135deg, #7f1d1d, #991b1b);
            border: 2px solid var(--hot);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            margin-top: 10px;
        }
        .fijo-title {
            color: #fca5a5;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .fijo-value {
            font-size: 26px;
            font-weight: 900;
            color: #ffffff;
            margin: 5px 0;
        }
        .opcion-box {
            display: flex;
            justify-content: space-between;
            background-color: #0f172a;
            padding: 10px 15px;
            border-radius: 8px;
            margin-top: 8px;
            font-weight: bold;
        }
        select, input {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            background-color: #0f172a;
            color: white;
            border: 1px solid #334155;
            border-radius: 6px;
            box-sizing: border-box;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SOTELOK ANIMAL QUANT</h1>
            <span class="badge-ai">3-AI Consensus Engine v2.0</span>
        </div>

        <div class="card">
            <h3>🤖 Generar Pronóstico Avanzado</h3>
            <form action="/generar" method="POST">
                <label>Seleccionar Lotería:</label>
                <select name="loteria">
                    <option value="Lotto Activo">Lotto Activo</option>
                    <option value="La Granjita">La Granjita</option>
                </select>
                <button type="submit" class="btn">EJECUTAR ANÁLISIS DE 3 IAs</button>
            </form>
        </div>

        {% if pronostico %}
        <div class="card">
            <h3>🔥 Resultado del Consenso Cuantitativo</h3>
            <p style="font-size: 12px; color: #94a3b8; margin-top: -10px;">Lotería: <b>{{ loteria }}</b> | Indice de Confianza: <b>{{ pronostico.confianza }}%</b></p>
            
            <div class="fijo-box">
                <div class="fijo-title">⭐ SUPER FIJO DEL DÍA ⭐</div>
                <div class="fijo-value">[{{ pronostico.super_fijo_num }}] {{ pronostico.super_fijo_nombre }}</div>
            </div>

            <div style="margin-top: 15px;">
                <span style="font-size: 12px; font-weight: bold; color: var(--gold);">🎯 OPCIONALES DE ALTA PROYECCIÓN:</span>
                <div class="opcion-box">
                    <span>Opcional 1:</span>
                    <span>[{{ pronostico.opcional1_num }}] {{ pronostico.opcional1_nombre }}</span>
                </div>
                <div class="opcion-box">
                    <span>Opcional 2:</span>
                    <span>[{{ pronostico.opcional2_num }}] {{ pronostico.opcional2_nombre }}</span>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="card">
            <h3>📥 Cargar Sorteo Oficial (Nutrir IA)</h3>
            <form action="/cargar_sorteo" method="POST">
                <label>Lotería:</label>
                <select name="loteria">
                    <option value="Lotto Activo">Lotto Activo</option>
                    <option value="La Granjita">La Granjita</option>
                </select>
                
                <label style="margin-top: 8px; display: block;">Número Ganador:</label>
                <input type="number" name="animal_num" min="0" max="36" placeholder="Ej: 12" required>
                
                <button type="submit" class="btn" style="background: #10b981; margin-top: 12px;">REGISTRAR RESULTADO</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar():
    loteria = request.form.get('loteria')
    resultado = ia_3_maestra_sintetizadora(loteria)
    return render_template_string(HTML_TEMPLATE, pronostico=resultado, loteria=loteria)

@app.route('/cargar_sorteo', methods=['POST'])
def cargar_sorteo():
    loteria = request.form.get('loteria')
    animal_num = int(request.form.get('animal_num'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sorteos (loteria, fecha, hora, animal_num)
        VALUES (?, DATE('now'), TIME('now'), ?)
    ''', (loteria, animal_num))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
