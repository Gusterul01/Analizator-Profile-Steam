import requests
from datetime import datetime
import json
import time


class AnalizareStatisticiSteam: #Creeam clasa pentru preluarea datelor folosing API-ul de la STEAM

    def __init__(self, api_key: str):
        self.base_url = "https://api.steampowered.com/"
        self.cheie_api = api_key

    def apel_api(self, interfata: str, metoda: str, versiune: str, parametri: dict): # Apelam API-ul de la STEAM
        url = f"{self.base_url}{interfata}/{metoda}/{versiune}/"

        # Adaugam cheia API si formatul JSON
        parametri['key'] = self.cheie_api
        parametri['format'] = 'json'

        try:
            # Implementam incercarea de apelare a API-ului
            max_reincercari = 3
            for i in range(max_reincercari):
                # Timeout pentru a ne asigura ca programul nu se blocheaza
                raspuns = requests.get(url, params=parametri, timeout=15)

                if raspuns.status_code == 200:
                    return raspuns.json()

                # Lista de erori comune la preluare
                if raspuns.status_code == 400:  # Bad Request
                    return {f"Eroare 400: Cerere invalida."}
                if raspuns.status_code == 401:  # Unauthorized
                    return {f"Eroare 401: Cheie API invalida sau gresita."}
                if raspuns.status_code == 403:  # Forbidden (profil privat)
                    return {f"Eroare 403: Acces interzis. Profilul Steam trebuie sa fie setat Public."}
                if raspuns.status_code == 429:  # Rate Limit
                    time.sleep(2 ** i)  # Pentru a relua procesul dupa cateva secunde
                    continue

                # Eroare generala
                raspuns.raise_for_status()
                return None

        except requests.exceptions.Timeout:
            return{"error": "Eroare la preluarea datelor. STEAM nu a raspuns la timp."}
        except requests.exceptions.ConnectionError:
            return {"Eroare la conectare: Nu se poate face conexiunea cu STEAM API."}
        except requests.exceptions.RequestException as e:
            return {f"Eroare la preluarea datelor de la API: {e}"}


    def preia_steam_id(self, input_id: str):
        """
        Pentru a putea face conversia unui nume de profil in STEAM ID (76561198xxxxxxxxx) daca acesta nu a introdus
        un STEAM ID.
        """
        if input_id.isdigit() and len(input_id) == 17:
            return input_id

        parametri = {'vanityurl': input_id}
        data = self.apel_api("ISteamUser", "ResolveVanityURL", "v0001", parametri)

        if isinstance(data, dict) and data.get('error'):
            return data # Returneaza eroarea de la API

        if data and data.get('response', {}).get('success') == 1:
            steam_id = data['response']['steamid']
            return steam_id

        return None

    def preluare_date_generale(self, steam_id: str):
        """
        Preia toate datele de pe profilul de STEAM al jucatorului (Jocuri, timp in jocuri, achievement, sumarul etc.

        """

        # Obtinem sumarul jucatorului de pe profil
        parametri_sumar = {'steamids': steam_id}
        sumar_data = self.apel_api("ISteamUser", "GetPlayerSummaries", "v0002", parametri_sumar)

        player_info = {}
        if sumar_data and sumar_data.get('response', {}).get('players'):
            player_info = sumar_data['response']['players'][0]
        else:
            return {"error": "Nu am putut obtine informatiile despre sumarul jucatorului."}

        # Obtinem numarul de jocuri si date despre acestea
        parametri_jocuri = {
            'steamid': steam_id,
            'include_appinfo': 1,  # Preluam numele jocurilor
            'include_played_free_games': 1  # Pentru a include si jocurile gratis
        }
        jocuri_data = self.apel_api("IPlayerService", "GetOwnedGames", "v0001", parametri_jocuri)

        if isinstance(jocuri_data, dict) and jocuri_data.get('error'):
            return jocuri_data #Returneaza eroarea de la API

        jocuri_detinute = []
        if jocuri_data and jocuri_data.get('response', {}).get('games'):
            jocuri_detinute = jocuri_data['response']['games']

            # Pentru cazurile in care profilul este public, dar informatiile despre jocuri sunt private
            if not player_info.get('communityvisibilitystate') == 3 and not jocuri_detinute:
                return {"error": "Profilul de STEAM este public, dar detaliile despre jocuri sunt private."}
        elif jocuri_data and 'response' in jocuri_data and 'game_count' in jocuri_data['response'] and \
                jocuri_data['response']['game_count'] == 0:
            # In cazul in care profilul nu are niciun joc (improbabil)
            pass

        return {
            'player_info': player_info,
            'owned_games': jocuri_detinute
        }

    def extragere_statistici_esentiale(self, data: dict):
        """
        Pentru a extrage statisticile esentiale ale profilului
        """
        if not data or not data.get('player_info'):
            return {}

        player = data['player_info']
        jocuri = data.get('owned_games', [])

        # Preluam informatiile de baza
        profil_status = "Public" if player.get('communityvisibilitystate') == 3 else "Privat/Prieteni"
        nume_profil = player.get('personaname', 'N/A')
        data_creare = datetime.fromtimestamp(player.get('timecreated', 0)).strftime('%Y-%m-%d') if player.get(
            'timecreated') else 'N/A'

        # Statisticile pentru jocuri
        total_jocuri = len(jocuri)

        # Timpul in minute care trebuie convertit in ore
        total_ore_minute = sum(j.get('playtime_forever', 0) for j in jocuri)
        total_ore = total_ore_minute / 60

        def preia_timp_joc(joc):
            """Pentru a returna timpul petrecut in joc in minute, ajutandu-ne la sortare"""
            return joc.get('playtime_forever', 0)

        jocuri_sortate = sorted(jocuri, key=preia_timp_joc, reverse=True)
        top_jocuri = [{'nume': j.get('name', 'N/A'), 'ore': j.get('playtime_forever', 0) / 60} for j in
                      jocuri_sortate[:3]]

        # Jocurile jucate in ultimele 2 saptamani
        jocuri_recente = [
            {'nume': j.get('name', 'N/A'), 'minute': j.get('playtime_2weeks', 0)}
            for j in jocuri if j.get('playtime_2weeks', 0) > 0
        ]

        statistici = {
            'nume_profil': nume_profil,
            'profil_status': profil_status,
            'data_creare': data_creare,
            'total_jocuri': total_jocuri,
            'total_ore': total_ore,
            'top_jocuri': top_jocuri,
            'jocuri_recente': jocuri_recente
        }

        return statistici

    def analiza_statistici(self, stats: dict):
        """
        Face o analiza despre modul de joc si tipul de jucator dupa statisticile jocurilor jucate si timpul de joc
        petrecute in fiecare titlu
        """
        analiza = {
            'tip_jucator': 'N/A',
            'observatii': [],
        }

        total_ore = stats.get('total_ore', 0)
        total_jocuri = stats.get('total_jocuri', 0)
        jocuri_recente = stats.get('jocuri_recente', [])

        # Tipul de jucator
        if total_ore > 5000:
            analiza['tip_jucator'] = "Jucator Inrait"
        elif total_ore > 1000:
            analiza['tip_jucator'] = "Jucator Experimentat"
        elif total_ore > 200:
            analiza['tip_jucator'] = "Jucator Casual"
        else:
            analiza['tip_jucator'] = "Jucator de 'duminica' "
            analiza['observatii'].append("Contul pare a fi foarte nou sau neutilizat.")

        # Diversitatea de jocuri si timpul petrecut in medie
        if total_jocuri > 0:
            ore_medii_pe_joc = total_ore / total_jocuri
            if ore_medii_pe_joc < 10:
                analiza['observatii'].append(
                    f"Diversitate ridicata: Timpul mediu petrecut in jocuri este de {ore_medii_pe_joc:.1f} ore."
                    f"Te joci o gama variata de jocuri!")
            elif ore_medii_pe_joc > 50:
                analiza['observatii'].append(
                    f"Iti place sa te concentrezi anumitor titluri: {ore_medii_pe_joc:.1f} ore jucate in medie per joc."
                    f"Te dedici jocurilor favorite!")

        # Activitatea recenta in jocuri
        if len(jocuri_recente) >= 3:
            analiza['observatii'].append(
                f"Ai jucat {len(jocuri_recente)} titluri diferite in ultimele 2 saptamani.")
        elif len(jocuri_recente) == 1:
            analiza['observatii'].append(
                f"Esti concentrat pe anumite jocuri {jocuri_recente[0]['nume']} (doar in ultimele 2 saptamani).")
        elif len(jocuri_recente) == 0 and total_ore > 50:
            analiza['observatii'].append("Ai luat o pauza. Niciun joc jucat in ultimele 2 saptamani.")

        return analiza

    def generare_raport(self, input_id: str):
        """Pentru a genera raportul general al activitatii profilului."""

        # Preluam ID-ul steam
        steam_id_result = self.preia_steam_id(input_id)

        if isinstance(steam_id_result, dict) and steam_id_result.get('error'):
            return steam_id_result

        if not steam_id_result:
            return {"error": " Raportul nu a putut fi realizat. Verifica ID-ul introdus."}

        steam_id = steam_id_result

        # Preluam datele
        data_result = self.preluare_date_generale(steam_id)

        if isinstance(data_result, dict) and data_result.get('error'):
            return data_result #Eroare API sau detalii private despre profil

        if not data_result:
            return {"error": " Datele nu au putut fi preluate. Verifica profilul de STEAM"}

        # Extragem datele preluate
        stats = self.extragere_statistici_esentiale(data_result)
        if not stats or stats.get('total_jocuri', 0) == 0:
            nume_profil = stats.get('nume_profil', 'N/A')
            return {"error": " Raport incomplet: {nume_profil} nu detine jocuri sau are profilul privat."}

        analizare = self.analiza_statistici(stats)

        # Crearea raportului propriu-zis
        raport = []
        raport.append("\n" + "=" * 50)
        raport.append(f" RAPORT STATISTICI STEAM: {stats['nume_profil']}")
        raport.append("=" * 50)
        raport.append(f"  Steam ID: {steam_id}")
        raport.append(f"  Status Profil: {stats['profil_status']}")
        raport.append(f"  Cont creat pe data de: {stats['data_creare']}")
        raport.append(f"  Data Raport: {datetime.now().strftime('%Y.%m.%d %H:%M:%S')}")
        raport.append("")

        # Statistici generale despre biblioteca de jocuri detinuta
        raport.append("STATISTICI BIBLIOTECA DE JOCURI")
        raport.append("-" * 50)
        raport.append(f"  Total Jocuri Detinute: {stats['total_jocuri']}")
        raport.append(f"  Total Ore Jucate: {stats['total_ore']:.1f} ore")
        ore_zile = stats['total_ore'] / 24
        raport.append(f"  (Adica, echivalentul a {ore_zile:.1f} de zile jucate in continuu)")
        raport.append("")

        # Topul jocurilor jucate
        raport.append("TOP 3 CELE MAI JUCATE JOCURI (IN ORE)")
        raport.append("-" * 50)
        if stats['top_jocuri']:
            for i, joc in enumerate(stats['top_jocuri'], 1):
                raport.append(f"  {i}. {joc['nume']}: {joc['ore']:.1f} ore")
        else:
            raport.append("Nu exista date disponibile.")
        raport.append("")

        # Activitatea recenta a contului
        raport.append("ACTIVITATE RECENTA ( 2 SAPTAMANI)")
        raport.append("-" * 50)
        if stats['jocuri_recente']:
            for joc in stats['jocuri_recente']:
                ore_recente = joc['minute'] / 60
                raport.append(f"  • {joc['nume']}: {ore_recente:.1f} ore")
        else:
            raport.append("Nu au fost gasite date despre niciun joc jucat in ultimele 2 saptamani")
        raport.append("")

        # Analiza stilului de joc (casual, veteran, etc.)
        raport.append("ANALIZĂ STIL DE JOC")
        raport.append("-" * 60)
        raport.append(f"  Tip de jucator: {analizare['tip_jucator']}")
        raport.append("")

        if analizare['observatii']:
            raport.append("  Observatii:")
            for obs in analizare['observatii']:
                raport.append(f"     • {obs}")
        raport.append("")

        return {
            "report_content": "\n".join(raport),
            "steam_id": steam_id,
            "profile_name": stats["nume_profil"]
        }