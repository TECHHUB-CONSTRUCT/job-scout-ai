# =============================================================================
# ÉTAPE 4 : ANALYSE DE PERTINENCE (VIA DONNÉES API)
# =============================================================================

import json
import os

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
OFFRES_FILENAME = "offres_api.json" # On utilise le fichier de l'API
OUTPUT_FILENAME = "offres_finales_scored.json"

# =============================================================================
# FONCTIONS
# =============================================================================

def charger_json(filename):
    """Charge un fichier JSON et retourne son contenu."""
    if not os.path.exists(filename):
        print(f"❌ ERREUR : Fichier '{filename}' introuvable.")
        print(f"   Veuillez d'abord lancer le script 'etape2_api.py' pour le générer.")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculer_score(description, competences):
    """
    Calcule un score simple basé sur le nombre de compétences trouvées.
    Chaque compétence trouvée vaut 10 points.
    """
    if not description:
        return 0, []

    description_lower = description.lower()
    score = 0
    competences_trouvees = []

    for comp in competences:
        # On s'assure que la compétence est un mot "entier" pour éviter les faux positifs
        # Ex: chercher "rip" ne doit pas matcher dans "description"
        if f" {comp.lower()} " in f" {description_lower} ":
            score += 10
            competences_trouvees.append(comp)
    
    return score, list(set(competences_trouvees)) # On retourne des compétences uniques

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 4 (ANALYSE API)")
    print("=" * 60)

    profil = charger_json(PROFIL_FILENAME)
    offres = charger_json(OFFRES_FILENAME)

    if not profil or not offres:
        print("\n❌ Arrêt du script. Données manquantes.")
    else:
        competences_cv = profil.get("competences_extraites", [])
        print(f"✅ {len(offres)} offres à analyser avec vos {len(competences_cv)} compétences.")
        
        offres_analysees = []
        for i, offre in enumerate(offres):
            print(f"   -> Analyse de l'offre {i+1}/{len(offres)} : {offre.get('titre', 'Titre inconnu')[:50]}...")
            
            description = offre.get("description", "")
            score, competences_match = calculer_score(description, competences_cv)

            # On enrichit l'objet de l'offre avec les nouvelles informations
            offre['score_pertinence'] = score
            offre['competences_match'] = competences_match
            
            offres_analysees.append(offre)
        
        # On trie la liste finale par score, du plus élevé au plus bas
        offres_analysees.sort(key=lambda x: x['score_pertinence'], reverse=True)
        
        # On sauvegarde le résultat
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(offres_analysees, f, ensure_ascii=False, indent=4)
            
        print("\n" + "=" * 60)
        print("✅ Analyse terminée avec succès !")
        print(f"💾 {len(offres_analysees)} offres analysées, notées et triées sauvegardées dans :")
        print(f"   {OUTPUT_FILENAME}")
        print("=" * 60)