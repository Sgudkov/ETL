# Пример ETL-проекта

Этот проект представляет собой минимально базовый, но расширяемый пример ETL-процесса.

## Ключевые компоненты

### DAGs
-   **Регистрация DAGs**: ``@dag.py``
-   **Базовый DAG**: ``@dag_base.py``

### Абстрактный механизм
Реализован гибкий механизм с использованием абстрактных классов, который позволяет легко расширять функционал.
-   **Абстракции**: ``@excel.py``, ``@repositories.py``, ``@unit_of_work.py``
-   **Реализации**: ``@base_sql_repository.py``, ``@sql_uow.py``, ``@excel_processor_base.py``

### Примеры использования
-   **Пример обработки Excel**: ``@excel_processor1.py``
-   **Репозитории для примера**: ``@excel1_repositories.py``

### Локальный запуск без airflow
-   **База для локального запуска**: ``@local_base.py``
-   **Пример локального запуска**: ``@local_run.py``

### Клиенты хранилищ
Гибко настроена работа с внешними хранилищами данных.
-   **Клиент S3 (MinIO)**: ``@minio_client.py``
-   **Клиент PostgreSQL**: ``@postgres_client.py``

## Структура проекта

*   ``dag.py``: Точка входа для регистрации всех DAG-ов.
*   ``dag_base.py``: Базовая реализация DAG, от которой наследуются другие DAG-и.
*   ``excel.py``, ``repositories.py``, ``unit_of_work.py``: Абстрактные классы, определяющие интерфейс для обработки данных, репозиториев и unit of work.
*   ``base_sql_repository.py``, ``sql_uow.py``, ``excel_processor_base.py``: Конкретные реализации абстрактных классов для работы с SQL-базой данных и обработкой Excel-файлов.
*   ``excel_processor1.py``, ``excel1_repositories.py``: Пример использования реализованных абстракций для обработки конкретного Excel-файла.
*   ``local_base.py``, ``local_run.py``: Скрипты для настройки и запуска ETL-процесса в локальной среде.
*   ``minio_client.py``: Клиент для взаимодействия с S3-совместимым хранилищем (например, MinIO).
*   ``postgres_client.py``: Клиент для взаимодействия с базой данных PostgreSQL.


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
 