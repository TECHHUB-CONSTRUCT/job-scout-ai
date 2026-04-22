# =============================================================================
# ÉTAPE 5 : RAPPORT QUOTIDIEN PAR E-MAIL
# =============================================================================

import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# --- CONFIGURATION ---
CONFIG_FILENAME = "config.json"
OFFRES_SCORED_FILENAME = "offres_finales_scored.json"
HISTORIQUE_FILENAME = "historique_offres_envoyees.json"
NOMBRE_OFFRES_A_ENVOYER = 10

# =============================================================================
# FONCTIONS
# =============================================================================

def charger_json(filename, default_value=None):
    if not os.path.exists(filename):
        return default_value if default_value is not None else []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default_value if default_value is not None else []

def sauvegarder_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def formater_email_html(offres):
    """Crée le corps de l'e-mail en HTML pour un joli rendu."""
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { width: 90%; max-width: 800px; margin: 20px auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
            .header { background-color: #4285F4; color: white; padding: 20px; text-align: center; }
            .header h1 { margin: 0; }
            .offre { padding: 15px; border-bottom: 1px solid #eee; }
            .offre:last-child { border-bottom: none; }
            .offre h2 { margin-top: 0; color: #1a0dab; }
            .offre h2 a { text-decoration: none; color: #1a0dab; }
            .offre .entreprise { font-weight: bold; color: #555; }
            .offre .lieu { font-style: italic; color: #777; }
            .offre .score { background-color: #f2f2f2; border-radius: 4px; padding: 5px 10px; display: inline-block; font-weight: bold; }
            .competences { margin-top: 10px; }
            .competences span { background-color: #e0e0e0; border-radius: 12px; padding: 3px 8px; font-size: 0.9em; margin-right: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Votre Rapport d'Emploi IA</h1>
                <p>""" + datetime.now().strftime("%d %B %Y") + """</p>
            </div>
    """
    for offre in offres:
        titre = offre.get('titre', 'N/A')
        lien = offre.get('lien', '#')
        entreprise = offre.get('entreprise', 'N/A')
        lieu = offre.get('lieu_annonce', 'N/A')
        score = offre.get('score_pertinence', 0)
        competences_match = offre.get('competences_match', [])

        html += f"""
            <div class="offre">
                <h2><a href="{lien}">{titre}</a></h2>
                <p>
                    <span class="entreprise">{entreprise}</span> - <span class="lieu">{lieu}</span>
                </p>
                <p>
                    <span class="score">Score de pertinence : {score}</span>
                </p>
                <div class="competences">
                    {''.join([f'<span>{comp}</span>' for comp in competences_match])}
                </div>
            </div>
        """
    html += """
        </div>
    </body>
    </html>
    """
    return html

def envoyer_email(sujet, corps_html, config):
    """Se connecte au serveur SMTP de Gmail et envoie l'e-mail."""
    expediteur = config["email_expediteur"]
    destinataire = config["email_destinataire"]
    mot_de_passe = config["email_mot_de_passe_app"]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = sujet
    msg['From'] = expediteur
    msg['To'] = destinataire
    
    msg.attach(MIMEText(corps_html, 'html'))

    try:
        print(f"📧 Connexion au serveur SMTP de Gmail (smtp.gmail.com)...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(expediteur, mot_de_passe)
            print(f"   ✅ Connexion réussie. Envoi de l'e-mail à {destinataire}...")
            smtp_server.sendmail(expediteur, destinataire, msg.as_string())
            print("   ✅ E-mail envoyé avec succès !")
        return True
    except Exception as e:
        print(f"   ❌ Échec de l'envoi de l'e-mail : {e}")
        print("   Vérifiez que :")
        print("   1. La validation en 2 étapes est activée sur votre compte Google.")
        print("   2. Le mot de passe d'application dans config.json est correct.")
        print("   3. Votre antivirus ou pare-feu ne bloque pas la connexion sur le port 465.")
        return False

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 5 (RAPPORT E-MAIL)")
    print("=" * 60)

    config = charger_json(CONFIG_FILENAME)
    offres_triees = charger_json(OFFRES_SCORED_FILENAME)
    historique_ids = set(charger_json(HISTORIQUE_FILENAME, default_value=[]))
    
    if not config or not offres_triees:
        print("❌ Arrêt : Fichier de configuration ou d'offres manquant.")
    else:
        # Filtrer pour ne garder que les NOUVELLES offres
        nouvelles_offres = [offre for offre in offres_triees if offre['id'] not in historique_ids]
        
        print(f"📊 {len(offres_triees)} offres au total.")
        print(f"🆕 {len(nouvelles_offres)} nouvelles offres trouvées.")

        # On prend les 10 meilleures parmi les NOUVELLES
        offres_a_envoyer = nouvelles_offres[:NOMBRE_OFFRES_A_ENVOYER]
        
        if offres_a_envoyer:
            print(f"   -> Préparation de l'e-mail avec les {len(offres_a_envoyer)} meilleures nouvelles offres.")
            
            sujet_email = f"🤖 Votre Top {len(offres_a_envoyer)} des Offres d'Emploi du Jour"
            corps_email_html = formater_email_html(offres_a_envoyer)
            
            if envoyer_email(sujet_email, corps_email_html, config):
                # Si l'envoi réussit, on met à jour l'historique
                nouveaux_ids_envoyes = {offre['id'] for offre in offres_a_envoyer}
                historique_ids.update(nouveaux_ids_envoyes)
                sauvegarder_json(list(historique_ids), HISTORIQUE_FILENAME)
                print(f"   💾 Historique mis à jour. {len(nouveaux_ids_envoyes)} offres ajoutées.")
        else:
            print("✅ Aucune nouvelle offre pertinente à envoyer aujourd'hui.")