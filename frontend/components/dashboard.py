"""
Dashboard component displaying key metrics and charts for the Safe Air application.

This module renders the respiratory risk index gauge, current weather and air
quality conditions, detailed analysis of normalised factors with weighted
contributions, and visualisation charts comparing factor composition and
current pollutant levels against recommended limits. All sections are laid
out responsively using columns to make efficient use of available space.

The design follows these principles:
    * Gauge and interpretation are shown together, with enlarged numbers.
    * Weather conditions and air quality metrics are displayed side by side.
    * Detailed factor analysis and visualisations are presented in parallel.
    * Risk thresholds and descriptions align with the backend algorithm and
      the accompanying documentation.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple

from utils.constants import (
    RISK_COLORS,
    POLLUTION_THRESHOLDS,
    WEATHER_THRESHOLDS,
    POLLUTION_INFO,
    WEATHER_INFO,
    RISK_INFO,
    COMPONENT_WEIGHTS,
)
from utils.helpers import format_timestamp, get_status_label_color, truncate


class DashboardComponent:
    """Render the dashboard containing all metrics and charts."""

    def render(self, risk_data: Dict) -> None:
        """Render the full dashboard.

        This method orchestrates the display of the risk index, weather
        conditions, air quality, visualisations and detailed factor analysis.
        The order of sections follows: risk index, visualisations and
        comparisons, then factor analysis. All section headers are centred.
        """
        if not risk_data:
            st.warning("⚠️ No data available")
            return
        # Extract normalised data once to share across sections
        norm_data = risk_data.get("norm", {})
        # 1. Risk index section
        self._render_risk_section(risk_data)
        # Extract components for subsequent sections
        weather_data = risk_data.get("weather", {})
        pollution_data = risk_data.get("pollution", {})
        # 2. Weather conditions
        st.markdown(
            "<h4 style='text-align:center;'>🌤️ Weather conditions</h4>",
            unsafe_allow_html=True,
        )
        self._render_weather_section(weather_data, norm_data)
        # 3. Air quality
        st.markdown(
            "<h4 style='text-align:center;'>🏭 Air quality</h4>", unsafe_allow_html=True
        )
        self._render_pollution_section(pollution_data, norm_data)
        # 4. Visualisations (placed before factor analysis)
        st.markdown(
            "<h4 style='text-align:center;'>📈 Visualisations</h4>",
            unsafe_allow_html=True,
        )
        self._render_visualisations(risk_data)
        # 5. Detailed factor analysis
        st.markdown(
            "<h4 style='text-align:center;'>🔬 Detailed factor analysis</h4>",
            unsafe_allow_html=True,
        )
        self._render_factor_table(norm_data, risk_data)

    # ------------------------------------------------------------------
    # Risk index gauge and interpretation
    def _render_risk_section(self, risk_data: Dict) -> None:
        risk_index = risk_data["risk_index"]
        # Determine label and colour based on normalised risk index
        label, colour_name = get_status_label_color(risk_index)
        st.markdown("#### 🎯 Respiratory Risk Index")
        # Centre the gauge using columns
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            # Use the full risk_index for colour calculations but truncate
            # the displayed value to two decimals without rounding.
            display_idx = truncate(risk_index, 2)
            fig = self._create_risk_gauge(display_idx, label)
            st.plotly_chart(fig, use_container_width=True)
            # Short interpretation below the gauge
            # Display a concise interpretation based on the risk level
            if label == "Optimal":
                st.success("🟢 OPTIMAL – conditions safe for all.")
            elif label == "Precaution":
                st.warning(
                    "🟡 PRECAUTION – recommended limitations for sensitive people."
                )
            else:
                st.error("🔴 RISK – avoid outdoor activities.")
        # Last updated timestamp for risk index uses weather timestamp
        ts = risk_data.get("weather", {}).get("timestamp", "")
        st.caption(f"🕐 Last updated: {format_timestamp(ts)}")

    def _create_risk_gauge(self, risk_index: float, risk_label: str) -> go.Figure:
        """Create a circular gauge visualising the risk index.

        Threshold ranges align with the backend: 0–0.2 (low), 0.2–0.4 (moderate), >0.4 (high).
        The gauge number font is enlarged for better readability.
        """
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_index,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Risk index"},
                number={"font": {"size": 36}},
                gauge={
                    "axis": {"range": [0, 1], "tickwidth": 1, "tickcolor": "#888888"},
                    # Colour the bar according to the adjusted thresholds (<0.21 green, <0.41 yellow, else red)
                    "bar": {
                        "color": (
                            RISK_COLORS["LOW"]
                            if risk_index < 0.21
                            else (
                                RISK_COLORS["MODERATE"]
                                if risk_index < 0.41
                                else RISK_COLORS["HIGH"]
                            )
                        )
                    },
                    "steps": [
                        {"range": [0.0, 0.21], "color": RISK_COLORS["LOW"]},
                        {"range": [0.21, 0.41], "color": RISK_COLORS["MODERATE"]},
                        {"range": [0.41, 1.0], "color": RISK_COLORS["HIGH"]},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 2},
                        "thickness": 0.75,
                        "value": 0.8,
                    },
                },
            )
        )
        fig.update_layout(height=350, margin={"t": 40, "b": 0, "l": 20, "r": 20})
        return fig

    def _get_risk_interpretation(self, risk_label: str) -> str:
        """Return a short interpretation string for the risk level."""
        info = RISK_INFO.get(risk_label.upper())
        if not info:
            return "Risk level undetermined"
        description = info["description"]
        # Use only the first sentence for a concise message
        if "." in description:
            description = description.split(".", 1)[0] + "."
        return description.strip()

    # ------------------------------------------------------------------
    # Weather conditions
    def _render_weather_section(self, weather_data: Dict, norm_data: Dict) -> None:
        """Display temperature, humidity and wind with statuses based on
        normalised values.

        The backend provides a dictionary ``norm_data`` with normalised values
        for each factor. These values (0–1) are used to derive a
        qualitative label and colour (green/yellow/red) via
        ``get_status_label_color``. If a normalised value is missing, it is
        approximated using the thresholds defined in ``WEATHER_THRESHOLDS``.
        """
        temp = weather_data.get("temp_celsius", 0.0)
        humidity = weather_data.get("humidity", 0.0)
        wind_speed = weather_data.get("wind_speed", 0.0)
        timestamp = weather_data.get("timestamp", "")
        # Retrieve normalised values; approximate if absent
        norm_temp = norm_data.get("temp")
        norm_hum = norm_data.get("hum")
        norm_wind = norm_data.get("wind")

        # Approximation helper: 0 when within range, else linear outside
        def approx_norm(value: float, min_val: float, max_val: float) -> float:
            if min_val <= value <= max_val:
                return 0.0
            elif value < min_val:
                return min((min_val - value) / (max_val - min_val), 1.0)
            else:
                return min((value - max_val) / (max_val - min_val), 1.0)

        if norm_temp is None:
            norm_temp = approx_norm(
                temp, WEATHER_THRESHOLDS["temp_min"], WEATHER_THRESHOLDS["temp_max"]
            )
        if norm_hum is None:
            norm_hum = approx_norm(
                humidity,
                WEATHER_THRESHOLDS["humidity_min"],
                WEATHER_THRESHOLDS["humidity_max"],
            )
        if norm_wind is None:
            # Wind is optimal above 10 m/s; risk increases as wind decreases
            norm_wind = 0.0 if wind_speed >= 10 else min((10 - wind_speed) / 10, 1.0)
        # Map colours to emoji
        emoji_map = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
        temp_label, temp_colour = get_status_label_color(norm_temp)
        hum_label, hum_colour = get_status_label_color(norm_hum)
        wind_label, wind_colour = get_status_label_color(norm_wind)
        # Display metrics in columns
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="🌡️ Temperature", value=f"{truncate(temp,2):.2f}\u00a0°C")
            st.caption(f"Status: {emoji_map[temp_colour]} {temp_label}")
        with c2:
            st.metric(label="💧 Humidity", value=f"{truncate(humidity,2):.2f}%")
            st.caption(f"Status: {emoji_map[hum_colour]} {hum_label}")
        with c3:
            wind_kmh = wind_speed * 3.6
            st.metric(
                label="💨 Wind",
                value=f"{truncate(wind_speed,2):.2f}\u00a0m/s",
                help=f"≈ {truncate(wind_kmh,2):.2f}\u00a0km/h",
            )
            st.caption(f"Status: {emoji_map[wind_colour]} {wind_label}")
        # Show last updated time in local timezone
        st.caption(f"🕐 Last updated: {format_timestamp(timestamp)}")

    def _get_weather_description(self, raw_weather: Dict) -> str:
        """Extract a human‑readable weather description from OpenWeather data."""
        try:
            if raw_weather.get("weather"):
                desc = raw_weather["weather"][0].get("description", "")
                return desc.title()
        except Exception:
            pass
        return "N/A"

    # ------------------------------------------------------------------
    # Air quality
    def _render_pollution_section(self, pollution_data: Dict, norm_data: Dict) -> None:
        """Display air quality metrics and their statuses based on normalised values.

        Each pollutant's normalised value is used to derive a label and colour via
        ``get_status_label_color``. When a normalised value is missing, it is
        approximated by dividing the concentration by its threshold (capped at 1).
        The update timestamp is displayed below the metrics.
        """
        components = pollution_data.get("components", {})
        timestamp = pollution_data.get("timestamp", "")

        # Helper to get normalised value (fallback: value / threshold)
        def get_norm(pollutant: str, value: float) -> float:
            nval = norm_data.get(pollutant)
            if nval is not None:
                return nval
            threshold = POLLUTION_THRESHOLDS.get(pollutant, 1.0)
            return min(value / threshold, 1.0)

        # Map colours to emoji
        emoji_map = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
        # Primary pollutants displayed in columns
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            pm25 = components.get("pm2_5", 0.0)
            n = get_norm("pm2_5", pm25)
            label, colour = get_status_label_color(n)
            st.metric(
                label="PM2.5",
                value=f"{truncate(pm25,2):.2f}\u00a0µg/m³",
                help=POLLUTION_INFO["pm2_5"]["description"],
            )
            st.caption(f"Status: {emoji_map[colour]} {label}")
        with p_col2:
            pm10 = components.get("pm10", 0.0)
            n = get_norm("pm10", pm10)
            label, colour = get_status_label_color(n)
            st.metric(
                label="PM10",
                value=f"{truncate(pm10,2):.2f}\u00a0µg/m³",
                help=POLLUTION_INFO["pm10"]["description"],
            )
            st.caption(f"Status: {emoji_map[colour]} {label}")
        with p_col3:
            o3 = components.get("o3", 0.0)
            n = get_norm("o3", o3)
            label, colour = get_status_label_color(n)
            st.metric(
                label="O₃",
                value=f"{truncate(o3,2):.2f}\u00a0µg/m³",
                help=POLLUTION_INFO["o3"]["description"],
            )
            st.caption(f"Status: {emoji_map[colour]} {label}")
        # Secondary pollutants in an expander
        with st.expander("🔬 Other pollutants"):
            s1, s2, s3 = st.columns(3)
            with s1:
                no2 = components.get("no2", 0.0)
                n = get_norm("no2", no2)
                label, colour = get_status_label_color(n)
                st.metric(
                    "NO₂",
                    f"{truncate(no2,2):.2f}\u00a0µg/m³",
                    help=POLLUTION_INFO["no2"]["description"],
                )
                st.caption(f"Status: {emoji_map[colour]} {label}")
            with s2:
                so2 = components.get("so2", 0.0)
                n = get_norm("so2", so2)
                label, colour = get_status_label_color(n)
                st.metric(
                    "SO₂",
                    f"{truncate(so2,2):.2f}\u00a0µg/m³",
                    help=POLLUTION_INFO["so2"]["description"],
                )
                st.caption(f"Status: {emoji_map[colour]} {label}")
            with s3:
                co = components.get("co", 0.0)
                n = get_norm("co", co)
                label, colour = get_status_label_color(n)
                st.metric(
                    "CO",
                    f"{truncate(co,2):.2f}\u00a0µg/m³",
                    help=POLLUTION_INFO["co"]["description"],
                )
                st.caption(f"Status: {emoji_map[colour]} {label}")
        # Last updated time for pollution data
        st.caption(f"🕐 Last updated: {format_timestamp(timestamp)}")

    # ------------------------------------------------------------------
    # Detailed factor analysis
    def _render_factor_table(self, norm_data: Dict, risk_data: Dict) -> None:
        """Display a table summarising each factor's contribution, value and normalised value.

        The table includes the weight contribution percentage, factor label, raw value with
        units, normalised value and qualitative status (Optimal/Precaution/Risk).
        Rows are sorted by contribution from highest to lowest.
        """
        if not norm_data:
            st.info("No normalised data available")
            return
        # Use static component weights (defined in constants) for the contribution column.  These
        # percentages reflect the relative importance of each factor in the risk algorithm as
        # described in the documentation.  Dynamic contributions can be misleading if used here.
        contributions = COMPONENT_WEIGHTS.copy()
        # Build data rows
        rows: List[Dict[str, str]] = []
        # Mapping for units and raw values
        weather = risk_data.get("weather", {})
        pollution = risk_data.get("pollution", {}).get("components", {})
        factor_values = {
            "temp": (weather.get("temp_celsius"), "°C"),
            "hum": (weather.get("humidity"), "%"),
            "wind": (weather.get("wind_speed"), "m/s"),
            "pm2_5": (pollution.get("pm2_5"), "µg/m³"),
            "pm10": (pollution.get("pm10"), "µg/m³"),
            "o3": (pollution.get("o3"), "µg/m³"),
            "no2": (pollution.get("no2"), "µg/m³"),
            "so2": (pollution.get("so2"), "µg/m³"),
            "co": (pollution.get("co"), "µg/m³"),
        }
        # Create rows
        for factor, weight in contributions.items():
            value, unit = factor_values.get(factor, (None, ""))
            norm_val = norm_data.get(factor, 0.0)
            label, colour = get_status_label_color(norm_val)
            emoji_map = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
            rows.append(
                {
                    "Factor": factor.upper(),
                    "Contribution (%)": f"{weight * 100:.0f}",
                    "Value": (
                        f"{truncate(value,2):.2f} {unit}"
                        if value is not None
                        else "N/A"
                    ),
                    "Normalised": f"{truncate(norm_val,2):.2f}",
                    "Status": f"{emoji_map[colour]} {label}",
                }
            )
        # Sort rows by contribution descending
        rows.sort(key=lambda r: float(r["Contribution (%)"]), reverse=True)
        import pandas as pd

        df = pd.DataFrame(rows)[
            ["Factor", "Contribution (%)", "Value", "Normalised", "Status"]
        ]
        # Display table with index hidden and full width
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # Visualisation charts
    def _render_visualisations(self, risk_data: Dict) -> None:
        """Render charts comparing current values with their health limits.

        This method displays two charts:
          • A bar/line chart for pollutants comparing current concentrations with
            their health limits (µg/m³).
          • A bar/line chart for meteorological factors comparing current values
            with their optimal ranges or thresholds.
        """
        # Weather threshold chart
        self._render_weather_threshold_chart(risk_data.get("weather", {}))

        # Pollutant threshold chart
        self._render_pollutant_threshold_chart(risk_data.get("pollution", {}))

    def _render_pollutant_threshold_chart(self, pollution_data: Dict) -> None:
        """Bar/line chart comparing current pollutant levels with health limits."""
        components = pollution_data.get("components", {})
        # Exclude CO from this chart due to its much larger scale, which makes
        # the chart hard to read.  Only include pollutants with comparable
        # thresholds.
        pollutants = ["pm2_5", "pm10", "o3", "no2", "so2"]
        current_values = [components.get(p, 0.0) for p in pollutants]
        thresholds = [POLLUTION_THRESHOLDS.get(p, 0.0) for p in pollutants]
        # Names for display (use chemical symbols)
        labels = ["PM2.5", "PM10", "O₃", "NO₂", "SO₂"]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name="Current value",
                x=labels,
                y=current_values,
                marker_color="lightblue",
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Health limit",
                x=labels,
                y=thresholds,
                mode="markers",
                line=dict(color="red", width=3, dash="dash"),
                marker=dict(size=8),
            )
        )
        fig.update_layout(
            title="Pollutant levels vs health limits",
            xaxis_title="Pollutants",
            yaxis_title="Concentration (µg/m³)",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)

    def _render_weather_threshold_chart(self, weather_data: Dict) -> None:
        """Chart comparing current weather metrics with their optimal ranges."""
        temp = weather_data.get("temp_celsius", 0.0)
        humidity = weather_data.get("humidity", 0.0)
        wind_speed = weather_data.get("wind_speed", 0.0)
        # Prepare data
        metrics = ["Temperature", "Humidity", "Wind speed"]
        current_values = [temp, humidity, wind_speed]
        # Define bounds for each metric: (lower, upper). For wind, upper bound is None.
        bounds = [
            (WEATHER_THRESHOLDS["temp_min"], WEATHER_THRESHOLDS["temp_max"]),
            (WEATHER_THRESHOLDS["humidity_min"], WEATHER_THRESHOLDS["humidity_max"]),
            (10.0, None),
        ]
        # Colour palette for bounds (distinct per metric)
        bound_colors = ["#d62728", "#9467bd", "#2ca02c"]  # red, purple, green
        fig = go.Figure()
        # Bars for current values (same colour as pollutant chart bars)
        fig.add_trace(
            go.Bar(
                name="Current value",
                x=metrics,
                y=current_values,
                marker_color="lightblue",
            )
        )
        # Add markers for bounds for each metric without connecting lines
        for idx, (metric, (lower, upper)) in enumerate(zip(metrics, bounds)):
            # Lower bound marker
            fig.add_trace(
                go.Scatter(
                    name=f"{metric} bound",
                    x=[metric],
                    y=[lower],
                    mode="markers",
                    marker=dict(color=bound_colors[idx], size=10, symbol="circle-open"),
                    # Use double curly braces in the f-string to escape the Plotly placeholder
                    hovertemplate=f"{metric} lower bound: %{{y:.2f}}",
                    showlegend=False,
                )
            )
            # Upper bound marker if exists
            if upper is not None:
                fig.add_trace(
                    go.Scatter(
                        name=f"{metric} bound",
                        x=[metric],
                        y=[upper],
                        mode="markers",
                        marker=dict(
                            color=bound_colors[idx], size=10, symbol="circle-open"
                        ),
                        hovertemplate=f"{metric} upper bound: %{{y:.2f}}",
                        showlegend=False,
                    )
                )
        fig.update_layout(
            title="Weather metrics vs comfort ranges",
            xaxis_title="Metrics",
            yaxis_title="Value",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
