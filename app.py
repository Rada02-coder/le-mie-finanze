import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURAZIONE ---
# 1. Incolla l'URL della Web App (Apps Script) che finisce con /exec
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbx_wmDS8GV77xx9CQUj8kAz2Z7BXq_wTZVrkjRoJXLc_uZuqFl5WtEuZoYW5qqoYtJi/exec"
# 2. Incolla l'URL del tuo Foglio Google normale
SHEET_URL = "https://docs.google.com/spreadsheets/d/1aYMaJ9ZmkD4lo0-dgr3TZKhGr9_kTgKpAOq67nt7xs4/edit?gid=0#gid=0"

st.set_page_config(page_title="Pocket Manager", page_icon="💳", layout="centered")

# Stile pulito
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 Pocket Manager")

# --- 1. LETTURA DATI (Forziamo l'aggiornamento) ---
def load_data():
    try:
        # Aggiungiamo un timestamp per bypassare la cache di Google
        ts = str(datetime.now().timestamp())
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv&cachebust=" + ts
        df = pd.read_csv(csv_url)
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'])
            # Pulizia numeri: togliamo spazi o simboli strani
            df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])

df = load_data()

# --- 2. INSERIMENTO OPERAZIONI ---
with st.expander("➕ REGISTRA NUOVA OPERAZIONE"):
    tipo = st.radio("Cosa vuoi registrare?", ["Uscita", "Entrata"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Entrata":
            voce = st.selectbox("Voce", ["Stipendio Brt", "Lezioni Cologno", "Lezioni Melzo", "Altre entrate"])
        else:
            voce = st.selectbox("Voce", ["Risparmi tatuaggio (fissa)", "Risparmi personali", "Risparmi Pipi", "Benzina", "Spese Deadfall", "Spese varie"])
    with col2:
        metodo = st.selectbox("Metodo", ["💳 Carta", "💵 Contanti"])
    
    importo_input = st.number_input("Importo (€)", min_value=0.0, step=1.0)
    nota = st.text_area("Nota")
    
    if st.button("SALVA SUL CLOUD", use_container_width=True):
        payload = {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tipo": tipo,
            "Voce": voce,
            "Importo": importo_input if tipo == "Entrata" else -importo_input,
            "Metodo": metodo,
            "Nota": nota
        }
        try:
            res = requests.post(WEBAPP_URL, json=payload, timeout=10)
            if res.status_code == 200:
                st.success("Salvato correttamente!")
                st.rerun()
            else:
                st.error("Errore Google Script")
        except:
            st.error("Errore di connessione")

# --- 3. DASHBOARD E RISPARMI ---
if not df.empty:
    st.subheader("📊 Riepilogo Mensile")
    
    entrate = df[df["Importo"] > 0]["Importo"].sum()
    uscite = abs(df[df["Importo"] < 0]["Importo"].sum())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"{entrate:.2f} €")
    c2.metric("Uscite", f"{uscite:.2f} €")
    c3.metric("Bilancio", f"{(entrate-uscite):.2f} €")

    st.divider()
    st.subheader("🎯 I Tuoi Risparmi")
    
    # Calcolo con gestione nomi identica al menu
    tot_tatuaggio = abs(df[df["Voce"] == "Risparmi tatuaggio (fissa)"]["Importo"].sum())
    tot_pipi = abs(df[df["Voce"] == "Risparmi Pipi"]["Importo"].sum())
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**🎨 Tatuaggio**")
        # Mostriamo il numero pulito per evitare l'errore f-string di prima
        valore_testo = str(round(tot_tatuaggio, 2)) + " / 600€"
        st.write(valore_testo)
        st.progress(min(tot_tatuaggio/600, 1.0))
    with col_b:
        st.write("**❤️ Pipi**")
        st.write(str(round(tot_pipi, 2)) + " €")

    with st.expander("🗒️ Storico completo"):
        st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
else:
    st.info("Nessun dato trovato. Inserisci la prima operazione!")
