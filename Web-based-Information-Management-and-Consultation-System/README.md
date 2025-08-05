# **UPY-Crypto-Market-Pipeline (Django + Airflow + MongoDB + Docker)**

Este proyecto implementa un **Pipeline ETL Batch** con **Apache Airflow** para extraer, transformar y cargar datos de 3 APIs principales de criptomonedas.
Los datos se almacenan en **MongoDB** y se visualizan en un **dashboard web con Django**, con rutas específicas para cada fuente y un dashboard central.
La orquestación de servicios se realiza con **Docker Compose**.

---

## 📂 **Estructura del Proyecto**

```
.
├── dags/                           # DAGs de Airflow para ETL
│   ├── binance_ticker_ingestion.py
│   ├── cryptocurrencymarket.py
│   ├── wazirx_ticker_ingestion.py
│   ├── load_mongo.py
│   ├── main_pipeline.py            # Orquestación general
│   └── utils/
│       ├── api_helpers.py
│       └── mongo_utils.py
├── webcrypto/                     # Proyecto Django (app 'crypto')
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
├── docker-compose.yml             # Orquestador de contenedores
├── requirements.txt
├── Dockerfile                    # Imagen Airflow (y Django si aplica)
└── README.md
```

---

## ⚙️ **Tecnologías usadas**

* **Orquestación**: Apache Airflow
* **Backend Web**: Django 5.2
* **Base de datos**: MongoDB
* **Visualización Web**: Django Templates (HTML+Bootstrap opcional)
* **Contenedores**: Docker & Docker Compose
* **Python**: pandas, plotly, pymongo, requests

---

## 🛡️ **Fuentes de datos**

1️⃣ **CoinGecko API**

* Datos globales del mercado (top 100 cryptos, precios, volumen, cambio 24h)
* URL: [https://api.coingecko.com/api/v3/coins/markets](https://api.coingecko.com/api/v3/coins/markets)

2️⃣ **Binance API**

* Tickers 24h para pares de trading (volumen, precios, cambio)
* URL: [https://api4.binance.com/api/v3/ticker/24hr](https://api4.binance.com/api/v3/ticker/24hr)

3️⃣ **WazirX API**

* Tickers con precios contra INR
* URL: [https://api.wazirx.com/sapi/v1/tickers/24hr](https://api.wazirx.com/sapi/v1/tickers/24hr)

---

## 💾 **Pipeline ETL**

* **Extraer** datos raw JSON desde las 3 APIs
* **Transformar** y limpiar datos, agregar metadata y KPIs
* **Cargar** datos procesados en MongoDB, en colecciones `processed_*` y guardar raw en `raw_*`

---

## 🔄 **Airflow DAGs**

* `cryptocurrencymarket.py` (CoinGecko)
* `binance_ticker_ingestion.py` (Binance)
* `wazirx_ticker_ingestion.py` (WazirX)
* `load_mongo.py` (consolidación, si se requiere)
* `main_pipeline.py` (orquestador maestro, dispara DAGs con TriggerDagRunOperator)

---

## 🖥️ **Dashboard Django**

* Rutas configuradas en `crypto/urls.py`:

| Ruta          | Vista                    | Descripción                           |
| ------------- | ------------------------ | ------------------------------------- |
| `/`           | `crypto_market_overview` | Vista general CoinGecko (overview)    |
| `/binance/`   | `binance_market_data`    | Datos y análisis Binance              |
| `/wazirx/`    | `wazirx_market_data`     | Datos y análisis WazirX               |
| `/dashboard/` | `main_dashboard`         | Dashboard central con enlaces a todas |

* Vistas (`crypto/views.py`) utilizan funciones helpers de `utils/mongo_conn.py` para extraer datos de MongoDB.
* Plantillas en `crypto/templates/crypto/` renderizan tablas y gráficos (Plotly.js opcional).

---

## 🗃️ **Colecciones MongoDB**

| Colección                   | Contenido                  |
| --------------------------- | -------------------------- |
| `raw_crypto_market`         | Datos crudos CoinGecko     |
| `processed_crypto_market`   | Datos procesados CoinGecko |
| `raw_binance_tickers`       | Datos crudos Binance       |
| `processed_binance_tickers` | Datos procesados Binance   |
| `raw_wazirx_tickers`        | Datos crudos WazirX        |
| `processed_wazirx_tickers`  | Datos procesados WazirX    |

---

## 🐳 **Docker Compose**

Servicios:

* `mongodb` (puerto 27017)
* `postgresql` (Airflow backend)
* `airflow-webserver` (puerto 8080)
* `airflow-scheduler`
* `django-web` (opcional, si quieres Django en contenedor)
* `streamlit-dashboard` (puerto 8501, opcional si usas Streamlit)

Ejemplo para iniciar:

```bash
docker compose up --build
```

---

## ⚡ **Cómo ejecutar el proyecto**

1. Clonar repo y entrar al proyecto:

```bash
git clone <https://github.com/RusselKu/CryptoInsight>
cd UPY-Crypto-Market-Pipeline
```

2. Inicializar la DB de Airflow:

```bash
docker compose run --rm airflow-webserver airflow db init
```

3. Crear usuario admin de Airflow:

```bash
docker compose run --rm airflow-webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow
```

4. Levantar todos los servicios:

```bash
docker compose up --build
```

5. Acceder a:

* Airflow UI: [http://localhost:8080](http://localhost:8080)
* Dashboard Django: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
* MongoDB Compass (si tienes): `mongodb://root:example@localhost:27017/project_db?authSource=admin`