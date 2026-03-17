import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. Configurazione Pagina
st.set_page_config(page_title="Pocket Manager Cloud", page_icon="💳", layout="centered")

# 2. Collegamento a Google Sheets
# Incolla qui il tuo URL
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/1aYMaJ9ZmkD4lo0-dgr3TZKhGr9_kTgKpAOq67nt7xs4/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Usiamo ttl=0 per non avere dati vecchi in memoria (cache)
        df = conn.read(spreadsheet=URL_FOGLIO, ttl=0)
        if df.empty:
            return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])
        return df
    except:
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])

df = load_data()

st.title("💳 Pocket Manager (Sync Cloud)")

# 3. INSERIMENTO NUOVI DATI
with st.expander("➕ REGISTRA NUOVA OPERAZIONE", expanded=False):
    tipo = st.radio("Cosa vuoi registrare?", ["Uscita", "Entrata"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Entrata":
            voce = st.selectbox("Voce", ["Stipendio Brt", "Lezioni Cologno", "Lezioni Melzo", "Altre entrate"])
        else:
            voce = st.selectbox("Voce", ["Risparmi tatuaggio (fissa)", "Risparmi personali", "Risparmi Pipi", "Benzina", "Spese Deadfall", "Spese Noumenia", "Spese varie"])
    
    with col2:
        metodo = st.selectbox("Metodo", ["💳 Carta", "💵 Contanti"])
    
    import_val = st.number_input("Importo (€)", min_value=0.0, step=1.0)
    nota = st.text_area("Nota (opzionale)")
    
    if st.button("SALVA SUL CLOUD", use_container_width=True):
        nuovo_dato = pd.DataFrame([{
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tipo": tipo,
            "Voce": voce,
            "Importo": import_val if tipo == "Entrata" else -import_val,
            "Metodo": metodo,
            "Nota": nota
        }])
        
        # AGGIORNAMENTO: Usiamo il comando .create invece di .update per i link pubblici
        updated_df = pd.concat([df, nuovo_dato], ignore_index=True)
        
        try:
            conn.update(spreadsheet=URL_FOGLIO, data=updated_df)
            st.success("Dati salvati correttamente!")
            st.rerun()
        except Exception as e:
            st.error(f"Errore di scrittura: {e}")
            st.info("Assicurati che il foglio sia condiviso come EDITOR con 'Chiunque abbia il link'.")

# --- PARTE GRAFICA (Sempre uguale) ---
if not df.empty:
    st.subheader(f"📊 Bilancio Mensile")
    # Assicuriamoci che Importo sia numerico
    df["Importo"] = pd.to_numeric(df["Importo"])
    
    tot_entrate = df[df["Importo"] > 0]["Importo"].sum()
    tot_uscite = abs(df
