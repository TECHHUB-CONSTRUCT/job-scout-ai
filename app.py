# Fichier : app.py

from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import os
import threading
from agent_pipeline import executer_pipeline_pour_utilisateur

# --- Initialisation ---
app = Flask(__name__)
app.secret_key = 'une_cle_secrete_tres_difficile_a_deviner'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Configuration de la Base de Données ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modèle de Données Utilisateur ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cv_path = db.Column(db.String(300), nullable=False)
    last_run = db.Column(db.DateTime, nullable=True)

# Créer les tables si elles n'existent pas (nécessaire au premier lancement)
with app.app_context():
    db.create_all()

# --- Interface Web ---
@app.route('/', methods=['GET', 'POST'])
def accueil():
    if request.method == 'POST':
        file = request.files.get('cv_file')
        email = request.form.get('email')

        if not file or not email or file.filename == '':
            flash('Veuillez fournir un email et un fichier CV valide.')
            return render_template('index.html')

        # NOTE: Sur Render, le stockage de fichiers est temporaire.
        # Pour une version plus avancée, il faudrait uploader les CV sur un service comme Amazon S3.
        # Pour notre MVP, c'est suffisant.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # --- Enregistrement dans la VRAIE base de données ---
        user = User.query.filter_by(email=email).first()
        if user:
            user.cv_path = filepath
        else:
            user = User(email=email, cv_path=filepath)
            db.session.add(user)
        db.session.commit()
        print(f"✅ Utilisateur {email} sauvegardé/mis à jour en base de données.")

        thread = threading.Thread(target=executer_pipeline_pour_utilisateur, args=(filepath, email))
        thread.start()
        
        flash(f'Merci ! Votre recherche a été lancée. Vous recevrez les résultats à l\'adresse : {email}')
        return render_template('index.html')

    return render_template('index.html')

# Le 'if __name__ == '__main__':' n'est pas nécessaire pour la production sur Render
# mais utile pour les tests locaux.