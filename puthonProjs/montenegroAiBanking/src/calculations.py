import pandas as pd

# --- MAPIRANJE (PRILAGODI OVO TVOJIM NAZIVIMA POZICIJA) ---
# Lijevo su naše varijable, Desno je TAČAN tekst iz tvoje kolone 'POZICIJA'
MAPPING = {
    'prihodi_kamata': '1. Prihodi od kamata i slicni prihodi',
    'rashodi_kamata': '3. Rashodi od kamata i slicni rashodi',
    'prihodi_naknada': '4. Prihodi od naknada i provizija',
    'rashodi_naknada': '5. Rashodi naknada i provizija',
    'admin_troskovi': '15. Opsti i administrativni troskovi',
    'troskovi_zaposlenih': '13. Troskovi zaposlenih',
    'amortizacija': '14. Troskovi amortizacije',
    'ostali_rashodi': '19. Ostali rashodi',
    'ostali_prihodi': '12. Ostali prihodi',
    'kursne_razlike': '10. Neto gubici/dobici od kursnih razlika',
    'rezervisanja': '18. Troskovi rezervisanja',
    'neto_dobit': '22. NETO PROFIT/GUBITAK (III - 21)' 
}

def calculate_kpis(df):
    """Prima pivotiranu tabelu (redovi=banke) i računa KPI."""
    df_calc = df.copy()
    
    def get_col(mapping_key):
        col_name = MAPPING.get(mapping_key)
        # Provjera da li ta kolona postoji u pivotiranoj tabeli
        if col_name in df_calc.columns:
            return df_calc[col_name]
        return 0.0

    # Kalkulacije
    df_calc['Neto_Kamate'] = get_col('prihodi_kamata') - get_col('rashodi_kamata')
    df_calc['Neto_Naknade'] = get_col('prihodi_naknada') - get_col('rashodi_naknada')
    
    df_calc['Operativni_Prihodi'] = (
        df_calc['Neto_Kamate'] + df_calc['Neto_Naknade'] + 
        get_col('ostali_prihodi') + get_col('kursne_razlike')
    )
    
    df_calc['Operativni_Troskovi'] = (
        get_col('troskovi_zaposlenih') + get_col('amortizacija') + 
        get_col('admin_troskovi') + get_col('ostali_rashodi')
    )
    
    # KPI: Cost to Income Ratio
    df_calc['CIR'] = df_calc.apply(
        lambda row: (row['Operativni_Troskovi'] / row['Operativni_Prihodi'] * 100) 
        if row['Operativni_Prihodi'] > 0 else 0, axis=1
    )
    
    # Dodajemo originalnu Neto Dobit u izlaz
    df_calc['Neto_Dobit_Final'] = get_col('neto_dobit')
    
    return df_calc

def get_market_averages(df_calc, exclude_bank=None):
    if exclude_bank:
        df_filtered = df_calc[df_calc['BANKA'] != exclude_bank]
    else:
        df_filtered = df_calc
    return df_filtered.mean(numeric_only=True)