import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. Configurazione Pagina
st.set_page_config(page_title="Pocket Manager", page_icon="💳", layout="centered")

# 2. Stile Grafico (CSS)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 3. Funzione per caricare/salvare i dati
def load_data():
    try:
        df = pd.read_csv("finanze_v2.csv")
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["Data", "Tipo", "Voce", "Importo", "Metodo", "Nota"])

df = load_data()

st.title("💳 Pocket Manager")

# 4. SEZIONE INSERIMENTO
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
    
    if st.button("SALVA MOVIMENTO", use_container_width=True):
        nuovo = {
            "Data": datetime.now(),
            "Tipo": tipo,
            "Voce": voce,
            "Importo": import_val if tipo == "Entrata" else -import_val,
            "Metodo": metodo,
            "Nota": nota
        }
        df = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
        df.to_csv("finanze_v2.csv", index=False)
        st.success("Registrato con successo!")
        st.rerun()

# 5. RIEPILOGO MENSILE
st.subheader(f"📊 Bilancio {datetime.now().strftime('%B %Y')}")

# Calcoli con protezione se i dati sono vuoti
if not df.empty:
    tot_entrate = df[df["Importo"] > 0]["Importo"].sum()
    tot_uscite = abs(df[df["Importo"] < 0]["Importo"].sum())
    bilancio = tot_entrate - tot_uscite
else:
    tot_entrate = tot_uscite = bilancio = 0.0

c1, c2, c3 = st.columns(3)
c1.metric("Entrate", f"{tot_entrate:.2f} €")
c2.metric("Uscite", f"{tot_uscite:.2f} €", delta=f"-{tot_uscite:.2f}" if tot_uscite > 0 else None, delta_color="inverse")
c3.metric("Bilancio", f"{bilancio:.2f} €")

# 6. SEZIONE RISPARMI
st.divider()
st.subheader("🎯 Obiettivi e Risparmi")

tatuaggio = abs(df[df["Voce"] == "Risparmi tatuaggio (fissa)"]["Importo"].sum()) if not df.empty else 0
personali = abs(df[df["Voce"] == "Risparmi personali"]["Importo"].sum()) if not df.empty else 0
pipi = abs(df[df["Voce"] == "Risparmi Pipi"]["Importo"].sum()) if not df.empty else 0

col_t, col_p, col_pp = st.columns(3)

with col_t:
    st.write(f"🎨 **Tatuaggio**")
    st.write(f"{tatuaggio:.2f} / 600 €")
    st.progress(min(tatuaggio/600, 1.0))

with col_p:
    st.write(f"🏦 **Personali**")
    st.write(f"{personali:.2f} €")
    st.caption("Senza limite")

with col_pp:
    st.write(f"❤️ **Pipi**")
    st.write(f"{pipi:.2f} €")

# 7. STORICO E GRAFICI
st.divider()
if not df.empty:
    with st.expander("🗒️ Storico Movimenti e Note"):
        st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)
        
        df_uscite = df[df["Importo"] < 0].copy()
        if not df_uscite.empty:
            df_uscite["Importo"] = abs(df_uscite["Importo"])
            fig = px.pie(df_uscite, values='Importo', names='Voce', title='Dove finiscono i tuoi soldi?')
            st.plotly_chart(fig, use_container_width=True)
