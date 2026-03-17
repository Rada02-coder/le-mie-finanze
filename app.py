import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# URL della Web App che hai appena creato su Google
WEBAPP_URL = "INCOLLA_QUI_IL_TUO_URL_DI_APPS_SCRIPT"
# URL del foglio normale (per leggere i dati)
SHEET_URL = "INCOLLA_QUI_IL_TUO_URL_DI_GOOGLE_SHEETS"

st.set_page_config(page_title="Pocket Manager", page_icon="💳")

st.title("💳 Pocket Manager")

# --- REGISTRAZIONE ---
with st.expander("➕ REGISTRA NUOVA OPERAZIONE"):
    tipo = st.radio("Tipo", ["Uscita", "Entrata"], horizontal=True)
    voce = st.selectbox("Voce", ["Stipendio Brt", "Lezioni Cologno", "Lezioni Melzo", "Risparmi tatuaggio (fissa)", "Risparmi personali", "Risparmi Pipi", "Benzina", "Varie"])
    metodo = st.selectbox("Metodo", ["💳 Carta", "💵 Contanti"])
    importo = st.number_input("Importo (€)", min_value=0.0, step=1.0)
    nota = st.text_area("Nota")

    if st.button("SALVA SUL CLOUD", use_container_width=True):
        payload = {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tipo": tipo,
            "Voce": voce,
            "Importo": importo if tipo == "Entrata" else -importo,
            "Metodo": metodo,
            "Nota": nota
        }
        res = requests.post(WEBAPP_URL, json=payload)
        if res.status_code == 200:
            st.success("Salvato!")
            st.rerun()
        else:
            st.error("Errore nel salvataggio")

# --- LETTURA DATI ---
st.divider()
try:
    csv_url = SHEET_URL.replace("/edit#gid=", "/export?format=csv&gid=")
    if "/edit" in SHEET_URL and "/export" not in csv_url:
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
        
    df = pd.read_csv(csv_url)
    
    if not df.empty:
        # Calcoli veloci
        entrate = df[df["Importo"] > 0]["Importo"].sum()
        uscite = abs(df[df["Importo"] < 0]["Importo"].sum())
        
        c1, c2 = st.columns(2)
        c1.metric("Entrate", f"{entrate:.2f} €")
        c2.metric("Uscite", f"{uscite:.2f} €")
        
        # Sezione Tatuaggio (600€)
        tatuaggio = abs(df[df["Voce"] == "Risparmi tatuaggio (fissa)"]["Importo"].sum())
        st.write(f"🎨 Tatuaggio: {tatuaggio:.2f} / 600€")
        st.progress(min(tatuaggio/600, 1.0))
        
        with st.expander("🗒️ Storico"):
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
except:
    st.info("Inizia a inserire dati per vedere il riepilogo.")
