from django.shortcuts import render

# Create your views here.
import pandas as pd
import json
import plotly.express as px
import plotly
from utils.mongo_conn import get_crypto_market_data, get_binance_tickers, get_wazirx_tickers
from utils.charts import plot_top_cryptos, plot_price_change, plot_binance_volume

def main_dashboard(request):
    return render(request, 'crypto/main_dashboard.html')

def crypto_market_overview(request):
    data = get_crypto_market_data()
    context = {}

    if data and isinstance(data, list):
        latest = data[0]
        crypto_list = latest.get("crypto_data", [])
        metadata = latest.get("metadata", {})

        if crypto_list:
            # Convertimos el dataframe para la tabla simplificada
            import pandas as pd
            columns_to_show = [
                "id", "symbol", "name", "image",
                "current_price", "price_change_24h", "price_change_percentage_24h"
            ]
            df = pd.DataFrame(crypto_list)[columns_to_show]

            # Convertimos la columna "image" para HTML
            def render_image(url):
                return f'<img src="{url}" width="30">'
            df["image"] = df["image"].apply(render_image)

            # Convertimos a HTML para el template
            table_html = df.to_html(escape=False, index=False)

            # Generamos gráficos (en Django necesitarás exportarlos a JSON o imagen)
            # Por simplicidad aquí pasamos funciones o rutas a imágenes
            # Pero para tu caso debes adaptar plotly a JSON y usar plotly.js en frontend

            context = {
                "total_coins": metadata.get("total_coins", 0),
                "top_coin": metadata.get("top_coin", "N/A"),
                "source": "CoinGecko",
                "table_html": table_html,
                # TODO: pasar datos para gráficos
            }
        else:
            context["warning"] = "No cryptocurrency data available in the latest record."
    else:
        context["warning"] = "No processed crypto data found in MongoDB."

    return render(request, "crypto/market_overview.html", context)


def binance_market_data(request):
    data = get_binance_tickers()
    context = {}

    if data and isinstance(data, list):
        latest = data[0]
        binance_data = latest.get("binance_data", [])
        metadata = latest.get("metadata", {})

        if binance_data:
            columns_to_show = [
                "symbol", "price_change", "price_change_percent",
                "last_price", "high_price", "low_price"
            ]
            df = pd.DataFrame(binance_data)[columns_to_show]

            # Filtrar filas con valores estrictamente 0 en columnas numéricas
            numeric_cols = ["price_change", "price_change_percent", "last_price", "high_price", "low_price"]
            for col in numeric_cols:
                df = df[df[col] != 0]

            # Convertir DataFrame para mostrar en HTML
            table_html = df.to_html(classes="table table-striped", index=False)

            context = {
                "total_symbols": metadata.get("total_symbols", 0),
                "top_symbol": metadata.get("top_symbol", "N/A"),
                "source": "Binance API",
                "table_html": table_html,
                # Aquí se puede preparar datos para gráficos luego
            }
        else:
            context["warning"] = "No Binance ticker data found."
    else:
        context["warning"] = "No processed Binance data found in MongoDB."

    return render(request, "crypto/binance_market_data.html", context)


def wazirx_market_data(request):
    data = get_wazirx_tickers()
    context = {}

    if data and isinstance(data, list):
        latest = data[0]
        wazirx_data = latest.get("wazirx_data", [])
        metadata = latest.get("metadata", {})

        if wazirx_data:
            columns_to_show = ["symbol", "base_asset", "open_price", "high_price", "low_price"]
            df = pd.DataFrame(wazirx_data)[columns_to_show]

            numeric_cols = ["open_price", "high_price", "low_price"]
            for col in numeric_cols:
                df = df[df[col] != 0]

            # Crear gráfico con plotly.express
            top10 = df.sort_values(by="high_price", ascending=False).head(10)
            fig = px.bar(
                top10,
                x="symbol",
                y=["high_price", "low_price"],
                barmode="group",
                title="Top 10 WazirX Pairs: High vs Low Price",
                labels={"value": "Price (INR)", "symbol": "Trading Pair"}
            )

            # Convertir figura a JSON para renderizar con Plotly.js en frontend
            graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            context = {
                "total_symbols": metadata.get("total_symbols", 0),
                "top_symbol": metadata.get("top_symbol", "N/A"),
                "source": "WazirX API",
                "table_html": df.to_html(classes="table table-striped", index=False),
                "graph_json": graph_json,
            }
        else:
            context["warning"] = "No WazirX ticker data found."
    else:
        context["warning"] = "No processed WazirX data found in MongoDB."

    return render(request, "crypto/wazirx_market_data.html", context)
