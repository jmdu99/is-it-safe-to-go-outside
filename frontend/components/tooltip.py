"""
Tooltip component providing contextual help and guidance for the Safe Air app.

This component renders collapsible sections containing usage instructions,
explanations of the risk index levels, detailed information about pollutants
and weather factors, and notes about API limitations and data sources. It also
offers a sidebar version for quick reference. All content is presented in
English and reflects the current risk thresholds and factor weights.
"""

from __future__ import annotations

import streamlit as st

from utils.constants import POLLUTION_INFO, WEATHER_INFO, RISK_INFO


class TooltipComponent:
    @staticmethod
    def render_help_section() -> None:
        """Render an expandable help guide within the main page."""
        st.markdown("### ❓ User guide")
        # How to use the application
        with st.expander("🔍 How to use the application"):
            st.markdown(
                """
            **Steps:**
            1. **Search** for a place using the search bar.
            2. **Select** a suggestion from the list (press Enter to fetch suggestions).
            3. **View** the risk data on the interactive map and dashboard.
            4. **Interpret** the results using the colour‑coded indicators.

            **Features:**
            - 🔍 Real‑time search with autocompletion
            - 🗺️ Interactive map with coloured markers
            - 📊 Detailed dashboard with metrics and charts
            - 🎯 Respiratory risk index combining weather and air quality
            """
            )
        # Risk level explanation
        with st.expander("🎯 Understanding the risk index"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    """
                **🟢 LOW (0.00–0.20)**
                
                - Excellent conditions
                - Outdoor activities encouraged
                - No special precautions
                """
                )
            with col2:
                st.markdown(
                    """
                **🟡 MODERATE (0.21–0.40)**
                
                - Acceptable conditions
                - Sensitive individuals should take care
                - Reduce prolonged exposure
                """
                )
            with col3:
                st.markdown(
                    """
                **🔴 HIGH (0.41–1.00)**
                
                - Unfavourable conditions
                - Avoid prolonged outdoor activities
                - Consider wearing a mask
                """
                )
        # Pollutant information
        with st.expander("💨 Air quality – Pollutants"):
            TooltipComponent._render_pollution_info()
        # Weather information
        with st.expander("🌡️ Weather conditions"):
            TooltipComponent._render_weather_info()
        # Limitations and data sources
        with st.expander("⚠️ Limitations and sources"):
            st.markdown(
                """
            **Current limitations:**
            - Mapbox APIs primarily support the United States, Canada and Europe.
            - OpenWeather data updates approximately every 2 hours.
            - The risk index is calculated using our proprietary algorithm based on
              scientific evidence and public guidelines.

            **Data sources:**
            - 🗺️ **Geolocation:** Mapbox Search API
            - 🌡️ **Weather:** OpenWeather API
            - 💨 **Air quality:** OpenWeather Air Pollution API

            **Risk calculation:**
            The index combines weighted concentrations of pollutants
            (PM2.5, PM10, O₃, NO₂, SO₂, CO) and normalised weather
            factors (temperature, humidity, wind speed) according to
            the documentation.
            """
            )

    @staticmethod
    def _render_pollution_info() -> None:
        st.markdown("**Monitored pollutants:**")
        for pollutant, info in POLLUTION_INFO.items():
            with st.container():
                st.markdown(f"**{pollutant.upper()}** – {info['name']}")
                st.write(f"• {info['description']}")
                st.write(f"• Limit value: {info['threshold']} µg/m³")
                st.write(f"• Sources: {info['sources']}")
                st.markdown("---")

    @staticmethod
    def _render_weather_info() -> None:
        st.markdown("**Weather factors considered:**")
        for factor, info in WEATHER_INFO.items():
            st.markdown(f"**{info['name']}**")
            st.write(f"• {info['description']}")
            st.write(f"• Optimal range: {info['optimal_range']}")
            st.markdown("---")

    @staticmethod
    def render_contextual_tooltip(tooltip_type: str, data: dict | None = None) -> str:
        """Return a context‑specific tooltip message."""
        if tooltip_type == "risk_explanation":
            return TooltipComponent._risk_tooltip(data)
        elif tooltip_type == "pollutant_detail":
            return TooltipComponent._pollutant_tooltip(data)
        elif tooltip_type == "weather_impact":
            return TooltipComponent._weather_tooltip(data)
        else:
            return "ℹ️ No information available"

    @staticmethod
    def _risk_tooltip(risk_data: dict | None) -> str:
        if not risk_data:
            return "No risk data available"
        risk_label = risk_data.get("risk_label", "Unknown")
        risk_index = risk_data.get("risk_index", 0.0)
        explanation = RISK_INFO.get(risk_label.upper(), {})
        return f"""
        **Risk level: {risk_label.upper()}**

        Calculated index: {risk_index:.3f}

        {explanation.get('description', '')}

        **Recommendations:**
        {explanation.get('recommendations', 'Consult a healthcare professional')}
        """

    @staticmethod
    def _pollutant_tooltip(pollutant_data: dict | None) -> str:
        if not pollutant_data:
            return "No pollutant data available"
        pollutant = pollutant_data.get("type", "unknown").lower()
        value = pollutant_data.get("value", 0.0)
        info = POLLUTION_INFO.get(pollutant, {})
        return f"""
        **{info.get('name', pollutant.upper())}**

        Current concentration: {value:.1f} µg/m³
        Limit value: {info.get('threshold', 'N/A')} µg/m³

        {info.get('description', '')}

        **Main sources:**
        {info.get('sources', 'Not specified')}
        """

    @staticmethod
    def _weather_tooltip(weather_data: dict | None) -> str:
        if not weather_data:
            return "No weather data available"
        temp = weather_data.get("temp_celsius", 0.0)
        humidity = weather_data.get("humidity", 0.0)
        wind_speed = weather_data.get("wind_speed", 0.0)
        return f"""
        **Impact of weather conditions**

        🌡️ **Temperature**: {temp:.1f} °C
        {TooltipComponent._get_temp_impact(temp)}

        💧 **Humidity**: {humidity:.0f}%
        {TooltipComponent._get_humidity_impact(humidity)}

        💨 **Wind**: {wind_speed:.1f} m/s
        {TooltipComponent._get_wind_impact(wind_speed)}
        """

    @staticmethod
    def _get_temp_impact(temp: float) -> str:
        if temp < 5:
            return "❄️ Very cold – may worsen respiratory problems"
        elif temp < 15:
            return "🥶 Cold – dry air can irritate airways"
        elif temp <= 25:
            return "😊 Comfortable temperature"
        elif temp <= 30:
            return "🌡️ Warm – may increase pollutant concentration"
        else:
            return "🔥 Very hot – high ozone possible, avoid exposure"

    @staticmethod
    def _get_humidity_impact(humidity: float) -> str:
        if humidity < 30:
            return "🏜️ Dry air – can irritate airways"
        elif humidity <= 60:
            return "😊 Comfortable humidity"
        else:
            return "💧 Humid air – may promote allergens"

    @staticmethod
    def _get_wind_impact(wind_speed: float) -> str:
        if wind_speed < 2:
            return "🌫️ Weak wind – pollutant accumulation likely"
        elif wind_speed <= 6:
            return "🍃 Moderate wind – normal dispersion of pollutants"
        else:
            return "💨 Strong wind – good dispersion but resuspended particles possible"

    @staticmethod
    def render_sidebar_help() -> None:
        """Render a quick help reference in the sidebar."""
        with st.sidebar:
            st.markdown("### 🆘 Quick help")
            with st.expander("🎯 Risk index"):
                st.markdown(
                    """
                - 🟢 **0.00–0.20**: Low
                - 🟡 **0.21–0.40**: Moderate
                - 🔴 **0.41–1.00**: High
                """
                )
            with st.expander("💨 Key pollutants"):
                st.markdown(
                    """
                - **PM2.5**: Fine particulate matter
                - **PM10**: Coarse particulate matter
                - **O₃**: Ozone
                - **NO₂**: Nitrogen dioxide
                - **SO₂**: Sulphur dioxide
                - **CO**: Carbon monoxide
                """
                )
            st.markdown("---")
            st.markdown("**🌍 Coverage**: US, Canada & Europe")
            st.markdown("**🕐 Data updates**: approx. every 2 hours")
