"""
Composant de recherche avec autocomplétion
"""
import streamlit as st
import time
from services.api_client import APIClient
from utils.helpers import debounce

class SearchComponent:
    def __init__(self):
        self.api_client = APIClient()
    
    def render(self):
        """Rendu du composant de recherche"""
        
        # Input de recherche
        search_query = st.text_input(
            "Tapez un nom de lieu :",
            placeholder="Ex: Paris, London, New York...",
            key="search_input",
            help="Commencez à taper pour voir les suggestions"
        )
        
        # État pour les suggestions
        if 'suggestions' not in st.session_state:
            st.session_state.suggestions = []
        
        if 'selected_suggestion' not in st.session_state:
            st.session_state.selected_suggestion = None
        
        # Recherche en temps réel avec debounce
        if search_query and len(search_query.strip()) >= 2:
            # Debounce pour éviter trop d'appels API
            if self._should_search(search_query):
                with st.spinner("Recherche en cours..."):
                    suggestions = self.api_client.suggest_locations(
                        query=search_query.strip(),
                        session_token=st.session_state.session_token
                    )
                    st.session_state.suggestions = suggestions
                    st.session_state.last_search = search_query
                    st.session_state.last_search_time = time.time()
        
        # Affichage des suggestions
        if st.session_state.suggestions and search_query:
            st.markdown("**Suggestions :**")
            
            # Conteneur pour les suggestions
            suggestions_container = st.container()
            
            with suggestions_container:
                for i, suggestion in enumerate(st.session_state.suggestions):
                    # Création d'un bouton pour chaque suggestion
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        suggestion_text = self._format_suggestion(suggestion)
                        if st.button(
                            suggestion_text,
                            key=f"suggestion_{i}",
                            help=f"Sélectionner {suggestion.get('name', 'ce lieu')}"
                        ):
                            st.session_state.selected_suggestion = suggestion
                            st.session_state.suggestions = []  # Nettoyer les suggestions
                            st.rerun()
                    
                    with col2:
                        # Badge pour le type de lieu
                        place_type = self._get_place_type(suggestion)
                        st.markdown(f"<span class='place-badge'>{place_type}</span>", 
                                  unsafe_allow_html=True)
        
        # Retour de la suggestion sélectionnée
        if st.session_state.selected_suggestion:
            selected = st.session_state.selected_suggestion
            
            # Affichage de la sélection actuelle
            st.success(f"✅ Lieu sélectionné : **{selected.get('name', 'Lieu')}**")
            st.info(f"📍 {selected.get('full_address', selected.get('place_formatted', ''))}")
            
            # Bouton pour changer de lieu
            if st.button("🔄 Changer de lieu", key="change_location"):
                st.session_state.selected_suggestion = None
                st.session_state.suggestions = []
                st.session_state.search_input = ""
                st.rerun()
            
            return selected
        
        return None
    
    def _should_search(self, query):
        """Détermine si une nouvelle recherche doit être effectuée"""
        last_search = getattr(st.session_state, 'last_search', '')
        last_time = getattr(st.session_state, 'last_search_time', 0)
        
        # Recherche si la requête a changé ou si assez de temps s'est écoulé
        return (
            query != last_search or 
            time.time() - last_time > 1.0  # Debounce de 1 seconde
        )
    
    def _format_suggestion(self, suggestion):
        """Formate l'affichage d'une suggestion"""
        name = suggestion.get('name', 'Lieu sans nom')
        address = suggestion.get('place_formatted', suggestion.get('full_address', ''))
        
        if address:
            return f"📍 {name} - {address}"
        return f"📍 {name}"
    
    def _get_place_type(self, suggestion):
        """Détermine le type de lieu pour le badge"""
        address = suggestion.get('full_address', '') or suggestion.get('place_formatted', '')
        
        if not address:
            return "🏷️"
        
        address_lower = address.lower()
        
        if any(country in address_lower for country in ['france', 'paris']):
            return "🇫🇷"
        elif any(country in address_lower for country in ['spain', 'españa']):
            return "🇪🇸"
        elif any(country in address_lower for country in ['usa', 'united states']):
            return "🇺🇸"
        elif any(country in address_lower for country in ['uk', 'england', 'london']):
            return "🇬🇧"
        else:
            return "🌍"
