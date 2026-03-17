import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pocket Manager Locale", page_icon="💰")

# --- STILE ---
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Pocket Manager")
st.info("Nota: I dati sono temporanei. Scarica il file prima di chiudere l'app per non perderli!")

# --- INIZIALIZZAZIONE MEMORIA ---
if 'dati' not in st.session_state:
    st.session_state.dati = pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo"])

# --- INSERIMENTO ---
with st.expander("➕ AGGIUNGI MOVIMENTO", expanded=True):
    t1, t2 = st.columns(2)
    with t1:
        tipo = st.radio("Categoria", ["Uscita", "Entrata", "Risparmio"], horizontal=True)
    with t2:
        data_mov = st.date_input("Data", datetime.now())

    c1, c2 = st.columns(2)
    with c1:
        if tipo == "Entrata":
            voce = st.selectbox("Voce", ["Stipendio", "Lezioni", "Altro"])
        elif tipo == "Risparmio":
            voce = st.selectbox("Voce", ["Tatuaggio", "Pipi", "Personali"])
        else:
            voce = st.selectbox("Voce", ["Benzina", "Deadfall", "Noumenia", "Spese varie"])
    with c2:
        importo = st.number_input("Importo (€)", min_value=0.0, step=1.0)

    if st.button("AGGIUNGI ALLA LISTA", use_container_width=True):
        valore = importo if tipo == "Entrata" else -importo
        nuova_riga = pd.DataFrame([[data_mov, tipo, voce, valore]], columns=["Data", "Tipo", "Voce", "Importo"])
        st.session_state.dati = pd.concat([st.session_state.dati, nuova_riga], ignore_index=True)
        st.success("Aggiunto!")

# --- DASHBOARD ---
if not st.session_state.dati.empty:
    df = st.session_state.dati
    st.divider()
    
    col1, col2 = st.columns(2)
    entrate = df[df['Importo'] > 0]['Importo'].sum()
    uscite = abs(df[df['Importo'] < 0]['Importo'].sum())
    
    col1.metric("Tot. Entrate", f"{entrate:.2f}€")
    col2.metric("Tot. Uscite/Risp", f"{uscite:.2f}€")

    # Target Tatuaggio
    tat = abs(df[df['Voce'] == 'Tatuaggio']['Importo'].sum())
    st.write(f"🎨 **Tatuaggio**: {tat:.2f} / 600€")
    st.progress(min(tat/600, 1.0))

    st.divider()
    st.subheader("🗒️ Riepilogo Attuale")
    st.dataframe(df, use_container_width=True)

    # --- TASTO SCARICA ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 SCARICA REPORT (CSV)",
        data=csv,
        file_name=f"report_spese_{datetime.now().strftime('%d_%m')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    if st.button("🗑️ CANCELLA TUTTO E RICOMINCIA"):
        st.session_state.dati = pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo"])
        st.rerun()
else:
    st.write("Ancora nessun dato inserito.")
