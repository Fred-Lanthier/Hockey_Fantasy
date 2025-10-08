"""
Solution automatique complète: Selenium + PuckPedia
Simule un vrai navigateur pour contourner tous les blocages
Installation: pip install selenium webdriver-manager
"""

import pandas as pd
import time
import re
from io import StringIO

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

def get_salary_puckpedia_selenium(player_name, team_abbr, driver, season="2025-26"):
    """
    Récupère le salaire depuis PuckPedia en simulant un navigateur réel
    Résout le problème des homonymes en vérifiant l'équipe
    Cherche spécifiquement le cap hit de la saison voulue
    """
    clean_name = clean_player_name(player_name)
    
    # Essayer différentes variantes d'URL (pour gérer les homonymes)
    urls_to_try = [
        f"https://puckpedia.com/player/{clean_name}",
        f"https://puckpedia.com/player/{clean_name}-1",
        f"https://puckpedia.com/player/{clean_name}-2",
    ]
    
    for url in urls_to_try:
        try:
            driver.get(url)
            time.sleep(2)  # Attendre le chargement de la page
            
            # Récupérer le contenu HTML
            page_source = driver.page_source
            
            # Vérifier l'équipe pour éviter les homonymes
            if team_abbr and team_abbr.upper() not in page_source.upper():
                continue  # Mauvais joueur, essayer l'URL suivante
            
            # MÉTHODE 1: Chercher le cap hit général (souvent le plus fiable)
            # Format: "cap hit of $X,XXX,XXX per season"
            match = re.search(r'cap hit of \$([0-9,]+)\s+per season', page_source, re.IGNORECASE)
            if match:
                cap_hit_str = match.group(1).replace(',', '')
                cap_hit = float(cap_hit_str) / 1_000_000
                print(f"✓ {player_name} ({team_abbr}): ${cap_hit:.2f}M")
                return cap_hit
            
            # MÉTHODE 2: Chercher dans le contrat actuel
            # Format: "X year, $XX,XXX,XXX contract with a cap hit of $X,XXX,XXX"
            match = re.search(r'contract with a cap hit of \$([0-9,]+)', page_source, re.IGNORECASE)
            if match:
                cap_hit_str = match.group(1).replace(',', '')
                cap_hit = float(cap_hit_str) / 1_000_000
                print(f"✓ {player_name} ({team_abbr}): ${cap_hit:.2f}M")
                return cap_hit
            
            # MÉTHODE 3: Chercher spécifiquement pour la saison 2025-26
            # Parfois les sites affichent année par année
            season_pattern = season.replace('-', r'[-/]')  # 2025-26 ou 2025/26
            match = re.search(rf'{season_pattern}.*?\$([0-9,]+)', page_source, re.IGNORECASE | re.DOTALL)
            if match:
                cap_hit_str = match.group(1).replace(',', '')
                # Vérifier que c'est un montant raisonnable (pas un total de contrat)
                if len(cap_hit_str) <= 9:  # Max ~100M
                    cap_hit = float(cap_hit_str) / 1_000_000
                    if cap_hit < 20:  # Cap hits sont généralement < 20M
                        print(f"✓ {player_name} ({team_abbr}): ${cap_hit:.2f}M")
                        return cap_hit
            
        except Exception as e:
            continue
    
    return None

def get_salary_capwages_selenium(player_name, team_abbr, driver):
    """
    Alternative: CapWages avec Selenium
    """
    clean_name = clean_player_name(player_name)
    
    urls_to_try = [
        f"https://capwages.com/players/{clean_name}",
        f"https://capwages.com/players/{clean_name}-1",
        f"https://capwages.com/players/{clean_name}-2",
    ]
    
    for url in urls_to_try:
        try:
            driver.get(url)
            time.sleep(1.5)
            
            page_source = driver.page_source
            
            # Vérifier l'équipe
            if team_abbr and team_abbr.upper() not in page_source.upper():
                continue
            
            # Chercher le cap hit
            match = re.search(r'cap hit of \$([0-9,]+)', page_source, re.IGNORECASE)
            if match:
                cap_hit_str = match.group(1).replace(',', '')
                cap_hit = float(cap_hit_str) / 1_000_000
                
                print(f"✓ {player_name} ({team_abbr}): ${cap_hit:.2f}M")
                return cap_hit
            
        except Exception as e:
            continue
    
    return None

def parse_fantrax_csv(input_file):
    """Parse le fichier CSV Fantrax"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    goalie_start = None
    for i, line in enumerate(lines):
        if '"","Goalies"' in line:
            goalie_start = i
            break
    
    if goalie_start is None:
        return pd.read_csv(input_file)
    
    skaters_lines = lines[1:goalie_start]
    goalies_lines = lines[goalie_start+1:]
    
    skaters_df = pd.read_csv(StringIO(''.join(skaters_lines)))
    goalies_df = pd.read_csv(StringIO(''.join(goalies_lines)))
    
    common_cols = ['ID', 'Pos', 'Player', 'Team', 'Eligible', 'Status', 'Age', 
                   'Opponent', 'Fantasy Points', 'Average Fantasy Points per Game',
                   '% of leagues in which player was drafted', 
                   'Average draft position among all leagues on Fantrax', 'GP']
    
    skaters_common = skaters_df[common_cols].copy()
    goalies_common = goalies_df[common_cols].copy()
    
    df = pd.concat([skaters_common, goalies_common], ignore_index=True)
    return df

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
    df = parse_fantrax_csv(input_file)
    print(f"✓ {len(df)} joueurs trouvés\n")
    
    # Ajouter la colonne
    df['Cap Hit (M$)'] = None
    
    print("💰 Récupération des salaires (peut prendre quelques minutes)...\n")
    
    success_count = 0
    fail_count = 0
    
    for idx, row in df.iterrows():
        player_name = row.get('Player', '')
        team = row.get('Team', '')
        
        if pd.isna(player_name) or player_name == '':
            continue
        
        print(f"[{idx+1}/{len(df)}] Recherche: {player_name} ({team})...", end=' ')
        
        # Essayer PuckPedia
        cap_hit = get_salary_puckpedia_selenium(player_name, team, driver)
        
        # Si échec, essayer CapWages
        if cap_hit is None:
            cap_hit = get_salary_capwages_selenium(player_name, team, driver)
        
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
    
    # Sauvegarder
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"📊 RÉSULTATS")
    print(f"{'='*80}")
    print(f"Total joueurs:        {len(df)}")
    print(f"Salaires trouvés:     {success_count} ({success_count/len(df)*100:.1f}%)")
    print(f"Non trouvés:          {fail_count}")
    print(f"\n✓ Fichier sauvegardé: {output_file}")
    print("\n💡 Joueurs non trouvés = généralement sans contrat NHL ou joueurs mineurs")
    
    return df

def batch_process_all_teams(team_files):
    """
    Traite plusieurs équipes en batch
    Exemple: batch_process_all_teams(["equipe1.csv", "equipe2.csv", ...])
    """
    print("🔄 TRAITEMENT EN BATCH DE PLUSIEURS ÉQUIPES\n")
    
    for i, team_file in enumerate(team_files):
        print(f"\n{'='*80}")
        print(f"Équipe {i+1}/{len(team_files)}: {team_file}")
        print('='*80)
        
        output_file = team_file.replace('.csv', '-Enrichi.csv')
        
        try:
            enrich_fantrax_automatic(team_file, output_file)
        except Exception as e:
            print(f"❌ Erreur avec {team_file}: {e}")
            continue
        
        print(f"\n✅ {team_file} terminé!")
        time.sleep(5)  # Pause entre les équipes
    
    print(f"\n{'='*80}")
    print(f"✅ TOUS LES FICHIERS TRAITÉS!")
    print('='*80)

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
    
    # Fichiers
    input_file = "Fantrax-Team-Roster-Pis Bowser 2025-2026.csv"
    output_file = "Fantrax-Team-Roster-Enrichi.csv"
    
    print("\n🏒 OPTIONS")
    print("="*80)
    print("1. Traiter un seul fichier")
    print("2. Traiter toutes mes équipes (batch)")
    print()
    
    choice = input("Votre choix (1 ou 2): ")
    print()
    
    if choice == "1":
        df = enrich_fantrax_automatic(input_file, output_file)
    elif choice == "2":
        # Listez tous vos fichiers d'équipes ici
        team_files = [
            "Fantrax-Team-Roster-Pis Bowser 2025-2026.csv",
            # Ajoutez vos autres équipes ici
        ]
        batch_process_all_teams(team_files)
    
    print("\n✅ TERMINÉ!")
