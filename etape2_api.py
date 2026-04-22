# =============================================================================
# ÉTAPE 2 (FINALE & FIABLE) : COLLECTE VIA L'API GOOGLE JOBS
# =============================================================================

import json
import os
from serpapi import GoogleSearch

# --- CONFIGURATION ---
PROFIL_FILENAME = "profil_candidat.json"
CONFIG_FILENAME = "config.json"
OUTPUT_FILENAME = "offres_api.json"

# Correspondance des pays avec les codes Google (ex: fr = France)
GOOGLE_COUNTRY_CODES = {
    "France": "fr",
    "Canada": "ca",
    "Belgique": "be",
    "Suisse": "ch"
}

# =============================================================================
# FONCTIONS
# =============================================================================

def charger_json(filename):
    if not os.path.exists(filename):
        print(f"❌ ERREUR : Fichier '{filename}' introuvable.")
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def rechercher_offres_via_api(profil, config):
    """Interroge l'API Google Jobs de SerpApi."""
    
    api_key = config.get("serpapi_key")
    if not api_key:
        print("❌ Clé API SerpApi non trouvée dans config.json !")
        return []

    mots_cles = profil.get("mots_cles_recherche", [])
    toutes_les_offres = []
    offres_ids_vus = set()

    for lieu, code_pays in GOOGLE_COUNTRY_CODES.items():
        for mot_cle in mots_cles:
            print(f"\n--- Recherche API pour '{mot_cle}' en '{lieu}' ---")
            
            params = {
                "api_key": api_key,
                "engine": "google_jobs",
                "q": f"{mot_cle} {lieu}", # On combine les deux pour plus de précision
                "gl": code_pays, # Géolocalisation de la recherche
                "hl": "fr" # Langue des résultats
            }

            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                
                if "jobs_results" in results:
                    jobs = results["jobs_results"]
                    print(f"   ✅ Trouvé {len(jobs)} offres.")
                    
                    for job in jobs:
                        # On crée un ID unique pour chaque offre
                        offre_id = job.get("job_id")
                        
                        if offre_id and offre_id not in offres_ids_vus:
                            offre = {
                                "id": offre_id,
                                "titre": job.get("title"),
                                "entreprise": job.get("company_name"),
                                "lieu_annonce": job.get("location"),
                                "description": job.get("description"), # L'API nous donne la description directement !
                                "source": job.get("via"),
                                "lien": job.get("related_links", [{}])[0].get("link") # Le lien pour postuler
                            }
                            toutes_les_offres.append(offre)
                            offres_ids_vus.add(offre_id)
                else:
                    print("   ⚠️ Pas de résultats pour cette recherche.")

            except Exception as e:
                print(f"   ❌ Erreur lors de l'appel API : {e}")

    return toutes_les_offres

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 2 (API GOOGLE JOBS)")
    print("=" * 60)

    profil = charger_json(PROFIL_FILENAME)
    config = charger_json(CONFIG_FILENAME)

    if profil and config:
        offres = rechercher_offres_via_api(profil, config)
        if offres:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(offres, f, ensure_ascii=False, indent=4)
            print(f"\n💾 {len(offres)} offres via API sauvegardées dans : {OUTPUT_FILENAME}")
        else:
            print("\n🤷 Aucune offre n'a pu être extraite via l'API.")
        print("\n✅ Étape 2 (API) terminée !")
    else:
        print("\n❌ Arrêt du script. Vérifiez les fichiers profil_candidat.json et config.json.")