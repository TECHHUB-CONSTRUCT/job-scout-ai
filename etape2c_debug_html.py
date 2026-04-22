# =============================================================================
# ÉTAPE 2C : SCRIPT DE DEBUG - Que voit vraiment notre robot ?
# =============================================================================

import requests
from urllib.request import getproxies
import urllib3

# --- CONFIGURATION ---
MOT_CLE_TEST = "IT"
URL_TEST = f"https://www.emploi.cm/recherche-jobs-cameroun/{MOT_CLE_TEST}"
OUTPUT_HTML_FILE = "debug_output.html"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"

# --- EXÉCUTION DU TEST ---

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("\n" + "=" * 60)
    print("🕵️‍♂️ LANCEMENT DU SCRIPT DE DIAGNOSTIC HTML")
    print("=" * 60)

    proxies = getproxies()
    if proxies:
        print(f"🌍 Proxy détecté : {proxies}")
        if 'http' in proxies and 'https' not in proxies:
             proxies['https'] = proxies['http']
    else:
        print("🌍 Aucun proxy détecté.")

    print(f"🌐 Tentative de téléchargement de : {URL_TEST}")
    headers = {'User-Agent': USER_AGENT}

    try:
        response = requests.get(URL_TEST, headers=headers, proxies=proxies, timeout=30, verify=False)
        print(f"   ✅ Réponse reçue avec le code : {response.status_code}")

        # Sauvegarde du contenu HTML dans un fichier
        with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"\n💾 Fichier de débogage sauvegardé : {OUTPUT_HTML_FILE}")
        print("\n" + "=" * 60)
        print("ACTION REQUISE :")
        print(f"1. Allez dans votre dossier 'C:\\Recherche_Emploi'.")
        print(f"2. Ouvrez le fichier '{OUTPUT_HTML_FILE}' avec votre navigateur (Chrome, Firefox...).")
        print("3. Dites-moi ce que vous voyez sur la page.")
        print("=" * 60)

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur de requête HTTP : {e}")