"""
Search component for the Safe Air application.

This component provides a text input for users to search for a location.
It displays suggestions returned by the backend after the user enters at
least two characters and presses Enter (in practice suggestions are fetched
during typing with debouncing, but the help text reflects the behaviour
accurately). Selecting a suggestion stores the result in the session state
so it can be used by other components.

All labels, placeholders and messages are written in English.
"""

from __future__ import annotations

import streamlit as st
import time
from services.api_client import APIClient
from utils.helpers import debounce


class SearchComponent:
    def __init__(self) -> None:
        # Instantiate API client used for location suggestions
        self.api_client = APIClient()

    def render(self):
        """Render the search input and suggestion list.

        This implementation uses a form to ensure suggestions are only
        retrieved when the user explicitly submits the query (for example
        by pressing Enter).  Suggestions persist after a location is
        selected and do not reappear when interacting with other parts
        of the app (such as clicking on the map marker).

        Returns
        -------
        dict or None
            The selected suggestion dictionary if a location has been chosen,
            otherwise ``None``.
        """
        st.session_state.setdefault('suggestions', [])
        st.session_state.setdefault('selected_suggestion', None)
        st.session_state.setdefault('show_suggestions', False)

        # Use a form so that suggestions are fetched only when the form is submitted
        with st.form(key="search_form", clear_on_submit=False):
            search_query = st.text_input(
                label="Type a place name:",
                placeholder="e.g. Paris, London, New York...",
                key="search_input",
                help="Press Enter to fetch suggestions"
            )
            submitted = st.form_submit_button("Search")

        # When the form is submitted and the query is long enough, fetch suggestions
        if submitted and search_query and len(search_query.strip()) >= 2:
            with st.spinner("Searching..."):
                suggestions = self.api_client.suggest_locations(
                    query=search_query.strip(),
                    session_token=st.session_state.session_token
                )
            st.session_state.suggestions = suggestions
            st.session_state.show_suggestions = True

        # Show suggestions if flagged; they persist after selection until the user
        # performs a new search.  Do not depend on the current input value to
        # display suggestions so that clicking the map does not toggle them.
        if st.session_state.show_suggestions and st.session_state.suggestions:
            st.markdown("**Suggestions:**")
            suggestions_container = st.container()
            with suggestions_container:
                for i, suggestion in enumerate(st.session_state.suggestions):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        suggestion_text = self._format_suggestion(suggestion)
                        if st.button(
                            suggestion_text,
                            key=f"suggestion_{i}",
                            help=f"Select {suggestion.get('name', 'this location')}"
                        ):
                            st.session_state.selected_suggestion = suggestion
                            # Keep suggestions visible after selection
                            # They will be replaced only when a new search is submitted
                            # Trigger re‑run so that other components update
                            st.rerun()
                    with col2:
                        place_type = self._get_place_type(suggestion)
                        st.markdown(f"{place_type}", unsafe_allow_html=True)

        # If a suggestion is selected, display the address information
        if st.session_state.selected_suggestion:
            selected = st.session_state.selected_suggestion
            st.success(f"✅ Selected location: **{selected.get('name', 'Location')}**")
            address = selected.get('full_address') or selected.get('place_formatted') or "Address not available"
            st.info(f"📍 {address}")
            return selected
        return None

    def _should_search(self, query: str) -> bool:
        """Determine whether a new search should be executed based on debounce."""
        last_search = st.session_state.get('last_search', '')
        last_time = st.session_state.get('last_search_time', 0.0)
        return query != last_search or time.time() - last_time > 1.0

    def _format_suggestion(self, suggestion: dict) -> str:
        """Format a suggestion for display in the suggestions list."""
        name = suggestion.get('name', 'Unnamed location')
        address = suggestion.get('place_formatted', suggestion.get('full_address', ''))
        if address:
            return f"📍 {name} – {address}"
        return f"📍 {name}"

    def _get_place_type(self, suggestion: dict) -> str:
        """Return a flag emoji based on the suggestion's country or region."""
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