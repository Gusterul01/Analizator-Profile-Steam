from flask import Flask, render_template_string, request, jsonify
from Analiza_Profil_Steam import AnalizareStatisticiSteam
from baza_date import save_report, get_reports_history, get_report_by_id


app = Flask(__name__)

STEAM_API_KEY = "385A2D3230C4EBECFD7192F9D6E32D40"

# Initializam aplicatia din modulul Analiza_Profil_Steam
analyzer = AnalizareStatisticiSteam(STEAM_API_KEY)


@app.route('/', methods=['GET', 'POST'])
def index():

    history = get_reports_history()

    html_template = """
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analizarea Statisticilor Profilului Steam</title>
    <script src="https://cdn.tailwindcss.com"></script>
    {% raw %}
    <style>
        body { font-family: sans-serif; background-color: #0d1117; color: #c9d1d9; }
        .input-group input, .input-group textarea, .report-box {
            background-color: #21262d; border: 1px solid #30363d; color: #c9d1d9; border-radius: 0.5rem; padding: 0.5rem;
        }

        
        .btn-primary { background-color: #10b981; transition: all 0.15s; }
        .btn-primary:hover { background-color: #059669; }
        .btn-secondary { background-color: #3b82f6; }
        .btn-secondary:hover { background-color: #2563eb; }
        
        /* Text box-ul pentru generarea raportului */
        .report-box { 
            white-space: pre-wrap; font-family: monospace; min-height: 400px;
            border-left: 4px solid #3b82f6; /* Sincronizat cu butonul */
            overflow-y: auto;
        }
        
        /* Bara laterala pentru istoric */
        #history-sidebar {
        background-color: #1a0f12;}
        .history-item:hover { background-color: #3b0f15; cursor: pointer; }
        .text-accent { color: #f87171;}
        .error-message { color: #ef4444; }
        .loader { border: 4px solid #f3f3f3; border-top: 4px solid #10b981; border-radius: 50%; width: 20px;
         height: 20px; animation: spin 2s linear infinite; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
    {% endraw %}
</head>
<body>
    <div class="flex h-screen">
        <!-- Bara Laterala Istoric Rapoarte -->
        <div id="history-sidebar" class="w-64 bg-[#171d25] border-r border-[#30363d] p-4 overflow-y-auto">
            <h2 class="text-xl font-bold mb-4 text-white">Istoric Rapoarte</h2>
            <ul id="history-list">
                {% for report in history %}
                <li class="history-item p-2 border-b border-gray-700 text-sm" 
                    onclick="loadReport({{ report.id }})">
                    <span class="font-semibold text-green-400">{{ report.profile_name }}</span>
                    <span class="text-xs text-gray-500 block">{{ report.timestamp }}</span>
                </li>
                {% else %}
                <li class="p-2 text-gray-400 text-sm">Nu exista rapoarte salvate.</li>
                {% endfor %}
            </ul>
        </div>

        <!-- Continut Principal -->
        <div class="flex-1 p-8">
            <h1 class="text-3xl font-extrabold mb-6 text-white">Analizarea Statisticilor Profilului Steam</h1>
            <p class="mb-6 text-gray-400">Introdu STEAM ID-ul sau numele profilului (Trebuie sa fie public)</p>

            <!-- Formular de Intrare -->
            <div class="flex space-x-4 mb-8">
                <input type="text" id="steam_id_input" placeholder="Steam ID (17 cifre) sau numele profilului" 
                class="flex-1 px-4 py-2" required>
                <button onclick="generateReport()" class="btn-primary px-6 py-2 font-semibold rounded-lg flex items-center">
                    Genereaza Raportul
                    <div id="loader" class="loader ml-2"></div>
                </button>
            </div>

            <p id="message_area" class="error-message mb-4"></p>

            <!-- Casuta de Raport -->
            <h2 class="text-2xl font-bold mb-4 text-white">Raport Generat</h2>
            <pre id="report_output" class="report-box p-4"></pre>

            <!-- Buton Salvare -->
            <div id="save_container" class="mt-4 hidden">
                <button onclick="saveCurrentReport()" id="save_button" class="btn-secondary px-6 py-2 font-semibold rounded-lg">
                    Salveaza Raportul in Baza de Date
                </button>
            </div>
        </div>
    </div>

    {% raw %}
    <script>
        let currentReport = null; // Stocheaza ultimul raport generat pentru salvare

        async function generateReport() {
            const inputId = document.getElementById('steam_id_input').value.trim();
            const output = document.getElementById('report_output');
            const messageArea = document.getElementById('message_area');
            const loader = document.getElementById('loader');
            const saveContainer = document.getElementById('save_container');

            messageArea.textContent = '';
            output.textContent = '';
            saveContainer.classList.add('hidden');
            currentReport = null;

            if (!inputId) {
                messageArea.textContent = 'Eroare: Te rog introdu un STEAM ID sau numele profilului.';
                return;
            }

            loader.style.display = 'inline-block';

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input_id: inputId })
                });

                const data = await response.json();

                if (data.error) {
                    messageArea.textContent = 'Eroare' + data.error;
                } else {
                    output.textContent = data.report_content;
                    messageArea.textContent = 'Raport generat cu succes.';

                    // Salvarea raportului generat
                    currentReport = data;
                    saveContainer.classList.remove('hidden');
                }

            } catch (e) {
                messageArea.textContent = 'Eroare de conectare sau eroare interna: ' + e.message;
            } finally {
                loader.style.display = 'none';
            }
        }

        async function saveCurrentReport() {
            const messageArea = document.getElementById('message_area');
            if (!currentReport) {
                messageArea.textContent = 'Raport inexistent.';
                return;
            }

            try {
                const response = await fetch('/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentReport)
                });

                const data = await response.json();

                if (data.success) {
                    messageArea.textContent = 'Raport salvat cu succes!';
                    currentReport = null;
                    document.getElementById('save_container').classList.add('hidden');
                    // Reincarcarea istoricului dupa salvarea in baza de date
                    loadHistory(); 
                } else {
                    messageArea.textContent = 'Eroare la salvarea raportului: ' + data.error;
                }
            } catch (e) {
                 messageArea.textContent = 'Eroare la salvarea în baza de date: ' + e.message;
            }
        }

        // Functie pentru incarcarea continutului unui raport din istoric
        async function loadReport(reportId) {
            const output = document.getElementById('report_output');
            const messageArea = document.getElementById('message_area');
            const saveContainer = document.getElementById('save_container');

            saveContainer.classList.add('hidden');
            currentReport = null;

            try {
                const response = await fetch('/report/' + reportId);
                const data = await response.json();

                if (data.error) {
                    messageArea.textContent = 'Eroare la preluarea raportului: ' + data.error;
                    output.textContent = '';
                } else {
                    output.textContent = data.report_content;
                    messageArea.textContent = 'Se preia raportul din istoric. ';
                }
            } catch (e) {
                messageArea.textContent = 'Eroare la preluarea raportului.';
            }
        }

        // Functie pentru reincercarea preluarii raportului din istoric
        function loadHistory() {
            window.location.reload(); 
        }

    </script>
    {% endraw %}
</body>
</html>
"""
    return render_template_string(html_template, history=history)


# Analizam profilul de Steam

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    input_id = data.get('input_id')

    if not input_id:
        return jsonify({"error": "ID-ul profilului este obligatoriu."}), 400

    # Preia functionalitatea din clasa construita in Analiza_Profil_Steam
    result = analyzer.generare_raport(input_id)

    if isinstance(result, dict) and result.get('error'):
        # Returneaza erorile generate
        return jsonify({"error": result['error']}), 500

    return jsonify(result)


# Salvarea raportului

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()

    steam_id = data.get('steam_id')
    profile_name = data.get('profile_name')
    report_content = data.get('report_content')

    if not all([steam_id, profile_name, report_content]):
        return jsonify({"error": "Datele raportului sunt incomplete si nu pot fi salvate."}), 400

    try:
        save_report(steam_id, profile_name, report_content)
        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Eroare la salvarea in baza de date: {e}")
        return jsonify({"success": False, "error": "Eroare interna la salvarea in baza de date."}), 500


# Pentru a prelua un raport specific

@app.route('/report/<int:report_id>', methods=['GET'])
def get_report(report_id):
    report_content = get_report_by_id(report_id)

    if report_content:
        return jsonify({"report_content": report_content}), 200
    else:
        return jsonify({"error": "Nu am putut gasi raportul dorit."}), 404


if __name__ == '__main__':
    app.run(debug=True)
