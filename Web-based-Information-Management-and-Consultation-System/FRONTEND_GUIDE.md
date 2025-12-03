# Frontend Developer Guide

This guide provides an overview of the frontend structure and best practices for working on the Django templates and visualizations for the CryptoInsight project.

## 1. Frontend Overview

The frontend is built using **Django Templates** and **Plotly.js** for charting. The main templates are located in `django_app/crypto/templates/crypto/`.

*   `market_overview.html`: The main dashboard for CoinGecko data.
*   `binance_market_data.html`: The dashboard for Binance data.
*   `wazirx_market_data.html`: The dashboard for WazirX data.
*   `main_dashboard.html`: The central navigation dashboard.

The styling is done using a combination of inline CSS and a static CSS file located at `django_app/crypto/static/crypto/css/styles.css`.

## 2. Data Flow

The data is passed from the Django views in `django_app/crypto/views.py` to the templates as a context dictionary.

The main data for the tables is passed as a pre-rendered HTML string in the `table_html` context variable. This is done for simplicity, but it's not ideal for a modern frontend.

**⚠️ Warning:** Modifying the table structure requires changes in the `views.py` file, not in the HTML templates. The `df.to_html()` function in the views generates the table.

The data for the charts is passed as a JSON string in context variables like `scatter_chart`, `bar_chart`, `graph_json_bar`, etc. This JSON is then parsed by the JavaScript in the templates to render the charts using Plotly.js.

## 3. Working with Charts

The charts are rendered using **Plotly.js**. The chart data and layout are defined in the views and passed to the templates as JSON strings.

### **Existing Charts**
The existing charts are rendered with a script block in each template. The JSON data is parsed and then passed to `Plotly.newPlot()`.

### **Interactive Historical Charts**
The Binance and WazirX pages have interactive historical charts. The logic for these charts is in the `<script>` tag at the bottom of the `binance_market_data.html` and `wazirx_market_data.html` files.

The workflow is:
1.  The user selects a symbol from the dropdown menu.
2.  The user clicks the "Load Chart" button.
3.  A JavaScript event listener fetches the historical data from the corresponding API endpoint (e.g., `/predictions/binance/history/<symbol>/`).
4.  The JSON response is parsed, and a new Plotly chart is rendered in the `historical-chart` div.

**💡 Tip:** To modify the appearance of the charts, you can either change the layout dictionary in the `views.py` file or manipulate the layout object in the JavaScript before calling `Plotly.newPlot()`.

## 4. Development Best Practices & Warnings

To avoid breaking the application, please follow these guidelines:

*   **Check for `None` or empty data:** The data passed from the views can sometimes be empty if the underlying APIs fail. The templates use `{% if warning %}` to check for this and display a warning message. Always make sure your new frontend components handle cases where the data is not available.

*   **Symbol format:** Be mindful of the different symbol formats used by the APIs. For example, WazirX symbols are in the format `btcinr`, while the historical API for WazirX expects the symbol without the `inr` suffix. The JavaScript code in the templates handles this, but it's a potential source of errors.

*   **Django's Auto-Reload:** The Django development server has an auto-reload feature that automatically restarts the server when you make changes to Python files. However, as we experienced, sometimes a full container restart is necessary for changes to be applied correctly, especially after fixing critical errors like `ImportError`. If you make changes and don't see them reflected, try restarting the Django container:
    ```bash
    docker compose restart django
    ```
    If that doesn't work, a full rebuild is the next step:
    ```bash
    docker compose down
    docker compose up --build -d
    ```

*   **Browser Cache:** Your browser might cache the old version of the pages. If you don't see your changes, try a hard refresh (Ctrl+F5 or Cmd+Shift+R).

*   **Debugging:** Use the browser's developer tools (especially the JavaScript console) to check for any frontend errors. The Django logs are also invaluable for debugging backend issues. You can view them with:
    ```bash
    docker logs -f web-based-information-management-and-consultation-system-django-1
    ```

By following these guidelines, you can help ensure a smooth development process and avoid introducing new issues.
