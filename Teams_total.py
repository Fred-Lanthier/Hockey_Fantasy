import pandas as pd
from io import StringIO
import os
import sys
import subprocess

def main():
    df_raw = pd.read_csv("Output_Datas/Player_Salaries.csv")


    print(df_raw.head())
    df_merged_unique = df_raw.drop_duplicates(subset='Player', keep='first')
    df_merged_unique.to_csv("Output_Datas/Player_Salaries.csv", index=False)
if __name__ == "__main__":
    main()