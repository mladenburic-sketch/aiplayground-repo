import pandas as pd
from pathlib import Path
import re
import streamlit as st
from src.bank_names import get_bank_name

def load_and_clean_data(data_folder: str = "data", quarter_pattern: str = "0925"):
    """
    Učitava sve CSV fajlove iz data foldera za izabrani kvartal.
    Vraća jedan DataFrame sa kolonama: 'POZICIJA', 'IZNOS', 'BANKA'.
    
    Args:
        data_folder: Putanja do foldera sa CSV fajlovima (default: "data")
        quarter_pattern: Pattern za kvartal (npr. "0323" za I kvartal 2023, "0925" za III kvartal 2025)
    
    Returns:
        DataFrame sa kolonama 'POZICIJA', 'IZNOS', 'BANKA'
    """
    # Traži CSV fajlove bilo gde u repozitorijumu
    # Filtriraj samo *_bu.csv fajlove (bilans uspjeha), ne *_bs.csv (bilans stanja)
    all_csv = list(Path('.').rglob(f"{quarter_pattern}*.csv"))
    
    # Filtriraj samo _bu.csv fajlove
    csv_files = [f for f in all_csv if f.name.endswith('_bu.csv')]
    
    if not csv_files:
        return pd.DataFrame(columns=['POZICIJA', 'IZNOS', 'BANKA'])
    
        st.write(f"🔍 Debug: Pronađeno {len(csv_files)} CSV fajlova za pattern '{quarter_pattern}*'")
        if len(csv_files) > 0:
            st.write(f"📄 Prvih 5 fajlova: {[str(f) for f in csv_files[:5]]}")
    
    if not csv_files:
        st.warning(f"⚠️ Nema CSV fajlova za izabrani kvartal '{quarter_pattern}' u folderu {data_folder}")
        return pd.DataFrame(columns=['POZICIJA', 'IZNOS', 'BANKA'])
    
    all_dataframes = []
    
    for csv_file in csv_files:
        
        try:
            # Učitaj CSV
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # Proveri da li ima potrebne kolone
            if 'POZICIJA' not in df.columns or 'IZNOS' not in df.columns:
                print(f"Fajl {csv_file.name} nema potrebne kolone. Preskačem.")
                continue
            
            # Izvuci kod banke iz imena fajla
            # Format: 0925ckb_bu.csv -> uzmi "ckb" (prva tri slova posle brojeva)
            file_name = csv_file.stem  # Bez ekstenzije: "0925ckb_bu"
            # Ukloni brojeve i "_bu" deo, uzmi prva tri slova
            bank_code = re.sub(r'^\d+', '', file_name)  # Ukloni brojeve sa početka
            bank_code = bank_code.replace('_bu', '')  # Ukloni "_bu"
            bank_code = bank_code[:3].lower()  # Uzmi prva tri slova i konvertuj u lowercase
            
            # Konvertuj kod u puni naziv banke
            bank_name = get_bank_name(bank_code)
            
            # Dodaj kolonu BANKA sa punim nazivom
            df['BANKA'] = bank_name
            
            # Zadrži samo potrebne kolone
            df = df[['POZICIJA', 'IZNOS', 'BANKA']]
            
            all_dataframes.append(df)
            
        except Exception as e:
            print(f"Greška pri učitavanju fajla {csv_file.name}: {e}")
            continue
    
    if not all_dataframes:
        print("Nijedan CSV fajl nije uspešno učitan.")
        return pd.DataFrame(columns=['POZICIJA', 'IZNOS', 'BANKA'])
    
    # Kombinuj sve DataFrames u jedan
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    return combined_df

def clean_currency_string(value):
    """Ova funkcija osigurava da su podaci brojevi (float), čisteći 'hiljade'."""
    if isinstance(value, (int, float)):
        return float(value)
    if pd.isna(value):
        return 0.0
    
    # Ako je string, mičemo sve osim brojeva i minusa
    value_str = str(value).strip()
    clean_val = re.sub(r'[^\d-]', '', value_str)
    
    try:
        return float(clean_val)
    except ValueError:
        return 0.0

def process_user_dataframe(df):
    """
    Prima tvoj DataFrame sa kolonama: [POZICIJA, IZNOS, BANKA].
    Vraća DataFrame gdje su BANKE redovi, a POZICIJE kolone.
    """
    try:
        # 1. Osiguravamo da su imena kolona tačna (bez razmaka)
        df.columns = [c.strip().upper() for c in df.columns] 
        # Očekujemo: 'POZICIJA', 'IZNOS', 'BANKA'
        
        # 2. Čišćenje iznosa (za svaki slučaj, ako su stringovi)
        if df['IZNOS'].dtype == 'object':
            df['IZNOS'] = df['IZNOS'].apply(clean_currency_string)
            
        # 3. PIVOTIRANJE (Ključni korak!)
        # Pretvaramo "dugačku" tabelu u "široku"
        # index=BANKA (svaki red je jedna banka)
        # columns=POZICIJA (svaka pozicija postaje kolona)
        # values=IZNOS
        # aggfunc='sum' (sabira ako slučajno ima duplih redova, što je sigurnije)
        df_pivoted = df.pivot_table(
            index='BANKA', 
            columns='POZICIJA', 
            values='IZNOS', 
            aggfunc='sum'
        ).reset_index()
        
        # Popunjavamo praznine nulama (ako neka banka nema neku poziciju)
        df_pivoted = df_pivoted.fillna(0)
        
        return df_pivoted

    except Exception as e:
        st.error(f"Greška pri obradi DataFrame-a: {e}")
        return None