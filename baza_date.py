import sqlite3
from datetime import datetime

DATABASE_NAME = 'Baza_Date_Steam.db'


def get_db_connection(): # Creeam conexiunea catre baza de date
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Permite accesarea coloanelor prin nume
    return conn


def init_db(): # Initializam Baza de date
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            steam_id TEXT NOT NULL,
            profile_name TEXT NOT NULL,
            report_content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()


def save_report(steam_id, profile_name, report_content): # Salvam raportul in baza de date
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO reports (steam_id, profile_name, report_content) VALUES (?, ?, ?)',
        (steam_id, profile_name, report_content)
    )
    conn.commit()
    conn.close()


def get_reports_history(): # Preia istoricul rapoartelor salvate in baza de date
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, steam_id, profile_name, timestamp FROM reports ORDER BY timestamp DESC'
    )
    reports = cursor.fetchall()
    conn.close()

    # Convertim in lista de dictionare
    return [dict(row) for row in reports]


def get_report_by_id(report_id): # Preluarea continutului unui raport dupa ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT report_content FROM reports WHERE id = ?',
        (report_id,)
    )
    report = cursor.fetchone()
    conn.close()

    if report:
        return report['report_content']
    return None


init_db()
