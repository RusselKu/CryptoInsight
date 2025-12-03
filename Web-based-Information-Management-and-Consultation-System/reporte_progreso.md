# Reporte de Progreso: Implementación de Modelo Predictivo

Este documento detalla el progreso, los desafíos y los próximos pasos en la implementación de un modelo de regresión logística para la predicción de movimientos de precios de criptomonedas.

**Última actualización: 2 de Diciembre, 2025 - ¡Fase 1 Completada!**

## 1. Resumen del Objetivo

El objetivo principal de esta fase fue desarrollar e integrar un modelo de machine learning (Regresión Logística) dentro del proyecto `UPY-Crypto-Market-Pipeline`. El modelo busca predecir si el precio de una criptomoneda aumentará o disminuirá en las próximas 24 horas, utilizando los datos de la API de CoinGecko.

## 2. Progreso Realizado

Se han completado todas las tareas planificadas para la implementación del modelo predictivo.

### 2.1. Análisis Inicial y Planificación

Se analizaron los documentos del proyecto, se identificó una discrepancia entre el plan original y el estado actual del proyecto, y se propuso un nuevo plan de implementación, el cual fue aprobado.

### 2.2. Configuración del Entorno de Desarrollo

Se creó y configuró una nueva app de Django (`predictions`) para alojar la lógica del modelo, incluyendo la gestión de dependencias y la configuración del entorno Docker.

### 2.3. Análisis Exploratorio de Datos (EDA)

Se estableció una conexión robusta con la base de datos MongoDB desde el entorno de Docker y se analizó la estructura de los datos, superando desafíos de autenticación y formato de documentos.

### 2.4. Ingeniería de Características y Entrenamiento del Modelo

Se crearon scripts modulares para el preprocesamiento de datos y el entrenamiento del modelo. El modelo de Regresión Logística fue entrenado y evaluado con éxito, y los artefactos resultantes (modelo y escalador) fueron guardados para su uso en producción.

### 2.5. Creación del API de Predicciones

Se desarrolló un endpoint de API (`/predictions/crypto-predictions/`) capaz de cargar el modelo entrenado y servir predicciones en tiempo real en formato JSON.

### 2.6. Integración con el Frontend

Se modificó la vista principal (`crypto_market_overview`) para consumir la API de predicciones. Los resultados se integraron exitosamente en la tabla principal, mostrando una nueva columna "Prediction" (Up/Down) junto a cada criptomoneda.

### 2.7. Automatización con Airflow

Se creó un nuevo DAG en Airflow (`retrain_crypto_prediction_model`) que automatiza el re-entrenamiento del modelo, asegurando que se mantenga actualizado con los datos más recientes.

## 3. Errores Encontrados y Soluciones

Durante el desarrollo, se encontraron y solucionaron diversos problemas, desde errores de configuración del entorno y la base de datos hasta la gestión de dependencias en Docker y el manejo de la estructura de datos anidada en MongoDB. Todas estas soluciones han sido documentadas y aplicadas.

## 4. Estado Actual

**¡Implementación completada!** Todas las tareas planeadas se han finalizado con éxito. El sistema ahora cuenta con un modelo de predicción funcional, una API para servir los resultados y una integración visible en el frontend, además de un pipeline de re-entrenamiento automatizado.

## 5. Próximos Pasos

A petición del usuario, los siguientes pasos se centrarán en:

1.  **Documentación Final:** Actualizar el `README.md` principal para reflejar la nueva funcionalidad del modelo predictivo.
2.  **Expansión del Modelo:** Idear e implementar funcionalidades predictivas similares para las otras fuentes de datos del proyecto (Binance y WazirX), incluyendo nuevas visualizaciones y gráficos.

---
## Reporte de Progreso: Expansión de Modelos Predictivos

**Última actualización: 3 de Diciembre, 2025**

### Fase 2: Modelos para Binance y WazirX

*   **Completado:** Se ha finalizado la creación de los pipelines de entrenamiento para los modelos de Binance y WazirX.
    *   Se crearon los scripts `train_binance.py` y `train_wazirx.py`.
    *   Se implementaron los data loaders `data_loader_binance.py` y `data_loader_wazirx.py`.
    *   Se desarrollaron los scripts de feature engineering `feature_engineering_binance.py` y `feature_engineering_wazirx.py`, adaptados a las estructuras de datos de cada API.

*   **Completado:** Creación de los endpoints de API para las predicciones de Binance y WazirX.
    *   Se modificó `django_app/predictions/views.py` para añadir las funciones `predict_binance` y `predict_wazirx`.
    *   Se modificó `django_app/predictions/urls.py` para registrar las nuevas rutas.

*   **Completado:** Integración de los nuevos endpoints con el frontend.
    *   Se modificó `django_app/crypto/views.py` para llamar a las nuevas APIs de predicción.
    *   Se corrigieron errores (`NameError`, `ImportError`) que surgieron durante la integración.
    *   Se entrenaron los modelos de Binance y WazirX para que las predicciones se muestren correctamente.

*   **Completado:** Creación de la API de datos históricos.
    *   Se modificó `django_app/utils/mongo_conn.py` para añadir las funciones `get_historical_binance_data` y `get_historical_wazirx_data`.
    *   Se modificó `django_app/predictions/views.py` para añadir las funciones `historical_binance_data` y `historical_wazirx_data`.
    *   Se modificó `django_app/predictions/urls.py` para registrar las nuevas rutas de datos históricos.

*   **Completado:** Implementación de gráficos interactivos en el frontend.
    *   Se modificaron las plantillas `binance_market_data.html` y `wazirx_market_data.html` para añadir los nuevos gráficos.
    *   Se añadió el código JavaScript necesario para la interactividad.

### Estado Final de la Fase 2

**¡Implementación completada!** Todas las funcionalidades propuestas para la expansión de los modelos predictivos y las nuevas visualizaciones interactivas han sido implementadas y depuradas con éxito.