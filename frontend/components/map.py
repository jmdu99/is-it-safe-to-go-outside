"""
Interactive map component using Folium.

This component displays an interactive map centred on the selected location
with a marker coloured according to the risk level. It adds multiple base
layers (OpenStreetMap, Satellite, Terrain) and controls for layer selection,
measuring distance and geolocation. The default base layer is OpenStreetMap.

The popup on the marker summarises the risk index and shows a few key
metrics for weather and air quality. All user‑facing text is in English.
"""

from __future__ import annotations

import streamlit as st
import folium
from folium.plugins import MeasureControl, LocateControl
from streamlit_folium import st_folium

from utils.constants import RISK_COLORS, DEFAULT_COORDINATES
from utils.helpers import get_risk_color, format_coordinates, format_timestamp


class MapComponent:
    def __init__(self) -> None:
        # Default location and zoom when no data is available (Paris)
        self.default_location = DEFAULT_COORDINATES['PARIS']
        self.default_zoom = 10

    def render(self, risk_data: dict, location_data: dict):
        """Render the map centred on the provided risk and location data.

        This method ensures that OpenStreetMap is the default base layer by
        explicitly adding it first via ``TileLayer``. Additional layers are
        added afterwards so they can be selected via the layer control. The
        marker colour matches the risk label (green, orange or red)."""
        if not risk_data or not location_data:
            return self.render_default()
        latitude = risk_data['location']['latitude']
        longitude = risk_data['location']['longitude']
        # Start with an empty map (no default tile). We'll add base layers in
        # ``_add_map_layers``.  Creating the map with ``tiles=None`` lets us
        # explicitly set the order of layers, ensuring that OpenStreetMap is
        # added as the final base layer and therefore selected by default.
        m = folium.Map(
            location=[latitude, longitude],
            zoom_start=12,
            control_scale=True,
            tiles=None
        )
        # Add risk marker with colour reflecting the risk label
        self._add_risk_marker(m, risk_data, location_data)
        # Add base layers (satellite, terrain, OpenStreetMap) and controls
        self._add_map_layers(m)
        # Render map in Streamlit
        map_data = st_folium(
            m,
            width=700,
            height=500,
            returned_objects=["last_object_clicked"]
        )
        # Display coordinates below the map
        self._display_coordinates_info(latitude, longitude)
        return map_data

    def render_default(self):
        """Render a default map when no location is selected."""
        m = folium.Map(
            location=self.default_location,
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap',
            control_scale=True
        )
        folium.Marker(
            self.default_location,
            popup=folium.Popup(
                "🔍 Search for a location\nUse the search bar to see risk data",
                max_width=250
            ),
            icon=folium.Icon(color='blue', icon='search')
        ).add_to(m)
        self._add_map_layers(m)
        st_folium(
            m,
            width=700,
            height=500,
            returned_objects=["last_object_clicked"]
        )
        st.info("🗺️ Select a location in the search bar to view risk data")
        return None

    def _add_risk_marker(self, map_obj: folium.Map, risk_data: dict, location_data: dict) -> None:
        """Add a coloured marker to the map with a popup summarising the risk.

        The marker colour, popup text and tooltip all use the same
        classification logic as the rest of the application.  Instead of
        relying on the backend's ``risk_label`` (which uses different
        thresholds), we compute the risk category based on the normalised
        risk index: values < 0.21 are green/"Optimal", values < 0.41 are
        yellow/"Precaution" and values ≥ 0.41 are red/"Risk".  The
        marker colour is mapped to a Folium colour name (yellow → orange).
        """
        # Extract coordinates
        lat = risk_data['location']['latitude']
        lon = risk_data['location']['longitude']
        # Normalised risk index (0–1)
        risk_index = risk_data.get('risk_index', 0.0)
        # Determine label and colour according to our classification
        from utils.helpers import get_status_label_color, truncate
        label, colour_name = get_status_label_color(risk_index)
        # Map our colour names to Folium supported colours (yellow→orange)
        folium_colour = {
            'green': 'green',
            'yellow': 'orange',
            'red': 'red'
        }.get(colour_name, 'blue')
        # Create popup content using our truncated risk index and label
        popup_content = self._create_popup_content(risk_data, location_data, label, risk_index)
        # Tooltip shows the selected place and the risk category with truncated index
        truncated_index = truncate(risk_index, 2)
        tooltip_text = f"{location_data.get('name', 'Selected location')} – Risk: {label} (index: {truncated_index:.2f})"
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_content, max_width=320),
            tooltip=tooltip_text,
            icon=folium.Icon(color=folium_colour, icon='info-sign', prefix='glyphicon')
        ).add_to(map_obj)
        # Draw a circle with colour matching the risk category (using hex codes)
        colour_hex = {
            'green': RISK_COLORS['LOW'],
            'yellow': RISK_COLORS['MODERATE'],
            'red': RISK_COLORS['HIGH']
        }.get(colour_name, '#6c757d')
        folium.Circle(
            [lat, lon],
            radius=2000,
            popup=f"Influence zone – {label}",
            color=colour_hex,
            fill=True,
            fillOpacity=0.2
        ).add_to(map_obj)

    def _create_popup_content(self, risk_data: dict, location_data: dict, label: str, risk_index: float) -> str:
        """Construct HTML content for the popup on the risk marker.

        Parameters
        ----------
        risk_data : dict
            Data returned by the backend including weather and pollution.
        location_data : dict
            Selected location information (name, address, etc.).
        label : str
            The risk category computed from the normalised risk index (Optimal,
            Precaution or Risk).
        risk_index : float
            The normalised risk index.

        Returns
        -------
        str
            An HTML string rendered in the Folium popup.
        """
        weather = risk_data['weather']
        pollution = risk_data['pollution']
        # Truncate values for display without rounding
        from utils.helpers import truncate
        temp = weather['temp_celsius']
        humidity = weather['humidity']
        wind_speed = weather['wind_speed']
        timestamp = weather.get('timestamp', '')
        pm25 = pollution['components'].get('pm2_5', 0.0)
        pm10 = pollution['components'].get('pm10', 0.0)
        o3 = pollution['components'].get('o3', 0.0)
        popup_html = f"""
        <div style='font-size:0.9rem;'>
        <strong>📍 {location_data.get('name', 'Selected location')}</strong><br/>
        <br/>
        <strong>🎯 Risk index:</strong> {label} (index: {truncate(risk_index, 3):.3f})<br/>
        <br/>
        <strong>🌡️ Weather:</strong><br/>
        – Temperature: {truncate(temp, 1):.1f} °C<br/>
        – Humidity: {truncate(humidity, 0):.0f}%<br/>
        – Wind speed: {truncate(wind_speed, 1):.1f} m/s<br/>
        <br/>
        <strong>💨 Air quality:</strong><br/>
        – PM2.5: {truncate(pm25, 1):.1f} µg/m³<br/>
        – PM10: {truncate(pm10, 1):.1f} µg/m³<br/>
        – O₃: {truncate(o3, 1):.1f} µg/m³<br/>
        <br/>
        <small>📅 Updated: {format_timestamp(timestamp)}</small>
        </div>
        """
        return popup_html

    def _add_map_layers(self, map_obj: folium.Map) -> None:
        """Add extra tile layers and controls to the folium map."""
        # Add satellite and terrain layers first, then OpenStreetMap.  When
        # OpenStreetMap is added last, Folium selects it as the active base
        # layer by default.  This ensures the street map is visible at all
        # zoom levels with the option to switch to satellite or terrain.
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(map_obj)
        folium.TileLayer(
            tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(map_obj)
        # Add OpenStreetMap as a base layer last
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(map_obj)
        # Add layer control to switch between base layers
        folium.LayerControl().add_to(map_obj)
        # Add measurement and locate controls
        MeasureControl().add_to(map_obj)
        LocateControl().add_to(map_obj)

    def _display_coordinates_info(self, lat: float, lon: float) -> None:
        """Display the coordinates of the selected point below the map with larger font."""
        formatted = format_coordinates(lat, lon, precision=5)
        st.markdown(f"<p style='font-size:1rem; font-weight:500;'>📌 Coordinates: {formatted}</p>", unsafe_allow_html=True)