# =============================================================================
# MOTEUR DE L'AGENT IA - PIPELINE COMPLET (v5 - Lazy Import Playwright)
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
# ATTENTION : L'import de Playwright a été retiré d'ici !

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
    if not os.path.exists(filename):
        return default_value if default_value is not None else None
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return default_value if default_value is not None else None

# =============================================================================
# ÉTAPE 1 : ANALYSE DU CV
# =============================================================================

def extraire_texte(chemin_fichier):
    if not chemin_fichier or not os.path.exists(chemin_fichier): return None
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
    mots_cles_recherche = [
        "IT Support", "Technicien Informatique", "Administrateur Système", "Network Administrator",
        "Help Desk", "IT Officer", "ICT Specialist", "Support Technique", "Informatique", "Réseaux"
    ]
    if texte_cv and SPACY_LOADED:
        doc = nlp(texte_cv)
        ents = [ent.text for ent in doc.ents if ent.label_ == "ORG" or ent.label_ == "MISC"]
        for ent in ents:
            if len(ent) > 3 and ent not in mots_cles_recherche:
                mots_cles_recherche.append(ent)
    profil = {"mots_cles_recherche": list(set(mots_cles_recherche))[:4]}
    return profil

# =============================================================================
# ÉTAPE 2 : RÉCUPÉRATION DES OFFRES (MULTI-SOURCES)
# =============================================================================

def scraper_emploi_cm(mots_cles):
    """Scrape le site emploi.cm en utilisant Playwright."""
    # === IMPORT PARESSEUX (LAZY IMPORT) ===
    # On importe Playwright UNIQUEMENT à l'intérieur de cette fonction.
    # Cela évite que le site web Flask plante au démarrage sur Render.
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    # ======================================
    
    print("      -> Démarrage du scraper pour emploi.cm...")
    offres_locales = []
    ids_vus = set()
    BASE_URL = "https://www.emploi.cm"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page()
            
            for mot_cle in mots_cles:
                url = f"{BASE_URL}/recherche-jobs-cameroun/{mot_cle.replace(' ', '%20')}"
                try:
                    page.goto(url, timeout=45000, wait_until='domcontentloaded')
                    page.locator('div.job-item').first.wait_for(timeout=20000)
                    
                    job_cards = page.locator('div.job-item').all()
                    print(f"         - Trouvé {len(job_cards)} offres pour '{mot_cle}' sur emploi.cm")

                    for card in job_cards:
                        titre_loc = card.locator('div.job-item-title a')
                        if titre_loc.count() == 0: continue
                        
                        lien = titre_loc.get_attribute('href')
                        offre_id = f"{BASE_URL}{lien.split('?')[0]}"
                        
                        if offre_id not in ids_vus:
                            offre = {
                                "id": offre_id,
                                "titre": card.locator('div.job-item-title h3').inner_text().strip(),
                                "entreprise": card.locator('div.job-item-company').inner_text().strip(),
                                "lieu_annonce": "Cameroun",
                                "description": card.locator('div.job-item-description').inner_text().strip(),
                                "source": "emploi.cm",
                                "lien": offre_id
                            }
                            offres_locales.append(offre)
                            ids_vus.add(offre_id)
                except PlaywrightTimeoutError:
                    pass
                except Exception as e:
                    print(f"         - Erreur scraping emploi.cm pour '{mot_cle}': {e}")
            browser.close()
    except Exception as e:
        print(f"      ❌ Erreur majeure lors de l'initialisation de Playwright : {e}")
    
    print(f"      -> Fin du scraping emploi.cm : {len(offres_locales)} offres collectées.")
    return offres_locales

def recuperer_offres(profil, config):
    api_key = config.get("serpapi_key")
    if not api_key:
        print("   ❌ Clé API 'serpapi_key' non trouvée.")
        return []

    lieux_api = {"France": "fr", "Canada": "ca", "Cameroun": "cm"}
    mots_cles = profil["mots_cles_recherche"]
    toutes_les_offres = []
    offres_ids_vus = set()

    print("   --- Phase 1: Recherche via API Google Jobs ---")
    for lieu, code_pays in lieux_api.items():
        for mot_cle in mots_cles:
            print(f"      🔍 API : '{mot_cle}' en '{lieu}'...")
            params = {"api_key": api_key, "engine": "google_jobs", "q": f"{mot_cle} {lieu}", "gl": code_pays, "hl": "fr"}
            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                if "jobs_results" in results:
                    for job in results["jobs_results"]:
                        offre_id = job.get("job_id")
                        if offre_id and offre_id not in offres_ids_vus:
                            toutes_les_offres.append({
                                "id": offre_id, "titre": job.get("title"), "entreprise": job.get("company_name"),
                                "lieu_annonce": job.get("location"), "description": job.get("description"),
                                "source": job.get("via", "Google Jobs"), "lien": job.get("related_links", [{}])[0].get("link")
                            })
                            offres_ids_vus.add(offre_id)
            except Exception as e:
                print(f"      ❌ Erreur API : {e}")
            time.sleep(1)
    print(f"   ✅ {len(toutes_les_offres)} offres collectées via API.")

    print("\n   --- Phase 2: Recherche spécifique pour le Cameroun (Scraping) ---")
    offres_cameroun_local = scraper_emploi_cm(mots_cles)
    
    for offre in offres_cameroun_local:
        if offre['id'] not in offres_ids_vus:
            toutes_les_offres.append(offre)
            offres_ids_vus.add(offre['id'])
            
    print(f"\n   ✅ Total de {len(toutes_les_offres)} offres uniques après fusion.")
    return toutes_les_offres

# =============================================================================
# ÉTAPE 4 ET 5 : ANALYSE ET RAPPORT
# =============================================================================

def analyser_et_noter_offres(offres, texte_cv):
    competences_generiques = ["réseau", "support", "windows", "linux", "cisco", "firewall", "sécurité", "helpdesk", "ticketing", "itil", "scripting", "python", "powershell", "ad", "active directory", "office 365", "azure", "vmware", "hyper-v", "backup", "sauvegarde", "tcp/ip", "dns", "dhcp"]
    offres_analysees = []
    for offre in offres:
        score = 0; description = (offre.get("description") or "").lower()
        for comp in competences_generiques:
            if comp in description: score += 10
        if texte_cv:
            for mot_cv in texte_cv.lower().split():
                if len(mot_cv) > 3 and mot_cv in description: score += 1
        offre['score_pertinence'] = score
        offres_analysees.append(offre)
    return sorted(offres_analysees, key=lambda x: x['score_pertinence'], reverse=True)

def formater_email_html(offres):
    html = """<html><head><style>body { font-family: sans-serif; line-height: 1.6; color: #333; } .container { max-width: 800px; margin: 20px auto; border: 1px solid #ddd; border-radius: 8px; } .header { background-color: #0056b3; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; } .offre { padding: 15px; border-bottom: 1px solid #eee; } .offre:last-child { border-bottom: none; } .offre h2 a { text-decoration: none; color: #0056b3; } .score { background-color: #f2f2f2; padding: 5px 10px; border-radius: 4px; font-weight: bold; }</style></head><body><div class="container"><div class="header"><h1>Job Scout AI par TechHub Construct</h1><p>""" + datetime.now().strftime("%d %B %Y") + """</p></div>"""
    if not offres: html += "<div class='offre'><p>Aucune nouvelle offre pertinente trouvée aujourd'hui. Nous chercherons à nouveau demain !</p></div>"
    else:
        for offre in offres: html += f"""<div class="offre"><h2><a href="{offre.get('lien', '#')}">{offre.get('titre', 'N/A')}</a></h2><p><b>{offre.get('entreprise', 'N/A')}</b> - <i>{offre.get('lieu_annonce', 'N/A')}</i></p><p><span class="score">Score de Pertinence : {offre.get('score_pertinence', 0)}</span></p></div>"""
    html += "</div></body></html>"
    return html

def envoyer_rapport_email(offres, config, email_destinataire):
    expediteur = config.get("email_expediteur"); mot_de_passe = config.get("email_mot_de_passe_app")
    if not all([expediteur, mot_de_passe, email_destinataire]): print("   ❌ Infos email manquantes."); return False
    sujet = f"🤖 Votre Rapport d'Offres d'Emploi - {datetime.now().strftime('%d/%m/%Y')}"; corps_html = formater_email_html(offres)
    msg = MIMEMultipart('alternative'); msg['Subject'] = sujet; msg['From'] = f"Job Scout AI <{expediteur}>"; msg['To'] = email_destinataire; msg.attach(MIMEText(corps_html, 'html'))
    try:
        print(f"   📧 Connexion à smtp.gmail.com pour envoyer à {email_destinataire}...");
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server: smtp_server.login(expediteur, mot_de_passe); smtp_server.sendmail(expediteur, email_destinataire, msg.as_string())
        print(f"   ✅ E-mail envoyé avec succès !"); return True
    except Exception as e: print(f"   ❌ Échec de l'envoi : {e}"); return False

# =============================================================================
# LE PIPELINE PRINCIPAL
# =============================================================================

def executer_pipeline_pour_utilisateur(chemin_cv, email_utilisateur):
    print("\n" + "="*50); print(f"🤖 DÉBUT DU PIPELINE pour : {email_utilisateur}")
    texte_cv = None
    if chemin_cv and os.path.exists(chemin_cv):
        print(f"   [1/4] Analyse du CV : {chemin_cv}..."); texte_cv = extraire_texte(chemin_cv)
    else: print("   [1/4] Pas de CV fourni (mode tâche quotidienne).")
    profil = construire_profil_candidat(texte_cv); print(f"   ✅ Profil créé avec {len(profil['mots_cles_recherche'])} mots-clés.")

    print("   [2/4] Récupération des offres...");
    config = {"serpapi_key": os.environ.get('SERPAPI_KEY'), "email_expediteur": os.environ.get('EMAIL_SENDER'), "email_mot_de_passe_app": os.environ.get('EMAIL_PASSWORD')}
    if not config["serpapi_key"]: config_from_file = charger_json("config.json"); config.update(config_from_file or {})
    if not config.get("serpapi_key"): print("   ❌ Échec : Config API/email introuvable."); return

    offres_brutes = recuperer_offres(profil, config); print(f"   ✅ {len(offres_brutes)} offres brutes au total.")
    if not offres_brutes: envoyer_rapport_email([], config, email_utilisateur); return

    print("   [3/4] Analyse et calcul des scores..."); offres_notees = analyser_et_noter_offres(offres_brutes, texte_cv); print("   ✅ Offres notées et triées.")
    
    print("   [4/4] Envoi du rapport..."); top_10_offres = offres_notees[:10]; envoyer_rapport_email(top_10_offres, config, email_utilisateur)
    
    print(f"✅ PIPELINE TERMINÉ pour {email_utilisateur} !"); print("="*50 + "\n")