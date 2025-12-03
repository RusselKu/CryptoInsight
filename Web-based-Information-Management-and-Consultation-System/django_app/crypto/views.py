import requests
from django.shortcuts import render

# Create your views here.
import pandas as pd
import json
import plotly.express as px
import plotly
from utils.mongo_conn import get_crypto_market_data, get_binance_tickers, get_wazirx_tickers
from utils.charts import plot_top_cryptos, plot_price_change, plot_binance_volume

from django.shortcuts import render, redirect, get_object_or_404
from .models import CryptoMarket  # modelo mongoengine
from .forms import CryptoMarketForm  # crear formulario para editar/crear
from django.contrib.auth.decorators import login_required

@login_required
def crypto_list(request):
    items = CryptoMarket.objects.all()
    return render(request, 'crypto/crypto_list.html', {'items': items})

@login_required
def crypto_create(request):
    if request.method == 'POST':
        form = CryptoMarketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crypto_list')
    else:
        form = CryptoMarketForm()
    return render(request, 'crypto/crypto_form.html', {'form': form})

@login_required
def crypto_edit(request, pk):
    item = get_object_or_404(CryptoMarket, pk=pk)
    if request.method == 'POST':
        form = CryptoMarketForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('crypto_list')
    else:
        form = CryptoMarketForm(instance=item)
    return render(request, 'crypto/crypto_form.html', {'form': form})

@login_required
def crypto_delete(request, pk):
    item = get_object_or_404(CryptoMarket, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('crypto_list')
    return render(request, 'crypto/crypto_confirm_delete.html', {'item': item})




def main_dashboard(request):
    title = "Crypto Dashboard Central"
    
    # Comparison data example
    comparison_data = {
        "Binance": {
            "Description": "One of the largest exchanges worldwide, offering a wide variety of pairs and high liquidity.",
            "URL": "/binance/"
        },
        "WazirX": {
            "Description": "A popular exchange in India, rapidly growing with strong integration with Binance.",
            "URL": "/wazirx/"
        }
    }
    
    context = {
        "title": title,
        "comparison_data": comparison_data,
    }
    return render(request, 'crypto/main_dashboard.html', context)


def crypto_market_overview(request):
    data = get_crypto_market_data()
    context = {}

    if data and isinstance(data, list):
        latest = data[0]
        crypto_list = latest.get("crypto_data", [])
        metadata = latest.get("metadata", {})

        if crypto_list:
            # Columnas que queremos mostrar y sus nombres amigables
            columns_to_show = [
                "id", "symbol", "name", "image",
                "current_price", "price_change_24h", "price_change_percentage_24h"
            ]
            df = pd.DataFrame(crypto_list)

            # --- Call Prediction API ---
            try:
                # Running inside Docker, so we can use the service name or localhost
                prediction_url = "http://localhost:8000/predictions/crypto-predictions/"
                response = requests.get(prediction_url)
                response.raise_for_status() # Raise an exception for bad status codes
                predictions_data = response.json().get('predictions', [])
                
                if predictions_data:
                    preds_df = pd.DataFrame(predictions_data)[['symbol', 'prediction']]
                    # Convert prediction from 0/1 to a more descriptive string
                    preds_df['Prediction'] = preds_df['prediction'].apply(lambda x: 'Up' if x == 1 else 'Down')
                    
                    # Merge predictions into the main dataframe
                    df = pd.merge(df, preds_df[['symbol', 'Prediction']], on='symbol', how='left')
                    # Add 'Prediction' to the columns to show if it's not already there
                    if 'Prediction' not in columns_to_show:
                        columns_to_show.append('Prediction')

            except requests.exceptions.RequestException as e:
                print(f"Could not get predictions from API: {e}")
                df['Prediction'] = 'N/A' # Add a placeholder column
            
            df = df[columns_to_show]
            # --- End Prediction API Call ---

            # Ajustar formato de columnas numéricas
            df["current_price"] = df["current_price"].map(lambda x: f"${x:,.2f}")
            df["price_change_24h"] = df["price_change_24h"].map(lambda x: f"{x:.2f}")
           
            df["price_change_percentage_24h"] = df["price_change_percentage_24h"].map(lambda x: f"{x*100:.2f}%")

            # Renombrar columnas para mostrar en tabla
            df.rename(columns={
                "price_change_24h": "Price Change 24 h",
                "price_change_percentage_24h": "Percentage Change 24 h",
                "current_price": "Current Price",
                "id": "ID",
                "symbol": "Symbol",
                "name": "Name",
                "image": "Image"
            }, inplace=True)

            # Convertimos la columna "image" a etiqueta HTML para mostrar imagen
            def render_image(url):
                return f'<img src="{url}" width="30" />'
            df["Image"] = df["Image"].apply(render_image)

            # Generar tabla HTML 
            table_html = df.to_html(escape=False, index=False)

            # Datos para gráficos
            # Top 10 por current_price 
            df_graph = pd.DataFrame(crypto_list)
            df_graph["current_price_float"] = df_graph["current_price"].astype(float)
            top_10 = df_graph.nlargest(10, "current_price_float")[["symbol", "current_price_float"]]

            # Peores 6 por price_change_percentage_24h (orden ascendente)
            df_graph["price_change_percentage_24h_float"] = df_graph["price_change_percentage_24h"].astype(float)
            worst_6 = df_graph.nsmallest(6, "price_change_percentage_24h_float")[["symbol", "price_change_percentage_24h_float"]]

            # Crear diccionarios para pasar a JSON 
            top_10_chart = {
                "data": [{
                    "type": "bar",
                    "x": top_10["symbol"].tolist(),
                    "y": top_10["current_price_float"].tolist(),
                    "marker": {"color": "purple"}
                }],
                "layout": {
                    "title": "Top 10 Cryptocurrencies by Current Price",
                    "xaxis": {"title": "Symbol"},
                    "yaxis": {"title": "Price (USD)"}
                }
            }

            worst_6_chart = {
                "data": [{
                    "type": "pie",
                    "labels": worst_6["symbol"].tolist(),
                    "values": worst_6["price_change_percentage_24h_float"].abs().tolist(),
                    "marker": {"colors": ["#ff6666", "#ff4d4d", "#ff1a1a", "#cc0000", "#990000", "#660000"]}
                }],
                "layout": {
                    "title": "6 Worst Performing Cryptocurrencies (24h % Change)",
                }
            }

            context = {
                "total_coins": metadata.get("total_coins", 0),
                "top_coin": metadata.get("top_coin", "N/A"),
                "source": "CoinGecko",
                "table_html": table_html,
                "top_10_chart": json.dumps(top_10_chart),
                "worst_6_chart": json.dumps(worst_6_chart),
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
                "symbol", "price_change", "low_price", "high_price"
            ]
            df = pd.DataFrame(binance_data)

            # --- Call Prediction API ---
            try:
                prediction_url = "http://localhost:8000/predictions/binance/"
                response = requests.get(prediction_url)
                response.raise_for_status() 
                predictions_data = response.json().get('predictions', [])
                
                if predictions_data:
                    preds_df = pd.DataFrame(predictions_data)[['symbol', 'prediction']]
                    preds_df['Prediction'] = preds_df['prediction'].apply(lambda x: 'Up' if x == 1 else 'Down')
                    
                    df = pd.merge(df, preds_df[['symbol', 'Prediction']], on='symbol', how='left')
                    # Add 'Prediction' to the columns to show if it's not already there
                    columns_to_show.append('Prediction')

            except requests.exceptions.RequestException as e:
                print(f"Could not get Binance predictions from API: {e}")
                df['Prediction'] = 'N/A' 
            # --- End Prediction API Call ---

            # Filter rows with 0 values in numeric columns AFTER prediction merge
            numeric_cols = ["price_change", "low_price", "high_price"]
            for col in numeric_cols:
                df = df[df[col] != 0]
            
            df = df[columns_to_show] # Apply column selection after merge


            # Formatear números a 4 decimales
            df["price_change"] = df["price_change"].astype(float).map(lambda x: f"{x:.4f}")
            df["low_price"] = df["low_price"].astype(float).map(lambda x: f"{x:.4f}")
            df["high_price"] = df["high_price"].astype(float).map(lambda x: f"{x:.4f}")

            # Renombrar columnas para mostrar
            df.rename(columns={
                "price_change": "Price Change",
                "low_price": "Lowest Price",
                "high_price": "Highest Price",
                "symbol": "Symbol"
            }, inplace=True)

            # Tabla HTML con estilo bootstrap
            table_html = df.to_html(classes="table table-striped", index=False)

            # Preparar datos para gráficos

            # Top 10 mejor evaluados por price_change (mayor a menor)
            df_graph = pd.DataFrame(binance_data)
            df_graph = df_graph[(df_graph["price_change"].astype(float) != 0) &
                                (df_graph["low_price"].astype(float) != 0) &
                                (df_graph["high_price"].astype(float) != 0)]
            df_graph["price_change"] = df_graph["price_change"].astype(float)
            df_graph["low_price"] = df_graph["low_price"].astype(float)
            df_graph["high_price"] = df_graph["high_price"].astype(float)
            top_10 = df_graph.nlargest(10, "price_change")

            # Scatter plot: diferencia High - Low price
            scatter_data = {
                "x": top_10["symbol"].tolist(),
                "y": (top_10["high_price"] - top_10["low_price"]).tolist(),
                "mode": "markers",
                "type": "scatter",
                "marker": {"color": "blue", "size": 10},
            }
            scatter_layout = {
                "title": "Price Difference (High - Low) of Top 10 by Price Change",
                "xaxis": {"title": "Symbol"},
                "yaxis": {"title": "Price Difference"},
            }
            scatter_chart = {"data": [scatter_data], "layout": scatter_layout}

            # Bar horizontal para comparar price_change vs low_price
            bar_data = [
                {
                    "type": "bar",
                    "y": top_10["symbol"].tolist(),
                    "x": top_10["price_change"].tolist(),
                    "name": "Price Change",
                    "orientation": "h",
                    "marker": {"color": "green"},
                },
                {
                    "type": "bar",
                    "y": top_10["symbol"].tolist(),
                    "x": top_10["low_price"].tolist(),
                    "name": "Low Price",
                    "orientation": "h",
                    "marker": {"color": "orange"},
                }
            ]
            bar_layout = {
                "title": "Comparison of Price Change vs Lowest Price (Top 10)",
                "xaxis": {"title": "Value"},
                "barmode": "group",
            }
            bar_chart = {"data": bar_data, "layout": bar_layout}

            context = {
                "total_symbols": metadata.get("total_symbols", 0),
                "top_symbol": metadata.get("top_symbol", "N/A"),
                "source": "Binance API",
                "table_html": table_html,
                "scatter_chart": json.dumps(scatter_chart),
                "bar_chart": json.dumps(bar_chart),
                "symbols": df['Symbol'].unique().tolist()
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
            columns_to_show = ["symbol", "open_price", "high_price", "low_price"]
            df = pd.DataFrame(wazirx_data)

            # --- Call Prediction API ---
            try:
                print("--- Calling WazirX Prediction API ---")
                prediction_url = "http://localhost:8000/predictions/wazirx/"
                response = requests.get(prediction_url)
                response.raise_for_status() 
                predictions_data = response.json().get('predictions', [])
                
                if predictions_data:
                    preds_df = pd.DataFrame(predictions_data)[['symbol', 'prediction']]
                    preds_df['Prediction'] = preds_df['prediction'].apply(lambda x: 'Up' if x == 1 else 'Down')
                    
                    df = pd.merge(df, preds_df[['symbol', 'Prediction']], on='symbol', how='left')
                    columns_to_show.append('Prediction')

            except requests.exceptions.RequestException as e:
                print(f"Could not get WazirX predictions from API: {e}")
                df['Prediction'] = 'N/A' 
            # --- End Prediction API Call ---

            # Solo columnas necesarias
            df = df[columns_to_show]

            # Filtrar ceros
            numeric_cols = ["open_price", "high_price", "low_price"]
            for col in numeric_cols:
                df = df[df[col] != 0]

            # Formatear precios a 4 decimales
            for col in numeric_cols:
                df[col] = df[col].astype(float).map(lambda x: f"{x:.4f}")

            # Renombrar columnas para la tabla
            df.rename(columns={
                "symbol": "Symbol",
                "open_price": "Open Price",
                "high_price": "High Price",
                "low_price": "Low Price"
            }, inplace=True)

            # Gráfico barras actuales: top10 high vs low
            top10 = df.copy()
            # Para gráficas, mejor usar datos sin formatear
            top10_plot = pd.DataFrame(wazirx_data)
            top10_plot = top10_plot[top10_plot["high_price"].astype(float) != 0]
            top10_plot = top10_plot.nlargest(10, "high_price")

            import plotly.express as px
            import plotly

            fig_bar = px.bar(
                top10_plot,
                x="symbol",
                y=["high_price", "low_price"],
                barmode="group",
                title="Top 10 WazirX Pairs: High vs Low Price",
                labels={"value": "Price (INR)", "symbol": "Trading Pair"}
            )

            # Gráfica dinámica 1: línea de precios open_price de top10
            fig_line = px.line(
                top10_plot,
                x="symbol",
                y="open_price",
                title="Open Price of Top 10 WazirX Pairs",
                labels={"open_price": "Open Price (INR)", "symbol": "Trading Pair"},
                markers=True
            )

            # Gráfica dinámica 2: scatter de rango (high-low) vs open_price
            top10_plot["price_range"] = top10_plot["high_price"].astype(float) - top10_plot["low_price"].astype(float)
            fig_scatter = px.scatter(
                top10_plot,
                x="price_range",
                y="open_price",
                text="symbol",
                title="Price Range vs Open Price",
                labels={"price_range": "Price Range (High - Low)", "open_price": "Open Price (INR)"},
                size="open_price",
                color="open_price",
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig_scatter.update_traces(textposition='top center')

            # Convertir todas las figuras a JSON para Plotly.js
            graph_json_bar = json.dumps(fig_bar, cls=plotly.utils.PlotlyJSONEncoder)
            graph_json_line = json.dumps(fig_line, cls=plotly.utils.PlotlyJSONEncoder)
            graph_json_scatter = json.dumps(fig_scatter, cls=plotly.utils.PlotlyJSONEncoder)

            context = {
                "total_symbols": metadata.get("total_symbols", 0),
                "top_symbol": metadata.get("top_symbol", "N/A"),
                "source": "WazirX API",
                "table_html": df.to_html(classes="table table-striped", index=False),
                "graph_json_bar": graph_json_bar,
                "graph_json_line": graph_json_line,
                "graph_json_scatter": graph_json_scatter,
                "symbols": df['Symbol'].unique().tolist()
            }
        else:
            context["warning"] = "No WazirX ticker data found."
    else:
        context["warning"] = "No processed WazirX data found in MongoDB."

    return render(request, "crypto/wazirx_market_data.html", context)
