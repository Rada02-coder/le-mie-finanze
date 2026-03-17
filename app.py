import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Pocket Manager Pro", page_icon="💰")

# CSS per far leggere bene i numeri
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DATABASE (SQLite locale) ---
def init_db():
    conn = sqlite3.connect('finance_db.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movimenti 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, tipo TEXT, voce TEXT, importo REAL)''')
    conn.commit()
    conn.close()

def aggiungi_dato(data, tipo, voce, importo):
    conn = sqlite3.connect('finance_db.db')
    c = conn.cursor()
    c.execute("INSERT INTO movimenti (data, tipo, voce, importo) VALUES (?, ?, ?, ?)", 
              (data, tipo, voce, importo))
    conn.commit()
    conn.close()

def carica_dati():
    conn = sqlite3.connect('finance_db.db')
    df = pd.read_sql_query("SELECT * FROM movimenti", conn)
    conn.close()
    return df

def reset_db():
    conn = sqlite3.connect('finance_db.db')
    c = conn.cursor()
    c.execute("DELETE FROM movimenti")
    conn.commit()
    conn.close()

# Inizializza il database all'avvio
init_db()

st.title("💰 Pocket Manager")

# --- INSERIMENTO ---
with st.expander("➕ REGISTRA NUOVA VOCE", expanded=True):
    col_t, col_d = st.columns(2)
    with col_t:
        tipo = st.radio("Cosa registri?", ["Uscita", "Entrata", "Risparmio"], horizontal=True)
    with col_d:
        data_mov = st.date_input("Data", datetime.now()).strftime("%Y-%m-%d")

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

    if st.button("SALVA PER SEMPRE", width='stretch'):
        valore = importo if tipo == "Entrata" else -importo
        aggiungi_dato(data_mov, tipo, voce, valore)
        st.success("Salvato nel database!")
        st.rerun()

# --- DASHBOARD ---
df = carica_dati()

if not df.empty:
    st.divider()
    
    col1, col2 = st.columns(2)
    entrate = df[df['importo'] > 0]['importo'].sum()
    uscite_tot = abs(df[df['importo'] < 0]['importo'].sum())
    
    col1.metric("Tot. Entrate", f"{entrate:.2f}€")
    col2.metric("Tot. Uscite/Risp", f"{uscite_tot:.2f}€")

    # Target Tatuaggio
    tat = abs(df[df['voce'] == 'Tatuaggio']['importo'].sum())
    st.subheader(f"🎯 Tatuaggio: {tat:.2f} / 600€")
    st.progress(min(tat/600, 1.0))

    st.divider()
    with st.expander("🗒️ Storico Movimenti Salva"):
        st.dataframe(df.sort_values("data", ascending=False), width='stretch')
        
        # Tasto per scaricare comunque un backup Excel se serve
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Backup CSV", csv, "finanze.csv", "text/csv")

    if st.button("⚠️ CANCELLA TUTTI I DATI"):
        reset_db()
        st.rerun()
else:
    st.info("Il database è vuoto. Inizia a inserire le tue spese!")
