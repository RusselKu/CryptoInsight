# **UPY-Crypto-Market-Pipeline (Django + Airflow + MongoDB + Docker)**

This project implements a **Batch ETL Pipeline** using **Apache Airflow** to extract, transform, and load cryptocurrency data from 3 main APIs.
The data is stored in **MongoDB** and visualized via a **Django web dashboard**, featuring dedicated routes for each data source and a central overview dashboard.
It also includes a **Machine Learning component** to predict cryptocurrency price movements.
Service orchestration is handled with **Docker Compose**.

---

## 📂 **Project Structure**

```
.
├── dags/                           # Airflow DAGs for ETL and ML
│   ├── binance_ticker_ingestion.py
│   ├── cryptocurrencymarket.py
│   ├── wazirx_ticker_ingestion.py
│   ├── retrain_model_dag.py        # Retrains all predictive models
│   ├── main_pipeline.py            # Master orchestration
│   └── utils/
│       ├── api_helpers.py
│       └── mongo_utils.py
├── django_app/                     # Django project
│   ├── crypto/                     # Main crypto app for views and templates
│   │   ├── templates/crypto/
│   │   │   ├── market_overview.html
│   │   │   ├── binance_market_data.html
│   │   │   ├── wazirx_market_data.html
│   │   │   └── main_dashboard.html
│   │   ├── views.py
│   │   └── urls.py
│   ├── predictions/                # App for ML models and predictions
│   │   ├── train_model.py          # CoinGecko model training
│   │   ├── train_binance.py        # Binance model training
│   │   ├── train_wazirx.py         # WazirX model training
│   │   ├── views.py                # API endpoints for predictions
│   │   └── urls.py
│   ├── utils/                      # Utility functions (db connection)
│   └── webcrypto/                  # Django project settings
├── docker-compose.yml             # Container orchestrator
├── requirements.txt
├── Dockerfile                    # Airflow  image
└── README.md
```

---

## ⚙️ **Technologies Used**

* **Orchestration:** Apache Airflow
* **Web Backend:** Django
* **Database:** MongoDB
* **Web Visualization:** Django Templates, Plotly.js
* **Containers:** Docker & Docker Compose
* **Machine Learning:** Scikit-learn
* **Python Libraries:** pandas, plotly, pymongo, requests, scikit-learn

---

## 🛡️ **Data Sources**

1️⃣ **CoinGecko API**

* Global market data (top 100 cryptos, prices, volume, 24h change)
* URL: [https://api.coingecko.com/api/v3/coins/markets](https://api.coingecko.com/api/v3/coins/markets)

2️⃣ **Binance API**

* 24h tickers for trading pairs (volume, prices, changes)
* URL: [https://api4.binance.com/api/v3/ticker/24hr](https://api4.binance.com/api/v3/ticker/24hr)

3️⃣ **WazirX API**

* Tickers priced against INR
* URL: [https://api.wazirx.com/sapi/v1/tickers/24hr](https://api.wazirx.com/sapi/v1/tickers/24hr)

---

## 🖥️ **Django Dashboard Features**

The web dashboard provides a comprehensive overview of the cryptocurrency market from the three data sources.

### **1. Main Dashboards**
*   **CoinGecko Overview:** Displays a table with the top 100 cryptocurrencies, their prices, and 24h price changes. Includes charts for the top 10 best and worst performing assets.
*   **Binance Market Data:** Shows a filtered list of active trading pairs from Binance, with their price changes and high/low prices.
*   **WazirX Market Data:** Displays active trading pairs from WazirX, with open, high, and low prices.

### **2. Predictive Models**
For each data source, a **Logistic Regression** model predicts whether the price will **increase (Up)** or **decrease (Down)** in the next 24 hours. The "Prediction" column is displayed in the main table for each data source.

### **3. Interactive Historical Charts**
On the Binance and WazirX pages, users can select a trading pair from a dropdown menu to view an interactive historical chart of its price over time. This allows for a more detailed analysis of the asset's performance.

---

## 🚀 **Machine Learning Pipeline**

The project includes a full machine learning pipeline for price movement prediction, from data processing to automated retraining.

### **1. Training Pipelines**
*   Dedicated training scripts (`train_model.py`, `train_binance.py`, `train_wazirx.py`) are used for each data source.
*   **Feature Engineering:** Custom feature engineering is applied to each dataset to prepare it for training.
*   **Model Training:** A `LogisticRegression` model is trained for each data source.
*   **Artifact Saving:** The trained models and scalers are saved as `.joblib` files.

### **2. Prediction APIs**
*   The `predictions` Django app exposes API endpoints to get predictions for each data source.
*   These APIs are called by the frontend to display the "Prediction" column.

### **3. Historical Data APIs**
*   The `predictions` app also provides API endpoints to get historical price data for a given symbol, which is used to power the interactive charts.

---

## 🔄 **Airflow DAGs**

*   **ETL DAGs:**
    *   `cryptocurrencymarket.py`: Ingests data from CoinGecko.
    *   `binance_ticker_ingestion.py`: Ingests data from Binance.
    *   `wazirx_ticker_ingestion.py`: Ingests data from WazirX.
*   **ML DAG:**
    *   `retrain_model_dag.py`: Automatically retrains all three predictive models (CoinGecko, Binance, and WazirX) on a daily schedule to prevent model drift.
*   **Orchestration DAG:**
    *   `main_pipeline.py`: A master DAG that orchestrates the execution of all other DAGs.

---

## 🗃️ **MongoDB Collections**

| Collection                  | Content                  |
| --------------------------- | ------------------------ |
| `raw_crypto_market`         | Raw CoinGecko data       |
| `processed_crypto_market`   | Processed CoinGecko data |
| `raw_binance_tickers`       | Raw Binance data         |
| `processed_binance_tickers` | Processed Binance data   |
| `raw_wazirx_tickers`        | Raw WazirX data          |
| `processed_wazirx_tickers`  | Processed WazirX data    |

---

## 🐳 **Docker Compose Services**

* `mongodb` (default port 27017)
* `postgres` (Airflow metadata database)
* `webserver` (Airflow webserver, port 8080)
* `scheduler` (Airflow scheduler)
* `django` (Django web application, port 8000)

---

## ⚡ **How to Run the Project**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RusselKu/CryptoInsight.git
    cd Web-based-Information-Management-and-Consultation-System
    ```

2.  **Initialize the Airflow database:**
    ```bash
    docker compose run --rm webserver airflow db init
    ```

3.  **Create an Airflow admin user:**
    ```bash
    docker compose run --rm webserver airflow users create \
        --username airflow \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password airflow
    ```

4.  **Build and start all containers:**
    ```bash
    docker compose up --build -d
    ```

5.  **Access the services:**
    *   **Airflow UI:** [http://localhost:8080](http://localhost:8080)
    *   **Django Dashboard:** [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
    *   **MongoDB Compass (optional):**
        `mongodb://root:example@localhost:27017/project_db?authSource=admin`

6.  **Train the predictive models:**
    To see the predictions, you need to run the training scripts for each model at least once.
    ```bash
    docker compose exec django python /app/predictions/train_model.py
    docker compose exec django python /app/predictions/train_binance.py
    docker compose exec django python /app/predictions/train_wazirx.py
    ```

---

## 🛠️ **Custom Django Admin Panel and Security**

A custom admin panel was implemented within the `crypto` app to manage cryptocurrency data from the Django backend, using MongoDB as the main database via `mongoengine`.

### 1. Model Registration in Custom Admin

* The `ProcessedCryptoMarket` model was registered in `crypto/admin.py` to make it manageable through Django’s standard admin interface.
* Due to incompatibilities with `mongoengine.django.admin`, the native Django admin was used without inheriting from `DocumentAdmin`.

```python
from django.contrib import admin
from .models import ProcessedCryptoMarket

@admin.register(ProcessedCryptoMarket)
class ProcessedCryptoMarketAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'price', 'volume_24h', 'market_cap', 'last_updated')
    search_fields = ('symbol', 'name')
```

### 2. Securing Views with Login Required

* The custom CRUD views (`crypto_list`, `crypto_create`, `crypto_edit`, `crypto_delete`) were protected with the `@login_required` decorator to restrict access only to authenticated users.

```python
from django.contrib.auth.decorators import login_required

@login_required
def crypto_list(request):
    # logic...

@login_required
def crypto_create(request):
    # logic...
```

### 3. Creating the Superuser

* A superuser was created inside the Django container to enable access to the Django admin interface:

```bash
docker-compose exec django python manage.py createsuperuser
```

* This allowed managing users and data at `http://localhost:8000/admin/login/`.

### 4. URLs for the Custom Admin Panel

* The `crypto/urls.py` file defines the routes for the custom admin panel views:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('admin/cryptomarket/', views.crypto_list, name='crypto_list'),
    path('admin/cryptomarket/add/', views.crypto_create, name='crypto_create'),
    path('admin/cryptomarket/edit/<str:pk>/', views.crypto_edit, name='crypto_edit'),
    path('admin/cryptomarket/delete/<str:pk>/', views.crypto_delete, name='crypto_delete'),
]
```

* These routes allow creating, editing, listing, and deleting cryptocurrencies through the protected interface.

### 5. Django Login Configuration

* The login URL was configured in `webcrypto/settings.py` to redirect unauthenticated users to the default Django admin login page:

```python
LOGIN_URL = '/admin/login/'
```
