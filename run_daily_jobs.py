# =============================================================================
# SCRIPT POUR L'AUTOMATISATION QUOTIDIENNE (GitHub Actions)
# =============================================================================

import json
import os
# On importe le moteur depuis notre fichier existant
from agent_pipeline import executer_pipeline_pour_utilisateur, charger_json

USERS_DB_FILE = 'users.json'

if __name__ == "__main__":
    print("🚀 Lancement du batch de recherche quotidienne...")
    
    utilisateurs = charger_json(USERS_DB_FILE)
    
    if not utilisateurs:
        print("🤷 Aucun utilisateur trouvé dans la base de données. Fin de la tâche.")
    else:
        print(f"👥 {len(utilisateurs)} utilisateur(s) à traiter.")
        for email, data in utilisateurs.items():
            cv_path = data.get('cv_path')
            if cv_path and os.path.exists(cv_path):
                try:
                    # On lance le pipeline pour chaque utilisateur
                    executer_pipeline_pour_utilisateur(cv_path, email)
                except Exception as e:
                    print(f"❌ Erreur lors du traitement de l'utilisateur {email}: {e}")
            else:
                print(f"⚠️ CV non trouvé pour l'utilisateur {email}. Ignoré.")
        
        print("\n✅ Batch de recherche quotidienne terminé.")