import logging
from typing import Type, TypeVar

import pendulum
from airflow.decorators import task, task_group
from airflow.models.dag import dag
from config.settings import settings
from core.dag_base import DagBase
from core.excel_processor_base import ExcelProcessorBase
from processors import * # необходимо для регистрации дагов

logger = logging.getLogger(__name__)


def handle_file_failure(context):
    """Callback обработчик перемещает файл в папку ошибки"""
    logger.info(f'Перемещаем в ошибку, контекст {context}')
    processed_data = context["file_metadata"]
    DagBase.move_file_to(
        processed_data=processed_data,
        success_path=settings.SUCCESS_PATH,
        error_path=settings.ERROR_PATH,
        s3_conn_id=settings.S3_CONN_ID
    )


T = TypeVar("T", bound=ExcelProcessorBase)


def create_dag(processor_cls: Type[T]):
    @dag(
        dag_id=processor_cls.dag_id,
        schedule=processor_cls.schedule,
        catchup=False,
        max_active_runs=1,  # Только 1 dag активен в единицу времени
        max_active_tasks=10,  # Ограничим кол-во параллельных @task_group
        start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
        tags=["excel_loader"],
    )
    def processing_dag():
        @task
        def init_validate() -> bool:
            """Проверка соединений и инициализация данных"""

            return DagBase.init_validate(
                bucket=settings.MINIO_BUCKET,
                s3_conn_id=settings.S3_CONN_ID,
                pg_conn_id=settings.PG_CONN_ID,
                processor_cls=processor_cls
            )

        @task
        def get_file_list() -> list:
            """Получение списка файлов из MinIO"""

            return DagBase.get_file_list(
                bucket=settings.MINIO_BUCKET,
                s3_conn_id=settings.S3_CONN_ID
            )

        # Запустим всё одной группе
        @task_group(group_id="process_pipeline")
        def process_file_pipeline(file_info: dict):
            @task(on_failure_callback=handle_file_failure)
            def process_file(file_metadata: dict) -> dict:
                """Обработка одного файла"""

                return DagBase.process_file(
                    file_metadata=file_metadata,
                    bucket=settings.MINIO_BUCKET,
                    s3_conn_id=settings.S3_CONN_ID,
                    pg_conn_id=settings.PG_CONN_ID,
                    processor_cls=processor_cls
                )

            @task
            def move_files(processed_data: dict):
                """Перемещение обработанных файлов"""
                DagBase.move_file_to(
                    processed_data=processed_data,
                    success_path=settings.SUCCESS_PATH,
                    error_path=settings.ERROR_PATH,
                    s3_conn_id=settings.S3_CONN_ID
                )

            processed = process_file(file_metadata=file_info)
            move_files(processed_data=processed)

        is_valid = init_validate()

        # Получаем список файлов
        files = get_file_list()

        # Установим зависимость
        is_valid >> files

        # Для каждого файла запускам изолированный pipline параллельно
        process_file_pipeline.expand(file_info=files)

    return processing_dag()


# Создаем DAG
for cls in ExcelProcessorBase.__subclasses__():
    if hasattr(cls, 'dag_id'):
        globals()[cls.dag_id] = create_dag(cls)
