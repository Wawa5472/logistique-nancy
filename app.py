import streamlit as st
import time
import pandas as pd
import numpy as np
import os

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="Éco-Logistique Nancy | Wassim Abdelli",
    page_icon="🌱",
    layout="wide"
)

# ==========================================
# 2. INITIALISATION DES DONNÉES (Consolidées pour 30 vélos)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Bonjour ! Je suis l'assistant IA Éco-Nancy. Avec nos 30 vélos-cargos en ville, nous optimisons chaque trajet. Comment puis-je vous aider ?"
    })

# Chiffres mis à jour pour une flotte de 30 vélos
if "co2_saved" not in st.session_state:
    st.session_state.co2_saved = 54.2  # Environ 1.8kg par vélo/jour
if "success_rate" not in st.session_state:
    st.session_state.success_rate = 94.1 # Proche de ton objectif de 95%

# ==========================================
# 3. BARRE LATÉRALE (SIDEBAR)
# ==========================================
with st.sidebar:
    # Logo ICN
    st.image("https://www.icn-artem.com/wp-content/uploads/2021/05/logo-icn-business-school.png", use_container_width=True)
    
    st.markdown("---")
    st.title("⚙️ Pilotage de Flotte")
    
    st.subheader("Simulations Temps Réel")
    if st.button("🚨 Alerte : Congestion Stanislas"):
        st.warning("Réaffectation des 30 unités en cours...")
    if st.button("♻️ Recalculer l'impact Carbone"):
        # Gain proportionnel à une flotte plus large
        st.session_state.co2_saved += 4.5 
        st.success("Données consolidées mises à jour.")
        
    st.markdown("---")
    st.markdown("### 👤 Développé par :")
    
    # Gestion de la photo (Sécurisée)
    photo_path = "photo_wassim.jpg" 
    if os.path.exists(photo_path):
        try:
            st.image(photo_path, width=100)
        except Exception:
            st.info("👤 **Wassim Abdelli**")
    else:
        st.warning("Photo non trouvée")
        
    st.info(f"**Wassim Abdelli**")
    st.markdown("🏫 **ICN Business School**")
    st.caption("Projet Hackathon - Phase 2")

# ==========================================
# 4. EN-TÊTE PRINCIPAL
# ==========================================
st.title("🌱 Plateforme de Livraison Décarbonée - Grand Nancy")
st.markdown(f"**Analyse Consolidée :** Déploiement d'une flotte de **30 vélos-cargos** pilotée par IA Générative.")

# ==========================================
# 5. SYSTÈME D'ONGLETS
# ==========================================
tab1, tab2, tab3 = st.tabs(["💬 Interface Client (LLM)", "🗺️ Carte de la Flotte (30 unités)", "📊 Analyse d'Impact"])

# --- ONGLET 1 : CHATBOT ---
with tab1:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ex: Je suis absent, déposez le colis au micro-hub..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            user_input = prompt.lower()
            if any(word in user_input for word in ["suivi", "où"]):
                response = "Grâce à notre maillage de 30 vélos, un livreur est à moins de 500m de la Place Stanislas. Arrivée imminente."
            elif any(word in user_input for word in ["18h", "19h", "tard"]):
                response = "Itinéraire mis à jour. Le volume de notre flotte nous permet cette flexibilité horaire sans surcoût carbone."
                st.session_state.success_rate += 0.1
            elif any(word in user_input for word in ["voisin", "pot", "consigne"]):
                response = "Consigne validée. Cela nous permet de maintenir notre objectif de 95% de succès dès le premier passage."
                st.session_state.co2_saved += 1.5
            else:
                response = "Instruction bien reçue. Elle est transmise en temps réel au vélo-cargo le plus proche."
            
            time.sleep(0.5)
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- ONGLET 2 : CARTE (30 POINTS GPS) ---
with tab2:
    st.subheader("Localisation en temps réel (Nancy Centre)")
    # On génère 30 points pour la carte au lieu de 8
    df_map = pd.DataFrame(
        np.random.randn(30, 2) / [180, 180] + [48.6920, 6.1844],
        columns=['lat', 'lon']
    )
    st.map(df_map, zoom=14)
    st.caption("Visualisation du maillage territorial : 30 unités couvrant les zones ZFE.")

# --- ONGLET 3 : DASHBOARD (CHIFFRES CONSOLIDÉS) ---
with tab3:
    st.subheader("Performance Environnementale & Logistique")
    c1, c2, c3 = st.columns(3)
    # Les chiffres sont plus impressionnants ici
    c1.metric("Succès 1er passage", f"{st.session_state.success_rate:.1f} %", "+4.2% (vs Diesel)")
    c2.metric("CO2 Économisé / Jour", f"{st.session_state.co2_saved:.1f} kg", "+5.4 kg (Mise à jour)")
    c3.metric("Flotte Opérationnelle", "30 / 30", "Capacité Max")
    
    # Graphique montrant la chute drastique des émissions avec 30 vélos
    st.line_chart(pd.DataFrame({
        "Émissions Transport Classique (Camionnettes)": [100, 105, 110, 115],
        "Émissions Solution Wassim (30 Vélos-Cargos)": [100, 70, 40, 15]
    }))

st.markdown("---")
st.caption("© 2026 - Wassim Abdelli - ICN Business School - Projet de Transformation Écologique")
