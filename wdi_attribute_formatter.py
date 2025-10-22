import pandas as pd
import numpy as np
import re
import os

#1. GLOBAL MAPPING DICTIONARY 
COUNTRY_MAP = {
    'ITA': 'Italy', 'BRA': 'Brazil', 'URU': 'Uruguay', 'ARG': 'Argentina',
    'ENG': 'England', 'FRA': 'France', 'GER': 'Germany', 'NED': 'Netherlands',
    'POR': 'Portugal', 'SCO': 'Scotland', 'MEX': 'Mexico', 'USA': 'United States',
    'ESP': 'Spain', 'BEL': 'Belgium', 'CHN': 'China PR', 'WAL': 'Wales',
    'COD': 'Congo DR', 'COL': 'Colombia', 'SWE': 'Sweden', 'AUT': 'Austria',

}

#2. CORE HARMONIZATION FUNCTIONS

def harmonize_nationality(df, nat_col_name, new_col_name):
    """Converts 3-letter country codes (FBref/FM) to full names."""
    df[nat_col_name] = df[nat_col_name].str.strip()
    df[new_col_name] = df[nat_col_name].map(COUNTRY_MAP).fillna(df[nat_col_name])
    return df

def convert_value_range(value_str):
    """Converts FM value range (e.g., '€65K - €650K') to a single float midpoint."""
    if pd.isna(value_str) or 'Not for Sale' in value_str:
        return np.nan

    def parse_value(v):
        v = v.strip().replace('€', '').replace('K', 'e3').replace('M', 'e6').replace('€', '')
        try:
            return float(v)
        except ValueError:
            return np.nan

    parts = str(value_str).split('-')
    if len(parts) == 2:
        lower = parse_value(parts[0])
        upper = parse_value(parts[1])
        if not np.isnan(lower) and not np.isnan(upper):
            return (lower + upper) / 2
    elif len(parts) == 1:
        return parse_value(parts[0])
        
    return np.nan

#3. FORMATTING FUNCTION FOR TRANSFERMARKT

def format_transfermarkt(df):
    print("--- Formatting Transfermarkt Data ---")
    
    #1. Create Player Name & Harmonize Position
    df['Player_Name'] = df['player_slug'].str.replace('-', ' ').str.title()
    
    def canonicalize_tm_pos(pos):
        pos = str(pos).lower()
        if 'goalkeeper' in pos: return 'GK'
        elif 'defender' in pos or 'back' in pos: return 'DF'
        elif 'midfield' in pos: return 'MF'
        elif 'attack' in pos or 'winger' in pos or 'forward' in pos: return 'FW'
        return 'Other'

    df['Position_TM'] = df['position'].apply(canonicalize_tm_pos)

    #2. Type Conversion and Renaming
    df['Date_of_Birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
    df['Height_cm'] = df['height'].astype(float)
    
    df = df.rename(columns={'citizenship': 'Nationality_Full', 'value': 'Market_Value_EUR'})
    
    final_cols = ['Player_Name', 'Nationality_Full', 'Date_of_Birth', 'Position_TM',
                  'current_club_name', 'Height_cm', 'Market_Value_EUR']
    
    return df[final_cols]

#4. FORMATTING FUNCTION FOR FM DATA

def format_fm_data(df):
    print("--- Formatting FM Data ---")
    
    # 1. Core Cleaning
    df['Player_Name'] = df['Name'].str.strip()
  
    df['DoB_Str'] = df['DoB'].str.strip().str.split(' ').str[0]
    df['Date_of_Birth'] = pd.to_datetime(df['DoB_Str'], format='%d/%m/%Y', errors='coerce')
    
    df['Height_cm'] = df['Height'].str.replace(' cm', '', regex=False).str.strip().astype(int)

    # 2. Nationality Harmonization
    df = harmonize_nationality(df, 'Nat', 'Nationality_Full')

    # 3. Transfer Value Conversion
    df['Transfer_Value_EUR_FM'] = df['Transfer Value'].apply(convert_value_range)
    
    # 4. Position Canonicalization
    def canonicalize_fm_pos(pos):
        pos = str(pos).upper().strip()
        if 'GK' in pos: return 'GK'
        # D(C), D(RL), etc. -> DF
        elif 'D' in pos: return 'DF'
        # M(C), M(RL) -> MF (excluding AM)
        elif 'M' in pos and 'AM' not in pos: return 'MF'
        # AM(C), ST(C), etc. -> FW
        elif 'AM' in pos or 'ST' in pos: return 'FW'
        return 'Other'

    df['Position_FM'] = df['Position'].apply(canonicalize_fm_pos)

    # Select final columns (FM Ratings)
    fm_rating_cols = ['Dri', 'Fin', 'Han', 'Pac', 'Pas', 'Pen', 'Ref', 'Str', 'Tck']
    
    final_cols = ['Player_Name', 'Nationality_Full', 'Date_of_Birth', 'Position_FM', 
                  'Height_cm', 'Transfer_Value_EUR_FM', 'Club'] + fm_rating_cols

    return df[final_cols]

#5. FORMATTING FUNCTION FOR FBREF DATA

def format_fbref_data(df):
    print("--- Formatting FBRef Data ---")
    
    # 1. Core Name Cleaning
    df['Player_Name'] = df['Player'].str.strip()

    # 2. Nationality Harmonization
    df = harmonize_nationality(df, 'Nation', 'Nationality_Full')

    # 3. Position Canonicalization and Extraction
    def canonicalize_fbref_pos(pos_str):
        matches = re.findall(r"'(\w+)'", str(pos_str))
        if matches:
            primary_pos = matches[0].upper().strip()
            if primary_pos in ['DF']: return 'DF'
            if primary_pos in ['MF']: return 'MF'
            if primary_pos in ['FW']: return 'FW'
            if primary_pos == 'GK': return 'GK'
        return 'Other'
    
    df['Position_FBref'] = df['Pos'].apply(canonicalize_fbref_pos)

    # 4. Select Performance Metrics and Identifier Columns
    def format_fbref_data(df):
        print("--- Formatting FBRef Data ---")
    df = df.rename(columns={
        'MP_Playing': 'Matches_Played', 
        'Min_Playing': 'Minutes_Played',
        'Squad': 'Club_FBref'
    })

    perf_cols = ['Matches_Played', 'Minutes_Played', 'Gls', 'Ast', 'PK', 
                 'G_per_Sh_Standard', 'Cmp_percent_Total', 'TklW_Percent']
    
    final_cols = ['Player_Name', 'Nationality_Full', 'Position_FBref', 'Club_FBref'] + perf_cols
    
    return df[final_cols]

#6. MAIN EXECUTION BLOCK

if __name__ == '__main__':
    
    files = ['Transfermarkt_Dataset.csv', 'FM_Dataset.csv', 'FBRef_Dataset.csv']
    for file in files:
        if not os.path.exists(file):
            print(f"Error: Required file '{file}' not found in the current directory.")
            exit()
            
    tm_df_raw = pd.read_csv('Transfermarkt_Dataset.csv')
    tm_cleaned_df = format_transfermarkt(tm_df_raw)
    tm_cleaned_df.to_csv('Transfermarkt_Cleaned.csv', index=False)
    print(f"\nSuccessfully created Transfermarkt_Cleaned.csv ({len(tm_cleaned_df)} records)")

    fm_df_raw = pd.read_csv('FM_Dataset.csv')
    fm_cleaned_df = format_fm_data(fm_df_raw)
    fm_cleaned_df.to_csv('FM_Cleaned.csv', index=False)
    print(f"\nSuccessfully created FM_Cleaned.csv ({len(fm_cleaned_df)} records)")

    fbref_df_raw = pd.read_csv('FBRef_Dataset.csv')
    fbref_cleaned_df = format_fbref_data(fbref_df_raw)
    fbref_cleaned_df.to_csv('FBRef_Cleaned.csv', index=False)
    print(f"\nSuccessfully created FBRef_Cleaned.csv ({len(fbref_cleaned_df)} records)")

    print("\n--- Phase I: Attribute Formatting Complete ---")
    print("The three new 'Cleaned_Output.csv' files are ready for MapForce.")