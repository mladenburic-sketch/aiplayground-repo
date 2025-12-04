import streamlit as st
import pandas as pd
from src.data_loader import load_and_clean_data
from src.data_loader import process_user_dataframe
from src.calculations import calculate_kpis, get_market_averages, MAPPING
from src.ai_engine import get_gemini_analysis
from src.charts import plot_profit_comparison, plot_income_pie, plot_expense_pie

st.set_page_config(page_title="CG Banking AI", layout="wide")

st.title("🏦 AI Bankarski Savjetnik")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Podešavanja")
    
    api_key = st.text_input("Gemini API Key", type="password", help="Unesi svoj Google Gemini API ključ za AI analizu")

    # Uputstvo za API Key
    with st.expander("📝 Kako dobiti Gemini API Key?"):
        st.markdown("""
        1. **Idi na Google AI Studio:**
           - Otvori: https://aistudio.google.com/
        
        2. **Prijavi se:**
           - Koristi svoj Google nalog
        
        3. **Kreiraj API Key:**
           - Klikni na "Get API Key" ili "Create API Key"
           - Izaberi projekat ili kreiraj novi
           - Kopiraj generisani API ključ
        
        4. **Koristi ključ:**
           - Zalijepi ključ u polje ispod
           - API ključ se neće sačuvati (moraš ga unijeti svaki put)
        
        **Napomena:** API ključ je besplatan za ograničen broj zahtjeva mesečno.
        """)
    
    st.divider()
    
    # IZBOR KVARTALA
    st.header("Izbor Kvartala")
    #st.caption("Format: I kvartal 2023 = 0323, II = 0623, III = 0923, IV = 1223")
    
    # Generisanje opcija za kvartale (2023-2025)
    quarter_options = []
    for year in [21, 22, 23, 24, 25]:
        quarter_options.extend([
            f"I kvartal 20{year} (03{year})",
            f"II kvartal 20{year} (06{year})",
            f"III kvartal 20{year} (09{year})",
            f"IV kvartal 20{year} (12{year})"
        ])
    
    selected_quarter_label = st.selectbox(
        "Izaberi kvartal:",
        quarter_options,
        index=len(quarter_options) - 2  # Default na III kvartal 2025
    )
    
    # Ekstraktuj pattern iz izabranog kvartala
    quarter_pattern = selected_quarter_label.split("(")[1].split(")")[0]
    
    st.divider()

# 1. UČITAVANJE I OBRADA
# Automatsko učitavanje podataka iz data/bu foldera za izabrani kvartal
with st.spinner(f"Učitavam podatke za {selected_quarter_label}..."):
    raw_df = load_and_clean_data(data_folder="data/bu", quarter_pattern=quarter_pattern)

# Inicijalizacija varijabli
df_kpi = None
market_avg = None
selected_bank = None

if raw_df is not None and not raw_df.empty:
    # Pivotiranje
    df_ready = process_user_dataframe(raw_df)
    
    if df_ready is not None:
        # Kalkulacije KPI
        df_kpi = calculate_kpis(df_ready)
        
        # Prosjek tržišta
        market_avg = get_market_averages(df_kpi)
        
        # IZBOR BANKE - u sidebaru
        with st.sidebar:
            st.header("Izbor Banke")
            bank_list = df_kpi['BANKA'].unique()
            selected_bank = st.selectbox("Izaberi banku za analizu:", bank_list, label_visibility="collapsed")

if df_kpi is not None and selected_bank:
    # Izdvajamo red za tu banku
    bank_row = df_kpi[df_kpi['BANKA'] == selected_bank].iloc[0]
    
    # Kreiranje tabova
    tab1, tab2 = st.tabs(["📊 Uporedna analiza", "🤖 AI Preporuke"])
    
    # TAB 1: UPOREDNA ANALIZA
    with tab1:
        # Prikaz ključnih metrika za pojedinačnu banku
        st.subheader(f"📊 {selected_bank}")
        st.caption("💡 Napomena: Svi iznosi su u hiljadama €")
        col1, col2, col3, col4 = st.columns(4)
        
        nd_delta = bank_row['Neto_Dobit_Final'] - market_avg['Neto_Dobit_Final']
        col1.metric("Neto Dobit", f"€ {bank_row['Neto_Dobit_Final']:,.0f}", 
                    delta=f"{nd_delta:,.0f} vs Tržište", delta_color="normal")
        
        cir_delta = bank_row['CIR'] - market_avg['CIR']
        col2.metric("CIR (Cost To Income Ratio)", f"{bank_row['CIR']:.1f}%", 
                    delta=f"{cir_delta:.1f}% vs Tržište", delta_color="inverse")
        
        op_delta = bank_row['Operativni_Prihodi'] - market_avg['Operativni_Prihodi']
        col3.metric("Operativni Prihodi", f"€ {bank_row['Operativni_Prihodi']:,.0f}", delta=f"{op_delta:,.0f} vs Tržište", delta_color="normal")
        op_delta = bank_row['Operativni_Troskovi'] - market_avg['Operativni_Troskovi']
        col4.metric("Operativni Troškovi", f"€ {bank_row['Operativni_Troskovi']:,.0f}", delta=f"{op_delta:,.0f} vs Tržište", delta_color="inverse" )

        # Prikaz prosjeka tržišta
        st.subheader("📈 Prosjek Tržišta")
        col1_avg, col2_avg, col3_avg, col4_avg = st.columns(4)
        col1_avg.metric("Neto Dobit", f"€ {market_avg['Neto_Dobit_Final']:,.0f}")
        col2_avg.metric("CIR (Cost To Income Ratio)", f"{market_avg['CIR']:.1f}%")
        col3_avg.metric("Operativni Prihodi", f"€ {market_avg['Operativni_Prihodi']:,.0f}")
        col4_avg.metric("Operativni Troškovi", f"€ {market_avg['Operativni_Troskovi']:,.0f}")

        st.divider()

        # PIE CHARTS - Struktura prihoda i rashoda
        st.subheader("📊 Struktura Prihoda i Rashoda")
        pie_col1, pie_col2 = st.columns(2)
        
        with pie_col1:
            income_fig = plot_income_pie(bank_row, MAPPING)
            if income_fig:
                st.plotly_chart(income_fig, use_container_width=True)
            else:
                st.info("Nema podataka o prihodima.")
        
        with pie_col2:
            expense_fig = plot_expense_pie(bank_row, MAPPING)
            if expense_fig:
                st.plotly_chart(expense_fig, use_container_width=True)
            else:
                st.info("Nema podataka o rashodima.")
    
    # TAB 2: AI PREPORUKE
    with tab2:
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("🤖 AI Dijagnoza")
            if api_key:
                if st.button("Pokreni AI Analizu"):
                    with st.spinner("Konsultujem AI..."):
                        analysis = get_gemini_analysis(api_key, selected_bank, bank_row, market_avg)
                        st.markdown(analysis)
            else:
                st.warning("Unesi API ključ za tekstualnu analizu.")
                st.markdown("Preporuke bazirane na logici:")
                st.markdown("- Ako je CIR visok -> Smanji Admin troškove.")
                st.markdown("- Ako su Naknade niske -> Povećaj cross-selling.")

        with c2:
            st.subheader("🎛️ Simulator Rezultata")
            st.write("Šta ako primijenimo preporuke?")
            
            # Slajderi povezani sa stvarnim stavkama
            cut_admin = st.slider("Smanjenje Admin Troškova (%)", 0, 30, 0)
            boost_fees = st.slider("Rast Prihoda od Naknada (%)", 0, 30, 0)
            boost_interest = st.slider("Rast Prihoda od Kamata (%)", 0, 30, 0)
            
            # Kalkulacija uticaja (U apsolutnim iznosima)
            # Uzimamo vrijednosti iz MAPPING-a u calculations.py
            current_admin = bank_row[MAPPING['admin_troskovi']] if MAPPING['admin_troskovi'] in bank_row else 0
            current_fees = bank_row[MAPPING['prihodi_naknada']] if MAPPING['prihodi_naknada'] in bank_row else 0
            current_interest = bank_row[MAPPING['prihodi_kamata']] if MAPPING['prihodi_kamata'] in bank_row else 0
            
            savings_admin = current_admin * (cut_admin / 100)
            gain_fees = current_fees * (boost_fees / 100)
            gain_interest = current_interest * (boost_interest / 100)

            # Kalkulacija nove dobiti
            current_profit = bank_row['Neto_Dobit_Final']
            new_profit = current_profit + savings_admin + gain_fees + gain_interest
            
            # Crtanje grafika sa dva bara
            fig = plot_profit_comparison(current_profit, new_profit)
            st.plotly_chart(fig, use_container_width=True)
            
            # Prikaz razlike
            profit_change = new_profit - current_profit
            if profit_change > 0:
                st.success(f"Potencijalna Nova Dobit: € {new_profit:,.0f} (+€ {profit_change:,.0f}) - iznosi u hiljadama")
            elif profit_change < 0:
                st.warning(f"Potencijalna Nova Dobit: € {new_profit:,.0f} (€ {profit_change:,.0f}) - iznosi u hiljadama")
            else:
                st.info(f"Neto Dobit ostaje ista: € {current_profit:,.0f} - iznosi u hiljadama")

elif raw_df is not None and not raw_df.empty:
    st.error("Došlo je do greške u obradi podataka.")
else:
    st.warning("Nema podataka za prikaz. Proveri da li postoje CSV fajlovi u data/bu folderu za poslednji kvartal (0925).")