# Fichier : agent_pipeline.py (version finale pour la production)

# ... (toutes les sections import et fonctions utilitaires restent les mêmes) ...
import os
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pdfplumber
from docx import Document
import spacy
from serpapi import GoogleSearch

try:
    nlp = spacy.load("fr_core_news_sm")
    nlp.max_length = 2000000
    SPACY_LOADED = True
except OSError:
    print("❌ Modèle spaCy 'fr_core_news_sm' non trouvé.")
    SPACY_LOADED = False

def charger_json(filename, default_value=None):
    if not os.path.exists(filename):
        return default_value if default_value is not None else None
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return default_value if default_value is not None else None

# ... (les fonctions extraire_texte, construire_profil_candidat, recuperer_offres, analyser_et_noter_offres, formater_email_html, envoyer_rapport_email restent les mêmes)
# ... vous pouvez les recopier depuis la version précédente si besoin...

# Voici la seule fonction qui a besoin d'une modification logique

def executer_pipeline_pour_utilisateur(chemin_cv, email_utilisateur):
    """La fonction principale qui orchestre tout."""
    print("\n" + "="*50)
    print(f"🤖 DÉBUT DU PIPELINE pour : {email_utilisateur}")
    
    texte_cv = None
    # --- Étape 1 : Lire le CV seulement s'il est fourni ---
    if chemin_cv and os.path.exists(chemin_cv):
        print(f"   [1/4] Analyse du CV : {chemin_cv}...")
        texte_cv = extraire_texte(chemin_cv)
        if not texte_cv: print("   ⚠️ Avertissement : Impossible de lire le contenu du CV.")
    else:
        print("   [1/4] Pas de CV fourni (mode tâche quotidienne), utilisation de mots-clés génériques.")
    
    profil = construire_profil_candidat(texte_cv)
    print(f"   ✅ Profil de recherche créé avec {len(profil['mots_cles_recherche'])} mots-clés.")

    # --- Étape 2 : Charger la configuration et récupérer les offres ---
    print("   [2/4] Récupération des offres via API...")
    config = {
        "serpapi_key": os.environ.get('SERPAPI_KEY'),
        "email_expediteur": os.environ.get('EMAIL_SENDER'),
        "email_mot_de_passe_app": os.environ.get('EMAIL_PASSWORD')
    }
    if not config["serpapi_key"]:
        print("   -> Secrets non trouvés, lecture de config.json...")
        config_from_file = charger_json("config.json")
        if config_from_file: config.update(config_from_file)
    
    if not config.get("serpapi_key"):
        print("   ❌ Échec : Configuration API/email introuvable.")
        return

    offres_brutes = recuperer_offres(profil, config)
    print(f"   ✅ {len(offres_brutes)} offres brutes récupérées.")
    if not offres_brutes:
        print("   ⚠️ Aucune offre trouvée, envoi d'un email de notification.")
        envoyer_rapport_email([], config, email_utilisateur)
        return

    # --- Étape 4 : Analyser et noter les offres ---
    print("   [3/4] Analyse et calcul des scores...")
    # La fonction d'analyse utilisera le texte du CV s'il existe, sinon elle se basera sur une analyse plus simple
    offres_notees = analyser_et_noter_offres(offres_brutes, texte_cv)
    print("   ✅ Offres notées et triées.")
    
    # --- Étape 5 : Préparer et envoyer l'e-mail ---
    print("   [4/4] Préparation et envoi du rapport par e-mail...")
    top_10_offres = offres_notees[:10]
    envoyer_rapport_email(top_10_offres, config, email_utilisateur)
    
    print(f"✅ PIPELINE TERMINÉ pour {email_utilisateur} !")
    print("="*50 + "\n")