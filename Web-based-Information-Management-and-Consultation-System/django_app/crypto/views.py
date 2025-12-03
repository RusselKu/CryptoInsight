import requests
import json
import pandas as pd
import numpy as np # Necesario para limpieza de datos
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse # Importación clave para la API
from django.contrib.auth.decorators import login_required

# Importaciones locales
from utils.mongo_conn import get_crypto_market_data, get_binance_tickers, get_wazirx_tickers
from utils.charts import plot_top_cryptos, plot_price_change, plot_binance_volume
from .models import CryptoMarket  # modelo mongoengine
from .forms import CryptoMarketForm  # crear formulario para editar/crear

# ==========================================
# SECCIÓN 1: API ENDPOINTS (NUEVO FRONTEND)
# ==========================================

def api_market_overview(request):
    """
    Endpoint para el nuevo Frontend (React/Vue).
    Devuelve datos JSON crudos en lugar de HTML renderizado.
    Ruta sugerida: /api/market-overview/
    """
    data = get_crypto_market_data()
    
    # Manejo de errores si no hay datos en MongoDB
    if not data or not isinstance(data, list):
        return JsonResponse({
            "status": "error", 
            "message": "No processed crypto data found in MongoDB"
        }, status=404)

    latest = data[0]
    crypto_list = latest.get("crypto_data", [])
    metadata = latest.get("metadata", {})

    if not crypto_list:
         return JsonResponse({
             "status": "warning", 
             "message": "No cryptocurrency data available"
         }, status=200)

    # 1. Preparar DataFrame
    # Definimos columnas base, pero validaremos existencia más adelante
    columns_to_keep = [
        "id", "symbol", "name", "image",
        "current_price", "price_change_24h", "price_change_percentage_24h"
    ]
    df = pd.DataFrame(crypto_list)

    # 2. Lógica de Predicciones (Consumir servicio interno de ML)
    try:
        # Nota: Ajusta 'localhost' si usas nombres de servicios en Docker networks
        prediction_url = "http://localhost:8000/predictions/crypto-predictions/"
        # Timeout para no congelar la vista si la API de ML falla
        response = requests.get(prediction_url, timeout=5) 
        
        if response.status_code == 200:
            predictions_data = response.json().get('predictions', [])
            if predictions_data:
                preds_df = pd.DataFrame(predictions_data)[['symbol', 'prediction']]
                # Convertir 1/0 a texto
                preds_df['Prediction'] = preds_df['prediction'].apply(lambda x: 'Up' if x == 1 else 'Down')
                
                # Merge con el dataframe principal
                df = pd.merge(df, preds_df[['symbol', 'Prediction']], on='symbol', how='left')
                df['Prediction'] = df['Prediction'].fillna('N/A')
        else:
             df['Prediction'] = 'N/A'
    except Exception as e:
        print(f"API Prediction Error: {e}")
        df['Prediction'] = 'N/A'

    # 3. Filtrado y Limpieza Final
    # Solo mantenemos las columnas que existen en el DF actual
    final_cols = [c for c in columns_to_keep if c in df.columns]
    if 'Prediction' in df.columns:
        final_cols.append('Prediction')
    
    df = df[final_cols]

    # IMPORTANTE: JSON no acepta NaN, reemplazamos por 0 o string vacío
    df = df.fillna(0) 
    
    # 4. Generar Datos para Gráficas (Estructura JSON para Plotly)
    df_graph = pd.DataFrame(crypto_list)
    
    # Conversión segura a numérico para gráficas
    df_graph["current_price_float"] = pd.to_numeric(df_graph["current_price"], errors='coerce').fillna(0)
    top_10 = df_graph.nlargest(10, "current_price_float")[["symbol", "current_price_float"]]

    df_graph["price_change_percentage_24h_float"] = pd.to_numeric(df_graph["price_change_percentage_24h"], errors='coerce').fillna(0)
    worst_6 = df_graph.nsmallest(6, "price_change_percentage_24h_float")[["symbol", "price_change_percentage_24h_float"]]

    # Estructuras de datos para Plotly (Frontend las recibirá listas para usar)
    top_10_chart = {
        "data": [{
            "type": "bar",
            "x": top_10["symbol"].tolist(),
            "y": top_10["current_price_float"].tolist(),
            "marker": {"color": "purple"}
        }],
        "layout": {
            "title": "Top 10 Cryptocurrencies by Price", 
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
        "layout": {"title": "Worst 6 Performers (24h Change)"}
    }

    # 5. Respuesta Final
    response_data = {
        "metadata": {
            "total_coins": metadata.get("total_coins", 0),
            "top_coin": metadata.get("top_coin", "N/A"),
            "source": "CoinGecko",
            "last_updated": metadata.get("timestamp", "Now")
        },
        "table_data": df.to_dict(orient="records"),
        "charts": {
            "top_10": top_10_chart,
            "worst_6": worst_6_chart
        }
    }

    return JsonResponse(response_data)


# --- NUEVA API BINANCE ---
def api_binance_data(request):
    data = get_binance_tickers()
    if not data or not isinstance(data, list):
        return JsonResponse({"status": "error", "message": "No data found"}, status=404)

    latest = data[0]
    binance_data = latest.get("binance_data", [])
    metadata = latest.get("metadata", {})

    # Limpieza de datos básica
    df = pd.DataFrame(binance_data)
    # Convertir a float y manejar errores
    cols = ["price_change", "low_price", "high_price"]
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Filtrar ceros
    df = df[(df["price_change"] != 0) & (df["low_price"] != 0)]
    
    # Top 10 para gráficas
    top_10 = df.nlargest(10, "price_change")

    # Construir Gráficas
    scatter_chart = {
        "data": [{
            "x": top_10["symbol"].tolist(),
            "y": (top_10["high_price"] - top_10["low_price"]).tolist(),
            "mode": "markers",
            "type": "scatter",
            "marker": {"color": "#00ff41", "size": 12}, # Verde Matrix
        }],
        "layout": {"title": "Diferencia de Precio (High - Low)"}
    }

    return JsonResponse({
        "metadata": metadata,
        "table_data": df.to_dict(orient="records"),
        "charts": {"scatter": scatter_chart}
    })

# --- NUEVA API WAZIRX ---
def api_wazirx_data(request):
    data = get_wazirx_tickers()
    if not data:
         return JsonResponse({"status": "error", "message": "No data found"}, status=404)
    
    latest = data[0]
    wazirx_data = latest.get("wazirx_data", [])
    
    df = pd.DataFrame(wazirx_data)
    cols = ["high_price", "low_price", "open_price"]
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    df = df[df["high_price"] != 0]
    top_10 = df.nlargest(10, "high_price")

    bar_chart = {
        "data": [
            {"type": "bar", "x": top_10["symbol"].tolist(), "y": top_10["high_price"].tolist(), "name": "High", "marker": {"color": "#00ff41"}},
            {"type": "bar", "x": top_10["symbol"].tolist(), "y": top_10["low_price"].tolist(), "name": "Low", "marker": {"color": "#005515"}}
        ],
        "layout": {"title": "Top 10 WazirX: High vs Low", "barmode": "group"}
    }

    return JsonResponse({
        "metadata": latest.get("metadata", {}),
        "table_data": df.to_dict(orient="records"),
        "charts": {"bar": bar_chart}
    })

# ==========================================
# SECCIÓN 2: VISTAS CRUD (ADMINISTRACIÓN)
# ==========================================

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


# ==========================================
# SECCIÓN 3: VISTAS LEGACY (MONOLITO VIEJO)
# ==========================================

def main_dashboard(request):
    title = "Crypto Dashboard Central"
    
    # Comparison data example
    comparison_data = {
        "Binance": {
            "Description": "One of the largest exchanges worldwide.",
            "URL": "/binance/"
        },
        "WazirX": {
            "Description": "A popular exchange in India.",
            "URL": "/wazirx/"
        }
    }
    
    context = {
        "title": title,
        "comparison_data": comparison_data,
    }
    return render(request, 'crypto/main_dashboard.html', context)


def crypto_market_overview(request):
    """
    Vista original que renderiza HTML. Mantenida para compatibilidad.
    """
    data = get_crypto_market_data()
    context = {}

    if data and isinstance(data, list):
        latest = data[0]
        crypto_list = latest.get("crypto_data", [])
        metadata = latest.get("metadata", {})

        if crypto_list:
            columns_to_show = [
                "id", "symbol", "name", "image",
                "current_price", "price_change_24h", "price_change_percentage_24h"
            ]
            df = pd.DataFrame(crypto_list)

            # --- Call Prediction API ---
            try:
                prediction_url = "http://localhost:8000/predictions/crypto-predictions/"
                response = requests.get(prediction_url)
                response.raise_for_status()
                predictions_data = response.json().get('predictions', [])
                
                if predictions_data:
                    preds_df = pd.DataFrame(predictions_data)[['symbol', 'prediction']]
                    preds_df['Prediction'] = preds_df['prediction'].apply(lambda x: 'Up' if x == 1 else 'Down')
                    
                    df = pd.merge(df, preds_df[['symbol', 'Prediction']], on='symbol', how='left')
                    if 'Prediction' not in columns_to_show:
                        columns_to_show.append('Prediction')

            except requests.exceptions.RequestException as e:
                print(f"Could not get predictions from API: {e}")
                df['Prediction'] = 'N/A'
            
            df = df[columns_to_show]
            # --- End Prediction API Call ---

            # Ajustar formato de columnas numéricas (Solo para vista HTML)
            df["current_price"] = df["current_price"].map(lambda x: f"${x:,.2f}")
            df["price_change_24h"] = df["price_change_24h"].map(lambda x: f"{x:.2f}")
            df["price_change_percentage_24h"] = df["price_change_percentage_24h"].map(lambda x: f"{x*100:.2f}%")

            df.rename(columns={
                "price_change_24h": "Price Change 24 h",
                "price_change_percentage_24h": "Percentage Change 24 h",
                "current_price": "Current Price",
                "id": "ID",
                "symbol": "Symbol",
                "name": "Name",
                "image": "Image"
            }, inplace=True)

            def render_image(url):
                return f'<img src="{url}" width="30" />'
            df["Image"] = df["Image"].apply(render_image)

            table_html = df.to_html(escape=False, index=False)

            # Datos para gráficos
            df_graph = pd.DataFrame(crypto_list)
            df_graph["current_price_float"] = pd.to_numeric(df_graph["current_price"], errors='coerce')
            top_10 = df_graph.nlargest(10, "current_price_float")[["symbol", "current_price_float"]]

            df_graph["price_change_percentage_24h_float"] = pd.to_numeric(df_graph["price_change_percentage_24h"], errors='coerce')
            worst_6 = df_graph.nsmallest(6, "price_change_percentage_24h_float")[["symbol", "price_change_percentage_24h_float"]]

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
                "layout": {"title": "6 Worst Performing Cryptocurrencies (24h % Change)"}
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
            columns_to_show = ["symbol", "price_change", "low_price", "high_price"]
            df = pd.DataFrame(binance_data)

            try:
                prediction_url = "http://localhost:8000/predictions/binance/"
                response = requests.get(prediction_url)
                response.raise_for_status() 
                predictions_data = response.json().get('predictions', [])
                
                if predictions_data:
                    preds_df = pd.DataFrame(predictions_data)[['symbol', 'prediction']]
                    preds_df['Prediction'] = preds_df['prediction'].apply(lambda x: 'Up' if x == 1 else 'Down')
                    df = pd.merge(df, preds_df[['symbol', 'Prediction']], on='symbol', how='left')
                    columns_to_show.append('Prediction')
            except requests.exceptions.RequestException as e:
                print(f"Could not get Binance predictions from API: {e}")
                df['Prediction'] = 'N/A' 

            numeric_cols = ["price_change", "low_price", "high_price"]
            for col in numeric_cols:
                df = df[df[col] != 0]
            
            df = df[columns_to_show]

            df["price_change"] = df["price_change"].astype(float).map(lambda x: f"{x:.4f}")
            df["low_price"] = df["low_price"].astype(float).map(lambda x: f"{x:.4f}")
            df["high_price"] = df["high_price"].astype(float).map(lambda x: f"{x:.4f}")

            df.rename(columns={
                "price_change": "Price Change",
                "low_price": "Lowest Price",
                "high_price": "Highest Price",
                "symbol": "Symbol"
            }, inplace=True)

            table_html = df.to_html(classes="table table-striped", index=False)

            # Preparar datos para gráficos
            df_graph = pd.DataFrame(binance_data)
            # Limpieza para gráficos
            df_graph["price_change"] = pd.to_numeric(df_graph["price_change"], errors='coerce').fillna(0)
            df_graph["low_price"] = pd.to_numeric(df_graph["low_price"], errors='coerce').fillna(0)
            df_graph["high_price"] = pd.to_numeric(df_graph["high_price"], errors='coerce').fillna(0)
            
            df_graph = df_graph[(df_graph["price_change"] != 0) & (df_graph["low_price"] != 0) & (df_graph["high_price"] != 0)]
            top_10 = df_graph.nlargest(10, "price_change")

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

            try:
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

            df = df[columns_to_show]

            numeric_cols = ["open_price", "high_price", "low_price"]
            for col in numeric_cols:
                df = df[df[col] != 0]

            for col in numeric_cols:
                df[col] = df[col].astype(float).map(lambda x: f"{x:.4f}")

            df.rename(columns={
                "symbol": "Symbol",
                "open_price": "Open Price",
                "high_price": "High Price",
                "low_price": "Low Price"
            }, inplace=True)

            # Gráficos usando Plotly Express y conversion manual a JSON (legado)
            import plotly.express as px
            import plotly

            top10 = df.copy()
            top10_plot = pd.DataFrame(wazirx_data)
            top10_plot["high_price"] = pd.to_numeric(top10_plot["high_price"], errors='coerce').fillna(0)
            top10_plot["low_price"] = pd.to_numeric(top10_plot["low_price"], errors='coerce').fillna(0)
            top10_plot = top10_plot[top10_plot["high_price"] != 0]
            top10_plot = top10_plot.nlargest(10, "high_price")

            fig_bar = px.bar(
                top10_plot,
                x="symbol",
                y=["high_price", "low_price"],
                barmode="group",
                title="Top 10 WazirX Pairs: High vs Low Price",
                labels={"value": "Price (INR)", "symbol": "Trading Pair"}
            )

            fig_line = px.line(
                top10_plot,
                x="symbol",
                y="open_price",
                title="Open Price of Top 10 WazirX Pairs",
                labels={"open_price": "Open Price (INR)", "symbol": "Trading Pair"},
                markers=True
            )

            top10_plot["price_range"] = top10_plot["high_price"] - top10_plot["low_price"]
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