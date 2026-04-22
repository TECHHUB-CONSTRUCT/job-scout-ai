from flask import Flask, render_template, request, flash
import os
import threading
# On importe la fonction principale de notre moteur IA
from agent_pipeline import executer_pipeline_pour_utilisateur

# --- Initialisation de Flask ---
app = Flask(__name__)
app.secret_key = 'une_cle_secrete_tres_difficile_a_deviner'
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Interface Web ---
@app.route('/', methods=['GET', 'POST'])
def accueil():
    if request.method == 'POST':
        if 'cv_file' not in request.files or request.form['email'] == '':
            flash('Veuillez fournir un email et un fichier CV.')
            return render_template('index.html')
        
        file = request.files['cv_file']
        email = request.form['email']

        if file.filename == '':
            flash('Aucun fichier sélectionné.')
            return render_template('index.html')

        if file and email:
            # Créer un sous-dossier unique pour cet utilisateur/recherche pour éviter les conflits
            user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], email.split('@')[0])
            os.makedirs(user_upload_dir, exist_ok=True)
            filepath = os.path.join(user_upload_dir, file.filename)
            file.save(filepath)
            
            print(f"✅ Fichier reçu : {filepath}")
            
            # On lance le VRAI pipeline en tâche de fond
            thread = threading.Thread(target=executer_pipeline_pour_utilisateur, args=(filepath, email))
            thread.start()
            
            print("🚀 Tâche de fond pour le pipeline réel lancée.")
            
            flash(f'Merci ! Votre recherche a été lancée. Vous recevrez les résultats à l\'adresse : {email}')
            return render_template('index.html')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)