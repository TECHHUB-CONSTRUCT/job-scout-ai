# Job Scout AI - par TechHub Construct

[![Status](https://img.shields.io/badge/status-live-success.svg)](https://jobs.techhub-construct.com)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-Flask-orange.svg)](https://flask.palletsprojects.com/)
[![Déploiement](https://img.shields.io/badge/déployé%20sur-Render-brightgreen.svg)](https://render.com/)

**Job Scout AI** est une application web SaaS qui agit comme un agent de recherche d'emploi autonome. Elle analyse le CV d'un utilisateur, recherche des offres pertinentes sur le web via l'API Google Jobs, et envoie un rapport quotidien personnalisé par e-mail avec les 10 meilleures offres.

**➡️ Lien vers le projet en ligne :** [https://jobs.techhub-construct.com](https://jobs.techhub-construct.com)

---

## 🏛️ Architecture Finale

Le projet est basé sur une architecture moderne, découplée et pensée pour l'évolutivité :
-   **Frontend & Serveur Web :** Une application **Flask** qui fournit l'interface utilisateur et gère les inscriptions. Déployée sur **Render** en tant que "Web Service".
-   **Base de Données :** Une base de données **PostgreSQL**, également hébergée sur **Render**, pour stocker les informations des utilisateurs de manière persistante et sécurisée.
-   **Agent IA (Tâche Quotidienne) :** Un script Python exécuté via **GitHub Actions** qui se connecte à la base de données, lance les recherches via l'API **SerpApi**, analyse les résultats et envoie les e-mails.

---

## 🗂️ Structure Finale des Fichiers

Voici la liste des fichiers essentiels à retenir pour ce projet :

```
/
├── .github/
│   └── workflows/
│       └── daily_job_run.yml   # Fichier pour l'automatisation quotidienne
├── static/
│   └── images/
│       └── logo.png            # Logo de l'entreprise
├── templates/
│   ├── index.html              # Page d'accueil
│   └── privacy.html            # Page de politique de confidentialité
├── uploads/                    # (Ignoré par Git) Dossier pour les CVs uploadés
├── venv/                       # (Ignoré par Git) Environnement virtuel
├── .gitignore                  # Fichier pour ignorer les éléments non désirés
├── app.py                      # Le serveur web Flask
├── agent_pipeline.py           # Le moteur principal de l'IA
├── run_daily_jobs.py           # Le script lancé par GitHub Actions
├── config.json                 # (Ignoré par Git) Clés et secrets pour le test local
├── requirements.txt            # Liste des dépendances Python
├── README.md                   # Cette documentation
└── LICENSE                     # Licence du projet
```

---

## 🛠️ Guide de Reproduction Complet : Étapes et Vérifications

Ce guide retrace notre parcours de développement, incluant les tests de validation à chaque étape.

### Étape 0 : Préparation de l'Environnement Local

1.  **Action :** Créez un dossier de projet, naviguez dedans via un terminal et créez un environnement virtuel.
    ```bash
    mkdir job-scout-ai && cd job-scout-ai
    python -m venv venv
    # Sur Windows:
    venv\Scripts\activate
    ```
2.  **Vérification :** Le prompt de votre terminal doit maintenant commencer par `(venv)`. C'est la preuve que votre environnement est isolé et actif.

### Étape 1 : Fusionner les Scripts en un Moteur `agent_pipeline.py`

1.  **Action :** Créer le fichier `agent_pipeline.py` qui regroupe la logique de lecture de CV, d'appel API, de scoring et d'envoi d'email. Créer aussi `config.json` pour les tests locaux avec vos clés.
2.  **Vérification :** Pas de test d'exécution directe. Ce fichier est un "moteur" qui sera appelé par d'autres scripts. L'absence d'erreurs de syntaxe est la seule vérification à ce stade.

### Étape 2 : Création de l'Interface Web (SaaS MVP)

1.  **Action :**
    -   Installez Flask : `pip install Flask`.
    -   Créez `app.py` avec la logique de serveur web.
    -   Créez le dossier `templates` et le fichier `index.html`.
    -   Lancez le serveur localement : `python app.py`.
2.  **Vérification :**
    -   Le terminal affiche `* Running on http://127.0.0.1:5000`.
    -   En ouvrant cette URL dans un navigateur, la page web s'affiche correctement avec les champs de formulaire.

### Étape 3 : Connexion du Moteur à l'Interface Web

1.  **Action :** Modifiez `app.py` pour importer et appeler la fonction `executer_pipeline_pour_utilisateur` de `agent_pipeline.py` dans une tâche de fond (`threading`).
2.  **Vérification :**
    -   Lancez `python app.py`.
    -   Allez sur le site, soumettez un CV et un email.
    -   **Sur la page web :** Le message de confirmation "Merci ! Votre recherche a été lancée..." apparaît **instantanément**.
    -   **Dans le terminal :** Les logs du pipeline (`[1/4] Analyse...`, `[2/4] Récupération...`) s'affichent en différé. C'est la preuve que la tâche de fond fonctionne.
    -   **Dans votre boîte mail :** Vous recevez le premier email de rapport, envoyé par le pipeline.

### Étape 4 : Déploiement sur le Cloud

1.  **Action :**
    -   Créez les fichiers `requirements.txt` (`pip freeze > requirements.txt`), `.gitignore`, et `run_daily_jobs.py`.
    -   Poussez tout le projet sur un nouveau dépôt GitHub.
    -   Créez une **base de données PostgreSQL** et un **Web Service** sur Render.
    -   Configurez les variables d'environnement sur Render, notamment `DATABASE_URL` (avec l'URL interne).
2.  **Vérification :**
    -   Dans l'onglet "Events" de votre service sur Render, le déploiement se termine avec le statut **"Deploy live"**.
    -   L'URL en `.onrender.com` de votre application est accessible et affiche votre site.
    -   Soumettez le formulaire sur le site en ligne. Vérifiez dans l'onglet "Data" de votre base de données sur Render que l'utilisateur a bien été ajouté à la table `user`.

### Étape 5 : Automatisation Quotidienne avec GitHub Actions

1.  **Action :**
    -   Créez le fichier de workflow `.github/workflows/daily_job_run.yml`.
    -   Dans les paramètres de votre dépôt GitHub, configurez les "Secrets" (`DATABASE_URL` avec l'URL externe, `SERPAPI_KEY`, etc.).
    -   Poussez les nouveaux fichiers sur GitHub.
2.  **Vérification (Le Test Ultime) :**
    -   Allez dans l'onglet "Actions" de votre dépôt GitHub.
    -   Sélectionnez le workflow "Run Daily Job Search" et lancez-le manuellement ("Run workflow").
    -   Le statut du workflow passe à **"Success"** avec une coche verte.
    -   En cliquant sur le job `build-and-run`, vous pouvez lire les logs. Ils doivent montrer : `👥 X utilisateur(s) à traiter`, suivi des logs du pipeline pour chaque utilisateur.
    -   La preuve finale : **vous recevez un nouvel email**, cette fois généré et envoyé par l'environnement de GitHub Actions.

### Étape 6 : Configuration du Domaine Personnalisé

1.  **Action :**
    -   Dans Render, ajoutez votre sous-domaine (ex: `jobs.techhub-construct.com`) dans les "Custom Domains".
    -   Dans votre registraire de domaine (LWS), créez un enregistrement `CNAME` pointant vers l'adresse `.onrender.com` fournie par Render. Supprimez tout enregistrement `A` ou `AAAA` conflictuel.
2.  **Vérification :**
    -   Dans Render, le statut du domaine passe à **"Verified"** et **"Certificate Issued"**.
    -   Après la propagation DNS (qui peut prendre plusieurs heures), l'URL `https://jobs.techhub-construct.com` affiche votre application et non plus la page de votre hébergeur.

---

## 📈 Améliorations Possibles (Roadmap)

-   [ ] **Tableau de Bord Utilisateur :** Créer un espace connecté où l'utilisateur peut voir ses résultats, archiver des offres et gérer ses préférences.
-   [ ] **Amélioration de l'IA :** Utiliser des techniques de NLP plus avancées (similarité cosinus, vectorisation) pour un scoring de pertinence plus fin.
-   [ ] **Stockage de CV Cloud :** Uploader les CV sur un service de stockage d'objets (comme Amazon S3 ou Backblaze B2) pour une architecture plus robuste.
-   [ ] **Plus de Personnalisation :** Permettre aux utilisateurs de choisir les pays, la fréquence des rapports, et des mots-clés à exclure.
-   [ ] **Système de Paiement :** Intégrer Stripe ou PayPal pour proposer des fonctionnalités "Premium".

---

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.