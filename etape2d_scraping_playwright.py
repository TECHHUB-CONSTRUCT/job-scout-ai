# =============================================================================
# ÉTAPE 2D : SCRAPING AVEC PLAYWRIGHT - LA SOLUTION ROBUSTE
# Agent de Recherche d'Emploi - Edmond FOMBEN
# =============================================================================

import json
import time
import random
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
OUTPUT_FILENAME = "offres_playwright.json"
BASE_URL = "https://www.emploi.cm"
# Mettre HEADLESS sur True pour ne pas voir le navigateur, False pour le voir travailler
HEADLESS = False 

# =============================================================================
# FONCTIONS DE SCRAPING
# =============================================================================

def charger_profil(filename):
    """Charge les mots-clés de recherche depuis le profil JSON."""
    if not os.path.exists(filename):
        print(f"❌ ERREUR : Fichier de profil '{filename}' introuvable.")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        profil = json.load(f)
        return profil.get("mots_cles_recherche", [])

def scraper_avec_playwright(mots_cles):
    """Scrape le site en utilisant un vrai navigateur piloté par Playwright."""
    
    toutes_les_offres = []
    offres_ids_vus = set()

    # Playwright fonctionne avec un bloc "with" pour bien démarrer et fermer les ressources
    with sync_playwright() as p:
        # On lance un navigateur (chromium est rapide et stable)
        browser = p.chromium.launch(headless=HEADLESS)
        # On crée un "contexte" de navigation (comme une session privée)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        # On ouvre un nouvel onglet
        page = context.new_page()

        print("🤖 Navigateur lancé par Playwright.")

        for mot_cle in mots_cles:
            url = f"{BASE_URL}/recherche-jobs-cameroun/{mot_cle.replace(' ', '%20')}"
            print(f"\n--- Recherche pour '{mot_cle}' ---")
            print(f" navegar vers: {url}")

            try:
                # On navigue vers l'URL
                page.goto(url, timeout=60000) # Timeout de 60 secondes
                
                # C'est l'étape cruciale : on attend que les offres soient bien visibles à l'écran
                # On attend le premier élément avec la classe 'job-item' pendant 15 secondes max
                page.wait_for_selector('div.job-item', timeout=15000)
                print("   ✅ Contenu de la page chargé et offres visibles.")

                # Maintenant qu'on est sûr que la page est chargée, on extrait le HTML
                # C'est la même logique qu'avant, mais sur un contenu fiable
                job_cards = page.locator('div.job-item').all()
                print(f"   🔎 Trouvé {len(job_cards)} offres pour '{mot_cle}'.")

                for card in job_cards:
                    titre_tag = card.locator('div.job-item-title a')
                    titre_h3 = card.locator('div.job-item-title h3')
                    
                    titre = titre_h3.inner_text().strip() if titre_h3 else "N/A"
                    lien_relatif = titre_tag.get_attribute('href') if titre_tag else "N/A"
                    lien_absolu = f"{BASE_URL}{lien_relatif}" if lien_relatif != "N/A" else "N/A"
                    offre_id = lien_absolu

                    if offre_id in offres_ids_vus or offre_id == "N/A":
                        continue
                    
                    entreprise_tag = card.locator('div.job-item-company')
                    entreprise = entreprise_tag.inner_text().strip() if entreprise_tag else "N/A"
                    
                    lieu_tag = card.locator('div.job-item-location')
                    lieu = lieu_tag.inner_text().strip() if lieu_tag else "N/A"
                    
                    offre = {
                        'id': offre_id, 'titre': titre, 'entreprise': entreprise,
                        'lieu_annonce': lieu, 'source': 'Emploi.cm (Playwright)', 
                        'lien': lien_absolu, 'recherche_mot_cle': mot_cle, 
                        'recherche_lieu': 'Cameroun'
                    }
                    toutes_les_offres.append(offre)
                    offres_ids_vus.add(offre_id)

            except PlaywrightTimeoutError:
                print("   ⚠️ Timeout : La page n'a pas chargé les offres à temps, ou il n'y en a pas.")
            except Exception as e:
                print(f"   ❌ Une erreur est survenue : {e}")
            
            # Petite pause pour ne pas aller trop vite
            time.sleep(random.uniform(1, 2))
        
        # On ferme le navigateur proprement
        browser.close()
        print("\n Navigateur fermé.")

    return toutes_les_offres

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 2D (PLAYWRIGHT)")
    print("   Scraping robuste avec un navigateur simulé")
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
        
        print("\n✅ Étape 2D terminée avec succès !")
        print("👉 Prochaine étape : Analyse et matching de ces nouvelles offres.")
    else:
        print("\n❌ Arrêt du script. Le profil n'a pas pu être chargé.")