import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. Configurazione della pagina
st.set_page_config(page_title="Pocket Manager Cloud", page_icon="💳", layout="centered")

# 2. Collegamento a Google Sheets
# IMPORTANTE: Incolla qui l'URL del tuo foglio tra le virgolette
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/1aYMaJ9ZmkD4lo0-dgr3TZKhGr9_kTgKpAOq67nt7xs4/edit?usp=sharing"

# Creiamo la connessione
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Leggiamo i dati dal foglio Google
        df = conn.read(spreadsheet=URL_FOGLIO)
        # Convertiamo la colonna Data in formato leggibile da Python
        if not df.empty:
            df['Data'] = pd.to_datetime(df['Data'])
        return df
    except:
        # Se il foglio è vuoto o c'è un errore, creiamo una tabella vuota
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])

df = load_data()

# Stile estetico dell'app
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("💳 Pocket Manager (Sync Cloud)")

# 3. INSERIMENTO NUOVI DATI
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
        
        # Uniamo i vecchi dati con il nuovo e aggiorniamo il Foglio Google
        updated_df = pd.concat([df, nuovo_dato], ignore_index=True)
        conn.update(spreadsheet=URL_FOGLIO, data=updated_df)
        
        st.success("Dati salvati correttamente nel cloud!")
        st.rerun()

# 4. BILANCIO E OBIETTIVI
st.subheader(f"📊 Riepilogo {datetime.now().strftime('%B %Y')}")

if not df.empty:
    tot_entrate = df[df["Importo"] > 0]["Importo"].sum()
    tot_uscite = abs(df[df["Importo"] < 0]["Importo"].sum())
    bilancio = tot_entrate - tot_uscite

    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"{tot_entrate:.2f} €")
    c2.metric("Uscite", f"{tot_uscite:.2f} €")
    c3.metric("Bilancio", f"{bilancio:.2f} €")

    st.divider()
    st.subheader("🎯 I Tuoi Risparmi")

    # Filtriamo i risparmi specifici
    tatuaggio = abs(df[df["Voce"] == "Risparmi tatuaggio (fissa)"]["Importo"].sum())
    personali = abs(df[df["Voce"] == "Risparmi personali"]["Importo"].sum())
    pipi = abs(df[df["Voce"] == "Risparmi Pipi"]["Importo"].sum())

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.write(f"🎨 **Tatuaggio**")
        st.write(f"{tatuaggio:.2f} / 600 €")
        st.progress(min(tatuaggio/600, 1.0))
    with col_b:
        st.write(f"🏦 **Personali**")
        st.write(f"{personali:.2f} €")
    with col_c:
        st.write(f"❤️ **Pipi**")
        st.write(f"{pipi:.2f} €")

    # STORICO
    st.divider()
    with st.expander("🗒️ Storico completo dei movimenti"):
        st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
        
        # Grafico a torta delle uscite
        df_uscite = df[df["Importo"] < 0].copy()
        if not df_uscite.empty:
            df_uscite["Importo"] = abs(df_uscite["Importo"])
            fig = px.pie(df_uscite, values='Importo', names='Voce', title='Distribuzione Spese')
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Il foglio è vuoto. Inserisci la tua prima operazione!")
