import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione per Mobile
st.set_page_config(page_title="Gestione Finanze", layout="centered")

st.title("💰 Il Mio Registro")

# Funzione per gestire il database CSV
def load_data():
    try:
        return pd.read_csv("finanze_personali.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo"])

df = load_data()

# --- SEZIONE INSERIMENTO ---
tab1, tab2 = st.tabs(["📥 Entrate", "📤 Uscite"])

with tab1:
    voce_entrata = st.selectbox("Seleziona Entrata", [
        "Stipendio Brt", 
        "Lezioni Cologno", 
        "Lezioni Melzo", 
        "Altre entrate"
    ])
    importo_e = st.number_input("Importo Entrata (€)", min_value=0.0, step=10.0, key="ent")
    if st.button("Registra Entrata"):
        nuovo = {"Data": datetime.now().strftime("%d-%m-%Y"), "Tipo": "Entrata", "Voce": voce_entrata, "Importo": importo_e}
        df = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
        df.to_csv("finanze_personali.csv", index=False)
        st.success(f"Segnato: {voce_entrata}")
        st.rerun()

with tab2:
    voce_uscita = st.selectbox("Seleziona Uscita", [
        "Risparmi tatuaggio (fissa)",
        "Risparmi personali",
        "Benzina",
        "Spese Deadfall",
        "Spese Noumenia",
        "Spese varie"
    ])
    importo_u = st.number_input("Importo Uscita (€)", min_value=0.0, step=5.0, key="usc")
    if st.button("Registra Uscita"):
        # Le uscite vengono salvate come numeri negativi per il calcolo del saldo
        nuovo = {"Data": datetime.now().strftime("%d-%m-%Y"), "Tipo": "Uscita", "Voce": voce_uscita, "Importo": -importo_u}
        df = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
        df.to_csv("finanze_personali.csv", index=False)
        st.success(f"Segnato: {voce_uscita}")
        st.rerun()

# --- RIEPILOGO STATISTICHE ---
st.divider()
saldo = df["Importo"].sum()
st.metric("Saldo Totale", f"{saldo:.2f} €")

col1, col2 = st.columns(2)
entrate_tot = df[df["Importo"] > 0]["Importo"].sum()
uscite_tot = abs(df[df["Importo"] < 0]["Importo"].sum())

col1.info(f"Tot. Entrate\n\n{entrate_tot:.2f} €")
col2.warning(f"Tot. Uscite\n\n{uscite_tot:.2f} €")

if not df.empty:
    with st.expander("Vedi Storico Movimenti"):
        # Mostriamo i dati invertiti (l'ultimo inserito in alto)
        st.dataframe(df.iloc[::-1], use_container_width=True)
        if st.button("Cancella tutto (Reset)"):
            pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo"]).to_csv("finanze_personali.csv", index=False)
            st.rerun()
