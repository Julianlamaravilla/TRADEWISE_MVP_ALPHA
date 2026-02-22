"""
app.py
Aplicación Streamlit para análisis de trading con Gemini.
Punto de entrada: streamlit run app.py
"""

import streamlit as st
from data_fetcher import get_historical_data, get_news_headlines, validate_ticker
from indicators import compute_all_indicators
from llm_client import generate_analysis


# Configuración de la página
st.set_page_config(page_title="TradeWise MVP", page_icon="📈", layout="wide")

st.title("📈 TradeWise MVP")
st.caption("Análisis de trading asistido por IA (no sustituye asesoría profesional)")


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
        "1. **Análisis técnico**: Interpretación de medias móviles, RSI y volatilidad.",
        "2. **Sentimiento de noticias**: Clasifica el sentimiento general como POSITIVO, NEGATIVO o NEUTRAL y justifica brevemente.",
        "3. **Escenario alcista**: Posible evolución favorable y condiciones que la apoyarían.",
        "4. **Escenario bajista**: Posibles riesgos y evolución desfavorable.",
        "5. **Evaluación de riesgo**: Nivel de riesgo (bajo/medio/alto) y por qué.",
        "6. **Recomendación según perfil**: Adapta el tono y las consideraciones al perfil de riesgo indicado.",
        "7. **Advertencia**: Incluye una advertencia explícita de que este análisis NO es asesoría financiera y que el usuario debe consultar a un profesional.",
    ])
    return "\n".join(lines)


def main():
    ticker = st.text_input("Ticker", value="AAPL", placeholder="Ej: AAPL, MSFT, GOOGL").strip().upper()
    risk_profile = st.selectbox(
        "Perfil de riesgo",
        options=["Conservador", "Moderado", "Agresivo"],
        index=1,
    )
    horizon = st.selectbox(
        "Horizonte",
        options=["Corto plazo", "Mediano plazo", "Largo plazo"],
        index=1,
    )

    if not ticker:
        st.warning("Ingresa un ticker para continuar.")
        return

    if st.button("Generar análisis"):
        with st.spinner("Validando ticker y obteniendo datos..."):
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

        with st.spinner("Generando análisis con IA..."):
            success, result = generate_analysis(context)
        if not success:
            st.error(result)
            return

        # Mostrar resultados en secciones
        st.divider()
        st.subheader("Resultado del análisis")
        st.markdown(result)
        st.divider()
        st.caption("TradeWise MVP — Este contenido no constituye asesoría financiera. Consulta a un profesional.")


if __name__ == "__main__":
    main()
