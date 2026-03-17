import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Pocket Manager Pro", page_icon="💰", layout="centered")

# CSS per leggibilità e stile tasto elimina
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { color: white !important; }
    .stButton>button { border-radius: 5px; }
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

def elimina_riga(id_riga):
    conn = sqlite3.connect('finance_db.db')
    c = conn.cursor()
    c.execute("DELETE FROM movimenti WHERE id = ?", (id_riga,))
    conn.commit()
    conn.close()

def reset_db():
    conn = sqlite3.connect('finance_db.db')
    c = conn.cursor()
    c.execute("DELETE FROM movimenti")
    c.execute("DELETE FROM sqlite_sequence WHERE name='movimenti'") # Reset contatore ID
    conn.commit()
    conn.close()

# Inizializza il database
init_db()

st.title("💰 Pocket Manager")

# --- 1. INSERIMENTO ---
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

    if st.button("SALVA NEL DATABASE", width='stretch'):
        valore = importo if tipo == "Entrata" else -importo
        aggiungi_dato(data_mov, tipo, voce, valore)
        st.success("Salvato!")
        st.rerun()

# --- 2. DASHBOARD ---
df = carica_dati()

if not df.empty:
    st.divider()
    
    # Metriche principali
    col1, col2 = st.columns(2)
    entrate = df[df['importo'] > 0]['importo'].sum()
    uscite_tot = abs(df[df['importo'] < 0]['importo'].sum())
    
    col1.metric("Tot. Entrate", f"{entrate:.2f}€")
    col2.metric("Tot. Speso/Risparmiato", f"{uscite_tot:.2f}€")

    # Target Tatuaggio
    tat = abs(df[df['voce'] == 'Tatuaggio']['importo'].sum())
    st.subheader(f"🎯 Obiettivo Tatuaggio: {tat:.2f} / 600€")
    st.progress(min(tat/600, 1.0))

    st.divider()

    # --- 3. GESTIONE E CANCELLAZIONE ---
    st.subheader("🗒️ Gestione Movimenti")
    
    # Creiamo una lista con i dati per poterli cancellare riga per riga
    for index, row in df.sort_values("data", ascending=False).iterrows():
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        c1.write(f"📅 {row['data']}")
        c2.write(f"**{row['voce']}**")
        color = "green" if row['importo'] > 0 else "red"
        c3.markdown(f"<span style='color:{color}'>{row['importo']:.2f}€</span>", unsafe_allow_html=True)
        
        # Tasto elimina per la riga specifica
        if c4.button("🗑️", key=f"del_{row['id']}"):
            elimina_riga(row['id'])
            st.rerun()

    st.divider()
    if st.button("🚨 CANCELLA TUTTO IL DATABASE (RESET TOTALE)"):
        reset_db()
        st.rerun()
else:
    st.info("Nessun dato in memoria. Comincia a inserire!")
