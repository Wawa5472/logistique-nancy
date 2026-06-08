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
            "Notre flotte de **vélos-cargos électriques** couvre le centre-ville et la ZFE.\n\n"
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
if "congestion_active" not in st.session_state: st.session_state.congestion_active = False

# ==========================================
# 4. SIDEBAR (Avec Curseurs et État Persistant)
# ==========================================
with st.sidebar:
    st.image(
        "https://www.icn-artem.com/wp-content/uploads/2021/05/logo-icn-business-school.png",
        use_container_width=True
    )
    st.markdown("---")
    st.markdown("### ⚙️ Pilotage de Flotte")

    # --- AJOUT DES SLIDERS DYNAMIQUES ---
    flotte_totale = st.slider("🚲 Taille de la flotte totale", min_value=10, max_value=50, value=30, step=1)
    
    # Sécurité pour éviter que la flotte active dépasse la flotte totale
    max_active = flotte_totale
    flotte_active_init = min(30, max_active)
    flotte_active = st.slider("🟢 Vélos-cargos actifs en ville", min_value=0, max_value=max_active, value=flotte_active_init, step=1)

    st.markdown("---")
    st.markdown("### 🚨 Simulations Temps Réel")

    # Bouton Congestion lié au session_state pour rester activé
    if st.button("Basculer Alerte Stanislas", use_container_width=True):
        st.session_state.congestion_active = not st.session_state.congestion_active

    if st.session_state.congestion_active:
        st.warning("⚠️ Alerte Congestion Stanislas active !\n\n⚡ IA centrale : 8 unités déviées par Rue Callot ➔ Place Carnot.")
        # Ajustement dynamique basé sur l'alerte
        vélos_affichés = max(0, flotte_active - 8)
        st.caption(f"🚲 {vélos_affichés} unités sur les axes standards, 8 en déviation.")
    else:
        st.info("Secteur Stanislas fluide. Aucun itinéraire alternatif requis.")

    if st.button("♻️ Recalculer l'impact Carbone", use_container_width=True):
        st.session_state.co2_saved += 4.5
        st.success(f"✅ Données calculées : **{st.session_state.co2_saved:.1f} kg** économisés.")

    st.markdown("---")
    st.markdown(f"**Statut :** {flotte_active} / {flotte_totale} opérationnels")
    st.progress(flotte_active / flotte_totale)

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
    Analyse Consolidée : Flotte dynamique pilotée par IA Générative.
  </p>
</div>
""", unsafe_allow_html=True)

# Les KPIs s'adaptent désormais aux Sliders en temps réel !
c1, c2, c3, c4 = st.columns(4)
c1.metric("🚲 Flotte opérationnelle", f"{flotte_active} / {flotte_totale}", f"{int((flotte_active/flotte_totale)*100)}% active")
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
# ONGLET 1 — CHATBOT ENRICHI
# ─────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">💬 EcoBot — Assistant Livraison Décarbonée</div>', unsafe_allow_html=True)

    col_chat, col_aide = st.columns([2, 1])

    with col_aide:
        st.markdown(f"""
        <div style="background:#E8F5E9;border-radius:10px;padding:15px;">
        <b>💡 Exemples de requêtes :</b><br><br>
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

            if any(w in ui for w in ["suivi", "où", "colis", "livraison"]):
                response = (
                    "📍 **Suivi de livraison optimisé :**\n\n"
                    f"Grâce à notre maillage de {flotte_active} vélos actifs, l'unité **#{np.random.randint(1, flotte_active+1):02d}** est à "
                    f"moins de 500m du centre-ville.\n\n"
                    "⏱️ **Arrivée imminente :** Un SMS automatique vous sera envoyé 15 minutes avant le passage."
                )

            elif any(w in ui for w in ["absent", "18h", "19h", "soir", "tard"]):
                response = (
                    "🕒 **Modification d'itinéraire :**\n\n"
                    "L'IA centrale a réorganisé la tournée de livraison en direct. Notre capacité de traitement "
                    "nous permet cette flexibilité horaire sans générer d'émissions de carbone supplémentaires."
                )
                st.session_state.success_rate = min(98.0, st.session_state.success_rate + 0.1)

            elif any(w in ui for w in ["voisin", "consigne", "relais", "hub"]):
                response = (
                    "✅ **Consigne validée :**\n\n"
                    "La consigne de dépôt secondaire est enregistrée. Cela nous aide à maintenir notre objectif de "
                    "**95% de succès au premier passage**."
                )
                st.session_state.co2_saved += 1.5

            elif any(w in ui for w in ["co2", "carbone", "écolo", "impact"]):
                response = (
                    f"🌍 **Bilan de la flotte :**\n\n"
                    f"Avec nos vélos-cargos, nous avons déjà sécurisé l'équivalent de **{st.session_state.co2_saved:.1f} kg** "
                    f"de CO₂ évités aujourd'hui sur Nancy."
                )

            else:
                response = (
                    f"✅ **Instruction reçue :**\n\n"
                    f"Prise en compte par le système central logistique gérant nos {flotte_active} unités en mouvement."
                )

            time.sleep(0.4)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# ─────────────────────────────────────────
# ONGLET 2 — CARTE DYNAMIQUE
# ─────────────────────────────────────────
with tab2:
    st.markdown(f'<div class="section-title">🗺️ Localisation Temps Réel — {flotte_active} Vélos-Cargos</div>', unsafe_allow_html=True)
    
    np.random.seed(42)
    # Génère exactement le nombre de points sélectionnés sur le slider
    df_map = pd.DataFrame(
        np.random.randn(flotte_active, 2) / [180, 180] + [48.6920, 6.1844],
        columns=['lat', 'lon']
    )
    st.map(df_map, zoom=14, color="#2E7D32")
    st.caption(f"Visualisation dynamique du réseau : {flotte_active} positions GPS actives sur la ZFE de Nancy.")

# ─────────────────────────────────────────
# ONGLET 3 — DASHBOARD
# ─────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">📊 Analyse d\'Impact — Performance Écologique</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        semaines = ["S-4", "S-3", "S-2", "S-1", "S-En cours"]
        fig_em = go.Figure()
        fig_em.add_trace(go.Scatter(
            x=semaines, y=[100, 105, 110, 115, 120],
            mode="lines+markers", name="Customer System (Camionnettes)",
            line=dict(color="#E53935", width=3)
        ))
        fig_em.add_trace(go.Scatter(
            x=semaines, y=[100, 70, 40, 20, 15],
            mode="lines+markers", name="Flotte de Vélos-Cargos",
            line=dict(color="#43A047", width=3),
            fill="tozeroy", fillcolor="rgba(67,160,71,0.1)"
        ))
        fig_em.update_layout(
            title="📉 Chute des Émissions de CO₂ (Base 100)",
            plot_bgcolor="white", height=320,
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_em, use_container_width=True)

    with col_b:
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
# ONGLET 4 — TMC INTERACTIF
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
            <p><b>💪 Forces :</b> Économies d'échelle, puissance de lobbying, habitudes de livraison express.</p>
            <p><b>🔴 Vulnérabilités :</b> Dépendance aux énergies fossiles, congestion urbaine massive, amendes, et coûts du carburant indexés sur les crises mondiales (ex: Iran/Israël).</p>
            <hr>
            <h5 style="color:#C62828;">🛡️ Défense du système :</h5>
            <p>Lobbying pro-diesel, dumping tarifaire temporaire pour étouffer l'innovation, rachat de brevets logistiques.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_niche:
        st.markdown("""
        <div class="tmc-card tmc-niche">
            <h3 style="color:#1B5E20;">🌱 SYSTÈME DE NICHE</h3>
            <p><b>🔑 Éléments Clés :</b> L'IA agit comme un "cerveau central" analytique reliant commandes et transport de manière optimisée.</p>
            <p><b>🤝 Interactions :</b> Dialogue client via chatbot conversationnel 15 min avant le passage pour sécuriser le taux de succès.</p>
            <p><b>💚 Forces :</b> Agilité complète, zéro émission directe, préservation de la qualité de vie en ville, création d'emplois tech locaux.</p>
            <p><b>⚠️ Vulnérabilités :</b> Poids et volume par colis limités, exposition météo, logistique de rechargement/recyclage des batteries.</p>
            <hr>
            <h5 style="color:#1B5E20;">🚀 Stratégie de déstabilisation :</h5>
            <p>Campagnes sur le coût carbone réel par colis, alliances stratégiques d'externalisation, mutualisation d'outils d'IA.</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# ONGLET 5 — FAISABILITÉ & PROMPTS IA
# ─────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">🧪 Faisabilité & Documentation des Prompts IA</div>', unsafe_allow_html=True)

    st.markdown("### ✅ Éléments de Faisabilité et de Contexte Global")
    st.write("Le **Paysage (Landscape)** global pousse à la transition : accords de Paris, urbanisation accélérée, explosion structurelle de l'e-commerce (+30% d'ici 2030), sensibilité environnementale accrue de la population, et taxes carbone à la hausse.")
    
    st.markdown("### 🤖 Prompts Utilisés pour concevoir la solution")
    
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
  <small>Prototype Phase 2 &nbsp;·&nbsp; Données modulables en temps réel pour soutenance</small>
</div>
""", unsafe_allow_html=True)
