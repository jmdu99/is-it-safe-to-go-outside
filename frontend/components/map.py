"""
Composant de carte interactive avec Mapbox
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
from utils.constants import RISK_COLORS, DEFAULT_COORDINATES
from utils.helpers import get_risk_color, format_coordinates

class MapComponent:
    def __init__(self):
        self.default_location = DEFAULT_COORDINATES['PARIS']
        self.default_zoom = 10
    
    def render(self, risk_data, location_data):
        """Rendu de la carte avec données de risque"""
        
        if not risk_data or not location_data:
            return self.render_default()
        
        # Extraction des coordonnées
        latitude = risk_data['location']['latitude']
        longitude = risk_data['location']['longitude']
        
        # Création de la carte
        m = folium.Map(
            location=[latitude, longitude],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Ajout du marqueur principal avec popup
        self._add_risk_marker(m, risk_data, location_data)
        
        # Ajout des couches supplémentaires
        self._add_map_layers(m)
        
        # Affichage de la carte
        map_data = st_folium(
            m,
            width=700,
            height=500,
            returned_objects=["last_object_clicked"]
        )
        
        # Informations de géolocalisation
        self._display_coordinates_info(latitude, longitude)
        
        return map_data
    
    def render_default(self):
        """Rendu de la carte par défaut (sans données)"""
        
        # Carte centrée sur Paris par défaut
        m = folium.Map(
            location=self.default_location,
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap'
        )
        
        # Marqueur d'information
        folium.Marker(
            self.default_location,
            popup=folium.Popup(
                "<b>🔍 Recherchez un lieu</b><br>"
                "Utilisez la barre de recherche pour voir les données de qualité de l'air",
                max_width=200
            ),
            icon=folium.Icon(color='blue', icon='search')
        ).add_to(m)
        
        # Ajout des couches
        self._add_map_layers(m)
        
        # Affichage
        map_data = st_folium(
            m,
            width=700,
            height=500,
            returned_objects=["last_object_clicked"]
        )
        
        st.info("🗺️ Sélectionnez un lieu dans la barre de recherche pour voir les données de risque")
        
        return map_data
    
    def _add_risk_marker(self, map_obj, risk_data, location_data):
        """Ajoute le marqueur principal avec les données de risque"""
        
        latitude = risk_data['location']['latitude']
        longitude = risk_data['location']['longitude']
        risk_label = risk_data['risk_label']
        risk_index = risk_data['risk_index']
        
        # Couleur selon le niveau de risque
        marker_color = get_risk_color(risk_label)
        
        # Contenu du popup
        popup_content = self._create_popup_content(risk_data, location_data)
        
        # Marqueur principal
        folium.Marker(
            [latitude, longitude],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{location_data.get('name', 'Lieu sélectionné')} - Risque: {risk_label}",
            icon=folium.Icon(
                color=marker_color,
                icon='info-sign',
                prefix='glyphicon'
            )
        ).add_to(map_obj)
        
        # Cercle pour visualiser la zone d'influence
        folium.Circle(
            [latitude, longitude],
            radius=2000,  # 2km de rayon
            popup=f"Zone d'influence - Risque {risk_label}",
            color=RISK_COLORS[risk_label.upper()],
            fill=True,
            fillOpacity=0.2
        ).add_to(map_obj)
    
    def _create_popup_content(self, risk_data, location_data):
        """Crée le contenu HTML du popup"""
        
        weather = risk_data['weather']
        pollution = risk_data['pollution']
        risk_label = risk_data['risk_label']
        risk_index = risk_data['risk_index']
        
        # Formatage de la température
        temp = weather['temp_celsius']
        humidity = weather['humidity']
        wind_speed = weather['wind_speed']
        
        # Composants de pollution principaux
        pm25 = pollution['components'].get('pm2_5', 0)
        pm10 = pollution['components'].get('pm10', 0)
        o3 = pollution['components'].get('o3', 0)
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 250px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">
                📍 {location_data.get('name', 'Lieu sélectionné')}
            </h4>
            
            <div style="margin-bottom: 10px;">
                <strong>🎯 Indice de risque :</strong>
                <span style="background-color: {RISK_COLORS[risk_label.upper()]}; 
                           color: white; padding: 2px 8px; border-radius: 4px; 
                           font-weight: bold;">{risk_label}</span>
                <br><small>Index: {risk_index:.3f}</small>
            </div>
            
            <div style="margin-bottom: 10px;">
                <strong>🌡️ Météo :</strong><br>
                • Température : {temp}°C<br>
                • Humidité : {humidity}%<br>
                • Vent : {wind_speed} m/s
            </div>
            
            <div style="margin-bottom: 10px;">
                <strong>💨 Qualité de l'air :</strong><br>
                • PM2.5 : {pm25:.1f} µg/m³<br>
                • PM10 : {pm10:.1f} µg/m³<br>
                • Ozone : {o3:.1f} µg/m³
            </div>
            
            <div style="font-size: 11px; color: #666; margin-top: 10px;">
                📅 Mise à jour : {weather['timestamp'][:16].replace('T', ' ')}
            </div>
        </div>
        """
        
        return popup_html
    
    def _add_map_layers(self, map_obj):
        """Ajoute des couches supplémentaires à la carte"""
        
        # Couche satellite
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(map_obj)
        
        # Couche terrain
        folium.TileLayer(
            tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(map_obj)
        
        # Contrôle des couches
        folium.LayerControl().add_to(map_obj)
        
        # Plugin pour la mesure de distance
        from folium.plugins import MeasureControl
        MeasureControl().add_to(map_obj)
        
        # Plugin pour la localisation
        from folium.plugins import LocateControl
        LocateControl().add_to(map_obj)
    
    def _display_coordinates_info(self, latitude, longitude):
        """Affiche les informations de coordonnées"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📍 Latitude",
                value=f"{latitude:.6f}°"
            )
        
        with col2:
            st.metric(
                label="📍 Longitude", 
                value=f"{longitude:.6f}°"
            )
        
        with col3:
            # Lien vers Google Maps
            google_maps_url = f"https://www.google.com/maps/@{latitude},{longitude},15z"
            st.markdown(f"[🗺️ Voir sur Google Maps]({google_maps_url})")
