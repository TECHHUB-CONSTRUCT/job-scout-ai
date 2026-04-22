# =============================================================================
# ÉTAPE 4 : ANALYSE DE PERTINENCE DES OFFRES LINKEDIN
# Agent IA - Edmond FOMBEN
# =============================================================================

import json
import os
import time
import random
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
OFFRES_FILENAME = "offres_linkedin.json"
OUTPUT_FILENAME = "offres_scored.json"
HEADLESS = True  # Mettre False si vous voulez voir le navigateur

# =============================================================================
# OUTILS
# =============================================================================

def charger_json(filename):
    if not os.path.exists(filename):
        print(f"❌ Fichier introuvable : {filename}")
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def calculer_score(description, competences):
    """
    Calcule un score simple basé sur :
    - Nombre de compétences trouvées dans la description
    - Score pondéré
    """
    description_lower = description.lower()
    score = 0
    competences_match = []

    for comp in competences:
        comp_lower = comp.lower()
        if comp_lower in description_lower:
            score += 10
            competences_match.append(comp)

    return score, competences_match

# =============================================================================
# ANALYSE PRINCIPALE
# =============================================================================

def analyser_offres():
    profil = charger_json(PROFIL_FILENAME)
    offres = charger_json(OFFRES_FILENAME)

    if not profil or not offres:
        print("❌ Impossible de charger les données.")
        return

    competences = profil.get("competences_extraites", [])
    print(f"🔎 {len(competences)} compétences chargées pour analyse.")

    offres_scored = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=50)
        page = browser.new_page()

        for i, offre in enumerate(offres):
            print(f"\n--- Analyse {i+1}/{len(offres)} : {offre['titre']} ---")

            try:
                page.goto(offre["lien"], timeout=60000)
                page.wait_for_timeout(3000)

                # Description LinkedIn connectée
                description_locator = page.locator(".jobs-description-content__text")
                
                if description_locator.count() > 0:
                    description = description_locator.inner_text()
                else:
                    description = page.content()

                score, competences_match = calculer_score(description, competences)

                offre_enrichie = offre.copy()
                offre_enrichie["score"] = score
                offre_enrichie["competences_match"] = competences_match

                offres_scored.append(offre_enrichie)

                print(f"   ✅ Score : {score}")
                print(f"   🔧 Compétences matchées : {len(competences_match)}")

            except Exception as e:
                print(f"   ❌ Erreur : {e}")

            time.sleep(random.uniform(1, 2))

        browser.close()

    # Trier par score décroissant
    offres_scored.sort(key=lambda x: x["score"], reverse=True)

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(offres_scored, f, ensure_ascii=False, indent=4)

    print("\n✅ Analyse terminée.")
    print(f"💾 Fichier généré : {OUTPUT_FILENAME}")

# =============================================================================
# EXÉCUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 ÉTAPE 4 - ANALYSE DE PERTINENCE")
    print("=" * 60)
    analyser_offres()