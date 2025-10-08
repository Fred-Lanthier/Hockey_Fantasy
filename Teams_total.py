import pandas as pd
from io import StringIO
import os
import sys
import subprocess

def get_teams_total(df):
    teams = df['Status'].unique()
    teams_total = {}
    
    for team in teams:
        team_df = df[df['Status'] == team]
        total_salary = team_df['Cap Hit (M$)'].sum()
        teams_total[team] = total_salary
    
    return teams_total


def main():
    csv_file = "Output_Datas/Test_all-Enrichi.csv"
    df = pd.read_csv(csv_file)
    df = df[["Player", "Team", "Status", "Cap Hit (M$)"]]
    teams_total = get_teams_total(df)
    teams_total = dict(sorted(teams_total.items(), key=lambda item: item[1], reverse=True))

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
    out_csv = "Output_Datas/Test_all-Enrichi-with_totals.csv"
    df_with_totals.to_csv(out_csv, index=False)
    print(f"Fichier avec totaux sauvegardé")

if __name__ == "__main__":
    main()