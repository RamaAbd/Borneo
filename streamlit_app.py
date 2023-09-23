
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim, GeocoderTimedOut
from geopy.distance import geodesic
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
from shapely.geometry import Polygon
import time
import numpy as np
from plotly.subplots import make_subplots
import urllib.request
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from PIL import Image
import requests

# Charger les données
def load_data():
    data_region = pd.read_csv("https://www.data.gouv.fr/fr/datasets/r/dbe8a621-a9c4-4bc3-9cae-be1699c5ff25", usecols=['code_commune_INSEE', 'nom_commune', 'nom_departement', 'nom_region'])
    data = pd.read_csv("https://www.data.gouv.fr/fr/datasets/r/8d9398ae-3037-48b2-be19-412c24561fbb", low_memory=False)
    data.rename(columns={'code_insee_commune': 'code_commune_INSEE'}, inplace=True)
    merged_data = pd.merge(data, data_region, on='code_commune_INSEE', how='left')
    merged_data['date_mise_en_service'] = pd.to_datetime(merged_data['date_mise_en_service'], errors="coerce")
    merged_data["year"] = merged_data["date_mise_en_service"].dt.strftime('%Y')
    merged_data = merged_data[merged_data['year'] >= '2015']
    merged_data= merged_data.drop_duplicates(subset='nom_station')

    merged_data['nom_amenageur'] = merged_data['nom_amenageur'].replace({
        'Reveo': 'Révéo',
        'INDIGO FRANCE': 'Indigo',
        'TotalEnergies Marketing France': 'TotalEnergies',
        'Total RÃ©union': 'TotalEnergies',
        'TOYOTA': 'Toyota',
        'KIA': 'Kia',
        'MABORNEAUTO': 'MA BORNE AUTO',
        'ma borne auto': 'MA BORNE AUTO',
        'MAZDA': 'Mazda'
    })
    merged_data['nom_enseigne'] = merged_data['nom_enseigne'].replace({
        'Reveo': 'Révéo',
        'INDIGO FRANCE': 'Indigo',
        'TotalEnergies Marketing France': 'TotalEnergies',
        'Total RÃ©union': 'TotalEnergies',
    })
    merged_data['reservation'] = merged_data['reservation'].replace({
        'false': 'False',
        'true': 'True',
    })
    merged_data['paiement_acte'] = merged_data['paiement_acte'].replace({
        'false': 'False',
        'true': 'True',
    })
    merged_data['gratuit'] = merged_data['gratuit'].replace({
        'false': 'False',
        'true': 'True',
    })


    # Calculer le nombre de stations par groupe 'nom_station'
    merged_data['nbre_station'] = merged_data.groupby('nom_station')['nom_station'].transform('count')
    merged_data["year"] = merged_data["date_mise_en_service"].dt.strftime('%Y')
    bool_mapping = {True: 'Oui', False: 'Non', 'true': 'Oui', 'false': 'Non'}

    return merged_data

data = load_data()
# Pour la Page de bienvenue avec barre de progression
progress_bar = st.progress(0)
status_text = st.empty()
for i in range(101):
    progress_bar.progress(i)
    time.sleep(0.00025)
    if i == 100:
        status_text.text("Chargement terminé !")
    else:
        status_text.text(f"Chargement en cours. Veuillez patienter un instant ⏳... {i}%")

# Charger le logo
logo = Image.open("C:/Users/amato/Business_Intelligence/Streamlit/Borneo_Logo.png")

# Afficher le logo dans la barre de navigation
st.sidebar.image(logo, use_column_width=True, width=75)
# Menu de navigation
menu = st.sidebar.selectbox("**Menu**", ["Accueil", "Dashboard", "Emission de co2", "Trouver une borne électrique"])
st.sidebar.markdown("## Course Information")
st.sidebar.markdown("**Course Name**: Business Intelligence")
st.sidebar.markdown("**Year**: 2023")
st.sidebar.markdown("**Course Description**: This is a business intelligence course where we learn about analyzing datasets and showcasing our skills using Streamlit, Python, and analytical techniques.")
st.sidebar.markdown("**Professor**: Mr. Mano MATHEW")

st.sidebar.markdown("**Student**: Ramatou Abdou")
st.sidebar.markdown("[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/ramatou-abdou/)")
st.sidebar.markdown("[![GitHub](https://img.shields.io/badge/-GitHub-black?style=for-the-badge&logo=github)](https://github.com/RamaAbd)")


if menu == "Accueil":
    # Titre de l'application
    st.title("Bienvenue sur Borneo !")
    st.write("Explorez le réseau de bornes de recharge pour véhicules électriques en France et découvrez son impact environnemental.")
    
   # Vidéo d'illustration
    st.video(r"C:\Users\amato\Business_Intelligence\Streamlit\Borneo.mp4", start_time=0)
    import streamlit as st
    from PIL import Image
    import base64

    # Charger les icônes
    with open(r"C:\Users\amato\Business_Intelligence\Streamlit\icons8-home-24.png", "rb") as f:
        icon_home = base64.b64encode(f.read()).decode()

    with open(r"C:\Users\amato\Business_Intelligence\Streamlit\icons8-bar-chart-24.png", "rb") as f:
        icon_dashboard = base64.b64encode(f.read()).decode()

    with open(r"C:\Users\amato\Business_Intelligence\Streamlit\icons8-co2-24.png", "rb") as f:
        icon_co2 = base64.b64encode(f.read()).decode()

    with open(r"C:\Users\amato\Business_Intelligence\Streamlit\icons8-charging-station-24.png", "rb") as f:
        icon_find_station = base64.b64encode(f.read()).decode()

    with open(r"C:\Users\amato\Business_Intelligence\Streamlit\icons8-backhand-index-pointing-left-24.png", "rb") as f:
        icon_left = base64.b64encode(f.read()).decode()

    # Afficher le texte avec les icônes
    st.markdown(
        f"""
        Borneo vous permet d'explorer les données sur les bornes de recharge électrique en France et de les mettre en relation avec les émissions de CO2 par pays. Vous pourrez visualiser l'évolution des émissions de CO2, trouver les stations de recharge les plus proches de vous et prendre des décisions éclairées en faveur d'une mobilité plus durable.

        ### Comment utiliser l'application
        Utilisez le menu de navigation sur la gauche pour accéder aux différentes fonctionnalités de l'application :

        ![Home](data:image/png;base64,{icon_home}) **Accueil** : Obtenez une vue d'ensemble de l'application avec les différentes souces de Dataset.

        ![Dashboard](data:image/png;base64,{icon_dashboard}) **Dashboard** : Consultez les statistiques clés sur les bornes de recharge en France et explorez les graphiques interactifs.

        ![Emission de CO2](data:image/png;base64,{icon_co2}) **Emission de CO2** : Découvrez des visualisations avancées sur les bornes de recharge et les émissions de CO2.

        ![Trouver une borne électrique](data:image/png;base64,{icon_find_station}) **Trouver une borne électrique** : Utilisez votre adresse pour trouver les bornes de recharge les plus proches de vous.

        *Note : Les données sur les émissions de CO2 par pays proviennent d'un autre dataset et ont été mises en relation avec les données sur les bornes de recharge pour une analyse plus complète.*
        """
    )

    st.markdown(
        f"**Prêt à explorer le réseau de bornes de recharge électrique et son impact environnemental ? Utilisez le menu de navigation à gauche ![Flèche gauche](data:image/png;base64,{icon_left}) pour commencer !**"
    )


elif menu == "Dashboard":
    st.subheader("Dashboard")
    st.write("Les statistiques clés sur les bornes de recharge en France.")
    # Appliquer le thème sombre avec un style CSS personnalisé
    st.markdown(
            """
            <style>
            body {
                background-color: #222222;
                color: #FFFFFF;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    data = load_data()
    #premiere visualisation

    # Supprimer les doublons basés sur le nom de la station
    data_unique_stations = data.drop_duplicates(subset='nom_station')
    # Compteur pour afficher le nombre total de stations de recharge électrique en France
    nombre_stations_france = len(data_unique_stations)

    # Compteur pour afficher le nombre total de points de charge en France
    nombre_pdc_france = data_unique_stations['nbre_pdc'].sum()

    # Couleur utilisée dans le graphe d'évolution par années pour les stations de recharge
    stations_color = 'rgb(15, 67, 67)'

    # Couleur utilisée dans le graphe d'évolution par années pour les points de charge
    pdc_color = 'rgb(255, 101 ,0)'

    # Création du compteur 1 (Total des stations de recharge de VE) avec la couleur correspondante
    fig1 = go.Figure(go.Indicator(
        mode="number",
        value=nombre_stations_france,
        title={'text': "Stations de recharge pour VE", 'font': {'color': stations_color}},
        number={'suffix': " stations", 'font': {'color': stations_color}},
        number_font={'size': 20, 'family': 'Arial'},
        title_font={'size': 15, 'family': 'Arial'},
    ))
    fig1.update_layout(height=130)

    # Création du compteur 2 (Total EV Charging Points) avec la couleur correspondante
    fig2 = go.Figure(go.Indicator(
        mode="number",
        value=nombre_pdc_france,
        title={'text': "Points de charge pour VE", 'font': {'color': pdc_color}},
        number={'suffix': " points", 'font': {'color': pdc_color}},
        number_font={'size': 20, 'family': 'Arial'},
        title_font={'size': 15, 'family': 'Arial'},
    ))
    fig2.update_layout(height=130)

    # Création du graphique d'évolution par années
    stations_by_year = data_unique_stations.groupby('year').size().reset_index(name='count').astype(int)

    pdc_by_year = data_unique_stations.groupby('year')['nbre_pdc'].sum().reset_index(name='sum_pdc')
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=stations_by_year['year'], y=stations_by_year['count'], mode='lines+markers', name='EV Charging Stations', marker_color='rgb(43, 140, 190)'))
    fig3.add_trace(go.Scatter(x=pdc_by_year['year'], y=pdc_by_year['sum_pdc'], mode='lines+markers', name='Charging Points', marker_color='rgb(216, 99, 99)'))

    fig3.update_layout(title='Evolution des stations et points de recharge pour VE par année', xaxis_title='Year', yaxis_title='Count')
    fig3.update_layout(height=400, width=800)

    # Affichage des compteurs et du graphique
    col1, col2 = st.columns([1, 3])

    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr style='border:1px solid #f0f0f0'>", unsafe_allow_html=True)

   # Afficher la visualisation
    st.subheader("Comparaison de l'évolution du nombre de points de recharge entre régions")

    # Définir la valeur par défaut de la variable region
    regions = data['nom_region'].dropna().unique()
    default_region = "Île-de-France"
    region = [default_region] if default_region in data['nom_region'].unique() else []

    # Affichage du checkbox pour filtrer par région
    checkbox_region = st.checkbox("Filtrer par région")

    # Filtrer les données par région si une région a déjà été sélectionnée
    if checkbox_region:
        selected_regions = st.multiselect("Sélectionnez les régions", regions, default=region, key="regions")
        data_by_region = data[data['nom_region'].isin(selected_regions)]
    else:
        data_by_region = data

    # Supprimer les doublons basés sur le nom de la station
    data_unique_stations_by_region = data_by_region.drop_duplicates(subset='nom_station')

    # Convertir la colonne 'year' en entier
    data_unique_stations_by_region['year'] = data_unique_stations_by_region['year'].astype(int)
    # Convertir les valeurs de min_year et max_year en int
    min_year = int(data_unique_stations_by_region['year'].min())
    max_year = int(data_unique_stations_by_region['year'].max())

    # Demander à l'utilisateur de sélectionner la période
    start_year, end_year = st.slider("Sélectionnez la période", min_value=min_year, max_value=max_year, value=(min_year, max_year))

    # Filtrer les données en fonction de la période sélectionnée
    filtered_data_points_charge = data_unique_stations_by_region[(data_unique_stations_by_region['year'] >= start_year) & (data_unique_stations_by_region['year'] <= end_year)]

    # Group by année et effectuer la somme des nbre_pdc
    grouped_data = filtered_data_points_charge.groupby(['year', 'nom_region'])['nbre_pdc'].sum().reset_index()

    # Remplacer les valeurs manquantes par une valeur par défaut (par exemple, 0)
    grouped_data['nbre_pdc'] = grouped_data['nbre_pdc'].fillna(0)

    # Convertir la colonne en entier
    grouped_data['nbre_pdc'] = grouped_data['nbre_pdc'].astype(int)

    # Demander à l'utilisateur de sélectionner le type de visualisation
    visualization_type = st.selectbox("Sélectionnez le type de visualisation", ["Ligne", "Barre", "Aire"])

    # Réaliser la visualisation en fonction du type sélectionné
    if visualization_type == "Ligne":
        fig = px.line(grouped_data, x='year', y='nbre_pdc', color='nom_region',
                    title="Évolution du nombre de points de charge par région",
                    labels={'year': 'Année', 'nbre_pdc': 'Nombre de points de charge'})
    elif visualization_type == "Barre":
        fig = px.bar(grouped_data, x='year', y='nbre_pdc', color='nom_region',
                    title="Évolution du nombre de points de charge par région",
                    labels={'year': 'Année', 'nbre_pdc': 'Nombre de points de charge'})
    elif visualization_type == "Aire":
        fig = px.area(grouped_data, x='year', y='nbre_pdc', color='nom_region',
                    title="Évolution du nombre de points de charge par région",
                    labels={'year': 'Année', 'nbre_pdc': 'Nombre de points de charge'})

    # Afficher la visualisation
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<hr style='border:1px solid #f0f0f0'>", unsafe_allow_html=True)

    # Les acteurs du marché
    st.subheader("L'industrie des Infrastructures de Recharge pour Véhicule Électrique")
    st.write("Ces visualisations fournissent des informations clés sur les acteurs du marché,tels que les aménageurs, les enseignes et les opérateurs.")
    # Description pour le graphique en barres horizontales - Top 5 des aménageurs
    # Description pour le graphique en barres horizontales - Top 5 des aménageurs

    # Création de deux colonnes
    col1, col2 = st.columns(2)

    # Première colonne pour le graphique des aménageurs
    with col1:
        # Obtenir les données des acteurs du marché

        top_amenageurs = data['nom_amenageur'].value_counts().head(10)
        st.markdown("**Top 10 des aménageurs**")
        caption = "Ce graphique présente les dix principaux aménageurs en termes du nombre de points de charge."
        st.markdown(caption)  

        # Créer un graphique en barres verticales pour les aménageurs
        fig_amenageurs = go.Figure(go.Bar(
            x=top_amenageurs.index,
            y=top_amenageurs.values,
            marker=dict(color='seagreen'),
            hovertemplate='%{y} Nombre de point de charge <br>%{x}<extra></extra>',
        ))
        fig_amenageurs.update_layout(
            title=(''),
            xaxis_title='Aménageur',
            yaxis_title='Nombre de point de charge',
        )
        # Afficher le graphique des aménageurs avec la description
        st.plotly_chart(fig_amenageurs, use_container_width=True)

    # Deuxième colonne pour le graphique des enseignes
    with col2:
        # Obtenir les données des aménageurs
        st.markdown("**Top 10 des enseignes**")
        top_enseigne = data['nom_enseigne'].value_counts().head(10)
        caption = "Ce graphique présente les dix principales enseignes en termes du nombre de points de charge."
        st.markdown(caption)  
        # Créer un graphique à secteurs pour les enseigne
        fig_enseignes = go.Figure(go.Pie(
            labels=top_enseigne.index,
            values=top_enseigne.values,
            hole=0.4,
            marker=dict(colors=['rgb(15, 67, 67)', 'rgb(227, 167, 71)', 'rgb(117, 189, 100)', 'rgb(255, 101 ,0)', 'rgb(151, 240, 201)',
                                'rgb(255, 194, 102)', 'rgb(48, 139, 87)', 'rgb(91, 192, 222)', 'rgb(255, 165, 0)', 'rgb(0, 139, 139)']),
            hovertemplate='%{label}<br>%{value} Nombre de points de charge<br>%{percent}<extra></extra>',
            direction='clockwise',
        ))
        fig_enseignes.update_layout(
            title='',
        )
        # Afficher le graphique des aménageurs avec la description
        st.plotly_chart(fig_enseignes, use_container_width=True)

    # Création de deux colonnes
    col1, col2 = st.columns(2)

    # Première colonne pour le graphique des opérateurs
    with col1:
        # Obtenir les données des opérateurs
        top_operateurs = data['nom_operateur'].value_counts().head(10)

        # Créer un graphique en nuage de points pour les opérateurs
        fig_operateurs = go.Figure(data=[go.Scatter(
            x=top_operateurs.values,
            y=top_operateurs.index,
            mode='markers',
            marker=dict(
                size=10,
                color=top_operateurs.values,
                colorscale='Viridis',
                opacity=0.8,
            ),
            hovertemplate='%{y}<br>Nombre de points de charge: %{x}<extra></extra>',
        )])

        # Personnaliser l'axe des x et y
        fig_operateurs.update_layout(
            title='',
            xaxis_title='Nombre de points de charge',
            yaxis_title='Opérateur',
        )

        # Afficher le graphique en nuage de points des opérateurs avec la description
        st.markdown("**Top 10 des opérateurs**")
        caption = "Ce graphique présente les dix principaux opérateurs en fonction du nombre de points de charge."
        st.markdown(caption)
        st.plotly_chart(fig_operateurs, use_container_width=True)

    # Deuxième colonne pour le nuage de mots
    with col2:
        st.markdown("**Nuage de mots des acteurs principaux**")
        data = data.dropna(subset=['nom_amenageur'])
        caption = ("Ce nuage de mots représente les principaux acteurs en combinant les noms des aménageurs, des enseignes et des opérateurs.")
        st.markdown(caption)  
        amenageurs = data['nom_amenageur'] + ' ' + data['nom_enseigne'].fillna('') + ' ' + data['nom_operateur'].fillna('')
        wordcloud = WordCloud(width=800, height=600, background_color='white').generate(' '.join(amenageurs.astype(str)))
        st.image(wordcloud.to_array(), caption='Nuage de mots des acteurs principaux')
    st.markdown("<hr style='border:1px solid #f0f0f0'>", unsafe_allow_html=True)

    st.header("Caractéristiques des points de recharges de véhicules électrique")
    st.write("Cette section présente différentes caractéristiques des points de recharge de véhicules électriques.")
    # Création de deux colonnes
    col1, col2 = st.columns(2)

    # Première colonne pour le graphique de paiement
    with col1:
        # Liste des colonnes à convertir
        cols_to_convert = ['paiement_acte', 'paiement_cb', 'paiement_autre']
        st.markdown("**Les différents moyens de paiement**")

        caption = "Ce graphique représente les différents moyens de paiement des points de recharge de véhicules électriques."
        st.markdown(caption)    
        # Convertir les colonnes
        data = data_unique_stations
        for col in cols_to_convert:
            # Remplacer les chaînes 'true'/'false' par True/False
            data[col] = data[col].replace({'true': True, 'false': False})
            # Remplir les valeurs manquantes par False
            data[col].fillna(False, inplace=True)
            # Convertir en booléen
            data[col] = data[col].astype(bool)

        # Effectuer le compte des colonnes
        paiement_counts = data[cols_to_convert].sum().reset_index()
        paiement_counts.columns = ['Type de paiement', 'Nombre total']
        colors = ['#97f0c9', '#ff6500', '#0F4343']

        # Créer le graphique Donut 3D avec étiquettes
        fig_paiement = go.Figure(data=[
            go.Pie(
                labels=paiement_counts['Type de paiement'],
                values=paiement_counts['Nombre total'],
                hole=0.5,
                marker=dict(colors=['#97f0c9', '#ff6500', '#0F4343']),
                name='Type de paiement',
                hoverinfo='label+percent+name',
                textinfo='label+percent',  # Ajout des étiquettes
                textfont=dict(size=12)
            )
        ])

        fig_paiement.update_layout(
            title='',
            height=400
        )

        # Afficher le graphique
        st.plotly_chart(fig_paiement, use_container_width=True)

    # Deuxième colonne pour le graphique de type de prise
    with col2:
        cols_to_convert = ['prise_type_ef', 'prise_type_2', 'prise_type_combo_ccs', 'prise_type_chademo']
        st.markdown("**Répartition des différents types de prises**")

        caption = "Cette visualisation présente le nombre total de points de recharge par type de prise."
        st.markdown (caption)
        for col in cols_to_convert:
            data[col] = data[col].map({'true': True, 'false': False})
            data[col].fillna(0, inplace=True)
            data[col] = data[col].astype(int).astype(float)

        connector_totals = data[cols_to_convert].sum()

        df_visualization = connector_totals.transpose().reset_index()
        df_visualization.columns = ['Type de prise', 'Nombre total']

        fig_total_prise = px.bar(df_visualization, x='Type de prise', y='Nombre total', color='Type de prise',
                                color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_total_prise.update_layout(title='', height=400)

        st.plotly_chart(fig_total_prise, use_container_width=True)
    
    st.markdown("**Répartition des implantations de stations de recharge**")
    caption = "Le treemap ci-dessous représente la répartition des implantations de stations de recharge en fonction du nombre de stations dans chaque catégorie."
    st.markdown(caption)
    # Compter le nombre d'occurrences de chaque valeur dans la colonne "implantation_station"
    implantation_counts = data['implantation_station'].value_counts().reset_index()
    implantation_counts.columns = ['Implantation', 'Nombre de stations']
    # Calculer le pourcentage du total
    implantation_counts['Pourcentage'] = 100 * implantation_counts['Nombre de stations'] / implantation_counts['Nombre de stations'].sum()

    # Créer le treemap avec pourcentage dans le label
    fig_implantation = px.treemap(implantation_counts, path=['Implantation'], values='Nombre de stations',
                            title='',
                            color='Implantation',
                            hover_data=['Pourcentage'],
                            custom_data=['Implantation'])  # Ajout de l'argument custom_data

    fig_implantation.update_traces(textinfo='label+percent entry')

    fig_implantation.update_layout(height=700)

    # Afficher le treemap avec le type d'implantation en légende
    st.plotly_chart(fig_implantation, use_container_width=True)
    # Création de deux colonnes
    col1, col2 = st.columns(2)

    # Première colonne pour la visualisation de l'accessibilité PMR
    with col1:
        st.markdown("**Visualisation de l'accessibilité PMR**")

        # Préparation des données
        pmr_access = data[data['accessibilite_pmr'] != 'Accessibilité inconnue']
        pmr_access_counts = pmr_access['accessibilite_pmr'].value_counts()

        # Création de la figure
        fig_pmr = go.Figure(
            go.Bar(
                x=pmr_access_counts.index,
                y=pmr_access_counts.values,
                marker=dict(color='orangered'),
                hovertemplate='%{y} Points de charge <br>%{x}<extra></extra>',
            ))

        fig_pmr.update_layout(
            title='',
            xaxis_title='Accessibilité PMR',
            yaxis_title='Nombre de points de charge',
            
        )
        caption = "Ce graphique montre la répartition de l'accessibilité PMR (Personnes à Mobilité Réduite) pour les points de charge, à l'exception des points de charge où l'accessibilité est inconnue."
        st.markdown(caption)
        # Afficher le graphique
        st.plotly_chart(fig_pmr, use_container_width=True)


    # Deuxième colonne pour la visualisation des plages horaires
    with col2:
        st.markdown("**Visualisation des plages horaires**")

        def categorize_hours(hours):
            if any(time in hours for time in ['24/7', '00:00-23:59']):
                return 'Tout le temps (24/7)'
            else:
                return 'Autres'

        # Nettoyer et formater les données de la colonne 'horaires'
        data['horaires'] = data['horaires'].str.strip()  # Supprimer les espaces blancs en début et en fin de chaîne
        data['horaires'] = data['horaires'].apply(categorize_hours)  # Categoriser les heures

        # Calculer le compte des différentes catégories
        hour_category_counts = data['horaires'].value_counts()
        # Création de la figure
        fig_hours = go.Figure(
            data=go.Pie(
                labels=hour_category_counts.index,
                values=hour_category_counts.values,
                hovertemplate='%{value} Points de charge <br>%{label}<extra></extra>',
                marker=dict(colors=['#0F4343', '#ff6500']),
            )
        )

        fig_hours.update_layout(
            title='',
        )


        # Afficher le graphique
        caption = "Ce graphique montre la répartition des plages horaires pour les points de charge."
        st.markdown(caption)
        st.plotly_chart(fig_hours, use_container_width=True)

    # Créer le DataFrame des capacités
    Cap = pd.DataFrame({
        'annee': [2021, 2022, 2023],
        'Lente (P < 7,4kW)': [19718, 29259, 33914],
        'Moyenne (7,4 kW à 22 kW)': [30077, 44320, 52294],
        'Rapide (P > 22kW)': [1227, 1518, 1539]
    })
    st.markdown("**Evolution du nombre de points de recharge selon leur vitesse de recharge**")
    st.markdown("Cette visualisation présente l'évolution du nombre de points de recharge en fonction de leur vitesse de recharge sur les années 2021, 2022 et 2023.")
    # Créer la figure
    fig = px.bar(Cap, x='annee', y=['Lente (P < 7,4kW)',
                                    'Moyenne (7,4 kW à 22 kW)',
                                    'Rapide (P > 22kW)'],
                barmode='group')

    # Définir les couleurs pour chaque catégorie
    colors = ['#97f0c9', '#ff6500', '#0F4343']

    # Mettre à jour les couleurs des barres pour chaque catégorie
    for i, color in enumerate(colors):
        fig.data[i].marker.color = color

    # Mettre à jour le layout de la visualisation
    fig.update_layout(
        xaxis_title='Année',
        yaxis_title='Nombre de points de recharge',
        title="",
        height=400
    )

    # Afficher la visualisation
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("<hr style='border:1px solid #f0f0f0'>", unsafe_allow_html=True)


    st.subheader("Répartition des stations et des points de charge pour VE en France")
    st.write("")
    # Calculer le nombre de points de charge par région
    region_counts = data['nom_region'].value_counts().reset_index()
    region_counts.columns = ['Région', 'Nombre de points de charge']

    # Charger les données géographiques des régions françaises
    regions_geojson = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions-version-simplifiee.geojson'
    st.markdown("**Répartition du nombre de points de charge par région en France**")
    st.markdown("Certaines régions ont un nombre négligeable de stations de recharge, tandis que d'autres en ont un nombre considérable. Ces résultats soulignent l'inégalité actuelle de l'infrastructure de recharge en France, nécessitant un développement plus équilibré pour soutenir la mobilité électrique à l'échelle nationale.")

    # Créer la carte Folium pour la répartition par région
    m_region = folium.Map(location=[46.603354, 1.888334], zoom_start=6, tiles='Stamen Terrain')

    # Ajouter la carte choroplèthe
    folium.Choropleth(
        geo_data=regions_geojson,
        name='Choroplèthe',
        data=region_counts,
        columns=['Région', 'Nombre de points de charge'],
        key_on='feature.properties.nom',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Nombre de points de charge',
    ).add_to(m_region)

    # Créer la carte Folium pour la localisation des stations de recharge
    m_localisation = folium.Map(location=[46.603354, 1.888334], zoom_start=8, tiles="Stamen Terrain", control_scale=True)
    # Appliquer le mode nuit à la carte
    folium.TileLayer("CartoDB dark_matter").add_to(m_localisation)

    # Créer un groupe de marqueurs pour les stations de recharge
    marker_cluster = MarkerCluster().add_to(m_localisation)

    # Ajouter des marqueurs pour chaque station de recharge avec les coordonnées
    for _, row in data_unique_stations.iterrows():
        folium.Marker(
            location=[row["consolidated_latitude"], row["consolidated_longitude"]],
            popup=row["nom_station"],
            icon=folium.Icon(color="green", prefix="fa", icon="plug")
        ).add_to(marker_cluster)

    # Afficher les deux cartes dans Streamlit avec une largeur fixe de 800 pixels
    col1, col2 = st.columns(2)
    with col1:
        folium_static(m_region, width=600, height=600)
    with col2:
        folium_static(m_localisation, width=600, height=600)


    st.subheader("Conclusion")
    st.write("Le dashboard fournit des statistiques clés sur les bornes de recharge en France, "
                "y compris le nombre total de stations et de points de charge, "
                "l'évolution par années, les acteurs du marché, les caractéristiques des points de recharge, "
                "la répartition géographique et la localisation des stations de recharge. ")
    st.write("Ces informations sont essentielles pour comprendre l'état actuel de l'infrastructure de recharge "
                "pour les véhicules électriques en France et pour soutenir le développement de la mobilité électrique.")


elif menu == "Emission de co2":
    import pandas as pd
    # Charger les données
    dataC = pd.read_excel(r"C:\Users\amato\OneDrive\Documents\Modèles Office personnalisés\co2.xltx")
    dataC = dataC.rename(columns={'Annual COâ‚‚ emissions (per capita)': 'Annual CO₂ emissions (per capita)'})

    # Filtrer les entités incorrectes (continents et catégories de pays)
    continents = ['Africa', 'Asia', 'Europe', 'North America', 'Oceania', 'South America']
    countries = dataC[~dataC['Entity'].isin(continents)]
    income_groups = dataC[dataC['Entity'].isin(['Low income', 'Lower-middle income', 'Upper-middle income', 'High income'])]

    # Créer une catégorie 'Autres' pour regrouper les pays restants
    other_countries = dataC[~dataC['Entity'].isin(countries['Entity']) & ~dataC['Entity'].isin(income_groups['Entity'])]
    other_countries = other_countries.groupby('Year')['Annual CO₂ emissions (per capita)'].sum().reset_index()
    other_countries['Entity'] = 'Autres'
    
    # Demander à l'utilisateur de sélectionner les pays
    selected_countries = st.multiselect("Sélectionnez les pays", dataC[~dataC['Entity'].isin(dataC[dataC['Code'].isnull()]['Entity'].unique())]['Entity'].unique())


    # Convertir la colonne 'Year' en entier et gérer les valeurs manquantes
    dataC['Year'] = dataC['Year'].fillna(0).astype(int)

    # Obtenir la plage de dates disponibles dans les données filtrées
    min_year = int(dataC['Year'].min())
    max_year = int(dataC['Year'].max())

    # Demander à l'utilisateur de sélectionner la période
    start_year, end_year = st.slider("Sélectionnez la période", min_value=min_year, max_value=max_year, value=(min_year, max_year))

    # Filtrer les données en fonction de la période sélectionnée
    filtered_data = dataC[(dataC['Year'] >= start_year) & (dataC['Year'] <= end_year)]
    # Filtrer les données en fonction des pays sélectionnés
    filtered_data = dataC[dataC['Entity'].isin(selected_countries)]
    # Demander à l'utilisateur de sélectionner le type de visualisation
    visualization_type = st.selectbox("Sélectionnez le type de visualisation", ["Ligne", "Barre"])

    # Réaliser la visualisation en fonction du type sélectionné
    if visualization_type == "Ligne":
        fig = px.line(filtered_data, x='Year', y='Annual CO₂ emissions (per capita)', color='Entity',
                    title="Évolution des émissions de CO₂ par pays",
                    labels={'Year': 'Année', 'Annual CO₂ emissions (per capita)': 'Émissions de CO₂ (tonnes par habitant)'})

    elif visualization_type == "Barre":
        fig = px.bar(filtered_data, x='Year', y='Annual CO₂ emissions (per capita)', color='Entity',
                    title="Évolution des émissions de CO₂ par pays",
                    labels={'Year': 'Année', 'Annual CO₂ emissions (per capita)': 'Émissions de CO₂ (tonnes par habitant)'})

    # Afficher la visualisation
    st.plotly_chart(fig,use_container_width=True)

    # Groupement des données par pays et calcul du total des émissions de CO2
    data_grouped = dataC.groupby('Entity')['Annual CO₂ emissions (per capita)'].sum().reset_index()

    # Calcul du logarithme des émissions de CO2
    data_grouped['log_emissions'] = np.log10(data_grouped['Annual CO₂ emissions (per capita)'])

    # Création de la carte choroplèthe pour le total des émissions de CO2 avec échelle logarithmique
    fig = px.choropleth(data_grouped, locations='Entity', locationmode='country names', color='log_emissions',
                        title='Total des émissions de CO₂ par pays (échelle logarithmique)',
                        labels={'log_emissions': 'Log Émissions de CO₂'},
                        scope='world',
                        color_continuous_scale='Oranges')
    # Mise à jour des dimensions de la carte
    fig.update_geos(fitbounds='locations', visible=False)

    # Agrandir la boîte de la carte
    fig.update_layout(height=600, width=900)
    # Affichage de la carte choroplèthe
    st.plotly_chart(fig,use_container_width=True)


elif menu == "Trouver une borne électrique":
    import webbrowser
    st.subheader("Trouver une borne électrique à proximité")
    # Afficher le texte et les filtres
    st.write("Utilisez les filtres ci-dessous pour trouver les bornes les plus adaptées à vos besoins.")

    # Fonction pour obtenir les coordonnées à partir d'une adresse
    def get_coordinates(address):
        geolocator = Nominatim(user_agent="recharge_app")
        try:
            location = geolocator.geocode(address, timeout=10)
            return location.latitude, location.longitude
        except GeocoderTimedOut:
            return get_coordinates(address)  # Réessayer en cas de délai dépassé

    # Créer le formulaire de saisie de l'utilisateur
    col1, col2, col3 = st.columns(3)

    with col1:
        address = st.text_input("Adresse (numéro, rue, etc.)", help="Saisissez votre adresse complète, y compris le numéro de rue.")
        st.write("Exemple : 123 Rue du Commerce")

    with col2:
        postal_code = st.text_input("Code postal", help="Saisissez le code postal de votre adresse.")
        st.write("Exemple : 75001")

    with col3:
        city = st.text_input("Ville", help="Saisissez le nom de votre ville.")
        st.write("Exemple : Paris")
    if st.button("Rechercher"):
        if address and postal_code and city:
            full_address = f"{address}, {postal_code} {city}"
            latitude, longitude = get_coordinates(full_address)

            if latitude is None or longitude is None:
                st.warning("Impossible de trouver les coordonnées pour cette adresse. Veuillez saisir une adresse valide.")
            else:
            # Calculer la distance entre la position de l'utilisateur et chaque borne de recharge
                data["distance"] = data.apply(
                    lambda row: geodesic((latitude, longitude), (row["consolidated_latitude"], row["consolidated_longitude"])).km,
                    axis=1
                )

                # Trier les données par distance
                data_sorted = data.sort_values("distance")

                # Supprimer les doublons basés sur l'adresse et conserver la première occurrence
                data_sorted = data_sorted.drop_duplicates(subset="nom_station", keep="first")

                # Créer une colonne pour la carte et les informations
                col_map, col_info = st.columns([2, 1])

                            # Fonction pour générer l'URL de l'itinéraire GPS
                def generate_gps_url(lat, lon):
                    return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"

                # Afficher la carte dans la colonne de gauche
                with col_map:
                   # Créer une carte Folium centrée sur la position de l'utilisateur
                    m = folium.Map(location=[latitude, longitude], zoom_start=15, tiles="OpenStreetMap", width=800, height=600)

                    # Créer un groupe de marqueurs pour les bornes de recharge
                    marker_cluster = folium.FeatureGroup(name='Bornes de recharge')

                   # Ajouter des marqueurs pour chaque borne de recharge
                    for _, row in data_sorted.head(10).iterrows():
                        # Formater l'adresse en gras
                        address_html = f"<b>{row['adresse_station']}</b>"
                        popup_text = f"<b>{row['nom_station']}</b><br>{address_html}"

                        # Générer l'URL de l'itinéraire GPS
                        gps_url = generate_gps_url(row["consolidated_latitude"], row["consolidated_longitude"])

                        # Arrondir la distance à deux chiffres après la virgule
                        distance = round(row['distance'], 2)

                        # Ajouter un événement de clic pour rediriger l'utilisateur vers l'itinéraire GPS
                        popup_text += f"<br>La station se situe à {distance} km.<br> Cliquez <b><a href='{gps_url}' target='_blank'>ici</a></b> pour obtenir l'itinéraire GPS."
                        popup = folium.Popup(popup_text, max_width=300)  # Set the max width of the popup
                        marker = folium.Marker(
                            location=[row["consolidated_latitude"], row["consolidated_longitude"]],
                            popup=popup,
                            icon=folium.Icon(color="green", prefix="fa", icon="plug")
                        )
                        marker_cluster.add_child(marker)

                    # Ajouter un cercle avec un fond transparent pour délimiter la zone de l'utilisateur
                    user_circle = folium.Circle(
                        location=[latitude, longitude],
                        radius=700,  # Adjust the radius according to your preference
                        color='blue',
                        fill=True,
                        fill_opacity=0.2,  # Set the fill opacity to make the background transparent
                    )
                    m.add_child(user_circle)

                    # Ajouter le groupe de marqueurs à la carte
                    m.add_child(marker_cluster)
                    # Ajuster la taille de la carte
                    folium.plugins.Fullscreen(position='center').add_to(m)
                    # Afficher la carte Folium
                    folium_static(m)

                # Afficher les informations dans le conteneur de droite
                with col_info:
                    st.write("Voici des détails supplémentaires sur les différentes stations situées à proximité de l'emplacement que vous avez indiqué :")

                    # Créer un seul conteneur pour les informations des stations
                    info_container = st.container()

                    # Parcourir les stations les plus proches
                    for i, (_, row) in enumerate(data_sorted.head(5).iterrows(), 1):
                        # Récupérer le nom de la station
                        nom_station = row.get('nom_station', 'Nom de la station non disponible')

                        # Afficher le nom de la station dans un conteneur distinct avec un bouton "En savoir plus"
                        with info_container:
                            with st.expander(f" Station {i}: {nom_station}", expanded=False):
                                # Créer une liste de lignes de texte formatées avec Markdown
                                lines = []
                                lines.append("<ul>")

                                # Ajouter les informations disponibles de la station
                                if not pd.isnull(row['puissance_nominale']):
                                    lines.append(f"<li>⚡️ <b>Puissance nominale</b>: {row['puissance_nominale']}</li>")
                                if not pd.isnull(row['implantation_station']):
                                    lines.append(f"<li>📍 <b>Implantation</b>: {row['implantation_station']}</li>")
                                if not pd.isnull(row['prise_type_ef']):
                                    lines.append(f"<li>🔌 <b>Type de prise EF</b>: {'Oui' if row['prise_type_ef'] else 'Non'}</li>")
                                if not pd.isnull(row['prise_type_2']):
                                    lines.append(f"<li>🔌 <b>Type de prise 2</b>: {'Oui' if row['prise_type_2'] else 'Non'}</li>")
                                if not pd.isnull(row['prise_type_combo_ccs']):
                                    lines.append(f"<li>🔌 <b>Type de prise Combo CCS</b>: {'Oui' if row['prise_type_combo_ccs'] else 'Non'}</li>")
                                if not pd.isnull(row['prise_type_chademo']):
                                    lines.append(f"<li>🔌 <b>Type de prise CHAdeMO</b>: {'Oui' if row['prise_type_chademo'] else 'Non'}</li>")
                                if not pd.isnull(row['gratuit']):
                                    lines.append(f"<li>💲 <b>Gratuit</b>: {'Oui' if str(row['gratuit']).lower() == 'true' else 'Non'}</li>")
                                if not pd.isnull(row['paiement_acte']):
                                    lines.append(f"<li>💳 <b>Paiement acte</b>: {'Oui' if str(row['paiement_acte']).lower() == 'true' else 'Non'}</li>")
                                if not pd.isnull(row['condition_acces']):
                                    lines.append(f"<li>🔒 <b>Condition d'accès</b>: {row['condition_acces']}</li>")
                                if not pd.isnull(row['reservation']):
                                    lines.append(f"<li>📅 <b>Réservation</b>: {'Oui' if str(row['reservation']).lower() == 'true' else 'Non'}</li>")
                                if not pd.isnull(row['horaires']):
                                    lines.append(f"<li>⏰ <b>Horaires</b>: {row['horaires']}</li>")
                                if not pd.isnull(row['accessibilite_pmr']):
                                    lines.append(f"<li>♿️ <b>Accessibilité PMR</b>: {'Oui' if row['accessibilite_pmr'] else 'Non'}</li>")

                                # Utiliser st.markdown() pour afficher le contenu formaté dans l'expander
                                st.markdown("\n".join(lines), unsafe_allow_html=True)
        else:
            st.warning("Veuillez saisir une adresse complète.")

    

    # Fin du code
