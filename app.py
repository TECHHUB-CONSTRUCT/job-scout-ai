from flask import Flask, render_template, request, flash
import os
import threading
import json
from agent_pipeline import executer_pipeline_pour_utilisateur

# --- Initialisation ---
app = Flask(__name__)
app.secret_key = 'une_cle_secrete_tres_difficile_a_deviner'
UPLOAD_FOLDER = 'uploads'
USERS_DB_FILE = 'users.json' # Notre base de données d'utilisateurs
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Fonctions Utilitaires pour la "DB" ---
def charger_utilisateurs():
    if not os.path.exists(USERS_DB_FILE):
        return {}
    try:
        with open(USERS_DB_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def sauvegarder_utilisateur(email, cv_path):
    users = charger_utilisateurs()
    # On enregistre l'utilisateur avec son email comme clé
    users[email] = {'cv_path': cv_path, 'last_run': None}
    with open(USERS_DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# --- Interface Web ---
@app.route('/', methods=['GET', 'POST'])
def accueil():
    if request.method == 'POST':
        # ... (code de validation du formulaire identique) ...
        
        file = request.files['cv_file']
        email = request.form['email']
        
        if file and email:
            # On sauvegarde le CV
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # On enregistre le nouvel utilisateur dans notre "base de données"
            sauvegarder_utilisateur(email, filepath)
            print(f"✅ Nouvel utilisateur enregistré : {email}")

            # On lance le pipeline IMMÉDIATEMENT pour la première fois
            thread = threading.Thread(target=executer_pipeline_pour_utilisateur, args=(filepath, email))
            thread.start()
            
            flash(f'Merci ! Votre première recherche a été lancée. Vous recevrez les résultats à l\'adresse : {email}')
            return render_template('index.html')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)