import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# --- CONFIGURAZIONE ---
# 1. Incolla l'URL della Web App (Apps Script) che finisce con /exec
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbx_wmDS8GV77xx9CQUj8kAz2Z7BXq_wTZVrkjRoJXLc_uZuqFl5WtEuZoYW5qqoYtJi/exec"
# 2. Incolla l'URL del tuo Foglio Google normale
SHEET_URL = "https://docs.google.com/spreadsheets/d/1aYMaJ9ZmkD4lo0-dgr3TZKhGr9_kTgKpAOq67nt7xs4/edit?gid=0#gid=0"

st.set_page_config(page_title="Pocket Manager", page_icon="💳", layout="centered")

# Stile CSS per rendere l'app più bella
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 Pocket Manager")

# --- 1. FUNZIONE LETTURA DATI ---
@st.cache_data(ttl=10) # Aggiorna i dati ogni 10 secondi
def load_data():
    try:
        # Trasformiamo l'URL per scaricare il CSV direttamente
        csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
        df = pd.read_csv(csv_url)
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'])
            df['Importo'] = pd.to_numeric(df['Importo'])
        return df
    except:
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])

df = load_data()

# --- 2. INSERIMENTO OPERAZIONI ---
with st.expander("➕ REGISTRA NUOVA OPERAZIONE", expanded=False):
    tipo = st.radio("Cosa vuoi registrare?", ["Uscita", "Entrata"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if tipo == "Entrata":
            voce = st.selectbox("Voce", ["Stipendio Brt", "Lezioni Cologno", "Lezioni Melzo", "Altre entrate"])
        else:
            voce = st.selectbox("Voce", [
                "Risparmi tatuaggio (fissa)", 
                "Risparmi personali", 
                "Risparmi Pipi",
                "Benzina", 
                "Spese Deadfall", 
                "Spese Noumenia", 
                "Spese varie"
            ])
    with col2:
        metodo = st.selectbox("Metodo", ["💳 Carta", "💵 Contanti"])
    
    importo_input = st.number_input("Importo (€)", min_value=0.0, step=1.0)
    nota = st.text_area("Nota (opzionale)")
    
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
            res = requests.post(WEBAPP_URL, json=payload)
            if res.status_code == 200:
                st.success("Dato inviato con successo!")
                st.cache_data.clear() # Svuota la cache per vedere subito il dato
                st.rerun()
            else:
                st.error("Errore nell'invio a Google Sheets.")
        except:
            st.error("Errore di connessione. Controlla l'URL della Web App.")

# --- 3. DASHBOARD E RISPARMI ---
if not df.empty:
    st.subheader(f"📊 Riepilogo {datetime.now().strftime('%B %Y')}")
    
    entrate = df[df["Importo"] > 0]["Importo"].sum()
    uscite = abs(df[df["Importo"] < 0]["Importo"].sum())
    bilancio = entrate - uscite
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"{entrate:.2f} €")
    c2.metric("Uscite", f"{uscite:.2f} €")
    c3.metric("Bilancio", f"{bilancio:.2f} €")

    # SEZIONE RISPARMI (Corretta con abs() per far salire i totali)
    st.divider()
    st.subheader("🎯 I Tuoi Risparmi")
    
    # Calcoliamo i totali dei risparmi indipendentemente dal segno
    tot_tatuaggio = abs(df[df["Voce"] == "Risparmi tatuaggio (fissa)"]["Importo"].sum())
    tot_pipi = abs(df[df["Voce"] == "Risparmi Pipi"]["Importo"].sum())
    tot_personali = abs(df[df["Voce"] == "Risparmi personali"]["Importo"].sum())
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.write(f"🎨 **Tatuaggio**")
        st.write(f"{tot_tatuaggio:.2f} / 600€")
        st.progress(min(tot_tatuaggio/600, 1.0))
    with col_b:
        st.write(f"🏦 **Personali**")
        st.write(f"{tot_personali:.2f} €")
    with col_c:
        st.write(f"❤️ **Pipi**")
        st.write(f"{tot_pipi:.2f} €")

    # STORICO E GRAFICO
    st.divider()
    with st.expander("🗒️ Storico Movimenti"):
        st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
        
        df_uscite = df[df["Importo"] < 0].copy()
        if not df_uscite.empty:
            df_uscite["Importo"] = abs(df_uscite["Importo"])
            fig = px.pie(df_uscite, values='Importo', names='Voce', title='Dove spendi di più')
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Benvenuto! Registra la tua prima operazione per attivare i grafici.")
