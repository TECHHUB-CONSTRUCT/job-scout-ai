# =============================================================================
# ÉTAPE 2B : SCRAPING DÉDIÉ AUX SITES CAMEROUNAIS (v6 - SÉLECTEURS CORRIGÉS)
# Agent de Recherche d'Emploi - Edmond FOMBEN
# Cible : Emploi.cm
# =============================================================================

import json
import requests
from urllib.request import getproxies
from urllib.parse import quote
from bs4 import BeautifulSoup
import time
import random
import os
import urllib3

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
OUTPUT_FILENAME_CAMEROUN = "offres_cameroun.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
BASE_URL = "https://www.emploi.cm"

# =============================================================================
# FONCTIONS DE SCRAPING POUR EMPLOI.CM
# =============================================================================

def charger_profil(filename):
    if not os.path.exists(filename):
        print(f"❌ ERREUR : Fichier de profil '{filename}' introuvable.")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        profil = json.load(f)
        return profil.get("mots_cles_recherche", [])

def scraper_site_emploi_cm(mots_cles):
    toutes_les_offres = []
    offres_ids_vus = set()
    proxies = getproxies()
    
    if proxies:
        print("🌍 Détection d'une configuration proxy système. Utilisation du proxy.")
        if 'http' in proxies and 'https' not in proxies:
             proxies['https'] = proxies['http']
    else:
        print("🌍 Aucune configuration proxy système détectée.")

    for mot_cle in mots_cles:
        encoded_mot_cle = quote(mot_cle)
        url = f"{BASE_URL}/recherche-jobs-cameroun/{encoded_mot_cle}"
        
        print(f"\n--- Recherche pour '{mot_cle}' sur Emploi.cm ---")
        print(f"🌐 Scraping de l'URL : {url}")

        headers = {'User-Agent': USER_AGENT}
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30, verify=False)
            print(f"   État de la réponse : {response.status_code}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erreur de requête HTTP : {e}")
            time.sleep(random.uniform(2, 4))
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ===============================================================
        # CHANGEMENT 1 : On utilise le bon sélecteur pour les cartes d'offres
        # ===============================================================
        job_cards = soup.find_all('div', class_='job-item')
        # ===============================================================

        if not job_cards:
            print("   ⚠️ Aucune offre trouvée pour ce mot-clé.")
            continue
        
        print(f"   ✅ Trouvé {len(job_cards)} offres pour '{mot_cle}'.")

        for card in job_cards:
            # ===============================================================
            # CHANGEMENT 2 : On utilise les bons sélecteurs pour le titre et le lien
            # ===============================================================
            titre_tag = card.find('div', class_='job-item-title')
            lien_tag = titre_tag.find('a') if titre_tag else None
            titre_h3 = titre_tag.find('h3') if titre_tag else None
            
            if not lien_tag or not titre_h3: continue

            titre = titre_h3.text.strip()
            lien_relatif = lien_tag['href']
            lien_absolu = f"{BASE_URL}{lien_relatif}"
            offre_id = lien_absolu

            if offre_id in offres_ids_vus: continue
            
            # ===============================================================
            # CHANGEMENT 3 : On utilise les bons sélecteurs pour l'entreprise et le lieu
            # ===============================================================
            entreprise_tag = card.find('div', class_='job-item-company')
            entreprise = entreprise_tag.text.strip() if entreprise_tag else "N/A"
            
            lieu_tag = card.find('div', class_='job-item-location')
            lieu = lieu_tag.text.strip() if lieu_tag else "N/A"
            # ===============================================================

            offre = {
                'id': offre_id, 'titre': titre, 'entreprise': entreprise,
                'lieu_annonce': lieu, 'source': 'Emploi.cm', 'lien': lien_absolu,
                'recherche_mot_cle': mot_cle, 'recherche_lieu': 'Cameroun'
            }
            toutes_les_offres.append(offre)
            offres_ids_vus.add(offre_id)

        time.sleep(random.uniform(1, 3))
    
    return toutes_les_offres

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 2B (v6 - CORRIGÉE)")
    print("   Scraping des offres sur Emploi.cm (Cameroun)")
    print("=" * 60)

    mots_cles = charger_profil(PROFIL_FILENAME)
    if mots_cles:
        offres_cameroun = scraper_site_emploi_cm(mots_cles)
        if offres_cameroun:
            with open(OUTPUT_FILENAME_CAMEROUN, 'w', encoding='utf-8') as f:
                json.dump(offres_cameroun, f, ensure_ascii=False, indent=4)
            print(f"\n💾 {len(offres_cameroun)} offres uniques du Cameroun sauvegardées dans : {OUTPUT_FILENAME_CAMEROUN}")
        else:
            print("\n🤷 Aucune offre trouvée sur Emploi.cm lors de cette recherche.")
        
        print("\n✅ Étape 2B terminée avec succès !")
    else:
        print("\n❌ Arrêt du script.")