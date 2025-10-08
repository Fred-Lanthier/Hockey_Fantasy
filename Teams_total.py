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
    csv_file = "Output_Datas/Test_solo-Enrichi.csv"
    df = pd.read_csv(csv_file)
    
    df = df[['Status', 'Cap Hit (M$)']]
    teams_total = get_teams_total(df)

    # Afficher les résultats
    for team, total in teams_total.items():
        print(f"Total pour {team}: ${total:.2f}M")

if __name__ == "__main__":
    main()