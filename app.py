import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- CONFIGURAZIONE ---
# 1. Incolla l'URL della Web App (quello che finisce con /exec)
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbygBgw8Jn9iU1EO8MJ0JruuEcYSXJUaYBh2xFvB_0dpWIpkQM6e_z6jEimA7Nz31bMq/exec"
# 2. Incolla l'URL del tuo Foglio Google normale
SHEET_URL = "https://docs.google.com/spreadsheets/d/1aYMaJ9ZmkD4lo0-dgr3TZKhGr9_kTgKpAOq67nt7xs4/edit?gid=0#gid=0"

st.set_page_config(page_title="Pocket Manager", page_icon="💳", layout="centered")

# --- STILE CSS FORZATO (Testo Bianco su Sfondo Scuro) ---
st.markdown("""
    <style>
    /* Box delle metriche */
    [data-testid="stMetric"] {
        background-color: #1e1e1e !important; 
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #333333 !important;
    }
    /* Forza il colore del testo (Etichetta) */
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    /* Forza il colore del numero (Valore) */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    /* Rende l'app più scura e leggibile */
    .main {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 Pocket Manager")

# --- 1. FUNZIONE LETTURA DATI ---
def load_data():
    try:
        ts = str(datetime.now().timestamp())
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv&v=" + ts
        df = pd.read_csv(csv_url)
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'])
            df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])

df = load_data()

# --- 2. INSERIMENTO OPERAZIONI ---
with st.expander("➕ REGISTRA NUOVA OPERAZIONE", expanded=True):
    tipo = st.radio("Cosa vuoi registrare?", ["Uscita", "Entrata", "Risparmio"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Entrata":
            voce = st.selectbox("Voce Entrata", ["Stipendio Brt", "Lezioni Cologno", "Lezioni Melzo", "Altro"])
        elif tipo == "Risparmio":
            voce = st.selectbox("Destinazione", ["Tatuaggio", "Pipi", "Personali"])
        else:
            voce = st.selectbox("Voce Spesa", ["Benzina", "Deadfall", "Noumenia", "Spese varie"])
    
    with col2:
        metodo = st.selectbox("Metodo", ["💳 Carta", "💵 Contanti"])
    
    importo_input = st.number_input("Importo (€)", min_value=0.0, step=1.0)
    nota = st.text_area("Nota (opzionale)")
    
    if st.button("SALVA SUL CLOUD", use_container_width=True):
        valore_finale = importo_input if tipo == "Entrata" else -importo_input
        
        payload = {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tipo": tipo,
            "Voce": voce,
            "Importo": valore_finale,
            "Metodo": metodo,
            "Nota": nota
        }
        
        try:
            res = requests.post(WEBAPP_URL, json=payload, timeout=10)
            if res.status_code == 200:
                st.success("Dato salvato!")
                st.rerun()
            else:
                st.error("Errore Google Script")
        except:
            st.error("Errore di connessione")

# --- 3. DASHBOARD ---
if not df.empty:
    st.divider()
    
    tot_entrate = df[df["Importo"] > 0]["Importo"].sum()
    tot_uscite = abs(df[df["Tipo"] == "Uscita"]["Importo"].sum())
    tot_risparmi = abs(df[df["Tipo"] == "Risparmio"]["Importo"].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"{tot_entrate:.2f} €")
    c2.metric("Spese", f"{tot_uscite:.2f} €")
    c3.metric("Messi via", f"{tot_risparmi:.2f} €")

    st.subheader("🎯 Obiettivi Risparmio")
    
    risp_tatuaggio = abs(df[df["Voce"] == "Tatuaggio"]["Importo"].sum())
    risp_pipi = abs(df[df["Voce"] == "Pipi"]["Importo"].sum())
    risp_personali = abs(df[df["Voce"] == "Personali"]["Importo"].sum())
    
    st.write(f"🎨 **Tatuaggio**: {risp_tatuaggio:.2f} / 600.00 €")
    st.progress(min(risp_tatuaggio/600, 1.0))
    
    col_a, col_b = st.columns(2)
    col_a.metric("❤️ Fondo Pipi", f"{risp_pipi:.2f} €")
    col_b.metric("🏦 Personali", f"{risp_personali:.2f} €")

    with st.expander("🗒️ Storico e Grafico"):
        st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
        
        df_spese = df[df["Tipo"] == "Uscita"].copy()
        if not df_spese.empty:
            df_spese["Importo_Pos"] = abs(df_spese["Importo"])
            fig = px.pie(df_spese, values='Importo_Pos', names='Voce', title='Analisi Spese')
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👋 Inserisci la prima operazione!")
