# =============================================================================
# ÉTAPE 2 : SCRAPING DES OFFRES D'EMPLOI (VERSION CORRIGÉE)
# Agent de Recherche d'Emploi - Edmond FOMBEN
# =============================================================================

import json
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlencode

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
OUTPUT_FILENAME = "offres_brutes.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

# =============================================================================
# SECTION 1 : CONFIGURATION DE LA RECHERCHE
# =============================================================================

def charger_profil(filename):
    """Charge les données du profil candidat depuis un fichier JSON."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            print(f"📄 Lecture du profil depuis : {filename}")
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERREUR : Le fichier de profil '{filename}' est introuvable.")
        print("   Veuillez d'abord lancer le script 'etape1_lecture_cv.py'.")
        return None
    except json.JSONDecodeError:
        print(f"❌ ERREUR : Le fichier JSON '{filename}' est malformé.")
        return None

def definir_cibles():
    """
    Définit les cibles de recherche.
    Chaque cible est un dictionnaire avec un lieu et un domaine Indeed valide.
    """
    print("🎯 Définition des cibles de recherche...")
    cibles = [
        {'lieu_recherche': 'France', 'domaine': 'fr'},
        {'lieu_recherche': 'Canada', 'domaine': 'ca'},
        {'lieu_recherche': 'Belgique', 'domaine': 'be'},
        {'lieu_recherche': 'Suisse', 'domaine': 'ch'},
        # CORRECTION : Pour le Cameroun, on cherche sur le domaine français.
        {'lieu_recherche': 'Cameroun', 'domaine': 'fr'},
        # On ajoute le télétravail comme une cible à part entière.
        {'lieu_recherche': 'remote', 'domaine': 'fr', 'label': 'Télétravail'},
    ]
    return cibles

# =============================================================================
# SECTION 2 : FONCTIONS DE SCRAPING POUR INDEED
# =============================================================================

def construire_url_indeed(mot_cle, lieu, domaine_pays, page=0):
    """Construit une URL de recherche pour Indeed."""
    params = {'q': mot_cle, 'l': lieu, 'start': page * 10}
    return f"https://{domaine_pays}.indeed.com/jobs?" + urlencode(params)

def scraper_page_indeed(url):
    """Effectue une requête sur une URL Indeed et parse le HTML."""
    print(f"🌐 Scraping de l'URL : {url}")
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur de requête HTTP : {e}")
        return None

def extraire_offres_de_la_page(soup, mot_cle_recherche, lieu_recherche):
    """Extrait les informations des offres d'une page HTML Indeed."""
    offres = []
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    
    if not job_cards:
        print("   ⚠️ Aucune carte d'offre trouvée. La structure du site a peut-être changé ou il n'y a pas de résultat.")
        return []

    for card in job_cards:
        titre_tag = card.find('h2', class_='jobTitle')
        # On prend le lien du titre car il est plus fiable
        lien_tag = titre_tag.find('a') if titre_tag else None
        if not lien_tag:
            continue # Si pas de lien, on ignore cette carte

        titre = lien_tag.text.strip()
        lien_relatif = lien_tag['href']
        lien_absolu = f"https://fr.indeed.com{lien_relatif}" # On construit le lien absolu
        
        entreprise_tag = card.find('span', class_='companyName')
        entreprise = entreprise_tag.text.strip() if entreprise_tag else "N/A"

        lieu_tag = card.find('div', class_='companyLocation')
        lieu = lieu_tag.text.strip() if lieu_tag else "N/A"
        
        # Le lien unique est notre ID
        offre_id = lien_absolu.split('?')[0] # On nettoie l'URL pour avoir un ID plus stable

        offre = {
            'id': offre_id,
            'titre': titre,
            'entreprise': entreprise,
            'lieu_annonce': lieu,
            'source': 'Indeed',
            'lien': lien_absolu,
            'recherche_mot_cle': mot_cle_recherche,
            'recherche_lieu': lieu_recherche
        }
        offres.append(offre)
    
    print(f"   ✅ Trouvé {len(offres)} offres sur cette page.")
    return offres

# =============================================================================
# SECTION 3 : ORCHESTRATION DU SCRAPING
# =============================================================================

def lancer_recherche(profil):
    """Orchestre le processus de recherche sur les différentes cibles."""
    mots_cles_recherche = profil.get("mots_cles_recherche", [])
    if not mots_cles_recherche:
        print("❌ Aucun mot-clé de recherche trouvé dans le profil. Arrêt.")
        return []

    cibles = definir_cibles()
    toutes_les_offres = []
    offres_ids_vus = set()

    for cible in cibles:
        lieu_a_chercher = cible['lieu_recherche']
        domaine_a_utiliser = cible['domaine']
        # Le 'label' est ce qu'on affiche, par ex "Télétravail"
        label_recherche = cible.get('label', lieu_a_chercher) 

        for mot_cle in mots_cles_recherche:
            print(f"\n--- Recherche pour '{mot_cle}' en '{label_recherche}' ---")
            
            # Nous ne scrapans que la première page pour l'instant
            url = construire_url_indeed(mot_cle, lieu_a_chercher, domaine_a_utiliser)
            soup = scraper_page_indeed(url)
            
            if soup:
                offres_page = extraire_offres_de_la_page(soup, mot_cle, label_recherche)
                for offre in offres_page:
                    if offre['id'] not in offres_ids_vus:
                        toutes_les_offres.append(offre)
                        offres_ids_vus.add(offre['id'])
            
            # Pause polie et aléatoire pour ne pas surcharger le serveur
            time.sleep(random.uniform(2, 5))
    
    return toutes_les_offres


# =============================================================================
# SECTION 4 : SAUVEGARDE DES RÉSULTATS
# =============================================================================

def sauvegarder_offres(offres, filename):
    """Sauvegarde la liste des offres dans un fichier JSON."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(offres, f, ensure_ascii=False, indent=4)
        print(f"\n💾 {len(offres)} offres uniques sauvegardées dans : {filename}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du fichier JSON : {e}")

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 2 (v2)")
    print("   Scraping des offres sur Indeed")
    print("=" * 60)

    profil_candidat = charger_profil(PROFIL_FILENAME)

    if profil_candidat:
        offres_trouvees = lancer_recherche(profil_candidat)

        if offres_trouvees:
            sauvegarder_offres(offres_trouvees, OUTPUT_FILENAME)
        else:
            print("\n🤷 Aucune offre trouvée lors de cette recherche. Cela peut être normal.")
        
        print("\n✅ Étape 2 terminée !")
        print("👉 Prochaine étape : Analyse et matching des offres (etape3_analyse.py)")
    else:
        print("\n❌ Arrêt du script.")