import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- CONFIGURAZIONE ---
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzXHnZx0YJOEY4ar0UFKxuSe53XXGtTuyZTEF7tNF-WDqm6mYMRolw5TnHcT4D4ikGw/exec"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1aYMaJ9ZmkD4lo0-dgr3TZKhGr9_kTgKpAOq67nt7xs4/edit?gid=0#gid=0"

st.set_page_config(page_title="Pocket Manager", page_icon="💳")

# CSS FORZATO PER LEGGIBILITÀ
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #1e1e1e !important; 
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #333 !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 Pocket Manager")

# 1. CARICAMENTO DATI
def load_data():
    try:
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv&v=" + str(datetime.now().timestamp())
        df = pd.read_csv(csv_url)
        df['Data'] = pd.to_datetime(df['Data'])
        df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])

df = load_data()

# 2. INPUT NUOVA OPERAZIONE
with st.expander("➕ REGISTRA OPERAZIONE", expanded=True):
    tipo = st.radio("Tipo", ["Uscita", "Entrata", "Risparmio"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Entrata":
            voce = st.selectbox("Voce", ["Stipendio Brt", "Lezioni Cologno", "Lezioni Melzo", "Altro"])
        elif tipo == "Risparmio":
            voce = st.selectbox("Voce", ["Tatuaggio", "Pipi", "Personali"])
        else:
            voce = st.selectbox("Voce", ["Benzina", "Deadfall", "Noumenia", "Spese varie"])
    with col2:
        importo = st.number_input("Euro (€)", min_value=0.0, step=1.0)
    
    if st.button("SALVA DATI", use_container_width=True):
        valore = importo if tipo == "Entrata" else -importo
        payload = {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tipo": tipo, "Voce": voce, "Importo": valore, "Metodo": "App", "Nota": ""
        }
        try:
            r = requests.post(WEBAPP_URL, json=payload, timeout=10)
            if r.status_code == 200:
                st.success("Fatto!")
                st.rerun()
            else:
                st.error("Errore Google")
        except:
            st.error("Errore Connessione")

# 3. VISUALIZZAZIONE
if not df.empty:
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"{df[df['Importo']>0]['Importo'].sum():.2f}€")
    c2.metric("Spese", f"{abs(df[df['Tipo']=='Uscita']['Importo'].sum()):.2f}€")
    c3.metric("Risparmi", f"{abs(df[df['Tipo']=='Risparmio']['Importo'].sum()):.2f}€")

    st.subheader("🎯 Tatuaggio")
    risp_tat = abs(df[df['Voce']=='Tatuaggio']['Importo'].sum())
    st.write(f"{risp_tat:.2f} / 600€")
    st.progress(min(risp_tat/600, 1.0))
    
    with st.expander("Storico"):
        st.dataframe(df.sort_values("Data", ascending=False))
