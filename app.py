
import streamlit as st
import pandas as pd
import json
import pathlib

st.set_page_config(page_title="Dashboard Match", layout="wide")

DATA_DIR = pathlib.Path("data")

# Load data
stats = json.load(open(DATA_DIR / "match_stats.json", "r"))
events = pd.read_csv(DATA_DIR / "events.csv")
players = pd.read_csv(DATA_DIR / "players.csv")
team_stats = pd.read_csv(DATA_DIR / "team_stats.csv")
player_stats = pd.read_csv(DATA_DIR / "player_stats.csv")

st.title(f"{stats['teams']['home']} vs {stats['teams']['away']} — Dashboard")

# Tabs
tab_match, tab_team, tab_player = st.tabs(["🏟️ Match", "👥 Équipe", "🧍 Joueur"])

with tab_match:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", f"{stats['score']['home']} - {stats['score']['away']}")
    c2.metric(f"Possession {stats['teams']['home']}", f"{stats['possession']['home_pct']:.1f}%")
    c3.metric(f"Tirs (cadrés) {stats['teams']['home']}", f"{stats['shots']['home']} ({stats['shots_on']['home']})")
    c4.metric(f"Tirs (cadrés) {stats['teams']['away']}", f"{stats['shots']['away']} ({stats['shots_on']['away']})")

    st.markdown("### Chronologie des événements")
    st.dataframe(events, use_container_width=True, height=260)

    st.markdown("### Heatmap (équipe à domicile)")
    home_heat = DATA_DIR / "heatmap_home.png"
    if home_heat.exists():
        st.image(str(home_heat), use_column_width=True, caption="Zones les plus occupées (domicile)")
    else:
        st.info("Aucune heatmap d'équipe trouvée (heatmap_home.png).")

    st.markdown("### Joueurs en vue")
    top = pd.DataFrame(stats.get("top_players", []))
    if not top.empty:
        st.table(top)
    else:
        st.caption("Aucun top joueur défini dans match_stats.json.")

with tab_team:
    st.subheader("Statistiques par équipe")
    st.dataframe(team_stats, use_container_width=True)
    st.caption("Complétez ces colonnes (xG, PPDA, field tilt, etc.) lorsque votre pipeline les calcule.")

with tab_player:
    st.subheader("Fiche joueuse")
    # Sélection équipe -> joueuse
    if "team" in player_stats.columns:
        teams = sorted(player_stats["team"].dropna().unique().tolist())
    else:
        teams = sorted(players["team"].dropna().unique().tolist())

    team_selected = st.selectbox("Choisir une équipe", teams)
    df_team = player_stats[player_stats["team"] == team_selected]
    # fallback si player_stats ne contient pas toutes les joueuses
    if df_team.empty:
        df_team = players[players["team"] == team_selected].copy()
        # colonnes manquantes
        for col in ["minutes","distance_km","shots","shots_on","goals","assists","passes","player_id"]:
            if col not in df_team.columns:
                df_team[col] = 0

    player_selected = st.selectbox("Choisir une joueuse", df_team["name"].tolist())
    row = df_team[df_team["name"] == player_selected].squeeze()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Minutes", int(row.get("minutes", 0)))
    c2.metric("Distance (km)", f"{float(row.get('distance_km', 0)):.1f}")
    c3.metric("Tirs (cadrés)", f"{int(row.get('shots', 0))} ({int(row.get('shots_on', 0))})")
    c4.metric("Buts", int(row.get("goals", 0)))
    c5.metric("Passes", int(row.get("passes", 0)))

    # Heatmap individuelle
    pid = int(row.get("player_id", 0)) if "player_id" in row else 0
    heat_path = DATA_DIR / f"heatmap_player_{pid}.png"
    if pid and heat_path.exists():
        st.image(str(heat_path), caption=f"Heatmap — {player_selected}", use_column_width=True)
    else:
        st.caption("Aucune heatmap individuelle trouvée pour cette joueuse (fichier heatmap_player_{player_id}.png).")

    st.markdown("### Détails bruts")
    st.dataframe(df_team[df_team["name"] == player_selected], use_container_width=True)

st.markdown("---")
st.caption("Version démo. Remplacez le contenu de data/ par vos sorties réelles (pipeline YOLO + calculs).")
