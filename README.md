# **UPY-Crypto-Market-Pipeline (Django + Airflow + MongoDB + Docker)**

This project implements a **Batch ETL Pipeline** using **Apache Airflow** to extract, transform, and load cryptocurrency data from 3 main APIs.
The data is stored in **MongoDB** and visualized via a **Django web dashboard**, featuring dedicated routes for each data source and a central overview dashboard.
Service orchestration is handled with **Docker Compose**.

---

## 📂 **Project Structure**

```
.
├── dags/                           # Airflow DAGs for ETL
│   ├── binance_ticker_ingestion.py
│   ├── cryptocurrencymarket.py
│   ├── wazirx_ticker_ingestion.py
│   ├── load_mongo.py
│   ├── main_pipeline.py            # Master orchestration
│   └── utils/
│       ├── api_helpers.py
│       └── mongo_utils.py
├── webcrypto/                     # Django project (app 'crypto')
│   ├── crypto/
│   │   ├── templates/crypto/
│   │   │   ├── market_overview.html
│   │   │   ├── binance_market_data.html
│   │   │   ├── wazirx_market_data.html
│   │   │   └── main_dashboard.html
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ...
│   ├── webcrypto/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   └── manage.py
├── docker-compose.yml             # Container orchestrator
├── requirements.txt
├── Dockerfile                    # Airflow (and optionally Django) image
└── README.md
```

---

## ⚙️ **Technologies Used**

* **Orchestration:** Apache Airflow
* **Web Backend:** Django 5.2
* **Database:** MongoDB
* **Web Visualization:** Django Templates (HTML + optional Bootstrap)
* **Containers:** Docker & Docker Compose
* **Python Libraries:** pandas, plotly, pymongo, requests

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

## 💾 **ETL Pipeline**

* **Extract:** Raw JSON data from the 3 APIs
* **Transform:** Data cleaning, metadata enrichment, KPI calculations
* **Load:** Processed data stored in MongoDB collections `processed_*`, raw data stored in `raw_*` collections

---

## 🔄 **Airflow DAGs**

* `cryptocurrencymarket.py` (CoinGecko data ingestion)
* `binance_ticker_ingestion.py` (Binance data ingestion)
* `wazirx_ticker_ingestion.py` (WazirX data ingestion)
* `load_mongo.py` (optional consolidation)
* `main_pipeline.py` (master orchestrator, triggers all DAGs with TriggerDagRunOperator)

---

## 🖥️ **Django Dashboard**

* Routes configured in `crypto/urls.py`:

| Route         | View                     | Description                       |
| ------------- | ------------------------ | --------------------------------- |
| `/`           | `crypto_market_overview` | CoinGecko general market overview |
| `/binance/`   | `binance_market_data`    | Binance market data and analysis  |
| `/wazirx/`    | `wazirx_market_data`     | WazirX market data and analysis   |
| `/dashboard/` | `main_dashboard`         | Central dashboard with links      |

* Views (`crypto/views.py`) use helper functions in `utils/mongo_utils.py` to query MongoDB.
* Templates located in `crypto/templates/crypto/` render tables and interactive Plotly.js charts.

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
* `postgresql` (Airflow metadata database)
* `airflow-webserver` (port 8080)
* `airflow-scheduler`
* `django-web` (optional, for Django app container)
* `streamlit-dashboard` (optional, port 8501 if using Streamlit frontend)

Start all services:

```bash
docker compose up --build
```

---

## ⚡ **How to Run the Project**

1. Clone the repository and enter the project folder:

```bash
git clone https://github.com/RusselKu/CryptoInsight.git
cd UPY-Crypto-Market-Pipeline
```

2. Initialize the Airflow database:

```bash
docker compose run --rm airflow-webserver airflow db init
```

3. Create an Airflow admin user:

```bash
docker compose run --rm airflow-webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow
```

4. Build and start all containers:

```bash
docker compose up --build
```

5. Access the services:

* Airflow UI: [http://localhost:8080](http://localhost:8080)
* Django Dashboard: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
* MongoDB Compass:
  `mongodb://root:example@localhost:27017/project_db?authSource=admin`
  docker exec -it web-based-information-management-and-consultation-system-mongodb-1 mongosh -u root -p example --authenticationDatabase admin


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
