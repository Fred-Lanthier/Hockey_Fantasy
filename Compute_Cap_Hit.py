import numpy as np
import pandas as pd
import argparse

# --- Données de base (LNH 2025-2026) ---
P_NHL = 95.5  # Plafond LNH
L_NHL = 70.6  # Plancher LNH
M_NHL = 89.4  # Moyenne LNH

def trouver_limites_par_ratio(nouvelle_moyenne, p_base, l_base, m_base):
    """
    Calcule le nouveau plafond (P) et plancher (L) pour une nouvelle_moyenne (M),
    en conservant constants deux ratios :
    1. Le ratio structurel (L/P)
    2. Le ratio de position de la moyenne ((M-L)/(P-L))
    """

    # 1. Calculer les ratios constants de la ligue de base
    if p_base == 0 or (p_base - l_base) == 0:
        print("Erreur: Données de base invalides (division par zéro).")
        return None

    # Ratio Structurel (Plancher / Plafond)
    R_STRUCTURE = l_base / p_base
    
    # Ratio de Position (Où se situe la moyenne)
    R_POSITION = (m_base - l_base) / (p_base - l_base)

    print(f"--- Ratios de la ligue de base ---")
    print(f"Ratio Structurel (L/P) : {R_STRUCTURE:.6f}")
    print(f"Ratio de Position ((M-L)/(P-L)) : {R_POSITION:.6f}")
    print("----------------------------------\n")

    # 2. Résoudre le système d'équations pour le nouveau Plafond (P_nouveau)
    # 
    # M_nouveau = P_nouveau * [ (R_POSITION * (1 - R_STRUCTURE)) + R_STRUCTURE ]
    #
    # Donc, P_nouveau = M_nouveau / [ ... ]
    
    denominateur = (R_POSITION * (1 - R_STRUCTURE)) + R_STRUCTURE
    
    if denominateur == 0:
        print("Erreur: Combinaison de ratios impossible (division par zéro).")
        return None

    p_nouveau = nouvelle_moyenne / denominateur
    
    # 3. Calculer le nouveau Plancher (L_nouveau) en utilisant le Ratio Structurel
    l_nouveau = p_nouveau * R_STRUCTURE
    
    return p_nouveau, l_nouveau

def Compute_average_cap_hit(file):
    """
    Charge les données des équipes depuis un fichier CSV et retourne un DataFrame.
    """
    df = pd.read_csv(file)
    df_total = df[df['Status'].str.startswith('TOTAL')]
    # Remove two first columns
    df_total = df_total.iloc[:, 2:]
    
    # Get the Cap Hit values
    cap_hits = df_total['Cap Hit (M$)']
    
    # Remove min and max, then compute mean
    cap_hits_filtered = cap_hits[(cap_hits != cap_hits.min())] #& (cap_hits != cap_hits.max())]
    average = np.mean(cap_hits_filtered)
    
    return average, df_total

# --- Load file ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrichir un fichier Fantrax avec les salaires NHL.")
    parser.add_argument('--input', type=str, default="Output_Datas/Test_all.csv", help="Chemin du fichier CSV d'entrée Fantrax")
    args = parser.parse_args()

    # --- Utilisation ---
    average, df_total = Compute_average_cap_hit(args.input)
    print(df_total)
    MOYENNE_X = average

    resultat = trouver_limites_par_ratio(MOYENNE_X, P_NHL, L_NHL, M_NHL)

    if resultat:
        nouveau_plafond, nouveau_plancher = resultat
        print(f"Pour une moyenne de {MOYENNE_X:.2f}M$:")
        print(f"  Plafond Salarial (Max) estimé : {nouveau_plafond:.2f} M$")
        print(f"  Plancher Salarial (Min) estimé : {nouveau_plancher:.2f} M$")