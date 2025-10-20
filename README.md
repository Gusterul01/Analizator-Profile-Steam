# Analizator Pentru Profile Steam

Aplicația **Analizator Pentru Profile Steam** este un proiect complet dezvoltat în **Python**, folosind micro-framework-ul **Flask** și baza de date **SQLite3**.  
Aceasta este destinată **extragerii, analizării și stocării** datelor publice despre profiluri și statistici de joc de pe **Steam Web API**.

---

## Funcționalități Principale

**Preluare date Steam API** — conectare la platforma Steam și extragerea datelor de profil, a jocurilor și a timpului jucat.  
**Conversie automată Vanity URL → Steam ID** — permite introducerea unui nume personalizat în locul ID-ului numeric.  
**Analiză automată a statisticilor** — determinarea tipului de jucător și generarea de observații bazate pe activitatea contului.  
**Generare raport detaliat** — construirea unui raport text complet, cu topul jocurilor și activitatea recentă.  
**Salvare date în SQLite3** — păstrarea istoricului rapoartelor și a profilurilor analizate.  
**Interfață web (Flask)** — permite rularea aplicației din browser, cu rezultate afișate într-un mod prietenos și modern.  

---

## Tehnologii și Librării Utilizate

Aplicația este dezvoltată exclusiv în **Python**, folosind următoarele librării și module:

| Categoria | Pachet / Modul | Descriere |
|------------|----------------|-----------|
| **Framework Web** | `Flask` | Gestionează interfața web, rutele și șabloanele HTML |
| **Bază de date** | `sqlite3` | Păstrează istoricul analizelor și rapoartelor |
| **Apeluri HTTP** | `requests` | Comunicare cu Steam Web API |
| **Date și timp** | `datetime`, `time` | Conversii și formatare a datelor de creare/profil |
| **Prelucrare date** | `json` | Lucru cu structuri de date JSON de la API |
| **Logică aplicație** | Clasa `AnalizareStatisticiSteam` | Implementarea principală pentru preluare și analiză date |
| **Extensibilitate** | `Flask + SQLite` | Posibilitate de a salva și vizualiza rapoarte printr-o interfață web |

---

## Structura Proiectului

```bash
Analiza_Profilului_Steam/
├── Analiza_Profil_Steam.py    # Clasa de logică și interacțiune cu Steam API
├── baza_date.py         # Funcțiile pentru operarea bazei de date (SQLite3)
├── app.py               # Aplicația principală Flask și interfața web (HTML/CSS)
├── Baza_Date_Steam.db   # Baza de date locală (creată automat la prima rulare)
└── README.md            # Acest fișier
```

## Instalare si Rulare Locala

1. **Clonarea Proiectului**

   ```bash
   git clone https://github.com/<numele-tău-utilizator>/analizator-profile-steam.git
   cd analizator-profile-steam
   ```

2. **Creeaza si gestioneaza un mediu virtual**

   ```bash
   python -m venv venv
   source venv/bin/activate     # Linux / Mac
   venv\Scripts\activate        # Windows
   ```

3. **Instaleaza librariile auxiliare**
   ```bash
   pip install flask requests
   ```

4. **Configureaza cheia API de la Steam**

   Obține o cheie de la https://steamcommunity.com/dev/apikey

   În fișierul app.py, înlocuiește valoarea pentru STEAM_API_KEY cu cheia ta reală obținută de pe site-ul Steam API.

6. **Porneste aplicatia**
   ```bash
   python app.py
   ```
7. **Acceseaza in Browser**
   ```bash
   http://127.0.0.1:5000
   
