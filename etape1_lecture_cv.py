# =============================================================================
# ÉTAPE 1 : LECTURE ET ANALYSE DU CV (v2 - Ajout du mot-clé "IT")
# Agent de Recherche d'Emploi - Edmond FOMBEN
# =============================================================================

import pdfplumber
from docx import Document
import spacy
from spacy.matcher import Matcher
import json
import os

# --- CONFIGURATION ---
CV_FILENAME = "mon_cv.pdf"  # Changez en "mon_cv.docx" si besoin

# Charge le modèle de langue française de spaCy
nlp = spacy.load("fr_core_news_sm")
# Augmenter la limite pour les textes longs
nlp.max_length = 2000000


# =============================================================================
# SECTION 1 : EXTRACTION DU TEXTE BRUT
# =============================================================================

def extraire_texte_du_pdf(chemin_pdf):
    """Ouvre un fichier PDF et en extrait tout le texte brut."""
    texte_complet = ""
    print(f"📄 Lecture du fichier PDF : {chemin_pdf}...")
    try:
        with pdfplumber.open(chemin_pdf) as pdf:
            for page in pdf.pages:
                texte_page = page.extract_text()
                if texte_page:
                    texte_complet += texte_page + "\n"
        print("✅ Lecture PDF terminée avec succès.")
        return texte_complet
    except FileNotFoundError:
        print(f"❌ ERREUR : Le fichier '{chemin_pdf}' est introuvable.")
        print(f"   Assurez-vous qu'il est bien dans le dossier : {os.getcwd()}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du PDF : {e}")
        return None


def extraire_texte_du_docx(chemin_docx):
    """Ouvre un fichier Word .docx et en extrait tout le texte brut."""
    texte_complet = ""
    print(f"📄 Lecture du fichier Word : {chemin_docx}...")
    try:
        doc = Document(chemin_docx)
        for paragraphe in doc.paragraphs:
            texte_complet += paragraphe.text + "\n"
        print("✅ Lecture Word terminée avec succès.")
        return texte_complet
    except FileNotFoundError:
        print(f"❌ ERREUR : Le fichier '{chemin_docx}' est introuvable.")
        print(f"   Assurez-vous qu'il est bien dans le dossier : {os.getcwd()}")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier Word : {e}")
        return None


def extraire_texte(chemin_fichier):
    """Détecte le format du fichier et appelle la bonne fonction."""
    if chemin_fichier.lower().endswith(".pdf"):
        return extraire_texte_du_pdf(chemin_fichier)
    elif chemin_fichier.lower().endswith(".docx"):
        return extraire_texte_du_docx(chemin_fichier)
    else:
        print(f"❌ Format de fichier non supporté : {chemin_fichier}")
        print("   Formats acceptés : .pdf, .docx")
        return None


# =============================================================================
# SECTION 2 : EXTRACTION DES COMPÉTENCES
# =============================================================================

def extraire_competences(texte):
    """
    Analyse le texte avec spaCy Matcher pour extraire les compétences.
    La liste ci-dessous est personnalisée pour le CV d'Edmond FOMBEN.
    """
    print("\n🔍 Extraction des compétences avec spaCy...")
    matcher = Matcher(nlp.vocab)

    patterns_competences = [
        [{"LOWER": "mysql"}], [{"LOWER": "sql"}], [{"LOWER": "sql"}, {"LOWER": "server"}],
        [{"LOWER": "windows"}], [{"LOWER": "windows"}, {"LOWER": "server"}], [{"LOWER": "linux"}], [{"LOWER": "ubuntu"}], [{"LOWER": "debian"}],
        [{"LOWER": "lan"}], [{"LOWER": "wan"}], [{"LOWER": "tcp"}, {"TEXT": "/"}, {"LOWER": "ip"}], [{"LOWER": "tcp/ip"}], [{"LOWER": "voip"}], [{"LOWER": "ospf"}], [{"LOWER": "eigrp"}], [{"LOWER": "rip"}], [{"LOWER": "modèle"}, {"LOWER": "osi"}], [{"LOWER": "osi"}],
        [{"LOWER": "vpn"}], [{"LOWER": "ipsec"}], [{"LOWER": "ssh"}], [{"LOWER": "snmp"}], [{"LOWER": "acl"}], [{"LOWER": "dhcp"}], [{"LOWER": "dns"}], [{"LOWER": "vlan"}], [{"LOWER": "wlan"}], [{"LOWER": "sécurité"}, {"LOWER": "réseau"}],
        [{"LOWER": "hf"}], [{"LOWER": "vhf"}], [{"LOWER": "gsm"}], [{"LOWER": "gprs"}], [{"LOWER": "umts"}], [{"LOWER": "lte"}], [{"LOWER": "wimax"}], [{"LOWER": "radiocommunication"}], [{"LOWER": "communication"}, {"LOWER": "radio"}],
        [{"LOWER": "wdm"}], [{"LOWER": "sdh"}], [{"LOWER": "pdh"}], [{"LOWER": "faisceaux"}, {"LOWER": "hertziens"}], [{"LOWER": "fibre"}, {"LOWER": "optique"}],
        [{"LOWER": "vmware"}], [{"LOWER": "hyper-v"}], [{"LOWER": "hyper"}, {"TEXT": "-"}, {"LOWER": "v"}], [{"LOWER": "virtualbox"}], [{"LOWER": "esxi"}], [{"LOWER": "vsphere"}], [{"LOWER": "virtualisation"}],
        [{"LOWER": "itil"}], [{"LOWER": "itil"}, {"LOWER": "4"}], [{"LOWER": "support"}, {"LOWER": "technique"}], [{"LOWER": "help"}, {"LOWER": "desk"}], [{"LOWER": "amélioration"}, {"LOWER": "continue"}], [{"LOWER": "gestion"}, {"LOWER": "de"}, {"LOWER": "projet"}], [{"LOWER": "gestion"}, {"LOWER": "des"}, {"LOWER": "incidents"}],
        [{"LOWER": "administration"}, {"LOWER": "réseau"}], [{"LOWER": "administration"}, {"LOWER": "système"}], [{"LOWER": "administration"}, {"LOWER": "de"}, {"LOWER": "systèmes"}], [{"LOWER": "infrastructure"}, {"LOWER": "it"}], [{"LOWER": "câblage"}, {"LOWER": "réseau"}], [{"LOWER": "vidéoconférence"}], [{"LOWER": "déploiement"}], [{"LOWER": "maintenance"}], [{"LOWER": "inventaire"}], [{"LOWER": "p2p"}],
        [{"LOWER": "télécommunications"}], [{"LOWER": "télécoms"}], [{"LOWER": "cloud"}, {"LOWER": "computing"}],
    ]

    matcher.add("COMPETENCES", patterns_competences)
    doc = nlp(texte)
    matches = matcher(doc)

    competences_trouvees = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        competences_trouvees.add(span.text.strip())

    return sorted(list(competences_trouvees), key=str.lower)


# =============================================================================
# SECTION 3 : EXTRACTION DES TITRES DE POSTE RECHERCHÉS
# =============================================================================

def extraire_titres_postes(texte):
    """
    Cherche dans le texte les titres de postes pertinents.
    Ces titres seront utilisés comme mots-clés de recherche sur les sites d'emploi.
    """
    print("🔍 Extraction des titres de postes...")
    matcher = Matcher(nlp.vocab)

    patterns_postes = [
        [{"LOWER": "administrateur"}, {"LOWER": "réseaux"}], [{"LOWER": "administrateur"}, {"LOWER": "réseau"}], [{"LOWER": "administrateur"}, {"LOWER": "systèmes"}], [{"LOWER": "administrateur"}, {"LOWER": "système"}],
        [{"LOWER": "network"}, {"LOWER": "administrator"}], [{"LOWER": "system"}, {"LOWER": "administrator"}], [{"LOWER": "it"}, {"LOWER": "assistant"}], [{"LOWER": "ict"}, {"LOWER": "assistant"}],
        [{"LOWER": "it"}, {"LOWER": "support"}], [{"LOWER": "support"}, {"LOWER": "informatique"}], [{"LOWER": "help"}, {"LOWER": "desk"}], [{"LOWER": "telecoms"}, {"LOWER": "operator"}],
        [{"LOWER": "ingénieur"}, {"LOWER": "réseau"}], [{"LOWER": "ingénieur"}, {"LOWER": "réseaux"}], [{"LOWER": "ingénieur"}, {"LOWER": "systèmes"}], [{"LOWER": "ingénieur"}, {"LOWER": "télécommunications"}],
        [{"LOWER": "technicien"}, {"LOWER": "réseau"}], [{"LOWER": "responsable"}, {"LOWER": "it"}], [{"LOWER": "responsable"}, {"LOWER": "informatique"}],
    ]

    matcher.add("POSTES", patterns_postes)
    doc = nlp(texte)
    matches = matcher(doc)

    postes_trouves = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        postes_trouves.add(span.text.strip())

    return sorted(list(postes_trouves), key=str.lower)


# =============================================================================
# SECTION 4 : CONSTRUCTION DU PROFIL COMPLET
# =============================================================================

def construire_profil(texte):
    """
    Construit un dictionnaire structuré représentant le profil du candidat.
    Ce profil sera utilisé par les prochaines étapes (scraping, matching).
    """
    print("\n" + "=" * 60)
    print("🤖 CONSTRUCTION DU PROFIL CANDIDAT")
    print("=" * 60)

    competences = extraire_competences(texte)
    postes = extraire_titres_postes(texte)

    postes_recherche_supplementaires = [
        "Network Administrator", "System Administrator", "IT Support Specialist",
        "IT Officer", "ICT Officer", "Infrastructure Engineer",
        "Administrateur Réseaux et Systèmes", "Technicien Support Informatique",
        "IT Help Desk", "Telecommunications Officer",
    ]

    profil = {
        "nom": "Edmond FOMBEN MBOKOUOKO",
        "email": "efomben@gmail.com",
        "titre_principal": "Administrateur Réseaux et Support Informatique",
        "annees_experience": 9,
        "langues": ["Français", "Anglais (B1)"],
        "nationalite": "Camerounais",
        "competences_extraites": competences,
        "postes_trouves_dans_cv": postes,
        "postes_pour_recherche": postes_recherche_supplementaires,
        "secteurs_cibles": [
            "Organisations Internationales (ONU, ONG)", "Télécommunications",
            "IT / Services Informatiques", "Secteur Humanitaire",
        ],
        "mots_cles_recherche": [
            "IT",  # <-- MOT-CLÉ AJOUTÉ ICI
            "Network Administrator", "System Administrator", "IT Support",
            "ICT Officer", "Administrateur Réseau", "Administrateur Systèmes",
            "Support Informatique", "Infrastructure IT", "ITIL", "Help Desk",
            "Telecommunications",
        ],
    }
    return profil


# =============================================================================
# SECTION 5 : AFFICHAGE DES RÉSULTATS
# =============================================================================

def afficher_profil(profil):
    """Affiche le profil de manière claire et structurée dans le terminal."""
    print("\n" + "=" * 60)
    print("📋 PROFIL CANDIDAT - RÉSULTAT DE L'ANALYSE")
    print("=" * 60)
    print(f"\n👤 Nom            : {profil['nom']}")
    print(f"📧 Email          : {profil['email']}")
    print(f"💼 Titre          : {profil['titre_principal']}")
    print(f"📅 Expérience     : {profil['annees_experience']} ans")
    print(f"🌍 Nationalité    : {profil['nationalite']}")
    print(f"🗣️  Langues        : {', '.join(profil['langues'])}")
    print(f"\n🔧 COMPÉTENCES IDENTIFIÉES ({len(profil['competences_extraites'])}) :")
    print("-" * 40)
    for comp in profil["competences_extraites"]: print(f"   ✅ {comp}")
    print(f"\n💼 TITRES DE POSTES TROUVÉS DANS LE CV ({len(profil['postes_trouves_dans_cv'])}) :")
    print("-" * 40)
    for poste in profil["postes_trouves_dans_cv"]: print(f"   📌 {poste}")
    print(f"\n🔎 MOTS-CLÉS POUR LA RECHERCHE D'EMPLOI ({len(profil['mots_cles_recherche'])}) :")
    print("-" * 40)
    for mot in profil["mots_cles_recherche"]: print(f"   🔑 {mot}")
    print(f"\n🏢 SECTEURS CIBLES :")
    print("-" * 40)
    for secteur in profil["secteurs_cibles"]: print(f"   🎯 {secteur}")
    print("\n" + "=" * 60)


# =============================================================================
# SECTION 6 : SAUVEGARDE DU PROFIL
# =============================================================================

def sauvegarder_profil(profil, nom_fichier="profil_candidat.json"):
    """
    Sauvegarde le profil dans un fichier JSON.
    Ce fichier sera lu par les scripts des prochaines étapes.
    """
    try:
        with open(nom_fichier, "w", encoding="utf-8") as f:
            json.dump(profil, f, ensure_ascii=False, indent=4)
        print(f"\n💾 Profil sauvegardé dans : {nom_fichier}")
        print(f"   Ce fichier sera utilisé par l'étape 2 (scraping des offres).")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")


# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE D'EMPLOI - ÉTAPE 1")
    print("   Lecture et Analyse du CV")
    print("=" * 60)
    texte_cv = extraire_texte(CV_FILENAME)
    if texte_cv:
        profil = construire_profil(texte_cv)
        afficher_profil(profil)
        sauvegarder_profil(profil)
        print("\n✅ Étape 1 terminée avec succès !")
        print("👉 Prochaine étape : Scraping des offres d'emploi (etape2_scraping.py)")
    else:
        print("\n❌ Impossible de continuer sans le texte du CV.")
        print("   Vérifiez le fichier et réessayez.")