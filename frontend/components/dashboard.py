"""
Composant dashboard avec métriques et visualisations
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.constants import RISK_COLORS, POLLUTION_THRESHOLDS, WEATHER_THRESHOLDS
from utils.helpers import get_risk_color, format_timestamp

class DashboardComponent:
    
    def render(self, risk_data):
        """Rendu du dashboard principal"""
        
        if not risk_data:
            st.warning("⚠️ Aucune donnée disponible")
            return
        
        # Section principale - Indice de risque
        self._render_risk_section(risk_data)
        
        # Section météo
        self._render_weather_section(risk_data['weather'])
        
        # Section pollution
        self._render_pollution_section(risk_data['pollution'])
        
        # Section détaillée - Composants normalisés
        self._render_normalized_components(risk_data['norm'])
        
        # Graphiques de visualisation
        self._render_charts(risk_data)
    
    def _render_risk_section(self, risk_data):
        """Section principale avec l'indice de risque"""
        
        risk_index = risk_data['risk_index']
        risk_label = risk_data['risk_label']
        
        # Grande métrique centrale
        st.markdown("#### 🎯 Indice de Risque Respiratoire")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Jauge circulaire pour l'indice
            fig = self._create_risk_gauge(risk_index, risk_label)
            st.plotly_chart(fig, use_container_width=True)
        
        # Interprétation du risque
        interpretation = self._get_risk_interpretation(risk_label)
        
        if risk_label.upper() == 'LOW':
            st.success(f"✅ **{risk_label.upper()}** - {interpretation}")
        elif risk_label.upper() == 'MODERATE':
            st.warning(f"⚠️ **{risk_label.upper()}** - {interpretation}")
        else:
            st.error(f"🚨 **{risk_label.upper()}** - {interpretation}")
    
    def _render_weather_section(self, weather_data):
        """Section météorologique"""
        
        st.markdown("#### 🌡️ Conditions Météorologiques")
        
        col1, col2, col3, col4 = st.columns(4)
        
        temp = weather_data['temp_celsius']
        humidity = weather_data['humidity']
        wind_speed = weather_data['wind_speed']
        timestamp = weather_data['timestamp']
        
        with col1:
            # Température avec delta si on a des données précédentes
            temp_delta = self._calculate_temp_delta(temp)
            st.metric(
                label="🌡️ Température",
                value=f"{temp:.1f}°C",
                delta=temp_delta
            )
        
        with col2:
            st.metric(
                label="💧 Humidité",
                value=f"{humidity}%",
                help="Humidité relative de l'air"
            )
        
        with col3:
            # Conversion en km/h pour plus de clarté
            wind_kmh = wind_speed * 3.6
            st.metric(
                label="💨 Vent",
                value=f"{wind_speed:.1f} m/s",
                help=f"Soit {wind_kmh:.1f} km/h"
            )
        
        with col4:
            # Description météo depuis les données brutes
            weather_desc = self._get_weather_description(weather_data.get('raw', {}))
            st.metric(
                label="☁️ Conditions",
                value=weather_desc
            )
        
        # Timestamp de mise à jour
        formatted_time = format_timestamp(timestamp)
        st.caption(f"🕐 Dernière mise à jour : {formatted_time}")
    
    def _render_pollution_section(self, pollution_data):
        """Section qualité de l'air"""
        
        st.markdown("#### 💨 Qualité de l'Air")
        
        components = pollution_data['components']
        
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pm25 = components.get('pm2_5', 0)
            pm25_status = self._get_pollution_status('pm2_5', pm25)
            st.metric(
                label="PM2.5",
                value=f"{pm25:.1f} µg/m³",
                help="Particules fines (< 2.5µm) - Les plus dangereuses pour la santé"
            )
            st.caption(f"Status: {pm25_status}")
        
        with col2:
            pm10 = components.get('pm10', 0)
            pm10_status = self._get_pollution_status('pm10', pm10)
            st.metric(
                label="PM10",
                value=f"{pm10:.1f} µg/m³",
                help="Particules (< 10µm)"
            )
            st.caption(f"Status: {pm10_status}")
        
        with col3:
            o3 = components.get('o3', 0)
            o3_status = self._get_pollution_status('o3', o3)
            st.metric(
                label="Ozone (O₃)",
                value=f"{o3:.1f} µg/m³",
                help="Ozone troposphérique"
            )
            st.caption(f"Status: {o3_status}")
        
        # Composants secondaires
        with st.expander("🔬 Autres composants"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                no2 = components.get('no2', 0)
                st.metric("NO₂", f"{no2:.1f} µg/m³", help="Dioxyde d'azote")
            
            with col2:
                so2 = components.get('so2', 0)
                st.metric("SO₂", f"{so2:.1f} µg/m³", help="Dioxyde de soufre")
            
            with col3:
                co = components.get('co', 0)
                st.metric("CO", f"{co:.1f} µg/m³", help="Monoxyde de carbone")
    
    def _render_normalized_components(self, norm_data):
        """Section des composants normalisés"""
        
        st.markdown("#### 📊 Analyse Détaillée des Facteurs")
        
        # Graphique en barres horizontales pour les facteurs normalisés
        components = list(norm_data.keys())
        values = [norm_data[comp] for comp in components]
        
        # Couleurs selon l'intensité
        colors = ['red' if v > 0.7 else 'orange' if v > 0.4 else 'green' for v in values]
        
        fig = go.Figure(go.Bar(
            x=values,
            y=components,
            orientation='h',
            marker_color=colors,
            text=[f"{v:.3f}" for v in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Facteurs de Risque Normalisés (0-1)",
            xaxis_title="Niveau de Risque",
            yaxis_title="Composants",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Explication des facteurs les plus élevés
        sorted_factors = sorted(zip(components, values), key=lambda x: x[1], reverse=True)
        top_factors = sorted_factors[:3]
        
        st.markdown("**🔍 Facteurs principaux :**")
        for i, (factor, value) in enumerate(top_factors, 1):
            percentage = value * 100
            explanation = self._get_factor_explanation(factor)
            st.write(f"{i}. **{factor.upper()}** ({percentage:.1f}%) - {explanation}")
    
    def _render_charts(self, risk_data):
        """Graphiques de visualisation avancés"""
        
        st.markdown("#### 📈 Visualisations")
        
        tab1, tab2 = st.tabs(["🎯 Composition du Risque", "📊 Comparaison Seuils"])
        
        with tab1:
            # Graphique en secteurs pour la composition du risque
            self._render_risk_composition_chart(risk_data['norm'])
        
        with tab2:
            # Graphique de comparaison avec les seuils
            self._render_threshold_comparison_chart(risk_data['pollution'])
    
    def _create_risk_gauge(self, risk_index, risk_label):
        """Crée une jauge circulaire pour l'indice de risque"""
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = risk_index,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Indice de Risque"},
            delta = {'reference': 0.5},
            gauge = {
                'axis': {'range': [None, 1]},
                'bar': {'color': RISK_COLORS[risk_label.upper()]},
                'steps': [
                    {'range': [0, 0.25], 'color': RISK_COLORS['LOW']},
                    {'range': [0.25, 0.5], 'color': RISK_COLORS['MODERATE']},
                    {'range': [0.5, 1], 'color': RISK_COLORS['HIGH']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.9
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
    
    def _render_risk_composition_chart(self, norm_data):
        """Graphique en secteurs de la composition du risque"""
        
        # Filtrer les valeurs significatives (> 0.01)
        significant_factors = {k: v for k, v in norm_data.items() if v > 0.01}
        
        if not significant_factors:
            st.info("Tous les facteurs de risque sont très faibles")
            return
        
        labels = list(significant_factors.keys())
        values = list(significant_factors.values())
        
        fig = px.pie(
            values=values,
            names=labels,
            title="Composition du Risque par Facteur",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_threshold_comparison_chart(self, pollution_data):
        """Graphique de comparaison avec les seuils recommandés"""
        
        components = pollution_data['components']
        
        # Données pour le graphique
        pollutants = ['pm2_5', 'pm10', 'o3', 'no2', 'so2']
        current_values = [components.get(p, 0) for p in pollutants]
        thresholds = [POLLUTION_THRESHOLDS.get(p, 100) for p in pollutants]
        
        fig = go.Figure()
        
        # Barres des valeurs actuelles
        fig.add_trace(go.Bar(
            name='Valeur Actuelle',
            x=pollutants,
            y=current_values,
            marker_color='lightblue'
        ))
        
        # Ligne des seuils
        fig.add_trace(go.Scatter(
            name='Seuil Recommandé',
            x=pollutants,
            y=thresholds,
            mode='lines+markers',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Comparaison avec les Seuils Recommandés (µg/m³)",
            xaxis_title="Polluants",
            yaxis_title="Concentration (µg/m³)",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Méthodes utilitaires
    
    def _calculate_temp_delta(self, current_temp):
        """Calcule le delta de température (simplification)"""
        # Dans une version complète, on comparerait avec la température précédente
        return None
    
    def _get_weather_description(self, raw_weather):
        """Extrait la description météo des données brutes"""
        if 'weather' in raw_weather and raw_weather['weather']:
            return raw_weather['weather'][0].get('description', 'N/A').title()
        return "N/A"
    
    def _get_pollution_status(self, pollutant, value):
        """Détermine le statut d'un polluant"""
        threshold = POLLUTION_THRESHOLDS.get(pollutant, 50)
        
        if value <= threshold * 0.5:
            return "🟢 Bon"
        elif value <= threshold:
            return "🟡 Modéré"
        else:
            return "🔴 Élevé"
    
    def _get_risk_interpretation(self, risk_label):
        """Retourne l'interprétation du niveau de risque"""
        interpretations = {
            'LOW': "Conditions favorables pour sortir",
            'MODERATE': "Sortie possible avec précautions pour les personnes sensibles",
            'HIGH': "Éviter les activités extérieures prolongées"
        }
        return interpretations.get(risk_label.upper(), "Niveau de risque indéterminé")
    
    def _get_factor_explanation(self, factor):
        """Explique chaque facteur de risque"""
        explanations = {
            'pm2_5': "Particules fines très dangereuses pour les poumons",
            'pm10': "Particules en suspension dans l'air",
            'o3': "Ozone troposphérique, irritant respiratoire",
            'no2': "Dioxyde d'azote, pollution automobile",
            'so2': "Dioxyde de soufre, pollution industrielle",
            'co': "Monoxyde de carbone",
            'temp': "Température extrême",
            'hum': "Humidité inadéquate",
            'wind': "Conditions de vent défavorables"
        }
        return explanations.get(factor, "Facteur de risque")
