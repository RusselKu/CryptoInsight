import plotly.express as px
import pandas as pd

# ----- Charts for Cryptocurrency Market -----
def plot_top_cryptos(data, top_n=10):
    """
    Bar chart for top N cryptocurrencies by market cap.
    """
    df = pd.DataFrame(data)
    df = df.sort_values(by="market_cap", ascending=False).head(top_n)
    fig = px.bar(
        df,
        x="name",
        y="market_cap",
        text="market_cap_rank",
        title=f"Top {top_n} Cryptocurrencies by Market Cap",
        labels={"name": "Cryptocurrency", "market_cap": "Market Cap (USD)"},
        color="market_cap",
        color_continuous_scale="Blues"
    )
    fig.update_traces(texttemplate="#%{text}", textposition="outside")
    return fig

def plot_price_change(data, top_n=10):
    """
    Horizontal bar chart for price change percentage in 24h.
    """
    df = pd.DataFrame(data)
    df = df.sort_values(by="price_change_percentage_24h", ascending=False).head(top_n)
    fig = px.bar(
        df,
        x="price_change_percentage_24h",
        y="name",
        orientation="h",
        title="Top Movers (24h % Change)",
        labels={"price_change_percentage_24h": "% Change (24h)", "name": "Cryptocurrency"},
        color="price_change_percentage_24h",
        color_continuous_scale="RdYlGn"
    )
    return fig

# ----- Charts for Binance Tickers -----
def plot_binance_volume(data, top_n=10):
    """
    Bar chart for Binance trading pairs by base volume.
    """
    df = pd.DataFrame(data)
    df["volume_base"] = df["volume_base"].astype(float)
    df = df.sort_values(by="volume_base", ascending=False).head(top_n)
    fig = px.bar(
        df,
        x="symbol",
        y="volume_base",
        title=f"Top {top_n} Binance Pairs by Base Volume",
        labels={"symbol": "Trading Pair", "volume_base": "Volume (Base Asset)"},
        color="volume_base",
        color_continuous_scale="Purples"
    )
    return fig

# ----- Charts for WazirX -----
def plot_wazirx_prices(data, top_n=10):
    """
    Bar chart for WazirX crypto prices in INR.
    """
    df = pd.DataFrame(data)

    # ✅ Detect correct column name (camelCase vs snake_case)
    price_col = "lastPrice" if "lastPrice" in df.columns else "last_price"

    df[price_col] = df[price_col].astype(float)
    df = df.sort_values(by=price_col, ascending=False).head(top_n)

    fig = px.bar(
        df,
        x="symbol",
        y=price_col,
        title=f"Top {top_n} WazirX Prices (INR)",
        labels={"symbol": "Trading Pair", price_col: "Price (INR)"},
        color=price_col,
        color_continuous_scale="Oranges"
    )
    return fig
