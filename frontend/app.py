"""
Application principale Streamlit pour le projet Respiratory Risk
"""
import streamlit as st
import uuid
from components.search import SearchComponent
from components.map import MapComponent
from components.dashboard import DashboardComponent
from components.tooltip import TooltipComponent
from services.api_client import APIClient
from utils.config import Config
from utils.helpers import init_session_state

from utils.config import load_env_file
load_env_file()  # Charge .env automatiquement


# Configuration de la page
st.set_page_config(
    page_title="Est-il sûr de sortir ?",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé
def load_css():
    with open('static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    """Fonction principale de l'application"""
    
    # Chargement du CSS
    load_css()
    
    # Initialisation de l'état de session
    init_session_state()
    
    # Initialisation des composants
    search_component = SearchComponent()
    map_component = MapComponent()
    dashboard_component = DashboardComponent()
    tooltip_component = TooltipComponent()
    api_client = APIClient()
    
    # Header de l'application
    st.markdown("""
    <div class="main-header">
        <h1>🌬️ Est-il sûr de sortir ?</h1>
        <p>Une application simple combinant météo et qualité de l'air</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Composant de recherche
        st.markdown("### 🔍 Rechercher un lieu")
        selected_location = search_component.render()
        
        if selected_location:
            # Récupération des données de risque
            with st.spinner("Récupération des données..."):
                risk_data = api_client.get_risk_data(
                    mapbox_id=selected_location['id'],
                    session_token=st.session_state.session_token
                )
            
            if risk_data:
                # Stockage des données dans la session
                st.session_state.current_risk_data = risk_data
                st.session_state.selected_location = selected_location
                
                # Dashboard avec métriques
                st.markdown("### 📊 Données actuelles")
                dashboard_component.render(risk_data)
    
    with col2:
        st.markdown("### 🗺️ Carte interactive")
        
        if hasattr(st.session_state, 'current_risk_data') and st.session_state.current_risk_data:
            # Affichage de la carte avec les données
            map_component.render(
                st.session_state.current_risk_data,
                st.session_state.selected_location
            )
        else:
            # Carte par défaut (centrée sur Paris)
            map_component.render_default()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>⚠️ Limitations des plans gratuits :</p>
        <ul>
            <li>Mapbox Search Box API fonctionne principalement aux États-Unis, au Canada et en Europe</li>
            <li>Les API OpenWeather se mettent à jour environ toutes les 2 heures</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
