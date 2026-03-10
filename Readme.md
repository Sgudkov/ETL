# Пример ETL-проекта

Этот проект представляет собой минимально базовый, но расширяемый пример ETL-процесса.

## Ключевые компоненты

### DAGs
-   **Регистрация DAGs**: ``dags/dag.py``
-   **Базовый DAG**: ``dags/core/airflow/dag_base.py``

### Абстрактный механизм
Реализован гибкий механизм с использованием абстрактных классов, который позволяет легко расширять функционал.
-   **Абстракции**: ``dags/core/domain/base_processor.py``, ``dags/core/domain/base_repositories.py``, ``dags/core/domain/unit_of_work.py``
-   **Реализации**: ``dags/core/infrastructure/postgres/base_postgres_repository.py``, ``dags/core/infrastructure/postgres/postgres_uow.py`` 

### Примеры использования
-   **Пример обработки Excel**: ``dags/processors/processor_1/processor.py``
-   **Репозитории для примера**: ``dags/processors/processor_1/repositories/excel1_repositories.py``

### Локальный запуск без airflow
-   **База для локального запуска**: ``dags/core/airflow/local_base.py``
-   **Пример локального запуска**: ``dags/etl_local/local_run.py``

### Клиенты хранилищ
Гибко настроена работа с внешними хранилищами данных.
-   **Клиент S3 (MinIO)**: ``dags/core/infrastructure/minio/minio_client.py``
-   **Клиент PostgreSQL**: ``dags/core/infrastructure/postgres/postgres_client.py``

## Структура проекта

*   ``dag.py``: Точка входа для регистрации всех DAG-ов.
*   ``dag_base.py``: Базовая реализация DAG, от которой наследуются другие DAG-и.
*   ``base_processor.py``, ``base_repositories.py``, ``unit_of_work.py``: Абстрактные классы, определяющие интерфейс для обработки данных, репозиториев и unit of work.
*   ``base_postgres_repository.py``, ``postgres_uow.py``: Конкретные реализации абстрактных классов для работы с SQL-базой данных и обработкой Excel-файлов.
*   ``dags/processors/processor_1/processor.py``, ``dags/processors/processor_1/repositories/excel1_repositories.py``: Пример использования реализованных абстракций для обработки конкретного Excel-файла.
*   ``dags/core/airflow/local_base.py``, ``dags/etl_local/local_run.py``: Скрипты для настройки и запуска ETL-процесса в локальной среде.
*   ``dags/core/infrastructure/minio/minio_client.py``: Клиент для взаимодействия с S3-совместимым хранилищем (например, MinIO).
*   ``dags/core/infrastructure/postgres/postgres_client.py``: Клиент для взаимодействия с базой данных PostgreSQL.


## Локальный запуск

### Установка зависимостей
1. Poetry install

### Запуск Docker
1.  Убедитесь, что Docker и Docker Compose установлены.
2.  Запустите контейнеры, используя PostgreSQL и MinIO:
    ```bash
    docker-compose up -d
    ```

### Настройка MinIO
1.  Создайте бакет `excelbucket`.
2.  Внутри `excelbucket` создайте папки `success` и `error`.
3.  Поместите файл `test.xlsx` из папки `data` вашего проекта в корневую директорию бакета `excelbucket`.

### Настройка Airflow Connections
1.  **minio_default**:
    *   **Login**: `admin`
    *   **Password**: `password`
    *   **Extra**:
        ```json
        {
            "endpoint_url": "http://minio:9000"
        }
        ```
2.  **pg_default**:
    *   **Host**: `host.docker.internal`
    *   **Port**: `5433`
    *   **Schema**: `postgres`
    *   **Login**: `airflow`
    *   **Password**: `airflow`

### Запуск ETL
После выполнения вышеуказанных шагов, ETL-процесс готов к запуску. Вы можете запустить его, используя скрипт `@local_run.py` или через интерфейс Airflow.

---
 