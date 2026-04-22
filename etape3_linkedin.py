# =============================================================================
# ÉTAPE 3 : SCRAPING DE LINKEDIN (v3 - SÉLECTEURS FINALS)
# =============================================================================

import json
import time
import random
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
CONFIG_FILENAME = "config.json"
OUTPUT_FILENAME = "offres_linkedin.json"
# Remettez HEADLESS à True une fois que vous êtes sûr que tout fonctionne
HEADLESS = True 

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
    mots_cles = profil.get("mots_cles_recherche", [])
    lieux_recherche = ["France", "Canada", "Belgique", "Suisse", "Remote"]
    
    toutes_les_offres = []
    offres_ids_vus = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=50)
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
                    
                    # === SÉLECTEUR PRINCIPAL MIS À JOUR ===
                    # On attend la présence d'une carte par son ID qui commence par "job-card-list"
                    page.wait_for_selector('[id^="job-card-list"]', timeout=15000)
                    print("   ✅ Page de résultats chargée.")

                    # === NOUVEAU SÉLECTEUR POUR LES CARTES ===
                    job_cards = page.locator('div[class*="job-card-list"]').locator('div[class*="job-card-list__entity-lockup"]').all()
                    print(f"   📊 Trouvé {len(job_cards)} offres sur la page.")

                    for card in job_cards:
                        try:
                            # === NOUVEAUX SÉLECTEURS POUR LES DÉTAILS ===
                            titre_loc = card.locator('a[class*="job-card-list__title"]')
                            titre = titre_loc.inner_text().strip()
                            
                            entreprise_loc = card.locator('div[class*="job-card-container__company-name"]')
                            entreprise = entreprise_loc.inner_text().strip()
                            
                            lieu_loc = card.locator('ul[class*="job-card-container__metadata-wrapper"]').locator('li').first
                            lieu_annonce = lieu_loc.inner_text().strip()
                            
                            lien = titre_loc.get_attribute('href')
                            
                            if lien:
                                lien_propre = f"https://www.linkedin.com{lien.split('?')[0]}"
                                offre_id = lien_propre
                            else:
                                continue # Si pas de lien, on ignore
                            
                            if offre_id not in offres_ids_vus:
                                offre = {
                                    'id': offre_id, 'titre': titre, 'entreprise': entreprise,
                                    'lieu_annonce': lieu_annonce, 'source': 'LinkedIn', 'lien': offre_id,
                                    'recherche_mot_cle': mot_cle, 'recherche_lieu': lieu
                                }
                                toutes_les_offres.append(offre)
                                offres_ids_vus.add(offre_id)
                        except Exception:
                            continue

                except PlaywrightTimeoutError:
                    print(f"   ⚠️ Pas d'offres trouvées pour '{mot_cle}' en '{lieu}'.")
                except Exception as e:
                    print(f"   ❌ Erreur sur la recherche : {e}")

        browser.close()
        print("\n🛑 Navigateur fermé.")
    return toutes_les_offres

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 3 (LINKEDIN v3)")
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
        print("\n✅ Étape 3 terminée !")
    else:
        print("\n❌ Arrêt du script. Vérifiez les fichiers.")