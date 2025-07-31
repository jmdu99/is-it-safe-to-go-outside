"""
Composant pour les tooltips et informations contextuelles
"""
import streamlit as st
from utils.constants import POLLUTION_INFO, WEATHER_INFO, RISK_INFO

class TooltipComponent:
    
    @staticmethod
    def render_help_section():
        """Rendu de la section d'aide complète"""
        
        st.markdown("### ❓ Guide d'utilisation")
        
        with st.expander("🔍 Comment utiliser l'application"):
            st.markdown("""
            **Étapes simples :**
            1. **Recherchez** un lieu dans la barre de recherche
            2. **Sélectionnez** une suggestion dans la liste
            3. **Consultez** les données de risque sur la carte et le dashboard
            4. **Interprétez** les résultats grâce aux indicateurs colorés
            
            **Fonctionnalités :**
            - 🔍 **Recherche en temps réel** avec autocomplétion
            - 🗺️ **Carte interactive** avec marqueurs colorés
            - 📊 **Dashboard détaillé** avec métriques et graphiques
            - 🎯 **Indice de risque** combinant météo et qualité de l'air
            """)
        
        with st.expander("🎯 Comprendre l'indice de risque"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **🟢 FAIBLE (0.00-0.25)**
                - Conditions excellentes
                - Sortie recommandée
                - Aucune précaution particulière
                """)
            
            with col2:
                st.markdown("""
                **🟡 MODÉRÉ (0.26-0.50)**
                - Conditions acceptables
                - Précautions pour personnes sensibles
                - Réduire l'exposition prolongée
                """)
            
            with col3:
                st.markdown("""
                **🔴 ÉLEVÉ (0.51-1.00)**
                - Conditions défavorables
                - Éviter les sorties prolongées
                - Masque recommandé
                """)
        
        with st.expander("💨 Qualité de l'air - Polluants"):
            TooltipComponent._render_pollution_info()
        
        with st.expander("🌡️ Conditions météorologiques"):
            TooltipComponent._render_weather_info()
        
        with st.expander("⚠️ Limitations et sources"):
            st.markdown("""
            **Limitations actuelles :**
            - Les API Mapbox fonctionnent principalement en Amérique du Nord et Europe
            - Les données OpenWeather sont mises à jour toutes les ~2 heures
            - L'indice de risque est calculé selon notre algorithme propriétaire
            
            **Sources de données :**
            - 🗺️ **Géolocalisation** : Mapbox Search API
            - 🌡️ **Météo** : OpenWeather API
            - 💨 **Qualité de l'air** : OpenWeather Air Pollution API
            
            **Calcul de l'indice :**
            L'indice combine de manière pondérée :
            - Concentration des polluants (PM2.5, PM10, O₃, NO₂, SO₂, CO)
            - Conditions météorologiques (température, humidité, vent)
            """)
    
    @staticmethod
    def _render_pollution_info():
        """Informations détaillées sur les polluants"""
        
        st.markdown("**Principaux polluants surveillés :**")
        
        for pollutant, info in POLLUTION_INFO.items():
            with st.container():
                st.markdown(f"**{pollutant}** - {info['name']}")
                st.write(f"• {info['description']}")
                st.write(f"• Seuil recommandé : {info['threshold']} µg/m³")
                st.write(f"• Sources : {info['sources']}")
                st.markdown("---")
    
    @staticmethod
    def _render_weather_info():
        """Informations sur les conditions météorologiques"""
        
        st.markdown("**Facteurs météorologiques pris en compte :**")
        
        for factor, info in WEATHER_INFO.items():
            st.markdown(f"**{info['name']}**")
            st.write(f"• {info['description']}")
            st.write(f"• Plage optimale : {info['optimal_range']}")
            st.markdown("---")
    
    @staticmethod
    def render_contextual_tooltip(tooltip_type, data=None):
        """Rendu de tooltip contextuel selon le type"""
        
        if tooltip_type == "risk_explanation":
            return TooltipComponent._risk_tooltip(data)
        elif tooltip_type == "pollutant_detail":
            return TooltipComponent._pollutant_tooltip(data)
        elif tooltip_type == "weather_impact":
            return TooltipComponent._weather_tooltip(data)
        else:
            return "ℹ️ Information non disponible"
    
    @staticmethod
    def _risk_tooltip(risk_data):
        """Tooltip pour l'explication du risque"""
        if not risk_data:
            return "Aucune donnée de risque disponible"
        
        risk_label = risk_data.get('risk_label', 'Unknown')
        risk_index = risk_data.get('risk_index', 0)
        
        explanation = RISK_INFO.get(risk_label.upper(), {})
        
        return f"""
        **Niveau de risque : {risk_label.upper()}**
        
        Indice calculé : {risk_index:.3f}
        
        {explanation.get('description', '')}
        
        **Recommandations :**
        {explanation.get('recommendations', 'Consultez un professionnel de santé')}
        """
    
    @staticmethod
    def _pollutant_tooltip(pollutant_data):
        """Tooltip détaillé pour un polluant"""
        if not pollutant_data:
            return "Aucune donnée de polluant disponible"
        
        pollutant = pollutant_data.get('type', 'unknown')
        value = pollutant_data.get('value', 0)
        
        info = POLLUTION_INFO.get(pollutant, {})
        
        return f"""
        **{info.get('name', pollutant.upper())}**
        
        Concentration actuelle : {value:.1f} µg/m³
        Seuil recommandé : {info.get('threshold', 'N/A')} µg/m³
        
        {info.get('description', '')}
        
        **Sources principales :**
        {info.get('sources', 'Non spécifié')}
        """
    
    @staticmethod
    def _weather_tooltip(weather_data):
        """Tooltip pour l'impact météorologique"""
        if not weather_data:
            return "Aucune donnée météo disponible"
        
        temp = weather_data.get('temp_celsius', 0)
        humidity = weather_data.get('humidity', 0)
        wind_speed = weather_data.get('wind_speed', 0)
        
        return f"""
        **Impact des conditions météorologiques**
        
        🌡️ **Température** : {temp}°C
        {TooltipComponent._get_temp_impact(temp)}
        
        💧 **Humidité** : {humidity}%
        {TooltipComponent._get_humidity_impact(humidity)}
        
        💨 **Vent** : {wind_speed} m/s
        {TooltipComponent._get_wind_impact(wind_speed)}
        """
    
    @staticmethod
    def _get_temp_impact(temp):
        """Évalue l'impact de la température"""
        if temp < 5:
            return "❄️ Très froid - Peut aggraver les problèmes respiratoires"
        elif temp < 15:
            return "🥶 Froid - Air sec, attention aux voies respiratoires"
        elif temp <= 25:
            return "😊 Température confortable"
        elif temp <= 30:
            return "🌡️ Chaud - Peut augmenter la concentration de polluants"
        else:
            return "🔥 Très chaud - Ozone élevé possible, éviter l'exposition"
    
    @staticmethod
    def _get_humidity_impact(humidity):
        """Évalue l'impact de l'humidité"""
        if humidity < 30:
            return "🏜️ Air sec - Peut irriter les voies respiratoires"
        elif humidity <= 60:
            return "😊 Humidité confortable"
        else:
            return "💧 Air humide - Peut favoriser les allergènes"
    
    @staticmethod
    def _get_wind_impact(wind_speed):
        """Évalue l'impact du vent"""
        if wind_speed < 2:
            return "🌫️ Vent faible - Accumulation possible de polluants"
        elif wind_speed <= 6:
            return "🍃 Vent modéré - Dispersion normale des polluants"
        else:
            return "💨 Vent fort - Bonne dispersion mais possibles particules en suspension"
    
    @staticmethod
    def render_sidebar_help():
        """Rendu de l'aide dans la sidebar"""
        
        with st.sidebar:
            st.markdown("### 🆘 Aide rapide")
            
            with st.expander("🎯 Indice de risque"):
                st.markdown("""
                - 🟢 **0.00-0.25** : Faible
                - 🟡 **0.26-0.50** : Modéré  
                - 🔴 **0.51-1.00** : Élevé
                """)
            
            with st.expander("💨 Polluants clés"):
                st.markdown("""
                - **PM2.5** : Particules fines
                - **PM10** : Particules en suspension
                - **O₃** : Ozone troposphérique
                - **NO₂** : Dioxyde d'azote
                """)
            
            st.markdown("---")
            st.markdown("**🌍 Couverture** : US, Canada, Europe")
            st.markdown("**🕐 Mise à jour** : ~2 heures")
