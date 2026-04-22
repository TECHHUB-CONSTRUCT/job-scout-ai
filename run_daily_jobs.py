# Fichier : run_daily_jobs.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from agent_pipeline import executer_pipeline_pour_utilisateur

# --- Configuration de la Base de Données ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Classe User minimale pour que SQLAlchemy comprenne la structure
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
Base = declarative_base()
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    cv_path = Column(String(300), nullable=False)
    last_run = Column(DateTime, nullable=True)

def get_all_users():
    if not DATABASE_URL:
        print("❌ Variable d'environnement DATABASE_URL non définie.")
        return []
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User).all()
    session.close()
    return users

if __name__ == "__main__":
    print("🚀 Lancement du batch de recherche quotidienne...")
    
    utilisateurs = get_all_users()
    
    if not utilisateurs:
        print("🤷 Aucun utilisateur trouvé dans la base de données. Fin de la tâche.")
    else:
        print(f"👥 {len(utilisateurs)} utilisateur(s) à traiter.")
        for user in utilisateurs:
            # NOTE: Le chemin du CV est un problème car les fichiers ne sont pas partagés.
            # Pour un vrai produit, le CV serait sur S3. Pour le MVP, on suppose
            # que le CV est accessible (ce qui ne sera pas le cas avec GitHub Actions).
            # Nous allons devoir adapter le workflow pour uploader le CV.
            # Pour l'instant, on se concentre sur l'envoi de l'email.
            cv_path = user.cv_path # Ce chemin n'est valide que sur le serveur de Render.
            email = user.email
            print(f"\n--- Traitement pour {email} ---")
            
            # Pour ce MVP, nous ne pouvons pas relire le CV depuis GitHub Actions.
            # Nous allons donc lancer une recherche plus générique.
            # L'étape suivante serait de stocker le CV sur un service partagé.
            # On simule en passant 'None' comme chemin de CV.
            try:
                executer_pipeline_pour_utilisateur(None, email)
            except Exception as e:
                print(f"❌ Erreur lors du traitement de l'utilisateur {email}: {e}")
            
    print("\n✅ Batch de recherche quotidienne terminé.")