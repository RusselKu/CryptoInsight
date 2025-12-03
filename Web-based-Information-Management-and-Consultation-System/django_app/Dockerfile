FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Migraciones iniciales (puedes comentarlo si no tienes el proyecto creado aún)
# RUN python manage.py migrate

# Exponer el puerto por defecto de Django
EXPOSE 8000

# Comando para ejecutar el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
