"""
app.py
Aplicación Streamlit para análisis de trading con Gemini.
Punto de entrada: streamlit run app.py
"""

import streamlit as st
import altair as alt
from data_fetcher import get_historical_data, get_news_headlines, validate_ticker
from indicators import compute_all_indicators
from llm_client import generate_analysis
from tickers import TOP_100_TICKERS


# Configuración de la página
st.set_page_config(page_title="TradeWise AI", page_icon="📈", layout="wide")

# Estilos personalizados (tema fintech azul, botones, contenedores)
st.markdown(
    """
    <style>
    /* Ajuste general de la zona principal */
    main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Botón principal más grande, redondeado y con sombra */
    .stButton > button {
        background-color: #1E3A8A;
        color: #E2E8F0;
        border-radius: 999px;
        padding: 0.6rem 1.6rem;
        border: none;
        font-weight: 600;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.55);
    }
    .stButton > button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.75);
    }

    /* Tarjetas de métricas con fondo contrastado y bordes redondeados */
    div[data-testid="stMetric"] {
        background-color: #020617;
        padding: 1rem 1.25rem;
        border-radius: 0.9rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.75);
    }

    /* Contenedores de análisis con fondo ligeramente más claro */
    .analysis-container {
        background-color: #020617;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 6px 22px rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def build_context(ticker: str, risk_profile: str, horizon: str, indicators: dict, headlines: list[str]) -> str:
    """Construye el contexto estructurado para enviar al LLM."""
    lines = [
        "# Contexto para análisis de trading",
        "",
        f"## Activo: {ticker}",
        f"- Perfil de riesgo del usuario: {risk_profile}",
        f"- Horizonte de inversión: {horizon}",
        "",
        "## Indicadores técnicos (últimos 6 meses)",
        f"- Precio de cierre más reciente: {indicators.get('last_close')}",
        f"- Media móvil 20 días: {indicators.get('ma_20')}",
        f"- Media móvil 50 días: {indicators.get('ma_50')}",
        f"- RSI (14): {indicators.get('rsi')}",
        f"- Volatilidad anualizada (desv. estándar retornos): {indicators.get('volatility')}",
        "",
        "## Titulares recientes",
    ]
    if headlines:
        for h in headlines:
            lines.append(f"- {h}")
    else:
        lines.append("- No se encontraron titulares recientes.")
    lines.extend([
        "",
        "---",
        "",
        "Responde en español, de forma clara y estructurada. Incluye las siguientes secciones:",
        "1. **Análisis técnico**: Explica detalladamente la relación entre medias móviles, RSI y volatilidad. Justifica cada interpretación con base en los valores proporcionados.",
        "2. **Sentimiento de noticias**: Clasifica el sentimiento general como POSITIVO, NEGATIVO o NEUTRAL y justifica brevemente.",
        "3. **Escenario alcista**: Describe condiciones específicas que deberían cumplirse para que este escenario ocurra. Sé técnico y específico.",
        "4. **Escenario bajista**: Describe riesgos concretos y señales técnicas que confirmarían este escenario.",
        "5. **Evaluación de riesgo**: Nivel de riesgo (bajo/medio/alto) y por qué.",
        "6. **Recomendación según perfil**: Adapta el tono y las consideraciones al perfil de riesgo indicado.",
        "7. **Advertencia**: Incluye una advertencia explícita de que este análisis NO es asesoría financiera y que el usuario debe consultar a un profesional.",
        "8. **Advertencia**: Para el sentimiento, primero analiza brevemente cada titular y luego sintetiza el sentimiento general justificando con ejemplos concretos.",
        "9. **Advertencia**: Desarrolla cada sección con al menos 2–3 párrafos explicativos. No seas breve. Profundiza en la interpretación técnica y contextual."
    ])
    return "\n".join(lines)


def main():
    # Sidebar: panel de control
    with st.sidebar:
        st.markdown("### Panel de control")
        selected_ticker = st.selectbox(
            "Seleccione una acción:",
            TOP_100_TICKERS,
        )
        ticker = selected_ticker
        risk_profile = st.selectbox(
            "Perfil de riesgo",
            options=["Conservador", "Moderado", "Agresivo"],
            index=1,
        )
        horizon = st.selectbox(
            "Horizonte de inversión",
            options=["Corto plazo", "Mediano plazo", "Largo plazo"],
            index=1,
        )
        generate_clicked = st.button("Generar análisis", use_container_width=True)

        st.markdown("---")
        st.caption(
            "Universo limitado a acciones del S&P 100 para garantizar "
            "liquidez y calidad de datos."
        )

    # Header principal en el área central
    st.markdown("## TradeWise AI")
    st.markdown(
        "_Análisis inteligente de acciones basado en IA — diseñado para una visión clara, "
        "profesional y orientada a decisiones._"
    )
    st.divider()

    if generate_clicked:
        with st.spinner("Validando ticker y obteniendo datos..."):
            if ticker not in TOP_100_TICKERS:
                st.error("Ticker no permitido. Solo se pueden analizar las 100 acciones principales.")
                return
            if not validate_ticker(ticker):
                st.error(f"Ticker '{ticker}' no válido o sin datos. Verifica el símbolo e intenta de nuevo.")
                return
            prices = get_historical_data(ticker, months=6)
            headlines = get_news_headlines(ticker, max_headlines=10)
        if prices is None or prices.empty:
            st.error("No se pudieron obtener datos históricos para este ticker.")
            return

        indicators = compute_all_indicators(prices)
        context = build_context(ticker, risk_profile, horizon, indicators, headlines)

        # Sección de métricas visuales
        st.markdown("### Indicadores clave")
        col1, col2, col3, col4, col5 = st.columns(5)
        last_close = indicators.get("last_close")
        ma_20 = indicators.get("ma_20")
        ma_50 = indicators.get("ma_50")
        rsi = indicators.get("rsi")
        vol = indicators.get("volatility")

        col1.metric(
            "Precio actual",
            f"${last_close:,.2f}" if last_close is not None else "N/A",
        )
        col2.metric(
            "SMA 20",
            f"${ma_20:,.2f}" if ma_20 is not None else "N/A",
        )
        col3.metric(
            "SMA 50",
            f"${ma_50:,.2f}" if ma_50 is not None else "N/A",
        )
        col4.metric(
            "RSI (14)",
            f"{rsi:.2f}" if rsi is not None else "N/A",
        )
        col5.metric(
            "Volatilidad anualizada",
            f"{vol * 100:.2f} %" if vol is not None else "N/A",
        )

        # Gráfico profesional de precio histórico
        st.markdown("### Evolución del precio (últimos 6 meses)")
        price_df = prices[["Close"]].reset_index()
        price_df.columns = ["Fecha", "Precio de cierre"]
        price_chart = (
            alt.Chart(price_df)
            .mark_line(interpolate="monotone")
            .encode(
                x=alt.X("Fecha:T", title="Fecha"),
                y=alt.Y("Precio de cierre:Q", title="Precio de cierre (USD)"),
                tooltip=["Fecha:T", "Precio de cierre:Q"],
            )
            .properties(height=400)
        )
        st.altair_chart(price_chart, use_container_width=True)

        # Análisis generado por IA en contenedor elegante
        with st.spinner("Analizando datos y generando informe con IA..."):
            success, result = generate_analysis(context)
        if not success:
            st.error(result)
            return

        st.markdown("### Análisis generado por IA")
        with st.container():
            st.markdown(
                '<div class="analysis-container">',
                unsafe_allow_html=True,
            )
            with st.expander("Ver análisis completo", expanded=True):
                st.markdown(result)
            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        st.caption(
            "TradeWise AI — Este contenido no constituye asesoría financiera. "
            "Consulta siempre a un profesional."
        )


if __name__ == "__main__":
    main()
