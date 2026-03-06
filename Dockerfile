# Используем базовый образ Airflow
FROM apache/airflow:2.6.3-python3.10

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow-providers-postgres==6.5.3" \
    "apache-airflow-providers-amazon==9.21.0" \
    "sqlalchemy<2.0" \
    "pydantic<2.0" \
    "openpyxl==3.1.2" \
    "minio==7.2.7" \
    "pandas==2.1.4" \
    "psycopg2-binary==2.9.9"
