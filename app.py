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
# 3. INITIALISATION DES ÉTATS
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "🌱 Bonjour ! Je suis **EcoBot**, l'assistant IA de la plateforme Éco-Nancy.\n\n"
            "Notre flotte de **30 vélos-cargos électriques** couvre toute la ZFE du Grand Nancy.\n\n"
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
        st.warning("⚡ 8 unités réaffectées — itinéraire alternatif : Rue Callot → Place Carnot")

    if st.button("♻️ Recalculer l'impact Carbone", use_container_width=True):
        st.session_state.co2_saved += 4.5
        st.success(f"✅ CO₂ mis à jour : **{st.session_state.co2_saved:.1f} kg** économisés")

    if st.button("📦 Simuler Pic de Livraisons", use_container_width=True):
        st.session_state.livraisons_jour += int(np.random.randint(5, 20))
        st.info(f"📈 {st.session_state.livraisons_jour} livraisons aujourd'hui")

    st.markdown("---")
    flotte_active = int(np.random.randint(27, 30))
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
    st.caption("Hackathon Phase 2 — 2026")
    st.markdown("---")
    st.markdown("**📊 Session**")
    st.caption(f"💬 {len(st.session_state.messages)} messages")
    st.caption(f"🌱 {st.session_state.co2_saved:.1f} kg CO₂ économisés")

# ==========================================
# 5. EN-TÊTE
# ==========================================
st.markdown("""
<div class="main-header">
  <h1 style="margin:0;font-size:26px;">🌱 Plateforme de Livraison Décarbonée — Grand Nancy</h1>
  <p style="margin:8px 0 0 0;opacity:.9;font-size:14px;">
    Flotte de <strong>30 vélos-cargos</strong> pilotée par IA Générative &nbsp;·&nbsp;
    Zone ZFE &nbsp;·&nbsp; <em>Hackathon ICN 2026 — Wassim Abdelli</em>
  </p>
</div>
""", unsafe_allow_html=True)

# KPIs rapides
c1, c2, c3, c4 = st.columns(4)
c1.metric("🚲 Flotte opérationnelle", "30 / 30", "100 % actif")
c2.metric("✅ Succès 1er passage",     f"{st.session_state.success_rate:.1f} %", "+4.2 % vs diesel")
c3.metric("🌿 CO₂ économisé/jour",    f"{st.session_state.co2_saved:.1f} kg",   "+5.4 kg")
c4.metric("📦 Livraisons aujourd'hui", str(st.session_state.livraisons_jour),    "+12 vs hier")

st.markdown("---")

# ==========================================
# 6. ONGLETS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Interface Client (IA)",
    "🗺️ Carte de la Flotte",
    "📊 Tableau de Bord",
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
        st.markdown("""
        <div style="background:#E8F5E9;border-radius:10px;padding:15px;">
        <b>💡 Exemples de questions :</b><br><br>
        🔍 <i>"Où est mon colis ?"</i><br>
        🕒 <i>"Je suis absent cet après-midi"</i><br>
        🏠 <i>"Déposez chez le voisin"</i><br>
        🌱 <i>"Quel est l'impact carbone ?"</i><br>
        📍 <i>"Zones couvertes à Nancy ?"</i><br>
        🚲 <i>"Comment fonctionne le service ?"</i><br>
        📦 <i>"Quels colis acceptez-vous ?"</i>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#FFF3E0;border-radius:10px;padding:15px;">
        <b>📊 Statistiques live :</b><br>
        💬 Messages échangés : <b>{len(st.session_state.messages)}</b><br>
        📦 Livraisons du jour : <b>{st.session_state.livraisons_jour}</b><br>
        🌿 CO₂ économisé : <b>{st.session_state.co2_saved:.1f} kg</b>
        </div>
        """, unsafe_allow_html=True)

    with col_chat:
        chat_container = st.container(height=430)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Votre demande (ex: Je suis absent, déposez au micro-hub…)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            ui = prompt.lower()

            # ── Moteur de réponses contextuelles ──────────────────────────
            if any(w in ui for w in ["suivi", "où", "colis", "livraison", "quand", "arrivée"]):
                response = (
                    "📍 **Suivi de votre colis en temps réel :**\n\n"
                    f"🚲 **Vélo #{np.random.randint(1,30):02d}** est à "
                    f"**{np.random.randint(200,600)}m** de votre adresse "
                    f"(secteur {np.random.choice(['Stanislas','Carnot','Beauregard','Vandœuvre'])}).\n\n"
                    f"⏱️ **Arrivée estimée :** dans **{np.random.randint(8,22)} minutes**.\n\n"
                    "🌡️ Conservation : ✅ Conforme\n\n"
                    "> Vous recevrez une notification SMS 5 min avant l'arrivée."
                )

            elif any(w in ui for w in ["absent", "pas là", "travail", "18h", "19h", "soir", "tard", "créneau"]):
                response = (
                    "🕒 **Modification de créneau — sans surcoût carbone !**\n\n"
                    "J'ai noté votre indisponibilité. Voici vos options :\n\n"
                    "1. 📬 **Micro-hub Place Carnot** (consigne sécurisée 24/7)\n"
                    "2. 🏠 **Voisin de confiance** — précisez le numéro\n"
                    "3. 📅 **Nouveau créneau** : demain 8h–12h ou 14h–18h\n"
                    "4. 📦 **Point relais** : Pharmacie Stanislas, Tabac Beauregard\n\n"
                    "> ✅ Notre IA réoptimise la tournée automatiquement — **zéro émission supplémentaire**."
                )
                st.session_state.success_rate = min(98.0, st.session_state.success_rate + 0.1)

            elif any(w in ui for w in ["voisin", "consigne", "relais", "gardien"]):
                response = (
                    "✅ **Consigne de livraison enregistrée !**\n\n"
                    "Votre instruction a été transmise en **temps réel** au livreur assigné.\n\n"
                    "📋 **Récapitulatif :**\n"
                    f"- Vélo assigné : #{np.random.randint(1,30):02d} (secteur Vandœuvre)\n"
                    "- Confirmation SMS envoyée au destinataire secondaire\n\n"
                    f"🌱 **Bonus** : Ce 2ᵉ passage évité = **+1.5 kg CO₂ économisés** sur votre livraison !\n"
                    f"> Taux de succès maintenant : **{st.session_state.success_rate:.1f}%** 🎯"
                )
                st.session_state.co2_saved += 1.5

            elif any(w in ui for w in ["co2", "carbone", "écolo", "environnement", "impact", "émission", "vert"]):
                response = (
                    "🌍 **Impact Environnemental de notre flotte :**\n\n"
                    "| Indicateur | Valeur |\n|---|---|\n"
                    f"| CO₂ économisé / jour | **{st.session_state.co2_saved:.1f} kg** |\n"
                    "| Équivalent arbres plantés | **~5 arbres/jour** |\n"
                    "| Carburant économisé | **~62 litres/jour** |\n"
                    "| Km sans diesel | **~340 km/jour** |\n\n"
                    "📊 1 camionnette diesel : **~2.7 kg CO₂/livraison**. Nos vélos : **0.02 kg**.\n\n"
                    "> 🎯 Objectif 2026 : **-85 %** d'émissions vs flotte diesel classique sur la ZFE."
                )

            elif any(w in ui for w in ["zone", "secteur", "quartier", "nancy", "couvre", "périmètre"]):
                response = (
                    "📍 **Zones couvertes par notre flotte (ZFE Nancy) :**\n\n"
                    "✅ Centre historique (Stanislas, Vieille Ville)\n"
                    "✅ Trois-Maisons & Boudonville\n"
                    "✅ Vandœuvre-lès-Nancy (Technopôle)\n"
                    "✅ Maxéville & Saint-Max\n"
                    "✅ Campus universitaires (Brabois)\n\n"
                    "🚲 **Maillage** : 1 vélo disponible dans un rayon de 500 m en heure de pointe\n"
                    "⏱️ **Délai max** : 90 min en zone ZFE"
                )

            elif any(w in ui for w in ["fonctionne", "comment", "service", "principe"]):
                response = (
                    "🚀 **Fonctionnement de la plateforme :**\n\n"
                    "1️⃣ **Commande reçue** → IA analyse l'itinéraire optimal\n"
                    "2️⃣ **Attribution** → Vélo-cargo le plus proche assigné automatiquement\n"
                    "3️⃣ **Livraison** → Livreur guidé (congestion, météo, batterie)\n"
                    "4️⃣ **Confirmation** → Photo + notification client instantanée\n"
                    "5️⃣ **Données** → Métriques CO₂ mises à jour en direct\n\n"
                    "🤖 Notre IA optimise **3 variables en simultané** :\n"
                    "⚡ Rapidité &nbsp;·&nbsp; 🌿 Carbone minimal &nbsp;·&nbsp; 🔋 Autonomie batterie"
                )

            elif any(w in ui for w in ["poids", "taille", "dimension", "volume", "acceptez", "colis"]):
                response = (
                    "📦 **Capacités de nos vélos-cargos :**\n\n"
                    "| Caractéristique | Capacité |\n|---|---|\n"
                    "| Poids max | **80 kg / vélo** |\n"
                    "| Volume max | **250 litres** |\n"
                    "| Format max | **120 × 60 × 60 cm** |\n"
                    "| Produits frais | ✅ 8 °C maintenu (3 h max) |\n"
                    "| Fragile | ✅ Caissons amortissants |\n\n"
                    "> 💡 Pour gros volumes : **groupage multi-vélos** sur demande."
                )

            elif any(w in ui for w in ["bonjour", "salut", "hello", "bonsoir", "bonne"]):
                response = (
                    "👋 **Bienvenue sur EcoNancy !**\n\n"
                    "Je suis **EcoBot**, votre assistant livraison décarbonée 🌱\n\n"
                    "Avec **30 vélos-cargos électriques** pilotés par IA, nous livrons dans toute la "
                    "ZFE de Nancy avec **zéro émission directe** de CO₂.\n\n"
                    "Comment puis-je vous aider aujourd'hui ?"
                )

            else:
                response = (
                    "✅ **Demande bien prise en compte !**\n\n"
                    "Votre instruction a été transmise en temps réel à notre système de dispatch.\n\n"
                    f"📊 **État de la flotte en ce moment :**\n"
                    f"- 🚲 Vélos actifs : **{np.random.randint(27,30)}/30**\n"
                    f"- 📦 Livraisons en cours : **{np.random.randint(15,25)}**\n"
                    f"- ⏱️ Délai moyen : **{np.random.randint(18,35)} minutes**\n\n"
                    "> Pour toute autre question, n'hésitez pas ! 🌿"
                )

            time.sleep(0.25)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# ─────────────────────────────────────────
# ONGLET 2 — CARTE
# ─────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">🗺️ Localisation Temps Réel — 30 Vélos-Cargos</div>', unsafe_allow_html=True)

    col_map, col_legend = st.columns([3, 1])

    with col_map:
        np.random.seed(42)
        df_map = pd.DataFrame({
            "lat":     np.random.randn(30) / 180 + 48.6920,
            "lon":     np.random.randn(30) / 180 + 6.1844,
            "vélo":    [f"Vélo #{i:02d}" for i in range(1, 31)],
            "statut":  np.random.choice(["En livraison 🚚", "Disponible ✅", "Retour hub 🔄"],
                                         30, p=[0.6, 0.3, 0.1]),
            "batterie": np.random.randint(45, 100, 30),
        })
        st.map(df_map, zoom=14, color="#2E7D32", size=40)
        st.caption("🌿 Maillage territorial en temps réel — 30 unités couvrant les zones ZFE de Nancy")

    with col_legend:
        st.markdown("""
        <div style="background:#F1F8E9;padding:15px;border-radius:10px;">
        <b>🔍 Légende</b><br><br>
        🟢 Disponible<br>🔵 En livraison<br>🟡 Retour hub<br><br>
        <hr>
        <b>📡 Mise à jour :</b> 30 s<br><br>
        <b>📍 Hub principal :</b><br>Place Carnot, Nancy
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        en_livraison = int((df_map["statut"] == "En livraison 🚚").sum())
        disponibles  = int((df_map["statut"] == "Disponible ✅").sum())
        st.metric("🚚 En livraison",  en_livraison)
        st.metric("✅ Disponibles",   disponibles)
        st.metric("🔋 Batterie moy.", f"{df_map['batterie'].mean():.0f} %")

# ─────────────────────────────────────────
# ONGLET 3 — DASHBOARD
# ─────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">📊 Tableau de Bord — Performance Écologique & Logistique</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    # Graphique 1 — Émissions comparatives
    with col_a:
        semaines = ["S-4", "S-3", "S-2", "S-1", "Aujourd'hui"]
        fig_em = go.Figure()
        fig_em.add_trace(go.Scatter(
            x=semaines, y=[100, 103, 107, 112, 115],
            mode="lines+markers", name="🚛 Camionnettes diesel",
            line=dict(color="#E53935", width=3), marker=dict(size=8)
        ))
        fig_em.add_trace(go.Scatter(
            x=semaines, y=[100, 72, 48, 28, 15],
            mode="lines+markers", name="🚲 Vélos-cargos",
            line=dict(color="#43A047", width=3), marker=dict(size=8),
            fill="tozeroy", fillcolor="rgba(67,160,71,0.12)"
        ))
        fig_em.update_layout(
            title="📉 Réduction des émissions CO₂ (base 100)",
            plot_bgcolor="white", paper_bgcolor="white", height=310,
            legend=dict(orientation="h", y=-0.25),
            yaxis_title="Indice d'émissions", xaxis_title="Période"
        )
        fig_em.update_yaxes(gridcolor="#E0E0E0")
        st.plotly_chart(fig_em, use_container_width=True)

    # Graphique 2 — Taux de succès par secteur
    with col_b:
        secteurs = ["Stanislas", "Vandœuvre", "Maxéville", "3-Maisons", "Brabois"]
        taux     = [96.2, 93.8, 95.1, 92.7, 94.5]
        colors   = ["#43A047" if t >= 95 else "#FB8C00" if t >= 93 else "#E53935" for t in taux]
        fig_sec = go.Figure(go.Bar(
            x=secteurs, y=taux, marker_color=colors,
            text=[f"{t}%" for t in taux], textposition="outside"
        ))
        fig_sec.add_hline(y=95, line_dash="dash", line_color="red",
                          annotation_text="Objectif 95 %", annotation_position="top right")
        fig_sec.update_layout(
            title="✅ Taux de succès 1er passage par secteur",
            plot_bgcolor="white", paper_bgcolor="white", height=310,
            yaxis=dict(range=[88, 100], title="Taux (%)"), xaxis_title="Secteur"
        )
        fig_sec.update_yaxes(gridcolor="#E0E0E0")
        st.plotly_chart(fig_sec, use_container_width=True)

    col_c, col_d = st.columns(2)

    # Graphique 3 — Livraisons par heure
    with col_c:
        heures    = list(range(8, 20))
        livs      = [3, 8, 12, 18, 22, 19, 14, 17, 21, 16, 9, 4]
        fig_heure = go.Figure(go.Bar(
            x=[f"{h}h" for h in heures], y=livs,
            marker_color=["#43A047" if l >= 18 else "#8BC34A" if l >= 12 else "#CDDC39" for l in livs],
            text=livs, textposition="outside"
        ))
        fig_heure.update_layout(
            title="⏱️ Livraisons par heure de la journée",
            plot_bgcolor="white", paper_bgcolor="white", height=300,
            yaxis_title="Livraisons", xaxis_title="Heure"
        )
        fig_heure.update_yaxes(gridcolor="#E0E0E0")
        st.plotly_chart(fig_heure, use_container_width=True)

    # Graphique 4 — Jauge succès
    with col_d:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=st.session_state.success_rate,
            delta={"reference": 90.0, "suffix": "%"},
            title={"text": "Taux de succès global", "font": {"size": 15}},
            gauge={
                "axis": {"range": [80, 100]},
                "bar":  {"color": "#2E7D32"},
                "steps": [
                    {"range": [80, 90], "color": "#FFEBEE"},
                    {"range": [90, 95], "color": "#FFF9C4"},
                    {"range": [95, 100], "color": "#E8F5E9"},
                ],
                "threshold": {"line": {"color": "orange", "width": 4},
                               "thickness": 0.75, "value": 95}
            },
            number={"suffix": "%"}
        ))
        fig_gauge.update_layout(height=300, paper_bgcolor="white")
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Ligne 3 — Impact cumulé
    st.markdown("### 🌍 Impact Environnemental Cumulé")
    ce1, ce2, ce3, ce4 = st.columns(4)
    ce1.metric("🌿 CO₂ semaine",       f"{st.session_state.co2_saved*7:.0f} kg",  "+8 %")
    ce2.metric("⛽ Litres évités",      f"{st.session_state.co2_saved*7/2.7:.0f} L", "vs diesel")
    ce3.metric("🌳 Arbres éq./an",      f"{int(st.session_state.co2_saved*365/21)}",  "absorbés")
    ce4.metric("💶 Économie/jour",      f"{st.session_state.livraisons_jour*2.3:.0f} €", "vs camionnette")

# ─────────────────────────────────────────
# ONGLET 4 — TMC INTERACTIF
# ─────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">🔄 Transition Model Canvas — Éco-Logistique Nancy</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#FFF8E1;border:1px solid #FFE082;border-radius:10px;padding:14px;margin-bottom:18px;">
    📚 <b>Qu'est-ce que le TMC ?</b> Le <i>Transition Model Canvas</i> est un outil stratégique qui analyse 
    comment une innovation de <em>niche</em> peut déstabiliser un <em>système dominant (incumbent)</em> 
    pour accélérer la transition écologique.
    </div>
    """, unsafe_allow_html=True)

    # OBJECTIF DE TRANSITION
    st.markdown("""
    <div class="tmc-card tmc-goal">
        <h3 style="color:#E65100;margin:0 0 10px 0;">🎯 OBJECTIF DE TRANSITION (SMART)</h3>
        <h4 style="color:#333;margin:0;">
          Assurer <strong>30 % des livraisons urbaines de Nancy en vélos-cargos électriques d'ici fin 2026</strong>,
          en réduisant les émissions CO₂ du dernier kilomètre de <strong>-85 %</strong> dans la ZFE,
          mesurables via dashboard IA en temps réel.
        </h4>
        <br>
        <span class="badge badge-blue">📌 Spécifique</span>
        <span class="badge badge-green">📊 Mesurable (−85 % CO₂)</span>
        <span class="badge badge-orange">✅ Atteignable (30 vélos opérationnels)</span>
        <span class="badge badge-red">📅 Temporel (fin 2026)</span>
    </div>
    """, unsafe_allow_html=True)

    col_inc, col_niche = st.columns(2)

    with col_inc:
        st.markdown("""
        <div class="tmc-card tmc-incumbent">
            <h3 style="color:#C62828;">⚠️ SYSTÈME DOMINANT (INCUMBENT)</h3>
            <h4>🚛 Livraison urbaine par camionnettes diesel</h4>
            <p><b>🔑 Éléments clés :</b></p>
            <ul>
                <li>Opérateurs : DHL, Chronopost, GLS, DPD</li>
                <li>Infrastructure lourde : centres de tri, dépôts périphériques</li>
                <li>Flotte diesel/GNV à renouvellement lent</li>
                <li>Réglementation ZFE Nancy 2024-2026</li>
            </ul>
            <p><b>💪 Forces :</b></p>
            <span class="badge badge-blue">Capacité volumique</span>
            <span class="badge badge-blue">Réseau national</span>
            <span class="badge badge-blue">Marques connues</span>
            <span class="badge badge-blue">Contrats B2B solides</span>
            <p><b>⚠️ Vulnérabilités :</b></p>
            <span class="badge badge-red">Coût carburant élevé</span>
            <span class="badge badge-red">Congestion urbaine</span>
            <span class="badge badge-red">Interdiction ZFE</span>
            <span class="badge badge-red">Image polluante</span>
            <span class="badge badge-red">Coût &gt;5 €/colis</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tmc-card" style="border-left:6px solid #1565C0;margin-top:14px;">
            <h4 style="color:#0D47A1;">🛡️ STRATÉGIES DE DÉFENSE (Incumbent)</h4>
            <ul>
                <li>📦 Transition partielle vers véhicules électriques lourds</li>
                <li>🤝 Sous-traitance vélos-cargos pour le dernier 500 m</li>
                <li>💰 Dumping tarifaire temporaire (rétention clients B2B)</li>
                <li>🏛️ Lobbying pour repousser les restrictions ZFE</li>
                <li>📱 Rachat de startups innovantes (absorption de la niche)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_niche:
        st.markdown("""
        <div class="tmc-card tmc-niche">
            <h3 style="color:#1B5E20;">🌱 SYSTÈME DE NICHE</h3>
            <h4>🚲 Livraison décarbonée par vélos-cargos IA</h4>
            <p><b>🔑 Éléments présents :</b></p>
            <ul>
                <li>30 vélos-cargos électriques assistés</li>
                <li>IA générative (optimisation de tournées)</li>
                <li>Dashboard temps réel (CO₂, GPS, taux succès)</li>
                <li>Micro-hubs urbains (Carnot, Stanislas)</li>
                <li>EcoBot — interface client adaptative</li>
            </ul>
            <p><b>❌ Éléments manquants :</b></p>
            <span class="badge badge-red">Volume &gt;80 kg</span>
            <span class="badge badge-red">Couverture nationale</span>
            <span class="badge badge-red">Notoriété grand public</span>
            <span class="badge badge-red">Financement d'amorçage</span>
            <p><b>💚 Forces :</b></p>
            <span class="badge badge-green">0 émission directe</span>
            <span class="badge badge-green">Coût opérationnel bas</span>
            <span class="badge badge-green">Rapidité centre-ville</span>
            <span class="badge badge-green">Image verte forte</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="tmc-card tmc-niche" style="margin-top:14px;">
            <h4 style="color:#1B5E20;">🚀 STRATÉGIES POUR DÉSTABILISER L'INCUMBENT</h4>
            <ul>
                <li>🏛️ Lobbying pro-ZFE : accélérer les restrictions diesel</li>
                <li>🤝 Partenariats e-commerce : Amazon, Cdiscount, Label Emmaüs</li>
                <li>🌐 Badge "livraison verte" visible à la commande</li>
                <li>💡 Prime éco acceptable : +0.30 €/colis acceptée par 72 % des clients</li>
                <li>📊 Offrir les données CO₂ aux collectivités (data partnership)</li>
                <li>🏆 Certification ISO 14001 pour crédibilité B2B</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # PAYSAGE
    st.markdown("""
    <div class="tmc-card tmc-landscape" style="margin-top:18px;">
        <h3 style="color:#283593;">🌐 PAYSAGE (LANDSCAPE) — Facteurs macro-environnementaux</h3>
        <div style="display:flex;flex-wrap:wrap;gap:18px;">
            <div style="flex:1;min-width:200px;">
                <b>🏛️ Réglementaire :</b><br>
                ZFE Nancy 2024 · Loi LOM 2019 · Plan Vélo National 2023-2027
            </div>
            <div style="flex:1;min-width:200px;">
                <b>💰 Économique :</b><br>
                Prix carburant +45 % · Subventions ADEME · Inflation logistique
            </div>
            <div style="flex:1;min-width:200px;">
                <b>👥 Social :</b><br>
                72 % Français préfèrent livraison verte · E-commerce +15 %/an
            </div>
            <div style="flex:1;min-width:200px;">
                <b>🔬 Technologique :</b><br>
                IA générative · Batteries LFP améliorées · GPS haute précision
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # RADAR TMC
    st.markdown("### 📊 Analyse comparative Incumbent vs Niche")
    categories = ["Coût opérationnel", "Impact carbone", "Rapidité urbaine",
                  "Capacité volume", "Conformité ZFE", "Image de marque"]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[3, 1, 2, 9, 2, 4], theta=categories, fill="toself",
        name="🚛 Incumbent (diesel)",
        line_color="#E53935", fillcolor="rgba(229,57,53,0.2)"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[8, 10, 9, 3, 10, 9], theta=categories, fill="toself",
        name="🚲 Niche (vélos-cargos)",
        line_color="#43A047", fillcolor="rgba(67,160,71,0.2)"
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True, title="Score comparatif (1–10)", height=420,
        paper_bgcolor="white"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ─────────────────────────────────────────
# ONGLET 5 — FAISABILITÉ & PROMPTS IA
# ─────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">🧪 Faisabilité & Documentation des Prompts IA</div>', unsafe_allow_html=True)

    st.markdown("### ✅ Analyse de Faisabilité du Projet")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        st.markdown("""
        <div class="feasibility-positive">
            <h4 style="color:#2E7D32;">✅ Facteurs Favorables</h4>
            <ul>
                <li><b>ZFE Nancy opérationnelle</b> : restrictions diesel = marché libéré pour les vélos</li>
                <li><b>Subventions ADEME</b> : jusqu'à 4 000 € par vélo-cargo électrique</li>
                <li><b>Micro-hubs disponibles</b> : Ville de Nancy partenaire (places publiques)</li>
                <li><b>E-commerce local +18 %/an</b> : demande croissante et structurelle</li>
                <li><b>IA open-source</b> : OSRM pour optimisation de tournées (gratuit)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feasibility-warning" style="margin-top:14px;">
            <h4 style="color:#E65100;">⚠️ Points de Vigilance</h4>
            <ul>
                <li><b>Volume limité</b> : colis > 30 kg nécessite une infrastructure complémentaire</li>
                <li><b>Météo</b> : efficacité réduite (Nancy : ~60 jours de pluie/an)</li>
                <li><b>Rayon d'action</b> : ~60 km/charge → suffisant pour la ZFE</li>
                <li><b>Recrutement</b> : compétences techniques + résistance physique</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feasibility-challenge" style="margin-top:14px;">
            <h4 style="color:#C62828;">🔴 Challenges à Adresser</h4>
            <ul>
                <li><b>Investissement initial</b> : ~5 000 € × 30 = 150 000 € (partiellement subventionné)</li>
                <li><b>Concurrence</b> : Amazon Flex, Stuart, Urb-it sur le segment urbain</li>
                <li><b>Break-even</b> : estimé à 18 mois (hypothèse : 8 €/livraison, 127/jour)</li>
                <li><b>Dépendance IA</b> : fallback manuel nécessaire si API indisponible</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_f2:
        # Graphique break-even
        mois       = [f"M{i}" for i in range(1, 19)]
        revenus_c  = [i * 4200 for i in range(1, 19)]
        couts_c    = [150000 + i * 1800 for i in range(1, 19)]

        fig_be = go.Figure()
        fig_be.add_trace(go.Scatter(x=mois, y=revenus_c, mode="lines+markers",
                                    name="Revenus cumulés", line=dict(color="#43A047", width=2)))
        fig_be.add_trace(go.Scatter(x=mois, y=couts_c, mode="lines+markers",
                                    name="Coûts cumulés",    line=dict(color="#E53935", width=2)))
        for i, (r, c) in enumerate(zip(revenus_c, couts_c)):
            if r >= c:
                fig_be.add_vline(x=mois[i], line_dash="dash", line_color="orange",
                                  annotation_text=f"Break-even M{i+1}")
                break
        fig_be.update_layout(
            title="💰 Trajectoire financière (hypothèse)",
            height=260, plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=-0.3), yaxis_title="€ cumulés"
        )
        fig_be.update_yaxes(gridcolor="#E0E0E0")
        st.plotly_chart(fig_be, use_container_width=True)

        # Graphique scoring décision
        criteres = ["Impact CO₂", "Viabilité financière", "Faisabilité tech.",
                    "Acceptabilité sociale", "Conformité réglementaire"]
        scores   = [9.5, 7.2, 8.1, 8.8, 9.3]
        fig_bar  = go.Figure(go.Bar(
            x=scores, y=criteres, orientation="h",
            marker_color=["#43A047" if s >= 8 else "#FB8C00" for s in scores],
            text=[f"{s}/10" for s in scores], textposition="outside"
        ))
        fig_bar.update_layout(
            title="🎯 Scoring de faisabilité (0–10)",
            height=260, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(range=[0, 11])
        )
        fig_bar.update_xaxes(gridcolor="#E0E0E0")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # SECTION PROMPTS IA
    st.markdown("### 🤖 Documentation des Prompts IA Utilisés")
    st.info("*Ces prompts ont été utilisés avec Gemini Pro et Claude pour concevoir ce prototype.*")

    prompts = [
        {
            "titre": "🎯 Prompt 1 — Analyse TMC initiale",
            "objectif": "Structurer l'analyse Transition Model Canvas",
            "prompt": (
                "Tu es un expert en transitions écologiques et en stratégie d'innovation.\n"
                "Applique le Transition Model Canvas à la problématique suivante :\n"
                "'Comment réduire les émissions CO₂ de la logistique du dernier kilomètre\n"
                "en zone urbaine (Nancy ZFE) grâce aux vélos-cargos électriques pilotés par IA ?'\n"
                "Identifie : système dominant, système de niche, objectif SMART,\n"
                "forces/vulnérabilités des deux systèmes, et stratégies de transition."
            ),
            "résultat": "TMC complet avec 4 stratégies par système"
        },
        {
            "titre": "📊 Prompt 2 — Calcul d'impact carbone",
            "objectif": "Estimer les économies de CO₂",
            "prompt": (
                "En tant qu'expert en logistique urbaine et bilan carbone,\n"
                "calcule l'impact environnemental d'une flotte de 30 vélos-cargos électriques\n"
                "remplaçant des camionnettes diesel à Nancy (~120 livraisons/jour, ZFE).\n"
                "Inclus : kg CO₂ économisés/jour, équivalent arbres plantés,\n"
                "comparaison énergétique, et sources (ADEME, ACEA)."
            ),
            "résultat": "54.2 kg CO₂/jour économisés (base de calcul validée ADEME)"
        },
        {
            "titre": "🚲 Prompt 3 — Business Model & Faisabilité",
            "objectif": "Valider la viabilité économique",
            "prompt": (
                "Analyse la faisabilité économique d'une startup de livraison\n"
                "décarbonée à Nancy avec : 30 vélos-cargos électriques (5 000 €/unité),\n"
                "2 micro-hubs (Place Carnot + Place Stanislas), IA pour optimisation tournées.\n"
                "Fournis : structure de coûts, revenus estimés (€/colis), break-even point,\n"
                "subventions disponibles (ADEME, Région Grand Est), et risques principaux."
            ),
            "résultat": "Break-even M18, subventions potentielles ~120 000 €"
        },
        {
            "titre": "💻 Prompt 4 — Génération du prototype Python/Streamlit",
            "objectif": "Créer le dashboard interactif",
            "prompt": (
                "Génère une application Streamlit complète pour une plateforme de livraison\n"
                "décarbonée à Nancy. Inclus : chatbot IA (réponses contextuelles),\n"
                "carte GPS temps réel (30 vélos), dashboard KPI (CO₂, taux de succès),\n"
                "thème vert cohérent avec Plotly. Rends-la 'vivante' avec des simulations."
            ),
            "résultat": "Application déployée sur Streamlit Cloud (lien public)"
        },
        {
            "titre": "🎨 Prompt 5 — Amélioration UX & enrichissement",
            "objectif": "Enrichir l'expérience et la documentation",
            "prompt": (
                "Améliore ce prototype Streamlit de livraison verte :\n"
                "Ajoute un thème CSS vert cohérent (palette #2E7D32), un TMC visuel interactif,\n"
                "un onglet faisabilité avec graphiques Plotly, et des réponses IA plus riches\n"
                "sans appel API. Garde tous les éléments existants (photo, KPIs, carte, logo ICN)."
            ),
            "résultat": "Interface 5 onglets avec TMC radar, jauge, break-even, scoring"
        },
    ]

    for p in prompts:
        with st.expander(p["titre"]):
            st.markdown(f"**🎯 Objectif :** {p['objectif']}")
            st.markdown(f'<div class="prompt-card">{p["prompt"]}</div>', unsafe_allow_html=True)
            st.success(f"✅ **Résultat obtenu :** {p['résultat']}")

    st.markdown("---")
    st.markdown("### 🛠️ Stack Technologique")
    ct1, ct2, ct3 = st.columns(3)
    with ct1:
        st.markdown("**🤖 IA & LLM**\n- Google Gemini Pro\n- Claude (Anthropic)\n- GPT-4 (validation)")
    with ct2:
        st.markdown("**💻 Développement**\n- Python 3.12\n- Streamlit\n- Plotly · Pandas · NumPy")
    with ct3:
        st.markdown("**☁️ Déploiement**\n- GitHub (versioning)\n- Streamlit Cloud\n- Lien public partageable")

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("""
<div class="footer">
  <strong>🌱 Plateforme Éco-Logistique Nancy</strong> — Hackathon ICN Business School 2026<br>
  Développé par <strong>Wassim Abdelli</strong> &nbsp;·&nbsp; PGE 2 Transformation Numérique &amp; Écologique<br>
  <small>Prototype Phase 2 &nbsp;·&nbsp; Python + Streamlit &nbsp;·&nbsp; IA Générative &nbsp;·&nbsp; Données simulées à des fins de démonstration</small>
</div>
""", unsafe_allow_html=True)
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
