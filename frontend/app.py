"""
Entry point for the Safe Air Streamlit application.

This script sets up the Streamlit page configuration, loads custom CSS,
initialises session state, and orchestrates rendering of the search bar,
interactive map, dashboard and contextual help. All interface elements are
translated into English and aligned with the backend logic and provided
documentation.
"""

from __future__ import annotations

import streamlit as st
from components.search import SearchComponent
from components.map import MapComponent
from components.dashboard import DashboardComponent
from components.tooltip import TooltipComponent
from services.api_client import APIClient
from utils.config import config, load_env_file
from utils.helpers import init_session_state


def load_css() -> None:
    """Inject custom CSS from the static directory if available.

    In addition to loading ``static/style.css``, this function injects a
    snippet to hide horizontal overflow on the main application container
    (preventing scrollbars on wide screens).
    """
    # Hide horizontal overflow to avoid sideways scrolling
    st.markdown("""
        <style>
        .stApp { overflow-x: hidden; }
        </style>
    """, unsafe_allow_html=True)
    # Load custom CSS if present
    import pathlib
    css_path = pathlib.Path(__file__).resolve().parent / 'static' / 'style.css'
    if css_path.is_file():
        with css_path.open() as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def main() -> None:
    """Main function of the Safe Air application."""
    # Load environment variables (supports .env for local development)
    load_env_file()
    # Configure the Streamlit page
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # Load custom styles
    load_css()
    # Initialise session state
    init_session_state()
    # Instantiate components
    search_component = SearchComponent()
    map_component = MapComponent()
    dashboard_component = DashboardComponent()
    tooltip_component = TooltipComponent()
    api_client = APIClient()
    # Render sidebar quick help
    tooltip_component.render_sidebar_help()
    # Page header
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1rem;">
            <h1>🫁 Is it safe to go outside?</h1>
            <p>An application combining weather and air quality</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # First row: search bar and map side by side
    left_col, right_col = st.columns([1, 2])
    risk_data = None
    selected_location = None
    with left_col:
        st.markdown("### 🔍 Search for a place")
        selected_location = search_component.render()
        if selected_location:
            # Fetch risk data when a location is selected
            with st.spinner("Retrieving risk data..."):
                risk_data = api_client.get_risk_data(
                    mapbox_id=selected_location['id'],
                    session_token=st.session_state.session_token
                )
            if risk_data:
                # Store risk data in session state for reuse
                st.session_state.current_risk_data = risk_data
                st.session_state.selected_location = selected_location
    with right_col:
        st.markdown("### 🗺️ Interactive map")
        if st.session_state.get('current_risk_data') and st.session_state.get('selected_location'):
            map_component.render(
                st.session_state.current_risk_data,
                st.session_state.selected_location
            )
        else:
            map_component.render_default()
    # Second row: dashboard occupies full width if risk data available
    if risk_data:
        # Indicate that data updates approximately every 1–2 hours due to free plans
        st.markdown("### 📊 Data updated every 1–2 hours")
        dashboard_component.render(risk_data)
    # Footer with limitations
    st.markdown(
        """
        <div style="margin-top:2rem; padding:1rem; border-top:1px solid #e9ecef;">
        ⚠️ <strong>Free plan limitations:</strong><br/>
        Mapbox Search Box API works primarily in the United States, Canada and Europe.<br/>
        OpenWeather APIs are updated approximately every 2 hours.
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()