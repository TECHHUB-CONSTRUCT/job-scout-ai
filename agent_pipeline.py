# =============================================================================
# MOTEUR DE L'AGENT IA - PIPELINE COMPLET (v3 - Prêt pour le Cloud)
# Ce fichier contient toute la logique de traitement et lit les secrets
# de l'environnement ou du fichier de configuration.
# =============================================================================

import os
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Import des bibliothèques nécessaires au pipeline
import pdfplumber
from docx import Document
import spacy
from serpapi import GoogleSearch

# --- Configuration Globale ---
try:
    nlp = spacy.load("fr_core_news_sm")
    nlp.max_length = 2000000
    SPACY_LOADED = True
except OSError:
    print("❌ Modèle spaCy 'fr_core_news_sm' non trouvé.")
    SPACY_LOADED = False


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def charger_json(filename, default_value=None):
    """Charge un fichier JSON et retourne son contenu."""
    if not os.path.exists(filename):
        print(f"   ⚠️ Fichier '{filename}' non trouvé.")
        return default_value if default_value is not None else None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"   ❌ Erreur lors de la lecture de '{filename}': {e}")
        return default_value if default_value is not None else None

def sauvegarder_json(data, filename):
    """Sauvegarde des données dans un fichier JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# =============================================================================
# ÉTAPE 1 : ANALYSE DU CV
# =============================================================================

def extraire_texte(chemin_fichier):
    if chemin_fichier.lower().endswith(".pdf"):
        texte_complet = ""
        with pdfplumber.open(chemin_fichier) as pdf:
            for page in pdf.pages:
                texte_page = page.extract_text()
                if texte_page: texte_complet += texte_page + "\n"
        return texte_complet
    elif chemin_fichier.lower().endswith(".docx"):
        texte_complet = ""
        doc = Document(chemin_fichier)
        for p in doc.paragraphs: texte_complet += p.text + "\n"
        return texte_complet
    return None

def construire_profil_candidat(texte_cv):
    if not SPACY_LOADED: return {"mots_cles_recherche": ["IT", "developer", "technician"]}
    mots_cles_recherche = [
        "IT Support", "Technicien Informatique", "Administrateur Système", "Network Administrator",
        "Help Desk", "IT Officer", "ICT Specialist", "Support Technique"
    ]
    profil = {"mots_cles_recherche": mots_cles_recherche}
    return profil

# =============================================================================
# ÉTAPE 2 : RÉCUPÉRATION DES OFFRES VIA API
# =============================================================================

def recuperer_offres(profil, config):
    api_key = config.get("serpapi_key")
    if not api_key:
        print("   ❌ Clé API 'serpapi_key' non trouvée.")
        return []

    lieux = {"France": "fr", "Canada": "ca", "Belgique": "be", "Suisse": "ch"}
    toutes_les_offres = []
    offres_ids_vus = set()

    for lieu, code_pays in lieux.items():
        for mot_cle in profil["mots_cles_recherche"]:
            print(f"      🔍 API : '{mot_cle}' en '{lieu}'...")
            params = {
                "api_key": api_key, "engine": "google_jobs",
                "q": f"{mot_cle} {lieu}", "gl": code_pays, "hl": "fr"
            }
            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                if "jobs_results" in results:
                    for job in results["jobs_results"]:
                        offre_id = job.get("job_id")
                        if offre_id and offre_id not in offres_ids_vus:
                            toutes_les_offres.append({
                                "id": offre_id, "titre": job.get("title"),
                                "entreprise": job.get("company_name"), "lieu_annonce": job.get("location"),
                                "description": job.get("description"), "source": job.get("via"),
                                "lien": job.get("related_links", [{}])[0].get("link")
                            })
                            offres_ids_vus.add(offre_id)
            except Exception as e:
                print(f"      ❌ Erreur API : {e}")
            time.sleep(1)
    return toutes_les_offres

# =============================================================================
# ÉTAPE 4 : ANALYSE DE PERTINENCE
# =============================================================================

def analyser_et_noter_offres(offres, texte_cv):
    if not texte_cv: return offres
    competences_generiques = [
        "réseau", "support", "windows", "linux", "cisco", "firewall", "sécurité",
        "helpdesk", "ticketing", "itil", "scripting", "python", "powershell",
        "ad", "active directory", "office 365", "azure", "vmware", "hyper-v",
        "backup", "sauvegarde", "tcp/ip", "dns", "dhcp"
    ]
    
    texte_cv_lower = texte_cv.lower()
    offres_analysees = []
    for offre in offres:
        score = 0
        description = (offre.get("description") or "").lower()
        for comp in competences_generiques:
            if comp in description: score += 10
        for mot_cv in texte_cv_lower.split():
            if len(mot_cv) > 3 and mot_cv in description: score += 1
        offre['score_pertinence'] = score
        offres_analysees.append(offre)
    return sorted(offres_analysees, key=lambda x: x['score_pertinence'], reverse=True)

# =============================================================================
# ÉTAPE 5 : RAPPORT PAR E-MAIL
# =============================================================================

def formater_email_html(offres):
    html = """
    <html><head><style>
        body { font-family: sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 800px; margin: 20px auto; border: 1px solid #ddd; border-radius: 8px; }
        .header { background-color: #0056b3; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .offre { padding: 15px; border-bottom: 1px solid #eee; }
        .offre:last-child { border-bottom: none; }
        .offre h2 a { text-decoration: none; color: #0056b3; }
        .score { background-color: #f2f2f2; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
    </style></head><body><div class="container">
        <div class="header"><h1>Job Scout AI par TechHub Construct</h1>
        <p>""" + datetime.now().strftime("%d %B %Y") + """</p></div>
    """
    if not offres:
        html += "<div class='offre'><p>Aucune nouvelle offre pertinente trouvée aujourd'hui. Nous chercherons à nouveau demain !</p></div>"
    else:
        for offre in offres:
            html += f"""
                <div class="offre">
                    <h2><a href="{offre.get('lien', '#')}">{offre.get('titre', 'N/A')}</a></h2>
                    <p><b>{offre.get('entreprise', 'N/A')}</b> - <i>{offre.get('lieu_annonce', 'N/A')}</i></p>
                    <p><span class="score">Score de Pertinence : {offre.get('score_pertinence', 0)}</span></p>
                </div>
            """
    html += "</div></body></html>"
    return html

def envoyer_rapport_email(offres, config, email_destinataire):
    expediteur = config.get("email_expediteur")
    mot_de_passe = config.get("email_mot_de_passe_app")
    if not all([expediteur, mot_de_passe, email_destinataire]):
        print("   ❌ Informations d'email manquantes (expéditeur, mot de passe, destinataire).")
        return False

    sujet = f"🤖 Votre Rapport d'Offres d'Emploi - {datetime.now().strftime('%d/%m/%Y')}"
    corps_html = formater_email_html(offres)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = sujet
    msg['From'] = f"Job Scout AI <{expediteur}>"
    msg['To'] = email_destinataire
    msg.attach(MIMEText(corps_html, 'html'))

    try:
        print(f"   📧 Connexion à smtp.gmail.com pour envoyer à {email_destinataire}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(expediteur, mot_de_passe)
            smtp_server.sendmail(expediteur, email_destinataire, msg.as_string())
        print(f"   ✅ E-mail envoyé avec succès à {email_destinataire} !")
        return True
    except Exception as e:
        print(f"   ❌ Échec de l'envoi de l'e-mail : {e}")
        return False

# =============================================================================
# LE PIPELINE PRINCIPAL
# =============================================================================

def executer_pipeline_pour_utilisateur(chemin_cv, email_utilisateur):
    """La fonction principale qui orchestre tout."""
    print("\n" + "="*50)
    print(f"🤖 DÉBUT DU PIPELINE pour : {email_utilisateur}")
    print(f"📄 Fichier CV : {chemin_cv}")
    
    # --- Étape 1 : Lire le CV et construire le profil ---
    print("   [1/4] Analyse du CV...")
    texte_cv = extraire_texte(chemin_cv)
    if not texte_cv:
        print("   ❌ Échec : Impossible de lire le CV.")
        return
    profil = construire_profil_candidat(texte_cv)
    print(f"   ✅ Profil créé avec {len(profil['mots_cles_recherche'])} mots-clés.")

    # --- Étape 2 : Charger la configuration et récupérer les offres ---
    print("   [2/4] Récupération des offres via API...")

    # === MODIFICATION POUR LIRE LES SECRETS ===
    # On essaie d'abord de lire depuis les variables d'environnement (pour GitHub Actions)
    # Sinon, on lit depuis le fichier config.json (pour le test local)
    config = {
        "serpapi_key": os.environ.get('SERPAPI_KEY'),
        "email_expediteur": os.environ.get('EMAIL_SENDER'),
        "email_mot_de_passe_app": os.environ.get('EMAIL_PASSWORD')
    }
    if not config["serpapi_key"]:
        print("   -> Secrets non trouvés dans l'environnement, lecture de config.json...")
        config_from_file = charger_json("config.json")
        if config_from_file:
            config.update(config_from_file) # On met à jour avec ce qui vient du fichier
    # =========================================
    
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
    offres_notees = analyser_et_noter_offres(offres_brutes, texte_cv)
    print("   ✅ Offres notées et triées.")
    
    # --- Étape 5 : Préparer et envoyer l'e-mail ---
    print("   [4/4] Préparation et envoi du rapport par e-mail...")
    top_10_offres = offres_notees[:10]
    envoyer_rapport_email(top_10_offres, config, email_utilisateur)
    
    print(f"✅ PIPELINE TERMINÉ pour {email_utilisateur} !")
    print("="*50 + "\n")