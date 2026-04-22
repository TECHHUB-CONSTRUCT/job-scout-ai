# =============================================================================
# ÉTAPE 2E : DEBUG INTERACTIF AVEC L'INSPECTEUR PLAYWRIGHT
# =============================================================================

from playwright.sync_api import sync_playwright

URL_TEST = "https://www.emploi.cm/recherche-jobs-cameroun/IT"

print("\n" + "=" * 60)
print("🕵️‍♂️ LANCEMENT DU SCRIPT DE DEBUG INTERACTIF")
print("   Suivez les instructions attentivement !")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print(f"\n1. Navigation vers : {URL_TEST}")
    page.goto(URL_TEST)

    print("\n2. MISE EN PAUSE DU SCRIPT. DEUX FENÊTRES SONT OUVERTES :")
    print("   - Le navigateur Chrome.")
    print("   - L'inspecteur Playwright (une petite fenêtre avec du code).")
    print("\n3. Passez à l'étape suivante dans le chat pour savoir quoi faire...")
    
    # Met le script en pause et ouvre l'inspecteur
    page.pause()

    # Le script ne continuera que lorsque vous fermerez l'inspecteur
    print("\n✅ L'inspecteur a été fermé. Fin du script de débogage.")
    browser.close()