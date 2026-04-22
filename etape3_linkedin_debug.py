# =============================================================================
# ÉTAPE 3 (DEBUG) : RENDRE LE ROBOT LINKEDIN "BAVARD"
# =============================================================================

import json
import time
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
CONFIG_FILENAME = "config.json"
OUTPUT_FILENAME = "offres_linkedin_debug.json" # Fichier de sortie différent
HEADLESS = False

# =============================================================================
# FONCTIONS
# =============================================================================

def charger_json(filename):
    if not os.path.exists(filename):
        print(f"❌ ERREUR : Fichier '{filename}' introuvable.")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def scraper_linkedin(profil, config):
    # === SIMPLIFICATION POUR LE DEBUG : 1 mot-clé, 1 lieu ===
    mots_cles = ["IT Support"]
    lieux_recherche = ["France"]
    
    toutes_les_offres = []
    offres_ids_vus = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=100)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        page = context.new_page()

        print("🤖 Navigateur lancé pour LinkedIn.")
        try:
            print("🔗 Connexion à LinkedIn...")
            page.goto("https://www.linkedin.com/login", timeout=60000)
            page.fill('input#username', config['linkedin_email'])
            page.fill('input#password', config['linkedin_password'])
            page.click('button[type="submit"]')
            page.wait_for_selector("a[href*='/feed/']", timeout=60000)
            print("   ✅ Connexion réussie !")
        except Exception as e:
            print(f"   ❌ Échec de la connexion : {e}")
            browser.close()
            return []

        for lieu in lieux_recherche:
            for mot_cle in mots_cles:
                url = f"https://www.linkedin.com/jobs/search/?keywords={quote(mot_cle)}&location={quote(lieu)}"
                print(f"\n--- Recherche pour '{mot_cle}' en '{lieu}' ---")
                
                try:
                    page.goto(url, timeout=60000, wait_until='domcontentloaded')
                    print("   ⏳ Attente de l'affichage des offres...")
                    page.wait_for_selector('.job-card-container', timeout=15000)
                    print("   ✅ Page de résultats chargée.")

                    job_cards = page.locator('.job-card-container').all()
                    print(f"   📊 Trouvé {len(job_cards)} cartes d'offres potentielles.")
                    print("-" * 40)

                    for i, card in enumerate(job_cards):
                        print(f"   🔎 Analyse de la carte n°{i+1}...")
                        try:
                            titre_loc = card.locator('.job-card-list__title')
                            titre = titre_loc.inner_text().strip() if titre_loc.count() > 0 else "VIDE"
                            print(f"      - Titre trouvé : '{titre}'")

                            entreprise_loc = card.locator('.job-card-container__company-name')
                            entreprise = entreprise_loc.inner_text().strip() if entreprise_loc.count() > 0 else "VIDE"
                            print(f"      - Entreprise trouvée : '{entreprise}'")

                            lieu_loc = card.locator('.job-card-container__metadata-item').first
                            lieu_annonce = lieu_loc.inner_text().strip() if lieu_loc.count() > 0 else "VIDE"
                            print(f"      - Lieu trouvé : '{lieu_annonce}'")

                            lien_loc = titre_loc
                            lien = lien_loc.get_attribute('href') if lien_loc.count() > 0 else "VIDE"
                            print(f"      - Lien trouvé : '{lien}'")

                            if lien != "VIDE":
                                lien_propre = f"https://www.linkedin.com{lien.split('?')[0]}"
                                offre_id = lien_propre
                                print(f"      - ID de l'offre : '{offre_id}'")
                            else:
                                offre_id = "VIDE"
                            
                            if offre_id != "VIDE" and offre_id not in offres_ids_vus:
                                print(f"      ==> ✅ Offre valide, ajoutée à la liste !")
                                offre = {'id': offre_id, 'titre': titre, 'entreprise': entreprise, 'lieu_annonce': lieu_annonce, 'lien': offre_id}
                                toutes_les_offres.append(offre)
                                offres_ids_vus.add(offre_id)
                            else:
                                print(f"      ==> ❌ Offre ignorée (ID vide ou déjà vue).")
                            
                            print("-" * 20)

                        except Exception as inner_e:
                            print(f"      *** ERREUR sur cette carte : {inner_e} ***")
                            continue

                except PlaywrightTimeoutError:
                    print(f"   ⚠️ Pas d'offres trouvées.")

        # === DIAGNOSTIC FINAL ===
        print("\n" + "="*50)
        print("DIAGNOSTIC FINAL DE LA RECHERCHE")
        print(f"Nombre total d'offres collectées : {len(toutes_les_offres)}")
        if not toutes_les_offres:
            print("Raison pour laquelle le fichier n'est pas créé : La liste d'offres est VIDE.")
        print("="*50 + "\n")
        
        browser.close()
        print("\n🛑 Navigateur fermé.")
    return toutes_les_offres

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 3 (MODE DEBUG)")
    print("=" * 60)

    profil = charger_json(PROFIL_FILENAME)
    config = charger_json(CONFIG_FILENAME)

    if profil and config:
        offres = scraper_linkedin(profil, config)
        if offres:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(offres, f, ensure_ascii=False, indent=4)
            print(f"\n💾 {len(offres)} offres de LinkedIn sauvegardées dans : {OUTPUT_FILENAME}")
        else:
            print("\n🤷 Aucune offre n'a pu être extraite et sauvegardée.")
        print("\n✅ Script de debug terminé !")