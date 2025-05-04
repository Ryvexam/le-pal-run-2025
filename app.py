import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from fetch_data import fetch_results
# Configuration de la page
st.set_page_config(
    layout="wide",
    page_title="Analyse des Résultats de Course",
    page_icon="🏃"
)

# Constantes
CACHE_FILE = "race_data.json"
MIN_PARTICIPANTS_FOR_STATS = 5
API_TIMEOUT = 10  # secondes


def format_timedelta(td: timedelta) -> str:
    """Formater un timedelta en HH:MM:SS"""
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def process_results(data: Dict[str, Any]) -> pd.DataFrame:
    """Traiter les résultats et créer un DataFrame"""
    try:
        results = data['data']['results']
        df = pd.DataFrame([
            {
                'id': r['id'],
                'time': r['time'],
                'ranking': r['ranking'],
                'gender_ranking': r['gender_ranking'],
                'category_ranking': r['category_ranking'],
                'firstname': r['participant']['firstname'],
                'lastname': r['participant']['lastname'],
                'gender': r['participant']['gender'],
                'category': r['participant']['category'],
                'country': r['participant']['country'],
                'club': 'Sans club' if not r['participant']['club'] or r['participant']['club'] == '-' else r['participant']['club'],
                'bib_number': r['participant']['bib_number'],
                'birthdate': r['participant']['birthdate']
            }
            for r in results
        ])
        
        # Convertir le temps en timedelta pour l'analyse
        df['time_timedelta'] = pd.to_timedelta(df['time'])
        
        # Exclure les temps de 00:00:00
        df = df[df['time_timedelta'] > pd.Timedelta(seconds=0)]
        
        # Calculer l'âge et la catégorie
        df['age'] = pd.to_datetime('now').year - pd.to_datetime(df['birthdate']).dt.year
        df['category_detailed'] = df['birthdate'].apply(determine_category)
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du traitement des données: {str(e)}")
        return pd.DataFrame()

def determine_category(birthdate: str) -> str:
    """Déterminer la catégorie en fonction de la date de naissance"""
    if not birthdate:
        return "Inconnu"
    
    try:
        birth_year = pd.to_datetime(birthdate).year
        current_year = datetime.now().year
        age = current_year - birth_year
        
        if birth_year >= 2019:
            return "Baby Athlé (BB)"
        elif 2016 <= birth_year <= 2018:
            return "Éveil Athlétique (EA)"
        elif 2014 <= birth_year <= 2015:
            return "Poussins (PO)"
        elif 2012 <= birth_year <= 2013:
            return "Benjamins (BE)"
        elif 2010 <= birth_year <= 2011:
            return "Minimes (MI)"
        elif 2008 <= birth_year <= 2009:
            return "Cadets (CA)"
        elif 2006 <= birth_year <= 2007:
            return "Juniors (JU)"
        elif 2003 <= birth_year <= 2005:
            return "Espoirs (ES)"
        elif 1991 <= birth_year <= 2002:
            return "Seniors (SE)"
        else:
            # Calcul des catégories Masters
            if birth_year >= 1990:
                return "Masters M0"
            elif 1986 <= birth_year <= 1989:
                return "Masters M0"
            elif 1981 <= birth_year <= 1985:
                return "Masters M1"
            elif 1976 <= birth_year <= 1980:
                return "Masters M2"
            elif 1971 <= birth_year <= 1975:
                return "Masters M3"
            elif 1966 <= birth_year <= 1970:
                return "Masters M4"
            elif 1961 <= birth_year <= 1965:
                return "Masters M5"
            elif 1956 <= birth_year <= 1960:
                return "Masters M6"
            elif 1951 <= birth_year <= 1955:
                return "Masters M7"
            elif 1946 <= birth_year <= 1950:
                return "Masters M8"
            elif 1941 <= birth_year <= 1945:
                return "Masters M9"
            else:
                return "Masters M10"
    except Exception:
        return "Inconnu"

def main():
    # En-tête
    st.title("🏃 Analyse des Résultats de Course")
    
    # Récupérer les données
    data = fetch_results()
    df = process_results(data)
    
    if df.empty:
        st.error("Aucune donnée disponible pour l'analyse.")
        return
    
    # Filtres
    st.subheader("Filtres")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_gender = st.multiselect(
            "Genre",
            options=df['gender'].unique(),
            default=df['gender'].unique(),
            help="Sélectionnez un ou plusieurs genres"
        )
    
    with col2:
        selected_category = st.multiselect(
            "Catégorie",
            options=df['category_detailed'].unique(),
            default=df['category_detailed'].unique(),
            help="Sélectionnez une ou plusieurs catégories"
        )
    
    with col3:
        selected_club = st.multiselect(
            "Club",
            options=df['club'].unique(),
            default=df['club'].unique(),
            help="Sélectionnez un ou plusieurs clubs"
        )
    
    # Appliquer les filtres
    filtered_df = df[
        (df['gender'].isin(selected_gender)) & 
        (df['category_detailed'].isin(selected_category)) &
        (df['club'].isin(selected_club))
    ]
    
    # Statistiques générales
    st.subheader("📊 Statistiques Générales")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total des Participants", len(filtered_df))
    with col2:
        st.metric("Catégories", filtered_df['category_detailed'].nunique())
    with col3:
        st.metric("Pays", filtered_df['country'].nunique())
    with col4:
        st.metric("Clubs", filtered_df['club'].nunique())
    
    # Statistiques par âge
    st.subheader("📊 Statistiques par Âge")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Âge Moyen", f"{filtered_df['age'].mean():.1f} ans")
    with col2:
        st.metric("Âge Minimum", f"{filtered_df['age'].min()} ans")
    with col3:
        st.metric("Âge Maximum", f"{filtered_df['age'].max()} ans")
    
    # Distribution des âges
    st.subheader("📈 Distribution des Âges")
    fig_age = px.histogram(
        filtered_df,
        x='age',
        nbins=50,
        title="Distribution des Âges des Participants",
        labels={'age': 'Âge', 'count': 'Nombre de Participants'}
    )
    st.plotly_chart(fig_age, use_container_width=True)
    
    # Distribution des catégories
    st.subheader("🏆 Distribution des Catégories")
    category_counts = filtered_df['category_detailed'].value_counts()
    fig_category = px.bar(
        x=category_counts.index,
        y=category_counts.values,
        title="Nombre de Participants par Catégorie",
        labels={'x': 'Catégorie', 'y': 'Nombre de Participants'}
    )
    fig_category.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_category, use_container_width=True)
    
    # Performance par catégorie d'âge
    st.subheader("⏱️ Performance par Catégorie d'Âge")
    age_category_perf = filtered_df.groupby('category_detailed').agg({
        'time_timedelta': ['count', 'mean', 'median'],
        'id': 'count'
    }).reset_index()
    age_category_perf.columns = ['Catégorie', 'Participants', 'Temps Moyen', 'Temps Médian', 'id']
    age_category_perf = age_category_perf[age_category_perf['Participants'] >= MIN_PARTICIPANTS_FOR_STATS]
    age_category_perf['Temps Moyen'] = age_category_perf['Temps Moyen'].apply(format_timedelta)
    age_category_perf['Temps Médian'] = age_category_perf['Temps Médian'].apply(format_timedelta)
    age_category_perf['time_seconds'] = age_category_perf['Temps Moyen'].apply(lambda x: pd.Timedelta(x).total_seconds())
    
    fig_age_perf = px.line(
        age_category_perf,
        x='Catégorie',
        y='time_seconds',
        title=f"Temps Moyen par Catégorie d'Âge (min. {MIN_PARTICIPANTS_FOR_STATS} participants)",
        markers=True,
        labels={'time_seconds': 'Temps Moyen', 'Catégorie': 'Catégorie'},
        custom_data=['Temps Moyen', 'Temps Médian']
    )
    fig_age_perf.update_traces(
        hovertemplate="<br>".join([
            "Catégorie: %{x}",
            "Temps Moyen: %{customdata[0]}",
            "Temps Médian: %{customdata[1]}",
            "Nombre de Participants: %{customdata[2]}"
        ])
    )
    fig_age_perf.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_age_perf, use_container_width=True)
    
    # Détail des performances par catégorie
    st.subheader("📊 Détail des Performances par Catégorie")
    age_category_stats = filtered_df.groupby('category_detailed').agg({
        'time_timedelta': ['count', 'mean', 'median', 'min', 'max'],
        'age': 'mean'
    }).reset_index()
    age_category_stats.columns = ['Catégorie', 'Participants', 'Temps Moyen', 'Temps Médian', 'Meilleur Temps', 'Temps Max', 'Âge Moyen']
    age_category_stats = age_category_stats[age_category_stats['Participants'] >= MIN_PARTICIPANTS_FOR_STATS]
    age_category_stats['Temps Moyen'] = age_category_stats['Temps Moyen'].apply(format_timedelta)
    age_category_stats['Temps Médian'] = age_category_stats['Temps Médian'].apply(format_timedelta)
    age_category_stats['Meilleur Temps'] = age_category_stats['Meilleur Temps'].apply(format_timedelta)
    age_category_stats['Temps Max'] = age_category_stats['Temps Max'].apply(format_timedelta)
    age_category_stats['Âge Moyen'] = age_category_stats['Âge Moyen'].round(1)
    
    st.dataframe(
        age_category_stats[['Catégorie', 'Participants', 'Âge Moyen', 'Temps Moyen', 'Temps Médian', 'Meilleur Temps', 'Temps Max']],
        use_container_width=True
    )
    
    # Meilleurs performeurs
    st.subheader("🏅 Meilleurs Performeurs")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Top 10 Général")
        top_10 = filtered_df.nsmallest(10, 'time_timedelta')
        top_10['time'] = top_10['time_timedelta'].apply(format_timedelta)
        st.dataframe(
            top_10[['firstname', 'lastname', 'time', 'category_detailed', 'country', 'club']],
            use_container_width=True
        )
    
    with col2:
        st.write("Meilleur par Catégorie")
        top_by_category = filtered_df.groupby('category_detailed').apply(
            lambda x: x.nsmallest(1, 'time_timedelta')
        ).reset_index(drop=True)
        top_by_category['time'] = top_by_category['time_timedelta'].apply(format_timedelta)
        st.dataframe(
            top_by_category[['firstname', 'lastname', 'time', 'category_detailed', 'country', 'club']],
            use_container_width=True
        )
    
    # Performance des clubs
    st.subheader("🏢 Performance des Clubs")
    club_stats = filtered_df.groupby('club').agg({
        'time_timedelta': ['count', 'mean', 'median', 'min'],
        'category_detailed': 'nunique'
    }).reset_index()
    club_stats.columns = ['Club', 'Participants', 'Temps Moyen', 'Temps Médian', 'Meilleur Temps', 'Catégories']
    club_stats = club_stats[club_stats['Participants'] >= 1]
    club_stats = club_stats.sort_values('Temps Moyen')
    club_stats['Temps Moyen'] = club_stats['Temps Moyen'].apply(format_timedelta)
    club_stats['Temps Médian'] = club_stats['Temps Médian'].apply(format_timedelta)
    club_stats['Meilleur Temps'] = club_stats['Meilleur Temps'].apply(format_timedelta)
    
    # Créer le podium
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Premier
    with col2:
        if len(club_stats) > 0:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <h2>🥇</h2>
                    <h3>{club_stats.iloc[0]['Club']}</h3>
                    <p>{club_stats.iloc[0]['Participants']} participants</p>
                    <p>Temps moyen: {club_stats.iloc[0]['Temps Moyen']}</p>
                    <p>Temps médian: {club_stats.iloc[0]['Temps Médian']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Deuxième
    with col1:
        if len(club_stats) > 1:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <h2>🥈</h2>
                    <h3>{club_stats.iloc[1]['Club']}</h3>
                    <p>{club_stats.iloc[1]['Participants']} participants</p>
                    <p>Temps moyen: {club_stats.iloc[1]['Temps Moyen']}</p>
                    <p>Temps médian: {club_stats.iloc[1]['Temps Médian']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Troisième
    with col3:
        if len(club_stats) > 2:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <h2>🥉</h2>
                    <h3>{club_stats.iloc[2]['Club']}</h3>
                    <p>{club_stats.iloc[2]['Participants']} participants</p>
                    <p>Temps moyen: {club_stats.iloc[2]['Temps Moyen']}</p>
                    <p>Temps médian: {club_stats.iloc[2]['Temps Médian']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Liste de tous les clubs
    st.subheader("Classement Complet des Clubs")
    st.dataframe(
        club_stats[['Club', 'Participants', 'Temps Moyen', 'Temps Médian', 'Meilleur Temps', 'Catégories']],
        use_container_width=True
    )

if __name__ == "__main__":
    main() 