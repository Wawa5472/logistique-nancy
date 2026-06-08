import streamlit as st
import time
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(
    page_title="Éco-Logistique Nancy | Wassim Abdelli",
    page_icon="🌱",
    layout="wide"
)

# ==========================================
# 2. THÈME CSS VERT / ÉCO
# ==========================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%);
        padding: 22px 30px;
        border-radius: 14px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 4px 18px rgba(46, 125, 50, 0.35);
    }
    .stButton > button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background-color: #1B5E20 !important;
        box-shadow: 0 3px 12px rgba(46,125,50,0.45) !important;
    }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
    .tmc-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    }
    .tmc-incumbent { border-left: 6px solid #E53935; }
    .tmc-niche { border-left: 6px solid #43A047; }
    .tmc-goal {
        border-top: 5px solid #FB8C00;
        background: linear-gradient(135deg, #FFF8E1, #FFF3E0);
        text-align: center;
    }
    .tmc-landscape {
        background: linear-gradient(135deg, #E3F2FD, #E8EAF6);
        border-top: 5px solid #3949AB;
    }
    .badge {
        display: inline-block;
        padding: 3px 11px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin: 3px 2px;
    }
    .badge-red   { background: #FFEBEE; color: #C62828; }
    .badge-green { background: #E8F5E9; color: #1B5E20; }
    .badge-blue  { background: #E3F2FD; color: #0D47A1; }
    .badge-orange{ background: #FFF3E0; color: #E65100; }
    .prompt-card {
        background: #F8F9FA;
        border: 1px solid #DEE2E6;
        border-left: 5px solid #43A047;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        white-space: pre-wrap;
    }
    .feasibility-positive { border-top: 4px solid #43A047; background: white; border-radius: 10px; padding: 18px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
    .feasibility-warning  { border-top: 4px solid #FB8C00; background: white; border-radius: 10px; padding: 18px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
    .feasibility-challenge{ border-top: 4px solid #E53935; background: white; border-radius: 10px; padding: 18px; margin: 10px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
    .footer {
        background: linear-gradient(135deg, #1B5E20, #2E7D32);
        color: white;
        padding: 16px 30px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1B5E20;
        border-bottom: 3px solid #43A047;
        padding-bottom: 8px;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INITIALISATION DES ÉTATS CONSOLIDÉS
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "🌱 Bonjour ! Je suis **EcoBot**, l'assistant IA de la plateforme Éco-Nancy.\n\n"
            "Notre flotte de **30 vélos-cargos électriques** couvre le centre-ville et la ZFE.\n\n"
            "Je peux vous aider à :\n"
            "- 📦 Suivre votre colis en temps réel\n"
            "- 🕒 Modifier un créneau de livraison\n"
            "- 🌍 Connaître notre impact environnemental\n"
            "- 📍 Identifier les zones couvertes\n\n"
            "Comment puis-je vous aider ?"
        )
    }]

if "co2_saved"         not in st.session_state: st.session_state.co2_saved         = 54.2
if "success_rate"      not in st.session_state: st.session_state.success_rate      = 94.1
if "livraisons_jour"   not in st.session_state: st.session_state.livraisons_jour   = 127

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.image(
        "https://www.icn-artem.com/wp-content/uploads/2021/05/logo-icn-business-school.png",
        use_container_width=True
    )
    st.markdown("---")
    st.markdown("### ⚙️ Pilotage de Flotte")

    if st.button("🚨 Alerte Congestion Stanislas", use_container_width=True):
        st.warning("⚡ IA a réaffecté les unités — itinéraire alternatif via les micro-hubs (Carnot).")

    if st.button("♻️ Recalculer l'impact Carbone", use_container_width=True):
        st.session_state.co2_saved += 4.5
        st.success(f"✅ Données consolidées : **{st.session_state.co2_saved:.1f} kg** de CO₂ économisés.")

    st.markdown("---")
    flotte_active = 30
    st.markdown(f"### 🚲 Flotte : {flotte_active}/30 actifs")
    st.progress(flotte_active / 30)

    st.markdown("---")
    st.markdown("### 👤 Développé par :")

    photo_path = "photo_wassim.jpg"
    if os.path.exists(photo_path):
        try:
            st.image(photo_path, width=100)
        except Exception:
            pass

    st.info("**Wassim Abdelli**")
    st.markdown("🏫 **ICN Business School**")
    st.caption("PGE 2: Transformation Numérique et Écologique - Phase 2")

# ==========================================
# 5. EN-TÊTE
# ==========================================
st.markdown("""
<div class="main-header">
  <h1 style="margin:0;font-size:26px;">🌱 Plateforme de Livraison Décarbonée — Grand Nancy</h1>
  <p style="margin:8px 0 0 0;opacity:.9;font-size:14px;">
    Analyse Consolidée : Flotte de <strong>30 vélos-cargos</strong> pilotée par IA Générative.
  </p>
</div>
""", unsafe_allow_html=True)

# KPIs rapides
c1, c2, c3, c4 = st.columns(4)
c1.metric("🚲 Flotte opérationnelle", "30 / 30", "100 % actif")
c2.metric("✅ Succès 1er passage",     f"{st.session_state.success_rate:.1f} %", "Objectif : 95%")
c3.metric("🌿 CO₂ économisé/jour",    f"{st.session_state.co2_saved:.1f} kg",   "vs diesel")
c4.metric("📦 Livraisons aujourd'hui", str(st.session_state.livraisons_jour),    "+12 vs hier")

st.markdown("---")

# ==========================================
# 6. ONGLETS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Interface Client (IA)",
    "🗺️ Carte de la Flotte",
    "📊 Analyse d'Impact",
    "🔄 TMC Interactif",
    "🧪 Faisabilité & Prompts IA",
])

# ─────────────────────────────────────────
# ONGLET 1 — CHATBOT ENRICHI (Sans API)
# ─────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">💬 EcoBot — Assistant Livraison Décarbonée</div>', unsafe_allow_html=True)

    col_chat, col_aide = st.columns([2, 1])

    with col_aide:
        st.markdown("""
        <div style="background:#E8F5E9;border-radius:10px;padding:15px;">
        <b>💡 Exemples de requêtes traitées par l'IA centrale :</b><br><br>
        🔍 <i>"Où est mon colis ?"</i><br>
        🕒 <i>"Je suis absent à 18h"</i><br>
        🏠 <i>"Déposez chez le voisin"</i><br>
        🌱 <i>"Quel est l'impact de ce trajet ?"</i>
        </div>
        """, unsafe_allow_html=True)

    with col_chat:
        chat_container = st.container(height=430)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ex: Je suis absent cet après-midi, déposez au micro-hub..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            ui = prompt.lower()

            # Moteur de réponses contextuelles (IA simulée par mots-clés)
            if any(w in ui for w in ["suivi", "où", "colis", "livraison"]):
                response = (
                    "📍 **Suivi de livraison optimisé :**\n\n"
                    f"Grâce à notre flotte consolidée de 30 vélos, l'unité **#{np.random.randint(1,31):02d}** est à "
                    f"moins de 500m de la Place Stanislas.\n\n"
                    "⏱️ **Arrivée imminente :** Je vous confirme mon passage 15 minutes avant l'arrivée."
                )

            elif any(w in ui for w in ["absent", "18h", "19h", "soir", "tard"]):
                response = (
                    "🕒 **Modification d'itinéraire :**\n\n"
                    "L'IA centrale a mis à jour la tournée en temps réel. Le volume de notre flotte nous "
                    "permet d'offrir cette flexibilité horaire **sans aucun surcoût carbone**."
                )
                st.session_state.success_rate = min(98.0, st.session_state.success_rate + 0.1)

            elif any(w in ui for w in ["voisin", "consigne", "relais", "hub"]):
                response = (
                    "✅ **Consigne validée :**\n\n"
                    "Instruction transmise. Cela nous aide grandement à maintenir notre objectif de "
                    "**95% de succès de livraison** dès le premier passage. "
                    "Vos colis consolidés au dernier moment réduisent l'impact."
                )
                st.session_state.co2_saved += 1.5

            elif any(w in ui for w in ["co2", "carbone", "écolo", "impact"]):
                response = (
                    "🌍 **Impact de notre solution :**\n\n"
                    "Comparé à un système dépendant des énergies fossiles, un vélo cargo affiche "
                    "**zéro émission directe**. Nous surveillons aussi l'usure de nos batteries en temps réel "
                    "pour garantir la durabilité de la flotte."
                )

            else:
                response = (
                    "✅ **Instruction reçue :**\n\n"
                    "L'information a été transmise au cerveau central de notre IA qui consolide les "
                    "tournées de nos 30 vélos en ville."
                )

            time.sleep(0.4)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# ─────────────────────────────────────────
# ONGLET 2 — CARTE
# ─────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">🗺️ Localisation Temps Réel — 30 Vélos-Cargos</div>', unsafe_allow_html=True)
    
    np.random.seed(42)
    # Simulation des 30 unités dans la ZFE de Nancy
    df_map = pd.DataFrame(
        np.random.randn(30, 2) / [180, 180] + [48.6920, 6.1844],
        columns=['lat', 'lon']
    )
    st.map(df_map, zoom=14, color="#2E7D32")
    st.caption("Visualisation du maillage territorial : 30 unités couvrant les zones ZFE du Grand Nancy.")

# ─────────────────────────────────────────
# ONGLET 3 — DASHBOARD (D'IMPACT)
# ─────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">📊 Analyse d\'Impact — Performance Écologique</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Graphique des émissions (chute avec 30 vélos)
        semaines = ["S-4", "S-3", "S-2", "S-1", "S-En cours"]
        fig_em = go.Figure()
        fig_em.add_trace(go.Scatter(
            x=semaines, y=[100, 105, 110, 115, 120],
            mode="lines+markers", name="🚛 Camionnettes (Système dominant)",
            line=dict(color="#E53935", width=3)
        ))
        fig_em.add_trace(go.Scatter(
            x=semaines, y=[100, 70, 40, 20, 15],
            mode="lines+markers", name="🚲 Flotte 30 vélos-cargos",
            line=dict(color="#43A047", width=3),
            fill="tozeroy", fillcolor="rgba(67,160,71,0.1)"
        ))
        fig_em.update_layout(
            title="📉 Réduction des émissions de CO₂",
            plot_bgcolor="white", height=320,
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_em, use_container_width=True)

    with col_b:
        # Taux de succès
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=st.session_state.success_rate,
            delta={"reference": 95.0, "suffix": "%"},
            title={"text": "Succès au 1er passage (Cible: 95%)", "font": {"size": 15}},
            gauge={
                "axis": {"range": [80, 100]},
                "bar":  {"color": "#2E7D32"},
                "steps": [
                    {"range": [80, 90], "color": "#FFEBEE"},
                    {"range": [90, 95], "color": "#FFF9C4"},
                    {"range": [95, 100], "color": "#E8F5E9"},
                ],
                "threshold": {"line": {"color": "orange", "width": 4}, "thickness": 0.75, "value": 95}
            },
            number={"suffix": "%"}
        ))
        fig_gauge.update_layout(height=320)
        st.plotly_chart(fig_gauge, use_container_width=True)

# ─────────────────────────────────────────
# ONGLET 4 — TMC INTERACTIF (Données Réelles du Projet)
# ─────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">🔄 Transition Model Canvas — Analyse Stratégique</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="tmc-card tmc-goal">
        <h3 style="color:#E65100;margin:0 0 10px 0;">🎯 OBJECTIF DE TRANSITION (SMART)</h3>
        <h4 style="color:#333;margin:0;">
          Réduire de <strong>30% l'empreinte carbone</strong> des livraisons du dernier kilomètre dans le centre-ville de Nancy d'ici 2027, 
          en remplaçant <strong>60% des trajets de camionnettes diesel</strong> par des vélos-cargos électriques, 
          tout en visant un taux de réussite de livraison au premier passage de <strong>95%</strong>.
        </h4>
    </div>
    """, unsafe_allow_html=True)

    col_inc, col_niche = st.columns(2)

    with col_inc:
        st.markdown("""
        <div class="tmc-card tmc-incumbent">
            <h3 style="color:#C62828;">⚠️ SYSTÈME DOMINANT (Incumbent)</h3>
            <p><b>🔑 Acteurs Clés :</b> Leaders mondiaux (DHL, UPS, La Poste) et géants de l'e-commerce (Amazon).</p>
            <p><b>🔗 Interactions rigides :</b> Contrats B2B massifs, horaires imposés (8h-18h), hubs logistiques lointains (Essey, Seichamps).</p>
            <p><b>💪 Forces :</b> Économies d'échelle, puissance de lobbying, habitudes ancrées des consommateurs.</p>
            <p><b>🔴 Vulnérabilités :</b></p>
            <ul>
                <li>Dépendance aux énergies fossiles.</li>
                <li>Congestion urbaine et amendes de stationnement.</li>
                <li>Pression réglementaire (ZFE).</li>
                <li>Coûts fluctuants du carburant (ex: géopolitique, crise Iran/Israël).</li>
            </ul>
            <hr>
            <h5 style="color:#C62828;">🛡️ Défense du système :</h5>
            <p>Lobbying pour retarder les ZFE, greenwashing (mise en avant de nouveaux moteurs diesel), baisse des prix pour étouffer les startups innovantes.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_niche:
        st.markdown("""
        <div class="tmc-card tmc-niche">
            <h3 style="color:#1B5E20;">🌱 SYSTÈME DE NICHE</h3>
            <p><b>🔑 Éléments Clés :</b> L'IA agit comme un "cerveau central" connectant les commandes et le transport pour consolider les livraisons.</p>
            <p><b>🤝 Interactions :</b> Communication bidirectionnelle (chatbot) pour valider la présence 15 min avant le passage. Maintenance anticipée des batteries.</p>
            <p><b>💚 Forces :</b></p>
            <ul>
                <li>Agilité en centre-ville et Zéro émission.</li>
                <li>Réduction drastique de l'énergie.</li>
                <li>Création d'emplois qualifiés (ingénieurs, dev IA).</li>
            </ul>
            <p><b>⚠️ Vulnérabilités :</b> Capacité de charge limitée, dépendance à la météo, technologie récente, filières de recyclage des batteries.</p>
            <hr>
            <h5 style="color:#1B5E20;">🚀 Stratégie de déstabilisation :</h5>
            <p>Campagnes sur le vrai "coût carbone", partenariats avec les municipalités pour microhubs, mutualisation des plateformes d'IA.</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# ONGLET 5 — FAISABILITÉ & PROMPTS IA
# ─────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">🧪 Faisabilité & Documentation des Prompts IA</div>', unsafe_allow_html=True)

    st.markdown("### ✅ Éléments de Faisabilité et de Contexte Global")
    st.write("Le **Paysage (Landscape)** est favorable à cette transition grâce aux facteurs suivants : accords de Paris, urbanisation croissante, explosion de l'e-commerce (+30% d'ici 2030), prise de conscience écologique des citoyens, crises énergétiques et hausses des taxes carbone.")
    
    st.markdown("### 🤖 Prompts Utilisés (Modélisation de l'IA Générative)")
    
    prompts = [
        {
            "titre": "Prompt de structuration du TMC",
            "prompt": "Génère un Transition Model Canvas pour réduire l'empreinte carbone logistique à Nancy. Identifie le système dominant (DHL, UPS) et le système de niche (vélos-cargos + IA). Dégage les vulnérabilités liées aux carburants et les forces de la niche."
        },
        {
            "titre": "Prompt de génération du Dashboard",
            "prompt": "Écris le code Streamlit (Python) pour un tableau de bord consolidant les données d'une flotte de 30 vélos. Inclus des graphiques Plotly montrant un taux de succès visé de 95% et une comparaison des émissions de CO2 face aux véhicules diesel."
        },
        {
            "titre": "Prompt de Simulation IA sans API",
            "prompt": "Développe une logique de chatbot en Python qui utilise des mots-clés (absent, voisin, co2, suivi) pour formuler des réponses intelligentes aux clients de la livraison, simulant ainsi une IA générative sans appel réseau."
        }
    ]

    for p in prompts:
        with st.expander(p["titre"]):
            st.markdown(f'<div class="prompt-card">{p["prompt"]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("""
<div class="footer">
  <strong>🌱 Projet Éco-Logistique Nancy</strong> — Hackathon ICN Business School<br>
  Développé par <strong>Wassim Abdelli</strong> &nbsp;·&nbsp; PGE 2 Transformation Numérique &amp; Écologique<br>
  <small>Prototype Phase 2 &nbsp;·&nbsp; Données consolidées pour 30 unités de livraison</small>
</div>
""", unsafe_allow_html=True)    st.image("https://www.icn-artem.com/wp-content/uploads/2021/05/logo-icn-business-school.png", use_container_width=True)
    
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
