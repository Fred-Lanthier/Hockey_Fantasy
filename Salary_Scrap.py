"""
Solution automatique complète: Selenium + PuckPedia
Simule un vrai navigateur pour contourner tous les blocages
Installation: pip install selenium webdriver-manager
"""

import pandas as pd
import time
import re
from io import StringIO
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Configure le navigateur Chrome en mode headless (invisible)"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Mode invisible
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent réaliste
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def clean_player_name(name):
    """Nettoie le nom du joueur pour l'URL"""
    name = name.lower().strip()
    name = name.replace(' ', '-')
    name = name.replace('.', '')
    name = name.replace("'", '')
    return name

def get_salary_puckpedia_selenium(player_name, team_abbr, driver):
    """
    VERSION ROBUSTE - Sans vérification d'équipe
    Si homonymes: prend le salaire maximum
    """
    clean_name = clean_player_name(player_name)
    
    urls_to_try = [
        f"https://puckpedia.com/player/{clean_name}"
    ]
    
    found_salaries = []  # Pour stocker tous les salaires trouvés
    
    for url in urls_to_try:
        try:
            driver.get(url)
            time.sleep(3)  # Augmenté à 3 secondes pour meilleur chargement
            
            page_source = driver.page_source
            
            # Ne plus vérifier l'équipe - juste chercher le salaire
            cap_hit = None
            
            # STRATÉGIE 1: Extraire entre CURRENT CONTRACT et PROFILE
            match = re.search(
                r'CURRENT\s+CONTRACT(.*?)PROFILE',
                page_source,
                re.IGNORECASE | re.DOTALL
            )
            
            if match:
                contract_section = match.group(1)
                dollar_match = re.search(r'\$([0-9,]+)', contract_section)
                
                if dollar_match:
                    cap_hit_str = dollar_match.group(1).replace(',', '')
                    cap_hit = float(cap_hit_str) / 1_000_000
                    
                    if 0.5 < cap_hit < 20:
                        found_salaries.append(cap_hit)
                        continue
            
            # STRATÉGIE 2: Chercher "Cap Hit" suivi du montant
            if cap_hit is None:
                cap_hit_match = re.search(
                    r'Cap\s+Hit[^$]*\$([0-9,]+)',
                    page_source,
                    re.IGNORECASE | re.DOTALL
                )
                
                if cap_hit_match:
                    cap_hit_str = cap_hit_match.group(1).replace(',', '')
                    cap_hit = float(cap_hit_str) / 1_000_000
                    
                    if 0.5 < cap_hit < 20:
                        found_salaries.append(cap_hit)
                        continue
            
            # STRATÉGIE 3: Chercher dans les balises span avec classe "val-lg"
            if cap_hit is None:
                span_match = re.search(
                    r'<span class="val-lg">\$([0-9,]+)</span>',
                    page_source
                )
                
                if span_match:
                    cap_hit_str = span_match.group(1).replace(',', '')
                    cap_hit = float(cap_hit_str) / 1_000_000
                    
                    if 0.775 < cap_hit < 50:
                        found_salaries.append(cap_hit)
            
        except Exception as e:
            continue
    
    # Si on a trouvé des salaires, prendre le maximum (en cas d'homonymes)
    if found_salaries:
        max_salary = max(found_salaries)
        print(f"✓ {player_name}: ${max_salary:.2f}M")
        return max_salary
    
    return 0.775  # Valeur par défaut si non trouvé

def enrich_fantrax_automatic(input_file, output_file):
    """
    Version automatique complète avec Selenium
    Fonctionne pour N'IMPORTE QUEL fichier Fantrax, n'importe quelle année
    """
    print("=" * 80)
    print("🏒 ENRICHISSEMENT AUTOMATIQUE AVEC SELENIUM")
    print("=" * 80)
    print()
    print("📌 Installation du driver Chrome...")
    
    # Setup du navigateur
    driver = setup_driver()
    print("✓ Navigateur Chrome configuré (mode invisible)\n")
    
    # Lire le fichier
    print(f"📂 Lecture: {input_file}")
    df = pd.read_csv(input_file)
    print(f"✓ {len(df)} joueurs trouvés\n")
    
    # Ajouter la colonne
    df['Cap Hit (M$)'] = None
    
    print("💰 Récupération des salaires (peut prendre quelques minutes)...\n")
    
    success_count = 0
    fail_count = 0
    for idx, row in df.iterrows():
        player_name = row.get('Player', '')
        if player_name == "Mack Celebrini":
            player_name = "Macklin Celebrini"
        team = row.get('Team', '')
        
        if pd.isna(player_name) or player_name == '':
            continue
        print(f"[{idx+1}/{len(df)}] Recherche: {player_name} ({team})...", end=' ')
        
        # Essayer PuckPedia
        cap_hit = get_salary_puckpedia_selenium(player_name, team, driver)
        
        if cap_hit:
            df.at[idx, 'Cap Hit (M$)'] = cap_hit
            success_count += 1
        else:
            print(f"✗ {player_name} ({team}): Non trouvé (probablement sans contrat NHL)")
            fail_count += 1
        
        # Petite pause pour ne pas surcharger les serveurs
        time.sleep(1)
    
    # Fermer le navigateur
    driver.quit()
    print("\n✓ Navigateur fermé")
    
    print(f"\n{'='*80}")
    print(f"📊 RÉSULTATS")
    print(f"{'='*80}")
    print(f"Total joueurs:        {len(df)}")
    print(f"Salaires trouvés:     {success_count} ({success_count/len(df)*100:.1f}%)")
    print(f"Non trouvés:          {fail_count}")
    print(f"\n✓ Fichier sauvegardé: {output_file}")
    print("\n💡 Joueurs non trouvés = généralement sans contrat NHL ou joueurs mineurs")
    
    return df

def create_csv_player_salary(df):
    """Créer un CSV en mémoire avec les joueurs et leurs salaires"""
    df = df[['Player', 'Cap Hit (M$)']].copy()
    output_file = "Output_Datas/Player_Salaries.csv"
    df.to_csv(output_file, index=False)

def get_teams_total(df):
    teams = df['Status'].unique()
    teams_total = {}
    
    for team in teams:
        team_df = df[df['Status'] == team]
        total_salary = team_df['Cap Hit (M$)'].sum()
        teams_total[team] = total_salary

    teams_total = dict(sorted(teams_total.items(), key=lambda item: item[1], reverse=True))
    return teams_total

if __name__ == "__main__":
    # Installer les dépendances si nécessaire
    print("📦 Vérification des dépendances...")
    try:
        import selenium
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("\n❌ Dépendances manquantes!")
        print("\nInstallez avec:")
        print("pip install selenium webdriver-manager")
        exit(1)
    
    print("✓ Toutes les dépendances sont installées\n")
    
    # Utiliser argparse pour gérer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Enrichir un fichier Fantrax avec les salaires NHL.")
    parser.add_argument('--input', type=str, default="Datas/Test_all.csv", help="Chemin du fichier CSV d'entrée Fantrax")
    parser.add_argument('--action', type=str, choices=['get', 'totals'], default='totals', help="Action à effectuer: 'get' pour obtenir les salaires, 'totals' pour calculer les totaux par équipe")
    args = parser.parse_args()

    # Fichiers
    input_file = args.input
    output_file = input_file.replace('.csv', '-Enrichi.csv')
    output_file = output_file.replace('Datas/', 'Output_Datas/')

    # Action selon l'argument
    if args.action == 'get':
        start = time.time()
        df = enrich_fantrax_automatic(input_file, output_file)
        create_csv_player_salary(df)
        print(f"\n⏱️  Temps écoulé: {time.time() - start:.1f} secondes\n")
    
    elif args.action == 'totals':
        print("📊 Calcul des totaux par équipe...\n")
        salary_file = "Output_Datas/Player_Salaries.csv"
        df_salary = pd.read_csv(salary_file)
        df_fantrax = pd.read_csv(input_file)

        df = pd.merge(df_fantrax, df_salary, on='Player', how='left')
        df = df[df["Status"] != "FA"]
        df['Cap Hit (M$)'] = df['Cap Hit (M$)'].fillna(0.775)
        teams_total = get_teams_total(df)

        # Classer par Status (dirigeant de l'équipe)
        df = df.sort_values(by='Status', ascending=True)
        df.reset_index(drop=True, inplace=True)
        print(df.head())
        # Afficher les résultats
        for team, total in teams_total.items():
            print(f"Total pour {team}: ${total:.2f}M")

        # Construire un nouveau DataFrame en insérant une ligne total après chaque groupe Status
        rows = []
        for status, group in df.groupby('Status'):
            # ajouter les lignes du groupe
            for _, r in group.iterrows():
                rows.append(r.to_dict())

            # ajouter la ligne total pour ce status
            total_value = teams_total.get(status, 0.0)
            total_row = {
                'Player': "",
                'Team': "",
                'Status': f"TOTAL POUR {status}",
                'Cap Hit (M$)': f"{total_value:.2f}"
            }
            rows.append(total_row)

        df_with_totals = pd.DataFrame(rows, columns=["Player", "Team", "Status", "Cap Hit (M$)"])

        # Sauvegarder le résultat dans un nouveau fichier CSV
        out_csv = input_file.replace('.csv', '-totals.csv')
        out_csv = out_csv.replace('Datas', 'Output_Datas')
        df_with_totals.to_csv(out_csv, index=False)
        print(f"Fichier avec totaux sauvegardé")
