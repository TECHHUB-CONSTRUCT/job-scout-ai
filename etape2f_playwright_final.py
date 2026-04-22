# =============================================================================
# ÉTAPE 2F : PLAYWRIGHT - LA VERSION FINALE ET PATIENTE (CORRIGÉE)
# Agent de Recherche d'Emploi - Edmond FOMBEN
# =============================================================================

import json
import time
import random
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
OUTPUT_FILENAME = "offres_finales.json"
BASE_URL = "https://www.emploi.cm"
HEADLESS = True 

# =============================================================================
# FONCTIONS
# =============================================================================

def charger_profil(filename):
    if not os.path.exists(filename):
        print(f"❌ ERREUR : Fichier de profil '{filename}' introuvable.")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        profil = json.load(f)
        return profil.get("mots_cles_recherche", [])

def scraper_avec_playwright(mots_cles):
    toutes_les_offres = []
    offres_ids_vus = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=50)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        page = context.new_page()

        print("🤖 Navigateur patient lancé par Playwright.")

        for mot_cle in mots_cles:
            url = f"{BASE_URL}/recherche-jobs-cameroun/{mot_cle.replace(' ', '%20')}"
            print(f"\n--- Recherche pour '{mot_cle}' ---")
            print(f"🌐 Navigation vers: {url}")

            try:
                page.goto(url, timeout=60000, wait_until='domcontentloaded')
                
                # ===============================================================
                # LA CORRECTION CRUCIALE : LA PATIENCE
                # ===============================================================
                print("   ⏳ Attente patiente que la page se stabilise...")
                page.wait_for_timeout(3000) 

                print("   🔎 Recherche de la première offre à l'écran...")
                page.locator('div.job-item').first.wait_for(timeout=30000)
                # ===============================================================

                print("   ✅ Contenu de la page chargé et offres visibles.")

                job_cards = page.locator('div.job-item').all()
                print(f"   🎯 Trouvé {len(job_cards)} offres pour '{mot_cle}'.")

                for card in job_cards:
                    try:
                        titre_tag = card.locator('div.job-item-title a')
                        titre_h3 = card.locator('div.job-item-title h3')
                        
                        # Version simple et robuste sans await
                        titre = titre_h3.inner_text().strip() if titre_h3.count() > 0 else "N/A"
                        lien_relatif = titre_tag.get_attribute('href') if titre_tag.count() > 0 else "N/A"
                        lien_absolu = f"{BASE_URL}{lien_relatif}" if lien_relatif != "N/A" else "N/A"
                        offre_id = lien_absolu

                        if offre_id in offres_ids_vus or offre_id == "N/A":
                            continue
                        
                        entreprise_tag = card.locator('div.job-item-company')
                        entreprise = entreprise_tag.inner_text().strip() if entreprise_tag.count() > 0 else "N/A"
                        
                        lieu_tag = card.locator('div.job-item-location')
                        lieu = lieu_tag.inner_text().strip() if lieu_tag.count() > 0 else "N/A"
                        
                        offre = {
                            'id': offre_id, 'titre': titre, 'entreprise': entreprise,
                            'lieu_annonce': lieu, 'source': 'Emploi.cm (Playwright)', 
                            'lien': lien_absolu, 'recherche_mot_cle': mot_cle, 
                            'recherche_lieu': 'Cameroun'
                        }
                        toutes_les_offres.append(offre)
                        offres_ids_vus.add(offre_id)
                    except Exception as e:
                        # Si une offre pose problème, on la saute et on continue
                        continue

            except PlaywrightTimeoutError:
                print("   ⚠️ Pas d'offres trouvées pour ce mot-clé après une attente patiente.")
            except Exception as e:
                print(f"   ❌ Une erreur est survenue : {e}")
            
            time.sleep(random.uniform(1, 2))
        
        browser.close()
        print("\n✅ Navigateur fermé.")

    return toutes_les_offres

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 2F (FINALE - CORRIGÉE)")
    print("   Scraping patient avec Playwright")
    print("=" * 60)

    mots_cles = charger_profil(PROFIL_FILENAME)
    if mots_cles:
        offres_trouvees = scraper_avec_playwright(mots_cles)
        
        if offres_trouvees:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(offres_trouvees, f, ensure_ascii=False, indent=4)
            print(f"\n💾 {len(offres_trouvees)} offres uniques sauvegardées dans : {OUTPUT_FILENAME}")
        else:
            print("\n🤷 Aucune offre trouvée lors de cette recherche.")
        
        print("\n✅ Étape 2F terminée avec succès !")
    else:
        print("\n❌ Arrêt du script.")